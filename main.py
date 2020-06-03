import json
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = "json"
    page_id_collector = PageIDCollector()
    page_id_list = page_id_collector.page_id_list

    for page_id in page_id_list:
        url = PageIDCollector.url + page_id
        page_crawler = PageCrawler(url)
        crawled_info_with_json = page_crawler.crawled_info_with_json

        with open(directory + "page_id" + ".json", "w") as f:
            json.dump(crawled_info_with_json, f)
