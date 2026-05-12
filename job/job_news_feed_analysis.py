"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any

import finfilo
from elasticsearch import Elasticsearch, helpers
from staffs import get_analysis_model_by_setting
from service import MarketNewsService
from service.stock_star_news import StockStarNewsScraper
from service.wallstreet_fetcher import WallStreetCNFetcher
from utils.common import string_to_md5, logger, timestamp_to_date
from staffs.prompts import prompt_155th
from prompts.prompt_generator import load_prompt_template
from backtest.text_embedding import get_embedding
from config import elasticsearch_setting

CURRENT_DIR = Path(__file__).parent

# ================= 配置常量 =================
INDEX_NAME = 'news_feed_v1'
VECTOR_FIELD = 'vector'
DEFAULT_VECTOR_DIMS = 1024  # ⚠️ 请根据实际使用的Embedding模型调整该值
EMBEDDING_TEXT_SEP = " | "

# ================= 基础设施初始化 =================
es_client = Elasticsearch(
    elasticsearch_setting['host'],
    basic_auth=(elasticsearch_setting['username'], elasticsearch_setting['password'])
)
analysis_model = get_analysis_model_by_setting('news_analysis')
analysis_model.set_response_json()
prompt_template = load_prompt_template(template_path=CURRENT_DIR / "prompt_news_analysis.md")


