import argparse
import os
import json
from crawler import (PageIDCollector, PageCrawler)

parser = argparse.ArgumentParser(description='크롤링 checkpoint')
parser.add_argument('--endpoint',
                    required=True,
                    type=str,
                    help='production endpoint')

if __name__ == "__main__":

    args = parser.parse_args()
    endpoint = args.endpoint
    uri = endpoint + "/production/api/checkpoint/"

    directory = "json"
    page_id_collector = PageIDCollector(url=None, last_page_id="7399")
    page_id_dict = page_id_collector.page_id_dict

    with open("page_ids.json", "w") as f:
        json.dump(page_id_dict, f)
