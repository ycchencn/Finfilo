"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import finfilo, json, time
from elasticsearch import Elasticsearch, helpers
from staffs import get_analysis_model_by_setting
from service import MarketNewsService
from service.stock_star_news import StockStarNewsScraper
from service.wallstreet_fetcher import WallStreetCNFetcher
from utils.common import string_to_md5, logger, timestamp_to_date
from staffs.prompts import prompt_155th
from prompts.prompt_generator import load_prompt_template
from pathlib import Path
from backtest.text_embedding import get_embedding
from config import elasticsearch_setting

CURRENT_DIR = Path(__file__).parent

"""
AI 汇总每日盘前新闻
"""

staff_analysis = get_analysis_model_by_setting('news_analysis')
staff_analysis.set_response_json()

# template = load_prompt_template_by_name(template_name="prompt_news_analysis")
template = load_prompt_template(template_path=f"{CURRENT_DIR}/prompt_news_analysis.md")

index_name = 'news_feed'

# 初始化 ES 客户端
es = Elasticsearch(elasticsearch_setting['host'], basic_auth=(elasticsearch_setting['username'], elasticsearch_setting['password']) )

def vector_search(query_text):
    """简单的向量搜索测试"""
    print(f"\n🔍 正在进行向量搜索测试: '{query_text}'")

    try:
        # 7. 同样需要使用 API 将查询词向量化
        query_vector = get_embedding(query_text)

        search_query = {
            "knn": {
                "field": "vector",
                "query_vector": query_vector,
                "k": 3,
                "num_candidates": 10
            }
        }

        response = es.search(index=index_name, body=search_query)
        hits = response['hits']['hits']

        if hits:
            print("找到相关研报：")
            for hit in hits:
                score = hit['_score']
                title = hit['_source']['title']
                print(hit['_source'])
                print(f"- [得分: {score:.4f}] {title}")
        else:
            print("未找到结果。")

    except Exception as e:
        print(f"❌ 搜索失败: {e}")