def _ensure_es_index() -> None:
    """确保Elasticsearch索引及Mapping已存在"""
    if not es_client.indices.exists(index=INDEX_NAME):
        mapping = {
            "mappings": {
                "properties": {
                    "digest": {"type": "text"},  # AI摘要/标题
                    "content": {"type": "text"},  # 原始新闻正文
                    "publish_date": {"type": "date"},  # 发布时间（ISO8601格式）
                    "author": {"type": "keyword"},
                    "news_type": {"type": "keyword"},
                    "bullish_level": {"type": "keyword"},  # 看多程度（若LLM返回数值可改为float）
                    "relation_level": {"type": "keyword"},  # 关联程度
                    "relations_stocks": {"type": "keyword"},  # 支持数组存储股票代码
                    "tags": {"type": "keyword"},  # 支持数组存储标签
                    "news_md5": {"type": "keyword"},  # 去重标识
                    "sources": {"type": "keyword"},  # 数据来源平台
                    "url": {"type": "keyword"},  # 原文链接
                    VECTOR_FIELD: {
                        "type": "dense_vector",
                        "dims": DEFAULT_VECTOR_DIMS,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        try:
            es_client.indices.create(index=INDEX_NAME, body=mapping)
            logger.info(f"✅ 成功创建ES索引: {INDEX_NAME} (维度: {DEFAULT_VECTOR_DIMS})")
        except Exception as e:
            logger.error(f"❌ ES索引创建失败: {e}")
            raise
    else:
        logger.debug(f"ℹ️ ES索引 {INDEX_NAME} 已存在，跳过创建。")


def _safe_extract_json(llm_response: str) -> Dict[str, Any]:
    """安全清洗并解析大模型返回的JSON字符串"""
    cleaned = re.sub(r'^\s*```(?:json)?\s*|\s*```\s*$', '', llm_response, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON解析失败: {e}\n原始片段: {llm_response[:200]}")
        raise ValueError("无法从大模型响应中提取有效的JSON数据")


def llm_news_summarize(
        news_content: str,
        news_time: str = '',
        news_type: str = 'normal',
        sources: str = 'ths',
        url: str = '',
        debug: bool = False
) -> bool:
    """
    @brief 使用大模型对金融新闻进行智能摘要、分类，并同步至业务数据库与ES

    @param news_content: [新闻正文内容或拼接后的标题+内容]
    @type news_content: str

    @param news_time: [新闻发布时间，ISO8601格式字符串]
    @type news_time: str

    @param news_type: [新闻类型标识，如 normal/report等]
    @type news_type: str

    @param sources: [数据来源平台标识]
    @type sources: str

    @param url: [新闻原文链接]
    @type url: str

    @param debug: [是否开启调试模式打印中间结果]
    @type debug: bool

    @return: [处理是否成功]
    @rtype: bool

    @throws: [ValueError: JSON解析失败时抛出]

    @example:
        # 基础用法
        result = llm_news_summarize(news_content="某公司发布财报...", news_time="2025-01-01T10:00:00Z")
        print(result)  # 输出: True
    """
    # 1. 去重检查
    news_md5 = string_to_md5(news_content)
    if MarketNewsService.get_by_md5(news_md5) is not None:
        logger.info(f"⏭️ 跳过重复记录 MD5: {news_md5}")
        return False

    # 2. 确保ES索引就绪（仅首次执行时会触发创建）
    _ensure_es_index()

    # 3. 构建Prompt并调用大模型
    question_prompt = prompt_template.safe_substitute(
        news_time=news_time,
        news_content=news_content,
        prompt_155th=prompt_155th
    )
    raw_answer = analysis_model.ask(question_prompt)
    answer_json = _safe_extract_json(raw_answer)

    # 4. 准备入库数据
    db_payload = {
        "digest": answer_json.get("digest", ""),
        "news_time": news_time,
        "news_type": news_type,
        "bullish_level": answer_json.get("bullish_level"),
        "relation_level": answer_json.get("relation_level"),
        "relations_stocks": answer_json.get("relations_stocks"),
        "tags": answer_json.get("tags"),
        "news_md5": news_md5,
        "sources": sources,
        "url": url
    }

    # 5. 向量化并写入ES
    embedding_text = f"{db_payload['digest']}{EMBEDDING_TEXT_SEP}{news_content}"
    try:
        vector = get_embedding(embedding_text)
        action = {
            "_index": INDEX_NAME,
            "_source": {**db_payload, "author": "", VECTOR_FIELD: vector}
        }
        helpers.bulk(es_client, [action])
        logger.info(f"✅ 向量数据已写入ES，标题: {db_payload['digest']}")
    except Exception as e:
        logger.error(f"❌ 向量化或ES写入失败: {e}")

    # 6. 持久化至业务库
    try:
        MarketNewsService.create(**db_payload)
        logger.info(f"📦 新闻数据已落库 MD5: {news_md5}")
    except Exception as e:
        logger.error(f"❌ 业务库保存失败: {e}")

    if debug:
        logger.debug(f"🔍 调试输出: {json.dumps(answer_json, ensure_ascii=False, indent=2)}")

    return True


def _process_batch_articles(articles: List[Dict[str, Any]], sources: str, news_type: str = 'normal') -> None:
    """统一调度文章抓取、清洗与AI分析任务"""
    logger.info(f"🚀 开始处理 [{sources}] 批量新闻，共 {len(articles)} 条")
    for idx, art in enumerate(articles, start=1):
        try:
            content = art.get('content_text', art.get('short', ''))
            title = art.get('title', '')
            full_text = f"digest: {title}{content}" if title else content

            # 兼容不同源的时间字段
            pub_date = art.get('publish_date') or timestamp_to_date(int(art.get('ctime', 0)))

            if not pub_date:
                logger.warning(f"⏭️ 第{idx}条缺失发布时间，跳过。Title: {title[:30]}")
                continue

            llm_news_summarize(
                news_content=full_text,
                news_time=str(pub_date),
                news_type=news_type,
                sources=sources,
                url=art.get('url', ''),
                debug=False
            )
            time.sleep(0.8)  # 礼貌性延迟，避免触发反爬或限流
        except Exception as e:
            logger.error(f"❌ 处理第{idx}条新闻时发生异常: {e}")
            continue  # 单条失败不阻断整体流程


def vector_search(query_text: str, top_k: int = 3) -> None:
    """简单的向量搜索测试接口"""
    logger.info(f"\n🔍 启动向量检索测试: '{query_text}'")
    try:
        query_vector = get_embedding(query_text)
        search_query = {
            "knn": {
                "field": VECTOR_FIELD,
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": 10
            }
        }
        response = es_client.search(index=INDEX_NAME, body=search_query)
        hits = response['hits']['hits']

        if hits:
            print("📊 检索结果:")
            for hit in hits:
                print(f"- [得分: {hit['_score']:.4f}] {hit['_source'].get('title')}")
        else:
            print("⚪ 未匹配到相关数据。")
    except Exception as e:
        logger.error(f"❌ 向量搜索失败: {e}")


# ================= 定时任务入口 =================
def job_news_feed_analysis_wallstreet() -> None:
    """
    @brief 采集华尔街见闻热门文章并推送至AI分析管线
    @throws [Exception: 网络请求或解析异常]
    """
    fetcher = WallStreetCNFetcher()
    article_ids = fetcher.get_hot_article_ids()[:15]
    articles = fetcher.fetch_articles(article_ids, delay=0.8)
    _process_batch_articles(articles, sources='wallstreet')


def job_news_feed_analysis_ths() -> None:
    """
    @brief 采集同花顺实时快讯并推送至AI分析管线
    @throws [Exception: 网络请求或解析异常]
    """
    news_list = finfilo.get_realtime_news_from_ths_short(pagesize=30)
    _process_batch_articles(news_list, sources='tonghuashun')


def job_news_feed_analysis_stock_star(is_roll: bool = False) -> None:
    """
    @brief 采集证券之星新闻/研报/滚动资讯并推送至AI分析管线
    @throws [Exception: 网络请求或解析异常]
    """
    scraper = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/2_1.shtml')
    time.sleep(5)
    scraper2 = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/5921.shtml')

    # 1. 抓新闻列表
    all_articles = scraper.scrape_list() + scraper2.scrape_list()

    _process_batch_articles(all_articles, sources='stock_star', news_type='report' if is_roll else 'normal')


def job_research_report_from_stock_star() -> None:
    """
    @brief 定向采集证券之星研究员专栏研报
    @throws [Exception: 网络请求或解析异常]
    """
    scraper = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/6003_1.shtml')
    articles = scraper.scrape_list()
    _process_batch_articles(articles, sources='stock_star', news_type='report')


def job_news_scrape_all() -> None:
    """
    @brief 全量聚合各数据源执行新闻分析与入库
    @throws [Exception: 子任务执行异常]
    """
    logger.info("🌐 启动全量新闻采集与分析任务")
    job_news_feed_analysis_ths()
    job_news_feed_analysis_wallstreet()
    job_news_feed_analysis_stock_star()
    job_research_report_from_stock_star()
    job_news_feed_analysis_stock_star(is_roll=True)
    logger.info("✅ 全量任务执行完毕")


if __name__ == '__main__':
    # 推荐在生产环境使用 schedule 或 Celery/APScheduler 接管
    job_news_feed_analysis_stock_star(is_roll=False)
