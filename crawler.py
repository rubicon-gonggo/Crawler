import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from collections import OrderedDict
import traceback


class MyHomeCrawler:
    def __init__(self):
        pass

    def run(self):
        # 1. Load Main page
        # 2. Get Last Contents id
        # 3. Turn Back Main Page
        # 4. Start Loop First Contents to Last Page
        # 5. Enter Detail Page & Collect Detail Information
        pass


SUPPLY_TYPE_BLACKLIST = ["매입임대", "전세임대"]


def get_chrome_web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(3)

    return driver


def get_pagenation_xpaths(driver):
    pagenation_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/div[2]/ul"
    pagenation = driver.find_elements_by_xpath(pagenation_xpath)[0]
    pagenation_list = pagenation.text.split("\n")

    num_pagenation = len(pagenation_list)

    candidates = []
    for i in range(1, num_pagenation + 1):
        candidates.append(f"li[{i}]")

    return [os.path.join(pagenation_xpath, candidate) for candidate in candidates]


def load_page(driver, url):
    driver.get(url)
    time.sleep(3)

    return driver


def move_page(driver, xpath):
    element = driver.find_elements_by_xpath(xpath)[0]
    element.click()
    time.sleep(3)
    return driver


def load_contents(driver, xpath):
    element = driver.find_elements_by_xpath(xpath)[0]
    return driver, element