def ingest_data_to_es():

    # 4.1 检查 ES 索引是否存在，不存在则创建
    if not es.indices.exists(index=index_name):
        print(f"🔨 正在创建索引: {index_name}")

        # 3. 获取模型维度 (演示如何动态获取，或者直接写死)
        # 这里为了简单，text-embedding-v4 默认通常是 1024 维
        sample_text = "Hello"
        sample_vector = get_embedding(sample_text)
        vector_dims = len(sample_vector)
        print(f"ℹ️  检测到向量维度: {vector_dims}")

        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "author": {"type": "keyword"},
                    "publish_date": {"type": "date"},
                    "content": {"type": "text"},
                    "sector": {"type": "keyword"},
                    # 4. 修改 Mapping 维度 (注意：如果是 text-embedding-v4，通常是 1024)
                    "vector": {
                        "type": "dense_vector",
                        "dims": vector_dims,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        try:
            es.indices.create(index=index_name, body=mapping)
        except Exception as e:
            print(f"❌ 创建索引失败: {e}")
            return
    else:
        print(f"ℹ️  索引 {index_name} 已存在。")

    # 4.2 获取 Mock 数据并开始处理
    # reports = list(mock_report_generator(count=5))
    actions = []

    print("🚀 开始调用 API 进行向量化并构建写入请求...")

    try:

        # --- 核心步骤：调用 API 向量化 ---
        # text_to_embed = f"{report['title']} {report['content']}"
        #
        # # 5. 调用函数获取向量
        # vector_embedding = get_embedding(text_to_embed)
        #
        # # 构建 ES 写入动作
        # action = {
        #     "_index": index_name,
        #     "_source": {
        #         "title": report['title'],
        #         "author": report['author'],
        #         "publish_date": report['publish_date'],
        #         "content": report['content'],
        #         "sector": report['sector'],
        #         "vector": vector_embedding
        #     }
        # }
        # actions.append(action)

        # 6. 简单的速率限制 (避免触发 API 频率限制)

        pass

    except Exception as e:
        print(f"❌ 向量化失败: {e}")

    # 4.3 批量写入 ES
    try:
        success, _ = helpers.bulk(es, actions)
        print(f"✅ 成功写入 {success} 条研报数据到 Elasticsearch！")
        # es.indices.refresh(index=index_name)

    except Exception as e:
        print(f"❌ 写入数据时发生错误: {e}")

def llm_news_summarize(
    new,
    news_time='',
    news_type='normal',
    sources='ths',
    url='',
    debug=False):
    """
    使用大模型对新闻进行归类
    """

    news_md5 = string_to_md5(new)

    # 唯一性处理
    if MarketNewsService.get_by_md5(news_md5) is not None:
        return False

    question_prompt = template.safe_substitute(
        news_time=news_time,
        news_content=str(new),
        prompt_155th=prompt_155th
    )

    answer = staff_analysis.ask(question_prompt)

    ai_ans = answer.replace("```json", "")
    ai_ans = ai_ans.replace("```", "")
    answer_json = json.loads(ai_ans)

    if debug:
        print(answer_json)
        return True

    MarketNewsService.create(
        digest=answer_json.get("digest"),
        news_time=news_time,
        news_type=news_type,
        bullish_level=answer_json.get("bullish_level"),
        relation_level=answer_json.get("relation_level"),
        relations_stocks=answer_json.get("relations_stocks"),
        tags=answer_json.get("tags"),
        news_md5=news_md5,
        sources=sources,
        url=url
    )

    # relations_stocks = answer_json.get("relations_stocks")

    logger.info(f"market news imported, {news_md5}")


def job_news_feed_analysis_wallstreet():
    """
    从华尔街见闻获取最新15条新闻
    """
    fetcher = WallStreetCNFetcher()

    # 1. 获取热门文章 ID
    ids = fetcher.get_hot_article_ids()[:15]

    # 2. 批量抓取
    articles = fetcher.fetch_articles(ids, delay=1.0)

    # 3. 打印结果
    for art in articles:
        # 忽略没有日期的新闻
        if art.get('publish_date') is None:
            continue
        llm_news_summarize(
            f"digest: {art['title']}{art['content_text']}",
            news_time=art['publish_date'],
            sources='wallstreet',
            url=art['url']
        )


def job_news_feed_analysis_ths():
    """
    从同花顺获取最新1新闻
    """
    news_size = 30
    news = finfilo.get_realtime_news_from_ths_short(pagesize=news_size)
    for new in news:
        llm_news_summarize(
            new['short'],
            news_time=timestamp_to_date(int(new['ctime'])),
            sources='tonghuashun',
            url=new['url']
        )


def job_news_feed_analysis_stock_star():
    """
    从证券之星获取最新新闻
    """
    scraper = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/2_1.shtml')
    time.sleep(5)
    scraper2 = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/5921.shtml')

    # 1. 抓新闻列表
    news_list = scraper.scrape_list() + scraper2.scrape_list()

    for art in news_list:
        llm_news_summarize(
            f"digest: {art['title']} - {art['content_text']}",
            news_time=art['publish_date'],
            sources='stock_star',
            url=art['url']
        )


def job_research_report_from_stock_star():
    """
    从证券之星获取 研究员专栏
    """

    time.sleep(5)

    scraper = StockStarNewsScraper(list_url='https://stock.stockstar.com/list/6003_1.shtml')

    # 1. 抓新闻列表
    news_list = scraper.scrape_list()

    for art in news_list:
        llm_news_summarize(
            f"digest: {art['title']} - {art['content_text']}",
            news_time=art['publish_date'],
            news_type='report',
            sources='stock_star',
            url=art['url']
        )

def job_roll_from_stock_star():
    """
    从证券之星获取 研究员专栏
    """

    time.sleep(5)

    scraper = StockStarNewsScraper(list_url='https://roll.stockstar.com/finance.shtml')

    # 1. 抓新闻列表
    news_list = scraper.scrape_list()

    for art in news_list:
        llm_news_summarize(
            f"digest: {art['title']} - {art['content_text']}",
            news_time=art['publish_date'],
            news_type='report',
            sources='stock_star',
            url=art['url']
        )

def job_news_scrape_all():

    job_news_feed_analysis_ths()

    job_news_feed_analysis_wallstreet()

    job_news_feed_analysis_stock_star()

    job_research_report_from_stock_star()

    job_roll_from_stock_star()


if __name__ == '__main__':

    job_roll_from_stock_star()
