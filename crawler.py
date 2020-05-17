import os

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time


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


def get_detail_page_xpath(driver, current_contents):
    deatil_root_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody/"
    tail = "td[4]"

    num_of_contents = len(current_contents.split("\n"))

    candidates = []
    for i in range(1, num_of_contents+1):
        candidates.append(f"tr[{i}]")

    return [os.path.join(deatil_root_xpath, candidate, tail) for candidate in candidates]


if __name__ == "__main__":
    url = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"

    table_xpath = "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody"

    driver = get_chrome_web_driver()

    # Load Main Page
    driver = load_page(driver, url)
    pagenation_xpaths = get_pagenation_xpaths(driver)

    # Move Last page for check End Points of Contents
    driver = move_page(driver, pagenation_xpaths[-1])
    driver, final_contents = load_contents(driver, table_xpath)

    # Move First Page Again for Crawling Sequentially
    pagenation_xpaths = get_pagenation_xpaths(driver)
    driver = move_page(driver, pagenation_xpaths[0])

    # Update Pagenation
    pagenation_xpaths = get_pagenation_xpaths(driver)
    driver, current_contents = load_contents(driver, table_xpath)
    print(current_contents.text, end="\n\n")
    detail_pages_xpaths = get_detail_page_xpath(driver, current_contents.text)

    for detail_page_xpath in detail_pages_xpaths:
        driver = move_page(driver, detail_page_xpath)
        element = driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[3]/div[3]/table/tbody/tr[1]/td[4]/a")
        # Link(URL)
        page_id = element.get_attribute('href').split("'")[-2]
        print(f'URL : {page_id}')
        element.click()
        time.sleep(3)

        # 공고종류
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[1]/span")[0]
        print(f"공고종류 : {element.text}", end="\n\n")

        # 공고명
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[1]/em")[0]
        print(f"공고명 : {element.text}", end="\n\n")

        # 공고대상
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[2]/div[2]/dl/dd[1]")[0]
        print(f"공고대상 : {element.text}", end="\n\n")

        # 공급기관
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[2]/div[2]/dl/dd[2]")[0]
        print(f"공급기관 : {element.text}", end="\n\n")

        # 공급유형
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[2]/div[2]/dl/dd[3]")[0]
        print(f"공급유형 : {element.text}", end="\n\n")

        # 주택유형
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[2]/div[2]/dl/dd[4]")[0]
        print(f"주택유형 : {element.text}", end="\n\n")

        # TODO
        # for loop 돌아야함

        # 단지정보
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[3]/div/div/ul")[0]
        print(f"단지정보 : {element.text}")

        # 위치정보
        element = driver.find_elements_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[4]/div/div[3]/div/table[1]/tbody/tr[1]/td/span")[0]
        print(f"위치정보 : {element.text}")
        exit()
    exit()

    # TODO
    # lastest data 조회 한 후 update 내역 확인
    # 업데이트 해야할 내용이 있다면 크롤링 시작
