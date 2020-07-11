import os
import json
import selenium
from typing import Dict
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback


class PageCrawler:
    def __init__(self, url: str, page_id: str):
        """
        마이홈의 상세페이지 크롤링

        Args:
            url (str) : 마이홈의 상세페이지 prefix
            page_id (str) : 상세 페이지 ID

        Returns:
            (PageCrawler)
        """
        self.url: str = url
        self.page_id: str = page_id
        self.driver = self.get_web_driver(url)
        self.driver.get(url)
        time.sleep(3)
        self.crawled_info_with_json = self.get_all_info()
        self.driver.quit()

    def get_web_driver(self, url: str) -> selenium.webdriver.chrome.webdriver.WebDriver:
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
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)
        driver.implicitly_wait(3)

        return driver

    def get_all_info(self) -> Dict:
        """
        상세 페이지의 모든 데이터를 크롤링

        Args:
            None

        Returns:
            (Dict) : {"gonggo_id" (str): 상세페이지 ID,
                      "name" (str): 상세페이지 제목,
                      "house_type" (str): 주택유형,
                      "supply_company" (str): 공급기관,
                      "supply_category" (str): 유형,
                      "candidates" (List): [공고대상],
                      "dangis" (List): [{
                                            "name" (str): 단지정보-단지이름,
                                            "location" (str): 단지정보-위치,
                                            "num_household" (str): 단지정보-총세대수,
                                            "num_recruit" (str): 단지정보-모집호수,
                                            "move_in_date" (str): 단지정보-최초입주월,
                                            "danchi_scale" (str): 단지정보-단지규모,
                                            "inquire" (str): 단지정보-문의처,
                                            "etc" (str): 단지정보-기타,
                                            "pdf_url" (str): 단지정보-공고문_PDF_url,

                                            "supply_type" (str): 공급정보-형명
                                            "area" (str): 공급정보-전용면적,
                                            "recruit_total" (str): 공급정보-모집호수-계,
                                            "recruit_prior" (str): 공급정보-모집호수-우선공급,
                                            "recruit_general" (str): 공급정보-모집호수-일반공급,
                                            "lease_total_cost" (str): 공급정보-임대보증금-계,
                                            "down_payment" (str): 공급정보-임대보증금-계약금,
                                            "intermediate_payment" (str): 공급정보-임대보증금-중도금,
                                            "postponing_payment" (str): 공급정보-임대보증금-잔금,
                                            "rent_cost_per_month" (str): 공급정보-임대보증금-월임대료(원),
                                        }
                                        ...]
                     "detail" (List): 일정정보
                                      [{
                                            "name" (): 상위 그룹
                                            "sub" (List): [{
                                                                "name" : 이름,
                                                                "condition": 조건,
                                                                "date": 일정,
                                                                "time": 시간
                                                            }
                                                           ]
                                       }
                                       ...
                                       ],
                     "guide_info" (str): 일정관련 안내사항,
                     "start_date" (str): 모집공고일,
                     "winner_announce_date" (str): 당첨자 발표일
                     }
        """

        try:
            # 단지정보 개수 및 이름확인
            danchi_ul_xpath = '//*[@id="hsmpNmUl"]'
            danchi_ul = self.driver.find_element_by_xpath(danchi_ul_xpath)
            danchi_lis = danchi_ul.find_elements_by_css_selector('li')
        except Exception as e:
            print("ERROR: ", self.url)
            traceback.print_exc()
            return

        supply_and_multi_danchi_info = {
            'gonggo_id': self.page_id, 'dangis': []}

        # 각 단지정보를 순회돌며 크롤링
        for danchi_li in danchi_lis:
            # 단지정보 이름
            name = danchi_li.text

            # 단지정보 버튼 href 획득
            danchi_href = danchi_li.find_elements_by_css_selector("a")[0]

            # 해당 단지정보 버튼을 클릭 해당 단지정보 로드
            danchi_href.click()
            time.sleep(3)

            d = supply_and_multi_danchi_info["dangis"]

            # 단일 단지정보 획득
            danchi_info = self.get_single_danchi_info()
            danchi_info["name"] = name
            d.append(danchi_info)

            # 공급정보 획득
            danchi_info.update(self.get_supply_info())

            supply_and_multi_danchi_info["dangis"] = d

        # 일정정보 획득
        schedule_info = self.get_schedule_info()
        supply_and_multi_danchi_info.update(schedule_info)

        try:
            # 기본정보 획득
            basic = self.get_basic_info()
            supply_and_multi_danchi_info.update(basic)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None

        return supply_and_multi_danchi_info

    def get_single_danchi_info(self):
        """
        get danchi information from detail page

        Args:
            None

        Returns:
            (Dict) : {"location" (str): 위치정보,
                      "num_household" (str): 총세대수,
                      "move_in_date" (str): 최초입주일,
                      "num_recruit" (str): 모집호수,
                      "danchi_scale" (str): 단지규모,
                      "inquire" (str): 문의처,
                      "etc" (str): 기타,
                      "pdf_url" (str): 공고문PDF URL}
        """
        # 위치정보
        location_xpath = '//*[@id="fullAdres"]'
        location = self.driver.find_element_by_xpath(location_xpath).text

        removed_map_text = location = location[:-5]

        # 총세대수
        num_household_xpath = '//*[@id="totHshldCo"]'
        num_household = self.driver.find_element_by_xpath(
            num_household_xpath).text

        # 최초입주일
        move_in_date_year_xpath = '//*[@id="mvnPrearngeYear"]'
        move_in_date_year = self.driver.find_element_by_xpath(
            move_in_date_year_xpath).text

        move_in_date_month_xpath = '//*[@id="mvnPrearngeMt"]'
        move_in_date_month = self.driver.find_element_by_xpath(
            move_in_date_month_xpath).text

        move_in_date = move_in_date_year + " " + move_in_date_month

        # 모집호수
        num_recruit_xpath = '//*[@id="lttotHoCo"]'
        num_recruit = self.driver.find_element_by_xpath(
            num_recruit_xpath).text

        # 단지규모
        danchi_scale_xpath = '//*[@id="dongCo"]'
        danchi_scale = self.driver.find_element_by_xpath(
            danchi_scale_xpath).text

        # 문의처
        inquire_xpath = '//*[@id="refrnc"]'
        inquire = self.driver.find_element_by_xpath(
            inquire_xpath).text.rstrip().replace("\n", "")
        removed_call_icon_inquire = inquire[2:]

        # 기타
        etc_xpath = '//*[@id="partclrMatter"]'
        etc = self.driver.find_element_by_xpath(etc_xpath).text.rstrip()
        removed_special_char_etc = etc[2:]

        # 공고문 PDF URL
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
        상세페이지에서 공급정보 크롤링

        Args:
            None

        Returns:
            (Dict) : {"supply_type" (str): 형명,
                      "area" (str): 전용면적,
                      "recruit_total" (str): 모집호수-계,
                      "recruit_prior" (str): 모집호수-우선공급,
                      "recruit_general" (str): 모집호수-일반공급,
                      "lease_total_cost" (str): 임대보증금(원)-계,
                      "down_payment" (str): 임대보증금(원)-계약금,
                      "intermediate_payment" (str): 임대보증금(원)-중도금,
                      "postponing_payment" (str): 임대보증금(원)-잔금,
                      "rent_cost_per_month" (str): 월 임대료}
        """

        supply_infos_xpath = '//*[@id="suplyTableBody"]'
        supply_infos = self.driver.find_elements_by_xpath(
            supply_infos_xpath)

        supply_info_dict = {}

        for idx, supply_info in enumerate(supply_infos):
            # 형명
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

            # 전용면적
            area_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[2]'.format(
                idx + 1)
            area = supply_info.find_element_by_xpath(area_xpath).text

            # 모집호수-계
            recruit_total_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[3]'.format(
                idx + 1)
            recruit_total = supply_info.find_element_by_xpath(
                recruit_total_xpath).text

            # 모집호수-우선공급
            recruit_prior_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[4]'.format(
                idx + 1)
            recruit_prior = supply_info.find_element_by_xpath(
                recruit_prior_xpath).text

            # 모집호수-일반공급
            recruit_general_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[5]'.format(
                idx + 1)
            recruit_general = supply_info.find_element_by_xpath(
                recruit_general_xpath).text

            # 모집호수-임대보증금(원)-계
            lease_total_cost_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[6]'.format(
                idx + 1)
            lease_total_cost = supply_info.find_element_by_xpath(
                lease_total_cost_xpath).text

            # 모집호수-임대보증금(원)-계약금
            down_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[7]'.format(
                idx + 1)
            down_payment = supply_info.find_element_by_xpath(
                down_payment_xpath).text

            # 모집호수-임대보증금(원)-중도금
            intermediate_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[8]'.format(
                idx + 1)
            intermediate_payment = supply_info.find_element_by_xpath(
                intermediate_payment_xpath).text

            # 모집호수-임대보증금(원)-잔금
            postponing_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[9]'.format(
                idx + 1)
            postponing_payment = supply_info.find_element_by_xpath(
                postponing_payment_xpath).text

            # 모집호수-임대보증금(원)-월임대료
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
        p_name = []
        c_name = []
        for idx, valid_row in enumerate(validated_table_rows):
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
                    if (len(parent_name) == 0) and (len(ths[0].text) == 0):
                        pass
                    else:
                        child_name = ths[1].text
                elif len(ths) == 1:
                    if (len(parent_name) == 0) and (len(ths[0].text) == 0):
                        pass
                    else:
                        child_name = ths[0].text
                p_name.append(parent_name)
                c_name.append(child_name)

                if (len(p_name[idx]) == 0) and (len(c_name[idx]) == 0):
                    parent_name = p_name[idx-1]
                    child_name = c_name[idx-1]

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

    def get_basic_info(self) -> Dict:
        """
        상세페이지로부터 기본적인 정보 크롤링

        Args:
            None

        Returns:
            (Dict) : {"name" (str): 공고명
                      "supply_category" (str): 공고유형,
                      "candidates" (list): 공고대상,
                      "supply_company" (str): 공급기관,
                      "supply_type" (str): 공급유형,
                      "house_type" (str): 주택유형
                      }
        """
        # 공고명
        name_xpath = '//*[@id="sub_content"]/div[@class="viewArea"]/div[@class="viewTop"]/em'
        name = self.driver.find_elements_by_xpath(name_xpath)[0].text

        info_xpath = '//*[@id="sub_content"]/div[@class="viewArea"]/div[@class="basicInfo"]/div[@class="info"]'

        # 공고대상
        candidates_xpath = info_xpath + '/dl/dd[1]'
        candidates_elements = self.driver.find_elements_by_xpath(
            candidates_xpath)
        candidates = [candidate.text for candidate in candidates_elements]

        # 공급기관
        supply_company_xpath = info_xpath + '/dl/dd[1]'
        supply_company = self.driver.find_elements_by_xpath(supply_company_xpath)[
            0].text

        # 공고유형
        supply_category_xpath = info_xpath + '/dl/dd[2]'
        supply_category = self.driver.find_elements_by_xpath(supply_category_xpath)[
            0].text

        # 공급유형
        supply_category_xpath = info_xpath + '/dl/dd[3]'
        supply_type = self.driver.find_elements_by_xpath(supply_category_xpath)[
            0].text

        # 주택유형
        house_type_xpath = info_xpath + '/dl/dd[4]'
        house_type = self.driver.find_element_by_xpath(house_type_xpath).text

        return {"name": name,
                "supply_category": supply_category,
                "candidates": candidates,
                "supply_company": supply_company,
                "supply_type": supply_type,
                "house_type": house_type}


if __name__ == "__main__":
    root_url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="
    test_ids = ["7130", "7138", "7048", "7104", "6886", "6730"]

    test_ids = ["7321"]
  
    generated_test_urls = ["".join([root_url, test_id])
                           for test_id in test_ids]

    for test_url in generated_test_urls:
        print(f"TEST URL : {test_url}")
        page_crawler = PageCrawler(test_url, "7321")
        print(page_crawler.crawled_info_with_json, end="\n\n")
