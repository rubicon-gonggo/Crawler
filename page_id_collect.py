import os
import json
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = "json"
    page_id_collector = PageIDCollector()
    page_id_list = page_id_collector.page_id_list

    page_id_dict = {"ids": page_id_list}
    with open("page_ids.json", "w") as f:
        json.dump(page_id_dict, f)
