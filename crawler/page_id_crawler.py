import os
import json
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from pprint import pprint


class PageIDCollector:
    url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"
    blacklist = ["매입임대", "전세임대"]

    def __init__(self, url=None, last_page_id: str = ""):
        """
        Collect validated Page ID from MyHome
        Args:
            url (str) : List page url in Myhome
            last_page_id (str) : lastest page id
        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        if not url:
            url = PageIDCollector.url
        self.last_page_id = last_page_id
        if self.last_page_id == "":
            # last page id
            # Last Board at 2015-06-11
            # `동해묵호,동해유성,삼척도계(1) 국민임대주택 입주자격완화 선착순입주자 모집공고`
            # Refs: https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId=128
            self.last_page_id = "128"
        self.driver = self.get_web_driver(url)
        self.driver.get(url)
        time.sleep(10)
        self.page_id_dict = self.collect_page_id(self.driver)
        self.driver.quit()

    def get_web_driver(self, url):
        """
        initialize webdriver
        Args:
            url (str) : List page url in Myhome
        Returns:
            (selenium.webdriver.chrome.webdriver.WebDriver)
        """
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("disable-gpu")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)
        driver.implicitly_wait(1)

        return driver

    def collect_page_id_in_one_loop(self, driver, pagenation_xpaths, keys, current_page_location):
        table_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody"

        end_signal = False
        page_id_list = []

        for index, pagenation_xpath in enumerate(pagenation_xpaths):
            print("[INFO] Current Page Location : {}".format(
                keys[index]))

            driver = self.move_page(driver, pagenation_xpath)
            driver, _ = self.load_contents(driver, table_xpath)

            # Get Validated Rows in Table
            driver.implicitly_wait(3)
            table_el = driver.find_element_by_css_selector(
                'table.bbs_type1')
            rows = table_el.find_elements_by_css_selector('tr')[1:]

            candidates = []
            for idx, row in enumerate(rows):
                xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                supply_type = row.find_element_by_xpath(xpath)

                if supply_type.text not in PageIDCollector.blacklist:
                    candidates.append((idx+1, row))

            for candidate in candidates:
                start_time = time.time()
                idx, row = candidate
                page_info = row.find_element_by_xpath(
                    '//tr[{}]/td[4]/a'.format(idx))
                page_id = page_info.get_attribute('href').split("'")[-2]

                print("[INFO]\t Comparison CUR PAGE: {}, CHECKPOINT: {}".format(
                    page_id, self.last_page_id))
                if page_id == self.last_page_id:
                    end_signal = True

                page_id_list.append(page_id)
                print("[INFO]\t - Current page id : {}".format(page_id))
                end_time = time.time()
                print("[INFO]\t - Elapsed Time: {}".format(end_time - start_time))

            current_page_location += 1

        return driver, page_id_list,  end_signal, current_page_location

    def collect_page_id(self, driver):
        table_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody"
        pagenation_xpaths = self.get_pagenation_xpaths(self.driver)

        page_id_dict = {}
        ARRIVED_END = False
        current_page_location = 1
        while True:
            if ARRIVED_END == True:
                break

            # Update Pagenation
            pagenation_xpaths, keys = self.get_pagenation_xpaths(self.driver)
            pagenation_xpaths = pagenation_xpaths[2:-1]
            keys = keys[2: -1]
            # Refresh driver
            # Avoiding Stale Element Reference Exception in Selenium Webdriver
            # self.driver.get(self.driver.current_url)
            # time.sleep(2)
            """
            driver, collected_page_id_list, ARRIVED_END, current_page_location = self.collect_page_id_in_one_loop(
                driver, pagenation_xpaths, keys, current_page_location)
            page_id_list = page_id_list + collected_page_id_list
            """
            for index, pagenation_xpath in enumerate(pagenation_xpaths):
                start_time = time.time()
                print("[INFO] Current Page Location : {}".format(
                    keys[index]))

                self.driver = self.move_page(self.driver, pagenation_xpath)
                self.driver, _ = self.load_contents(self.driver, table_xpath)

                # Get Validated Rows in Table
                table_el = self.driver.find_element_by_css_selector(
                    'table.bbs_type1')
                rows = table_el.find_elements_by_css_selector('tr')[1:]

                candidates = []
                for idx, row in enumerate(rows):
                    xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                    supply_type = row.find_element_by_xpath(xpath)

                    if supply_type.text not in PageIDCollector.blacklist:
                        candidates.append((idx+1, row))

                for candidate in candidates:
                    idx, row = candidate
                    status_objs = row.find_elements_by_xpath(
                        '//tr[{}]/td[2]/span'.format(idx))
                    status = "모집중" if status_objs else "모집완료"
                    page_info = row.find_element_by_xpath(
                        '//tr[{}]/td[4]/a'.format(idx))
                    page_id = page_info.get_attribute('href').split("'")[-2]

                    print("[INFO]\t Comparison CUR PAGE: {}, CHECKPOINT: {}".format(
                        page_id, self.last_page_id))
                    if page_id == self.last_page_id:
                        ARRIVED_END = True

                    page_id_dict[str(page_id)] = status
                    print("[INFO]\t - Current page id : {}".format(page_id))
                end_time = time.time()
                current_page_location += 1
                print("[INFO]\t - Elapsed Time : {}".format(end_time - start_time))

        return page_id_dict

    @ staticmethod
    def get_pagenation_xpaths(driver):
        pagenation_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/div[2]/ul"
        pagenation = driver.find_elements_by_xpath(pagenation_xpath)[0]
        pagenation_list = pagenation.text.split("\n")

        num_pagenation = len(pagenation_list)

        candidates = []
        for i in range(1, num_pagenation + 1):
            candidates.append(f"li[{i}]")

        return [os.path.join(pagenation_xpath, candidate) for candidate in candidates], pagenation_list

    @ staticmethod
    def move_page(driver, xpath):
        element = driver.find_elements_by_xpath(xpath)[0]
        element.click()
        time.sleep(10)
        return driver

    @ staticmethod
    def load_contents(driver, xpath):
        element = driver.find_elements_by_xpath(xpath)[0]
        return driver, element


if __name__ == "__main__":
    page_id_collector = PageIDCollector()
    print(page_id_collector.page_id_dict)
