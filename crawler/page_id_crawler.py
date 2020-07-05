import os
import json
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

from typing import (Optional, List, Dict)


class PageIDCollector:
    url: str = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"
    blacklist = ["매입임대", "전세임대"]

    def __init__(self,
                 url: Optional[str] = None,
                 last_page_id: Optional[str] = None) -> None:
        """
        마이홈의 임대주택 상세 페이지 id 크롤링

        Args:
            url (str) : 마이홈의 임대주택공고 목록 url
            last_page_id (str) : last_page_id가 나올때까지 탐색 진행
                                 last_page_id는 이전에 탐색한 page_id는 탐색하지 않고 필요한 부분만 탐색하기 위한 용도
                                 만약에 값이 없다면, 마이홈 마지막 페이지인 "128"을 기본값으로 정의함

        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        self.last_page_id = last_page_id

        if url == None:
            url = PageIDCollector.url

        if self.last_page_id == None:
            # last page id
            # Last Board at 2015-06-11
            # `동해묵호,동해유성,삼척도계(1) 국민임대주택 입주자격완화 선착순입주자 모집공고`
            # Refs: https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId=128
            self.last_page_id = "128"
        self.driver: selenium.webdriver.chrome.webdriver.WebDriver = self.get_web_driver(
            url)
        self.driver.get(url)
        # Wait load page
        time.sleep(10)
        self.page_id_dict = self.collect_page_id(self.driver)

        keys = list(self.page_id_dict.keys())
        remove_list = []
        for key in keys:
            if int(key) <= int(self.last_page_id):
                remove_list.append(key)
        print("REMOVE LIST : {}".format(remove_list))
        for remove_key in remove_list:
            self.page_id_dict.pop(remove_key, None)
        self.driver.quit()

    def get_web_driver(self,
                       url: str) -> selenium.webdriver.chrome.webdriver.WebDriver:
        """
        셀레니움 크롬 웹 드라이버를 로드
        Args:
            url (str) : 공공주택공고 리스트 URL
        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        options: selenium.webdriver.chrome.webdriver.Options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("disable-gpu")

        driver: selenium.webdriver.chrome.webdriver.WebDriver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)
        driver.implicitly_wait(1)

        return driver

    def collect_page_id(self,
                        driver: selenium.webdriver.chrome.webdriver.WebDriver) -> Dict:
        """
        마이홈 공공임대주택의 상세 페이지ID를 탐색하며 크롤링(제외해야할 주택 유형은 제외)
        페이지 ID를 key값으로 모집상태(`모집중`, `모집완료`)까지 수집


        Args:
            drvier (selenium.webdriver.chrome.webdriver.WebDriver) : 셀레니움 크롬 드라이버

        Returns:
            (Dict) : 공공임대주택 상세 페이지 ID 딕셔너리
        """
        # 수집할 상세 페이지 ID 딕셔너리
        page_id_dict = {}

        # 공공임대주택 리스트 페이지의 테이블 xpath
        table_xpath: str = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody"

        # 현재 공공임대주택 리스트 페이지에서 페이지네이션 리스트에 대한 xpath를 가져옴
        pagenation_xpaths = self.get_pagenation_xpaths(self.driver)

        # 최종탐색 페이지
        is_last_page: bool = False

        # 현재 탐색 위치
        current_page_location = 1

        while True:
            if is_last_page == True:
                break

            # 페이지네이션 리스트 갱신: 페이지네이션의 수가 변경될 수 있음
            # 예를들어 0~10까지 페이지네이션이 있다가 마지막쯤 가면 0~5개정도의 페이지네이션만 있음
            pagenation_xpaths, keys = self.get_pagenation_xpaths(self.driver)

            # 페이지네이션 양끝단의 `처음`, `이전`과, `다음`, `끝` 중에서
            # `다음`을 제외하고 탐색할 페이지네이션에서 제거
            pagenation_xpaths = pagenation_xpaths[2:-1]
            keys = keys[2: -1]

            for index, pagenation_xpath in enumerate(pagenation_xpaths):
                if is_last_page == True:
                    break
                start_time = time.time()
                print("[INFO] Current Page Location : {}".format(
                    keys[index]))

                self.driver = self.move_page(self.driver, pagenation_xpath)
                self.driver, _ = self.load_contents(self.driver, table_xpath)

                # 현재 공공임대주택 페이지의 테이블 열(row)을 가지고옴
                table_element = self.driver.find_element_by_css_selector(
                    'table.bbs_type1')
                rows = table_element.find_elements_by_css_selector('tr')[1:]

                # 크롤링 포맷 일관성이 안맞는 이슈로 인해
                # blacklist에 있는 주택 유형은 제외함
                candidates = []
                for idx, row in enumerate(rows):
                    xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                    supply_type = row.find_element_by_xpath(xpath)

                    if supply_type.text not in PageIDCollector.blacklist:
                        candidates.append((idx+1, row))

                # row의 href에서 page_id를 획득할 수 있음
                for candidate in candidates:
                    if is_last_page == True:
                        break
                    idx, row = candidate

                    status_objs = row.find_elements_by_xpath(
                        '//tr[{}]/td[2]/span'.format(idx))
                    status = "모집중" if status_objs else "모집완료"

                    region_objs = row.find_elements_by_xpath(
                        '//*[@id="schTbody"]/tr[{}]/td[3]'.format(idx))
                    region = region_objs[0].text if region_objs else "unknown"

                    page_info = row.find_element_by_xpath(
                        '//tr[{}]/td[4]/a'.format(idx))
                    page_id = page_info.get_attribute('href').split("'")[-2]

                    if int(page_id) <= int(self.last_page_id):
                        is_last_page = True

                    page_id_dict[str(page_id)] = {"status": status,
                                                  "region": region,
                                                  "region_depth": True if "외" in region else False}

                    print("[INFO]\t Comparison CURRENT PAGE: {}, CHECKPOINT: {}".format(
                        page_id, self.last_page_id))
                    print("[INFO]\t - Current page id : {}".format(page_id))

                current_page_location += 1
                end_time = time.time()

                print("[INFO]\t - Elapsed Time : {}".format(end_time - start_time))
        return page_id_dict

    @ staticmethod
    def get_pagenation_xpaths(driver: selenium.webdriver.chrome.webdriver.WebDriver):
        """
        현재 페이지의 임대주택 리스트에 대한 xpath를 불러옴

        Args:
            driver (selenium.webdriver.chrome.webdriver.WebDriver):
            셀레니움 크롬 드라이버
        Returns
            (List, List): 
        """
        pagenation_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/div[2]/ul"
        pagenation = driver.find_elements_by_xpath(pagenation_xpath)[0]
        pagenation_list = pagenation.text.split("\n")

        num_pagenation = len(pagenation_list)

        candidates = []
        for i in range(1, num_pagenation + 1):
            candidates.append(f"li[{i}]")

        return [os.path.join(pagenation_xpath, candidate) for candidate in candidates], pagenation_list

    @ staticmethod
    def move_page(driver: selenium.webdriver.chrome.webdriver.WebDriver,
                  xpath: str):
        """
        xpath를 기반으로 페이지를 이동

        Args:
            driver (selenium.webdriver.chrome.webdriver.WebDriver): 셀레니움 크롬 드라이버
            xpath (str) : xpath

        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        element = driver.find_elements_by_xpath(xpath)[0]
        element.click()
        time.sleep(10)
        return driver

    @ staticmethod
    def load_contents(driver, xpath):
        """
        xpath를 이용해서 페이지를 불러옴

        Args:
            driver (selenium.webdriver.chrome.webdriver.WebDriver): 셀레니움 크롬 드라이버
            xpath (str): xpath
        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        element = driver.find_elements_by_xpath(xpath)[0]
        return driver, element


if __name__ == "__main__":
    page_id_collector = PageIDCollector()
    print(page_id_collector.page_id_dict)
