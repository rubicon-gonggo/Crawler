import os
import json
import requests
import time
import traceback
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="

    with open("page_ids.json", "r") as f:
        page_id_dict = json.load(f)

    page_id_list = list(page_id_dict.keys())
    page_id_list.reverse()

    error_list = []
    for index, page_id in enumerate(page_id_list):
        start_time = time.time()
        print("[INFO] PAGE ID : {}".format(page_id))
        new_url = url + page_id
        print("[INFO] \t - URL : {}".format(url+str(page_id)))

        try:
            if os.path.exists((os.path.join(directory, "json", (str(page_id) + ".json")))):
                print("Alread Exist")
                continue
            page_crawler = PageCrawler(new_url, page_id)
            crawled_info_with_json = page_crawler.crawled_info_with_json
            end_time = time.time()
            print("[INFO] \t - ELPASED TIME : {}".format(end_time - start_time))

            with open(os.path.join(directory, "json", (str(page_id) + ".json")), "w") as f:
                json.dump(crawled_info_with_json, f)
        except Exception as e:
            error_list.append(page_id)
            print("[ERROR] {}".format(e))
            traceback.print_exc()
            continue

    error_dict = {"error_page_id": error_list}
    print("[INFO] ERROR LIST :{}".format(error_list))

    with open("error_page_id.json", "w") as f:
        json.dump(error_dict, f)