if __name__ == "__main__":

    try:
        page_ids = {"ids": []}
        FINISHED_FLAG = False
        url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"
        detail_page_url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId="
        table_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody"

        driver = get_chrome_web_driver()

        # Load Main Page
        driver = load_page(driver, url)
        pagenation_xpaths = get_pagenation_xpaths(driver)

        # Move Last page for check End Points of Contents
        driver = move_page(driver, pagenation_xpaths[-1])
        driver, final_contents = load_contents(driver, table_xpath)

        table_el = driver.find_element_by_css_selector('table.bbs_type1')
        last_rows = table_el.find_elements_by_css_selector('tr')[1:]
        last_page_xpath = '//tr[{}]/td[4]/a'.format(len(last_rows))
        page_info = last_rows[-1].find_element_by_xpath(last_page_xpath)
        last_page_id = page_info.get_attribute('href').split("'")[-2]

        # Move First Page Again for Crawling Sequentially
        pagenation_xpaths = get_pagenation_xpaths(driver)
        driver = move_page(driver, pagenation_xpaths[0])

        ARRIVED_END = False

        while True:

            if ARRIVED_END == True:
                break
            # Update Pagenation
            pagenation_xpaths = get_pagenation_xpaths(driver)[3:-1]

            for pagenation_xpath in pagenation_xpaths:
                driver = move_page(driver, pagenation_xpath)
                driver, current_contents = load_contents(driver, table_xpath)

                # Get Validated Rows in Table
                table_el = driver.find_element_by_css_selector(
                    'table.bbs_type1')
                rows = table_el.find_elements_by_css_selector('tr')[1:]
                candidates = []
                for idx, row in enumerate(rows):
                    xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                    supply_type = row.find_element_by_xpath(xpath)

                    if supply_type.text not in SUPPLY_TYPE_BLACKLIST:
                        candidates.append((idx+1, row))

                for checkpoint_num, candidate in enumerate(candidates):
                    idx, row = candidate
                    page_info = row.find_element_by_xpath(
                        '//tr[{}]/td[4]/a'.format(idx))
                    page_id = page_info.get_attribute('href').split("'")[-2]
                    if page_id == last_page_id:
                        ARRIVED_END = True
                    page_ids['ids'].append(page_id)

        with open("page_ids.json", "w") as json_file:
            json.dump(page_ids, json_file)

        raise RuntimeError("Finished")
        # TODO
        # Peding

        for pagenation_xpath in pagenation_xpaths:
            driver = move_page(driver, pagenation_xpath)
            driver, current_contents = load_contents(driver, table_xpath)

            # Get Validated Rows in Table
            table_el = driver.find_element_by_css_selector('table.bbs_type1')
            rows = table_el.find_elements_by_css_selector('tr')[1:]
            candidates = []
            for idx, row in enumerate(rows):
                xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                supply_type = row.find_element_by_xpath(xpath)

                if supply_type.text not in SUPPLY_TYPE_BLACKLIST:
                    candidates.append((idx+1, row))

            for checkpoint_num, candidate in enumerate(candidates):
                idx, row = candidate
                page_info = row.find_element_by_xpath(
                    '//tr[{}]/td[4]/a'.format(idx))
                page_id = page_info.get_attribute('href').split("'")[-2]
                page_ids['ids'].append(page_id)

        with open("page_ids.json", "w") as json_file:
            json.dump(page_ids, json_file)

        raise RuntimeError("Finished")
        # TODO
        # Peding

        for pagenation_xpath in pagenation_xpaths:
            if FINISHED_FLAG:

                with open("result_of_crawling.json", "w") as json_file:
                    json.dump(result, json_file)

                print("[INFO] Crawling FINISHED")
                driver.quit()
                exit()

            driver = move_page(driver, pagenation_xpath)
            driver, current_contents = load_contents(driver, table_xpath)

            # Get Validated Rows in Table
            table_el = driver.find_element_by_css_selector('table.bbs_type1')
            rows = table_el.find_elements_by_css_selector('tr')[1:]
            candidates = []
            for idx, row in enumerate(rows):
                xpath = '//*[@id="schTbody"]/tr[{}]/td[1]'.format(idx+1)
                supply_type = row.find_element_by_xpath(xpath)

                if supply_type.text not in SUPPLY_TYPE_BLACKLIST:
                    candidates.append((idx+1, row))

            result = OrderedDict()
            for checkpoint_num, candidate in enumerate(candidates):
                idx, row = candidate
                page_info = row.find_element_by_xpath(
                    '//tr[{}]/td[4]/a'.format(idx))
                page_id = page_info.get_attribute('href').split("'")[-2]
                if page_id == last_page_id:
                    FINISHED_FLAG = True
                result[page_id] = {}

                # Move Into Page
                page_info.click()
                time.sleep(3)

                ##############################################################
                # 공고종류
                # Type : Text
                # Key-Value : `supply_category` - String
                ##############################################################
                result[page_id] = {}
                supply_category_xpath = '//*[@id="sub_content"]/div/div[1]/span'
                supply_category = driver.find_element_by_xpath(
                    supply_category_xpath)
                result[page_id]["supply_category"] = supply_category.text

                ##############################################################
                # 공고명
                # Type : Text
                # Key-Value : `name` - String
                ##############################################################
                name_xpath = '//*[@id="sub_content"]/div/div[1]/em'
                name = driver.find_element_by_xpath(name_xpath)
                result[page_id]["name"] = name.text

                ##############################################################
                # 공고대상
                # Type : List[String]
                # Key-Value : `candidates` - [String]
                ##############################################################
                result[page_id]["candidates"] = []
                candidates_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[1]'
                candidates = driver.find_elements_by_xpath(candidates_xpath)

                for candidate in candidates:
                    result[page_id]["candidates"].append(candidate.text)

                ##############################################################
                # 공급기관
                # Type : String
                # Key-Value : `supply_company` - String
                ##############################################################
                supply_company_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[2]'
                supply_company = driver.find_element_by_xpath(
                    supply_company_xpath)
                result[page_id]["supply_company"] = supply_company.text

                ##############################################################
                # 공급유형
                # Type : String
                # Key-Value : `supply_type` - String
                ##############################################################
                supply_type_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[3]'
                supply_type = driver.find_element_by_xpath(supply_type_xpath)
                result[page_id]["supply_type"] = supply_type.text

                ##############################################################
                # 주택유형
                # Type : String
                # Key-Value : `house_type` - String
                ##############################################################
                house_type_xpath = '//*[@id="sub_content"]/div/div[2]/div[2]/dl/dd[4]'
                house_type = driver.find_element_by_xpath(house_type_xpath)
                result[page_id]["house_type"] = house_type.text

                ##############################################################
                # 단지정보
                # Type : List[Dict]
                # Key-Value : `danchis` - Dict
                # {"danchis" : {"<ID>" : "name": String}}
                ##############################################################
                result[page_id]["danchis"] = {}
                danchi_ul_xpath = '//*[@id="sub_content"]/div/div[3]/div/div'
                danchi_ul = driver.find_element_by_xpath(danchi_ul_xpath)

                danchi_lis = danchi_ul.find_elements_by_css_selector('li')
                for danchi_li in danchi_lis:
                    # Danchi ID
                    danchi_href_xpath = '//*[@id="hsmpNmLi1"]/a'
                    danchi_href = danchi_li.find_element_by_xpath(
                        danchi_href_xpath)
                    select_id_raw = danchi_href.get_attribute('href')
                    select_id = select_id_raw.split(",")[-1].split("'")[1]

                    result[page_id]["danchis"][select_id] = {}
                    result[page_id]["danchis"][select_id]["name"] = danchi_li.text

                    # Click Danch ID
                    danchi_href.click()
                    time.sleep(3)

                    #! <단지정보>

                    ##############################################################
                    # 위치정보
                    # Type : Text
                    # Key-Value : `location` - String
                    ##############################################################
                    location_xpath = '//*[@id="fullAdres"]'
                    location = driver.find_element_by_xpath(location_xpath)
                    result[page_id]["danchis"][select_id]["location"] = location.text[:-5]

                    ##############################################################
                    # 총세대수
                    # Type : Text
                    # Key-Value : `num_household` - String
                    ##############################################################
                    num_household_xpath = '//*[@id="sub_content"]/div/div[3]/div/table[1]/tbody/tr[2]/td[1]'
                    num_household = driver.find_element_by_xpath(
                        num_household_xpath)
                    result[page_id]["danchis"][select_id]["num_household"] = num_household.text

                    ##############################################################
                    # 최초입주일
                    # Type : Text
                    # Key-Value : `move_in_date` - String
                    ##############################################################
                    move_in_date_xpath = '//*[@id="mvnPrearngeMt"]'
                    move_in_date = driver.find_element_by_xpath(
                        move_in_date_xpath)
                    result[page_id]["danchis"][select_id]["move_in_date"] = move_in_date.text

                    ##############################################################
                    # 모집호수
                    # Type : Text
                    # Key-Value : `num_recruit` - String
                    ##############################################################
                    num_recruit_xpath = '//*[@id="lttotHoCo"]'
                    num_recruit = driver.find_element_by_xpath(
                        num_recruit_xpath)
                    result[page_id]["danchis"][select_id]["num_recruit"] = num_recruit.text

                    ##############################################################
                    # 단지규모
                    # Type : Text
                    # Key-Value : `danchi_scale` - String
                    ##############################################################
                    danchi_scale_xpath = '//*[@id="sub_content"]/div/div[3]/div/table[1]/tbody/tr[3]/td[2]'
                    danchi_scale = driver.find_element_by_xpath(
                        danchi_scale_xpath)
                    result[page_id]["danchis"][select_id]["danchi_scale"] = danchi_scale.text

                    ##############################################################
                    # 문의처
                    # Type : Text
                    # Key-Value : `inquire` - String
                    ##############################################################
                    inquire_xpath = '//*[@id="sub_content"]/div/div[3]/div/table[1]/tbody/tr[4]/td[2]'
                    inquire = driver.find_element_by_xpath(inquire_xpath)
                    contents = inquire.text.rstrip()
                    contents = contents.replace("\n", "")

                    result[page_id]["danchis"][select_id]["inquire"] = contents

                    ##############################################################
                    # 기타
                    # Type : Text
                    # Key-Value : `etc` - String
                    ##############################################################
                    etc_xpath = '//*[@id="sub_content"]/div/div[3]/div/table[1]/tbody/tr[5]/td'
                    etc = driver.find_element_by_xpath(etc_xpath)
                    contents = etc.text.rstrip()
                    result[page_id]["danchis"][select_id]["etc"] = contents

                    ##############################################################
                    # 공고문 PDF
                    # Type : Text
                    # Key-Value : `pdf_url` - String
                    ##############################################################
                    pdf_xpath = '//*[@id="sub_content"]/div/div[3]/div/table[1]/tbody/tr[6]/td/a'
                    pdf = driver.find_element_by_xpath(pdf_xpath)
                    pdf_url = pdf.get_attribute('href')
                    result[page_id]["danchis"][select_id]["pdf_url"] = pdf_url

                    #! </단지정보>

                    #! <공급정보>
                    result[page_id]["danchis"][select_id]["supply_info"] = []
                    supply_infos_xpath = '//*[@id="suplyTableBody"]'
                    supply_infos = driver.find_elements_by_xpath(
                        supply_infos_xpath)
                    for idx, supply_info in enumerate(supply_infos):
                        supply_info_dict = {}
                        ##############################################################
                        # 형명
                        # Type : Text
                        # Key-Value : `name` - String
                        ##############################################################
                        supply_type_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[1]'.format(
                            idx + 1)
                        supply_type = supply_info.find_element_by_xpath(
                            supply_type_xpath)
                        supply_info_dict["name"] = supply_type.text

                        ##############################################################
                        # 전용면적
                        # Type : Text
                        # Key-Value : `area` - String
                        ##############################################################
                        area_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[2]'.format(
                            idx + 1)
                        area = supply_info.find_element_by_xpath(area_xpath)
                        supply_info_dict["area"] = area.text[:-2]

                        ##############################################################
                        # 모집호수 - 계
                        # Type : Text
                        # Key-Value : `area` - String
                        ##############################################################
                        supply_info_dict["recruit_info"] = {}

                        total_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[3]'.format(
                            idx + 1)
                        total = supply_info.find_element_by_xpath(total_xpath)
                        supply_info_dict["recruit_info"]["total"] = total.text

                        ##############################################################
                        # 모집호수 - 우선공급
                        # Type : Text
                        # Key-Value : `priority` - String
                        ##############################################################
                        priority_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[4]'.format(
                            idx + 1)
                        priority = supply_info.find_element_by_xpath(
                            priority_xpath)
                        supply_info_dict["recruit_info"]["priority"] = priority.text

                        ##############################################################
                        # 모집호수 - 일반공급
                        # Type : Text
                        # Key-Value : `general` - String
                        ##############################################################
                        general_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[5]'.format(
                            idx + 1)
                        general = supply_info.find_element_by_xpath(
                            general_xpath)
                        supply_info_dict["recruit_info"]["general"] = general.text

                        ##############################################################
                        # 임대보증금(원)- 계
                        # Type : Text
                        # Key-Value : `total` - String
                        ##############################################################
                        supply_info_dict["lease_cost"] = {}

                        total_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[6]'.format(
                            idx + 1)
                        total = supply_info.find_element_by_xpath(total_xpath)
                        supply_info_dict["lease_cost"]["total"] = total.text

                        ##############################################################
                        # 임대보증금(원)- 계약금
                        # Type : Text
                        # Key-Value : `down_payment` - String
                        ##############################################################
                        down_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[7]'.format(
                            idx + 1)
                        down_payment = supply_info.find_element_by_xpath(
                            down_payment_xpath)
                        supply_info_dict["lease_cost"]["down_payment"] = down_payment.text

                        ##############################################################
                        # 임대보증금(원)- 중도금
                        # Type : Text
                        # Key-Value : `intermediate_payment` - String
                        ##############################################################
                        intermediate_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[8]'.format(
                            idx + 1)
                        intermediate_payment = supply_info.find_element_by_xpath(
                            intermediate_payment_xpath)
                        supply_info_dict["lease_cost"]["intermediate_payment"] = intermediate_payment.text

                        ##############################################################
                        # 임대보증금(원)- 잔금
                        # Type : Text
                        # Key-Value : `postponing_payment` - String
                        ##############################################################
                        postponing_payment_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[9]'.format(
                            idx + 1)
                        postponing_payment = supply_info.find_element_by_xpath(
                            postponing_payment_xpath)
                        supply_info_dict["lease_cost"]["postponing_payment"] = postponing_payment.text

                        ##############################################################
                        # 월 임대료
                        # Type : Text
                        # Key-Value : `rent_cost_per_month` - String
                        ##############################################################
                        rent_cost_per_month_xpath = '//*[@id="suplyTableBody"]/tr[{}]/td[10]'.format(
                            idx + 1)
                        rent_cost_per_month = supply_info.find_element_by_xpath(
                            rent_cost_per_month_xpath)
                        supply_info_dict["lease_cost"]["rent_cost_per_month"] = rent_cost_per_month.text

                        result[page_id]["danchis"][select_id]["supply_info"].append(
                            supply_info_dict)

                    ##############################################################
                    # 일정정보
                    # Type : Text
                    # Key-Value : `date_info` - Dict
                    ##############################################################
                    result[page_id]["danchis"][select_id]["date_info"] = {}

                    date_info_table_xpath = '//*[@id="sub_content"]/div/div[4]/table/tbody'
                    date_info_table = driver.find_element_by_xpath(
                        date_info_table_xpath)
                    date_infos = date_info_table.find_elements_by_css_selector(
                        'tr')

                    detail_list = range(2, len(date_infos)-1)

                    ##############################################################
                    # 모집공고일
                    # Type : Text
                    # Key-Value : `start_date` - String
                    ##############################################################
                    # '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[4]/td'
                    start_date_xpath = '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[1]/td'
                    start_date = date_infos[0].find_element_by_xpath(
                        start_date_xpath)
                    result[page_id]["danchis"][select_id]["date_info"]["start_date"] = start_date.text.rstrip(
                    )

                    ##############################################################
                    # 안내사항
                    # Type : Text
                    # Key-Value : `guide_info` - String
                    ##############################################################
                    # '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[4]/td'
                    guide_info_xpath = '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[{}]/td'.format(
                        len(date_infos))

                    guide_info = date_infos[-1].find_element_by_xpath(
                        guide_info_xpath)
                    result[page_id]["danchis"][select_id]["date_info"]["guide_info"] = guide_info.text.rstrip(
                    )

                    ##############################################################
                    # 당첨자 발표일
                    # Type : Text
                    # Key-Value : `winner_announce_date` - String
                    ##############################################################
                    winner_announce_date_xpath = '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[{}]/td'.format(
                        len(date_infos)-1)
                    winner_announce_date = date_infos[-1].find_element_by_xpath(
                        winner_announce_date_xpath)
                    result[page_id]["danchis"][select_id]["date_info"]["winner_announce_date"] = winner_announce_date.text.rstrip()

                    ##############################################################
                    # 상세내용
                    # Type : Text
                    # Key-Value : `detail` - Dict
                    ##############################################################
                    result[page_id]["danchis"][select_id]["date_info"]["detail"] = {}
                    result[page_id]["danchis"][select_id]["date_info"]["detail"]["root"] = {}
                    for num_detail in detail_list:
                        details_xpath = '//*[@id="sub_content"]/div/div[4]/table/tbody/tr[{}]'.format(
                            num_detail)
                        details = driver.find_elements_by_xpath(details_xpath)

                        flag = False
                        for detail in details:
                            roots_xpath = details_xpath + "/th"
                            roots = detail.find_elements_by_xpath(roots_xpath)

                            result[page_id]["danchis"][select_id]["date_info"]["detail"]["root"]["name"] = roots[0].text
                            result[page_id]["danchis"][select_id]["date_info"]["detail"]["root"]["sub"] = [
                            ]
                            sub_dict = {}
                            if len(roots) > 1:
                                sub_dict["name"] = roots[1].text
                                flag = True

                            if not flag:
                                sub_dict["name"] = ""

                            condition_xpath = details_xpath + '/td/dl/dd[1]'
                            condition = detail.find_element_by_xpath(
                                condition_xpath)
                            sub_dict["condition"] = condition.text.rstrip()

                            date_xpath = details_xpath + '/td/dl/dd[2]'
                            date = detail.find_element_by_xpath(date_xpath)
                            sub_dict["date"] = date.text.rstrip()

                            time_xpath = details_xpath + '/td/dl/dd[3]'
                            time = detail.find_element_by_xpath(time_xpath)
                            sub_dict["time"] = time.text.rstrip()
                            result[page_id]["danchis"][select_id]["date_info"]["detail"]["root"]["sub"].append(
                                sub_dict)

                with open("checkpoint_{}.json".format(checkpoint_num), "w") as json_file:
                    json.dump(result, json_file)
    except Exception as e:
        traceback.print_exc()
        print("ERROR : {}".format(e))
        driver.quit()
        exit()
