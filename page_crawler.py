import os
import json
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = "json"
    url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="

    with open("page_ids.json", "r") as f:
        page_id_dict = json.load(f)

    page_id_list = page_id_dict["ids"]

    for page_id in page_id_list:
        url = PageIDCollector.url + page_id
        page_crawler = PageCrawler(url)
        crawled_info_with_json = page_crawler.crawled_info_with_json

        with open(os.path.join(directory, (str(page_id) + ".json")), "w") as f:
            json.dump(crawled_info_with_json, f)
