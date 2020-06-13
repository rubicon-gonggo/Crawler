import os
import json
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = "json"
    root_url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="

    with open("page_ids.json", "r") as f:
        page_id_dict = json.load(f)

    lastpoint = "5390"
    page_id_list = page_id_dict["ids"]
    tmp = []
    for page_id in page_id_list:
        if page_id == lastpoint:
            tmp.append(page_id)
            break
        tmp.append(page_id)

    page_id_list = tmp
    page_id_list.reverse()
    print(page_id_list)

    for page_id in page_id_list:
        print("[INFO] PAGE ID : {}".format(page_id))
        url = root_url + page_id
        print("[INFO] \t - URL : {}".format(url))
        page_crawler = PageCrawler(url)
        crawled_info_with_json = page_crawler.crawled_info_with_json
        print("[INFO] Result\n {}".format(crawled_info_with_json))

        with open(os.path.join(directory, (str(page_id) + ".json")), "w") as f:
            json.dump(crawled_info_with_json, f)
