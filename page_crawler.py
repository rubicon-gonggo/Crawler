import os
import json
import requests
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="

    with open("page_ids.json", "r") as f:
        page_id_dict = json.load(f)

    page_id_list = page_id_dict["ids"]

    for index, page_id in enumerate(page_id_list):
        new_url = url + page_id
        print(new_url)

        page_crawler = PageCrawler(new_url, page_id)

        try:
            crawled_info_with_json = page_crawler.crawled_info_with_json

            if crawled_info_with_json is None:
                continue

            json_data = json.dumps(crawled_info_with_json)

            res = requests.post('http://localhost:8000/api/crawler/', data=json_data, headers={
                'content-type': 'application/json'
            })

            print(res.json())
        except:
            continue

        # with open(os.path.join(directory, (str(page_id) + ".json")), "w") as f:
        #     json.dump(crawled_info_with_json, f)
