"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import finfilo, json, time
from staffs import get_analysis_model_by_setting
from service import MarketNewsService
from service.stock_star_news import StockStarNewsScraper
from service.wallstreet_fetcher import WallStreetCNFetcher
from utils.common import string_to_md5, logger, timestamp_to_date
from staffs.prompts import prompt_155th
from prompts.prompt_generator import load_prompt_template
from pathlib import Path

CURRENT_DIR = Path(__file__).parent

"""
AI 汇总每日盘前新闻
"""

staff_analysis = get_analysis_model_by_setting('news_analysis')
staff_analysis.set_response_json()

# template = load_prompt_template_by_name(template_name="prompt_news_analysis")
template = load_prompt_template(template_path=f"{CURRENT_DIR}/prompt_news_analysis.md")

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
