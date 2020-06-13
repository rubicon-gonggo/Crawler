import os
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time


class PageCrawler:
    def __init__(self, url: str, page_id: str):
        """
        Crawling detail page in MyHome

        Args:
            url (str) : detail page url in Myhome

        Returns:
            (PageCrawler)
        """
        self.url = url
        self.page_id = page_id
        self.driver = self.get_web_driver(url)
        self.driver.get(url)
        time.sleep(3)
        self.crawled_info_with_json = self.get_all_info()
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
        driver.implicitly_wait(3)

        return driver

    def get_basic_info(self):
        """
        get basic information from detail page

        Args:
            None

        Returns:
            (Dict) : {name: 공고명 (str)
                      supply_category: 공고유형 (str),
                      candidates: 공고대상 (list),
                      supply_company: 공급기관 (str),
                      supply_type: 공급유형 (str),
                      house_type: 주택유형 (str)
                      }
        """
        name_xpath = '//*[@id="sub_content"]/div/div[1]/em'
        name = self.driver.find_element_by_xpath(name_xpath).text

        supply_category_xpath = '//*[@id="sub_content"]/div/div[1]/span'
        supply_category = self.driver.find_element_by_xpath(
            supply_category_xpath).text

        candidates_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[1]'
        candidates = [
            candidate.text for candidate in self.driver.find_elements_by_xpath(candidates_xpath)]

        supply_company_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[2]'
        supply_company = self.driver.find_element_by_xpath(
            supply_company_xpath).text

        supply_type_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[3]'
        supply_type = self.driver.find_element_by_xpath(supply_type_xpath).text

        house_type_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[4]'
        house_type = self.driver.find_element_by_xpath(house_type_xpath).text

        return {"name": name,
                "supply_category": supply_category,
                "candidates": candidates,
                "supply_company": supply_company,
                "supply_type": supply_type,
                "house_type": house_type}

    def get_all_info(self):
        """
        get all information from detail page

        Args:
            None

        Returns:
            (Dict) : {"select_id (int)" : {"name": 단지이름 (str),
                                           "location": 위치정보 (str),
                                           "num_household": 총세대수 (str),
                                           "move_in_date": 최초입주일 (str),
                                           "num_recruit": 모집호수 (str),
                                           "danchi_scale": 단지규모 (str),
                                           "inquire": 문의처 (str),
                                           "etc": 기타 (str),
                                           "pdf_url": 공고문PDF URL (str)
                                           "supply_info": 공급정보 (Dict) -> {"supply_type": 형명 (str),
                                                                            "area": 전용면적 (str),
                                                                            "recruit_total": 모집호수-계 (str),
                                                                            "recruit_prior": 모집호수-우선공급 (str),
                                                                            "recruit_general": 모집호수-일반공급 (str),
                                                                            "lease_total_cost": 임대보증금(원)-계 (str),
                                                                            "down_payment": 임대보증금(원)-계약금 (str),
                                                                            "intermediate_payment": 임대보증금(원)-중도금 (str),
                                                                            "postponing_payment": 임대보증금(원)-잔금 (str),
                                                                            "rent_cost_per_month": 월 임대료 (str)}
                                           },
                     "schedule_info (Dict)": {"start_date": 모집 공고일 (str),
                                              "guide_info": 일정관련 안내사항 (str),
                                              "winner_announce_date": 당첨자 발표일 (str),
                                              "detail" : [{"name": Parents name (str),
                                                           "sub": {"name": Child name (str),
                                                                   "condition": 조건 (str),
                                                                   "date": 일정 (str),
                                                                   "time": 시간 (str)}}]
                                                           ...}
                    }

        """

        try:
            danchi_ul_xpath = '//*[@id="hsmpNmUl"]'
            danchi_ul = self.driver.find_element_by_xpath(danchi_ul_xpath)
            danchi_lis = danchi_ul.find_elements_by_css_selector('li')
        except:
            print("ERROR: ", self.url)
            return

        supply_and_multi_danchi_info = {'gonggo_id': self.page_id, 'dangis': []}
        nums_danchi = len(danchi_lis)

        for idx, danchi_li in enumerate(danchi_lis):
            name = danchi_li.text

            danchi_href_xpath = '//*[@id="hsmpNmLi{}"]/a'.format(idx + 1)

            danchi_href = danchi_li.find_element_by_xpath(
                danchi_href_xpath)
            select_id = danchi_href.get_attribute(
                'href').split(",")[-1].split("'")[1]

            danchi_href.click()
            time.sleep(3)

            d = supply_and_multi_danchi_info["dangis"]

            danchi_info = self.get_single_danchi_info()
            danchi_info["name"] = name
            danchi_info.update(self.get_supply_info())
            d.append(danchi_info)

            supply_and_multi_danchi_info["dangis"] = d

        schedule_info = self.get_schedule_info()
        supply_and_multi_danchi_info.update(schedule_info)

        try:
            basic = self.get_basic_info()
            supply_and_multi_danchi_info.update(basic)
        except:
            return None

        return supply_and_multi_danchi_info

    def get_single_danchi_info(self):
        """
        get danchi information from detail page

        Args:
            None

        Returns:
            (Dict) : {"location": 위치정보 (str),
                      "num_household": 총세대수 (str),
                      "move_in_date": 최초입주일 (str),
                      "num_recruit": 모집호수 (str),
                      "danchi_scale": 단지규모 (str),
                      "inquire": 문의처 (str),
                      "etc": 기타 (str),
                      "pdf_url": 공고문PDF URL (str)}
        """
        location_xpath = '//*[@id="fullAdres"]'
        location = self.driver.find_element_by_xpath(location_xpath).text

        removed_map_text = location = location[:-5]

        num_household_xpath = '//*[@id="totHshldCo"]'
        num_household = self.driver.find_element_by_xpath(
            num_household_xpath).text

        move_in_date_year_xpath = '//*[@id="mvnPrearngeYear"]'
        move_in_date_year = self.driver.find_element_by_xpath(
            move_in_date_year_xpath).text

        move_in_date_month_xpath = '//*[@id="mvnPrearngeMt"]'
        move_in_date_month = self.driver.find_element_by_xpath(
            move_in_date_month_xpath).text

        move_in_date = move_in_date_year + " " + move_in_date_month

        num_recruit_xpath = '//*[@id="lttotHoCo"]'
        num_recruit = self.driver.find_element_by_xpath(
            num_recruit_xpath).text

        danchi_scale_xpath = '//*[@id="dongCo"]'
        danchi_scale = self.driver.find_element_by_xpath(
            danchi_scale_xpath).text

        inquire_xpath = '//*[@id="refrnc"]'
        inquire = self.driver.find_element_by_xpath(
            inquire_xpath).text.rstrip().replace("\n", "")
        removed_call_icon_inquire = inquire[2:]

        etc_xpath = '//*[@id="partclrMatter"]'
        etc = self.driver.find_element_by_xpath(etc_xpath).text.rstrip()
        removed_special_char_etc = etc[2:]

        pdf_xpath = '//div[contains(@class, "danjiWrap")]/table[1]/tbody/tr[6]/td/a'
        pdf_url = self.driver.find_element_by_xpath(
            pdf_xpath).get_attribute('href')

        return {"location": removed_map_text,
                "num_household": num_household,
                "move_in_date": move_in_date,
                "num_recruit": num_recruit,
                "danchi_scale": danchi_scale,
                "inquire": removed_call_icon_inquire,
                "etc": removed_special_char_etc,
                "pdf_url": pdf_url}

    def get_supply_info(self):
        """
        get supply information from detail page

        Args:
            None

        Returns:
            (Dict) : {"supply_type": 형명 (str),
                      "area": 전용면적 (str),
                      "recruit_total": 모집호수-계 (str),
                      "recruit_prior": 모집호수-우선공급 (str),
                      "recruit_general": 모집호수-일반공급 (str),
                      "lease_total_cost": 임대보증금(원)-계 (str),
                      "down_payment": 임대보증금(원)-계약금 (str),
                      "intermediate_payment": 임대보증금(원)-중도금 (str),
                      "postponing_payment": 임대보증금(원)-잔금 (str),
                      "rent_cost_per_month": 월 임대료 (str)}
        """

        supply_infos_xpath = '//*[@id="suplyTableBody"]'
        supply_infos = self.driver.find_elements_by_xpath(
            supply_infos_xpath)

        supply_info_dict = {}

        for idx, supply_info in enumerate(supply_infos):
            supply_type_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[1]'.format(
                idx + 1)
            supply_type = supply_info.find_element_by_xpath(
                supply_type_xpath).text
            td_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td'.format(idx + 1)
            td_elements = supply_info.find_elements_by_xpath(td_xpath)

            # 공급정보가 없는 경우가 있음
            # 강일리버파크 9단지
            # Refs : https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId=7130
            if len(td_elements) < 2:
                supply_info_dict = {"supply_type": "",
                                    "area": "",
                                    "recruit_total": "",
                                    "recruit_prior": "",
                                    "recruit_general": "",
                                    "lease_total_cost": "",
                                    "down_payment": "",
                                    "intermediate_payment": "",
                                    "postponing_payment": "",
                                    "rent_cost_per_month": ""}
                continue

            area_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[2]'.format(
                idx + 1)
            area = supply_info.find_element_by_xpath(area_xpath).text

            recruit_total_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[3]'.format(
                idx + 1)
            recruit_total = supply_info.find_element_by_xpath(
                recruit_total_xpath).text

            recruit_prior_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[4]'.format(
                idx + 1)
            recruit_prior = supply_info.find_element_by_xpath(
                recruit_prior_xpath).text

            recruit_general_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[5]'.format(
                idx + 1)
            recruit_general = supply_info.find_element_by_xpath(
                recruit_general_xpath).text

            lease_total_cost_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[6]'.format(
                idx + 1)
            lease_total_cost = supply_info.find_element_by_xpath(
                lease_total_cost_xpath).text

            down_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[7]'.format(
                idx + 1)
            down_payment = supply_info.find_element_by_xpath(
                down_payment_xpath).text

            intermediate_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[8]'.format(
                idx + 1)
            intermediate_payment = supply_info.find_element_by_xpath(
                intermediate_payment_xpath).text

            postponing_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[9]'.format(
                idx + 1)
            postponing_payment = supply_info.find_element_by_xpath(
                postponing_payment_xpath).text

            rent_cost_per_month_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[10]'.format(
                idx + 1)
            rent_cost_per_month = supply_info.find_element_by_xpath(
                rent_cost_per_month_xpath).text

            supply_info_dict = {"supply_type": supply_type,
                                "area": area,
                                "recruit_total": recruit_total,
                                "recruit_prior": recruit_prior,
                                "recruit_general": recruit_general,
                                "lease_total_cost": lease_total_cost,
                                "down_payment": down_payment,
                                "intermediate_payment": intermediate_payment,
                                "postponing_payment": postponing_payment,
                                "rent_cost_per_month": rent_cost_per_month}
        return supply_info_dict

    def get_schedule_info(self):
        """
        get schedule information from detail page

        Args:
            None

        Returns:
            (Dict) : {"start_date": 모집 공고일 (str),
                      "guide_info": 일정관련 안내사항 (str),
                      "winner_announce_date": 당첨자 발표일 (str),
                      "detail" : [{"name": Parents name (str),
                                   "sub": {"name": Child name (str),
                                   "condition": 조건 (str),
                                   "date": 일정 (str),
                                   "time": 시간 (str)}}]
                                ...}
        """

        date_info_table_xpath = '//div[contains(@class, "schInfo")]'
        date_info_table = self.driver.find_element_by_xpath(
            date_info_table_xpath)

        date_infos = date_info_table.find_elements_by_css_selector(
            'tr')

        table_rows = range(1, len(date_infos)+1)
        validated_table_rows = range(2, len(date_infos)-1)

        start_date_xpath = date_info_table_xpath + \
            '//tr[{}]/td'.format(table_rows[0])
        start_date = date_infos[0].find_element_by_xpath(
            start_date_xpath).text.rstrip()

        guide_info_xpath = date_info_table_xpath + \
            '//tr[{}]/td'.format(table_rows[-1])
        guide_info = date_infos[-1].find_element_by_xpath(
            guide_info_xpath).text.rstrip().replace("\n", " ")
        removed_special_char_guide_info = guide_info[1:]
        removed_click_char_guide_info = removed_special_char_guide_info[:-3]
        rectified_guide_info = removed_click_char_guide_info

        winner_announce_date_xpath = date_info_table_xpath + \
            '//tr[{}]/td'.format(table_rows[-2])
        winner_announce_date = date_infos[-2].find_element_by_xpath(
            winner_announce_date_xpath).text.rstrip()

        # TODO
        # Table Structure changed dinamically each page
        # so, Logic is little bit complex.
        detail_list = []
        for valid_row in validated_table_rows:
            rows_xpath = date_info_table_xpath + '//tr[{}]'.format(
                valid_row)
            rows = self.driver.find_elements_by_xpath(rows_xpath)

            root_dict = {"sub": []}

            parent_name = ""
            child_name = ""
            for row in rows:
                th_xpath = rows_xpath + "/th"
                ths = row.find_elements_by_xpath(th_xpath)

                # has hierarchy
                if len(ths) > 1:
                    parent_name = ths[0].text
                    child_name = ths[1].text
                else:
                    child_name = ths[0].text

                condition_xpath = rows_xpath + '/td/dl/dd[1]'
                condition = row.find_element_by_xpath(
                    condition_xpath).text.rstrip()

                date_xpath = rows_xpath + '/td/dl/dd[2]'
                date = row.find_element_by_xpath(date_xpath).text.rstrip()

                time_xpath = rows_xpath + '/td/dl/dd[3]'
                time = row.find_element_by_xpath(time_xpath).text.rstrip()

                root_dict["name"] = parent_name
                root_dict["sub"].append({"name": child_name,
                                         "condition": condition,
                                         "date": date,
                                         "time": time})
            detail_list.append(root_dict)

        return {"start_date": start_date,
                "guide_info": rectified_guide_info,
                "winner_announce_date": winner_announce_date,
                "detail": detail_list}


if __name__ == "__main__":
    root_url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="
    test_ids = ["7130", "7138", "7048", "7104", "6886", "6730"]
    test_ids = ["7193"]
    generated_test_urls = ["".join([root_url, test_id])
                           for test_id in test_ids]

    for test_url in generated_test_urls:
        print(f"TEST URL : {test_url}")
        page_crawler = PageCrawler(test_url)
        print(page_crawler.crawled_info_with_json, end="\n\n")
