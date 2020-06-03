from crawler import (PageIDCollector, PageCrawler)

if __name__ == "__main__":
    root_url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="
    test_ids = ["7138"]

    generated_test_urls = ["".join([root_url, test_id])
                           for test_id in test_ids]

    for test_url in generated_test_urls:
        page_crawler = PageCrawler(test_url)
        print(f"TEST URL : {test_url}")
        print(page_crawler.crawled_info_with_json, end="\n\n")
