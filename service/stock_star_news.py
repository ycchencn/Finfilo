"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

import requests
import time
from bs4 import BeautifulSoup

class StockStarNewsScraper:
    def __init__(self, list_url="https://stock.stockstar.com/list/2_1.shtml"):
        self.list_url = list_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }

    def scrape_list(self):
        """抓取新闻列表（仅标题、时间、链接）"""
        try:
            response = requests.get(self.list_url, headers=self.headers, timeout=10)
            response.encoding = 'gb2312'
            soup = BeautifulSoup(response.text, 'lxml')
            news_items = soup.find_all('li', recursive=True)
            results = []

            for item in news_items:

                time_span = item.find('span')
                link_tags = item.find_all('a', href=True)

                for link_tag in link_tags:

                    if time_span and link_tag and ('/IG' in link_tag['href'] or '/SS' in link_tag['href']):

                        pub_time = time_span.get_text(strip=True)
                        title = link_tag.get_text(strip=True)
                        href = link_tag['href']
                        full_url = href if href.startswith('http') else 'https://stock.stockstar.com' + href
                        content = self.fetch_article_content(full_url)

                        # 延迟抓取
                        time.sleep(0.3)
                        results.append({
                            "publish_date": pub_time,
                            "title": title,
                            "url": full_url,
                            "content_text": content
                        })

            return results
        except Exception as e:
            print(f"❌ 列表页抓取失败: {e}")
            return []

    def fetch_article_content(self, url):
        """抓取单篇新闻的详细内容（标题、发布时间、正文）"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gb2312'
            soup = BeautifulSoup(response.text, 'lxml')

            # 提取标题
            title_elem = soup.select_one('.tst h1')
            title = title_elem.get_text(strip=True) if title_elem else "未知标题"

            # 提取发布时间
            time_elem = soup.select_one('#pubtime_baidu')
            publish_time = time_elem.get_text(strip=True) if time_elem else "未知时间"

            # 提取正文：所有 .article_content 下的 <p> 文本
            content_div = soup.select_one('.article_content')
            paragraphs = []
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text(strip=True)
                    if text:
                        paragraphs.append(text)
            content = "\n".join(paragraphs)

            return {
                "title": title,
                "publish_time": publish_time,
                "content": content,
                "url": url
            }

        except Exception as e:
            print(f"❌ 详情页抓取失败 ({url}): {e}")
            return None

# ======================
# 使用示例：抓列表 + 抓前2篇正文
# ======================
if __name__ == "__main__":
    scraper = StockStarNewsScraper()

    # 1. 抓新闻列表
    news_list = scraper.scrape_list()
    print(f"✅ 共获取 {len(news_list)} 条新闻\n")

    for new in news_list:
        print(new)
