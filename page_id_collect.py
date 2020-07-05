import os
import json
from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    directory = "json"
    page_id_collector = PageIDCollector(url=None, last_page_id="7271")
    page_id_dict = page_id_collector.page_id_dict

    with open("page_ids.json", "w") as f:
        json.dump(page_id_dict, f)
