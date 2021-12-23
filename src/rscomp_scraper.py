#!/usr/bin/env python3
"""scraper for de.rs-online.com"""

import os
import datetime
import json
import logging
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src import constants as const


class RsCompBot(webdriver.Chrome):
    def __init__(self, wait: int = 60, headless: bool = const.HEADLESS, maximize: bool = False,
                 driver_path: str = const.CHROME_DRIVER_PATH, teardown: bool = True, logger=None) -> None:
        self.maximize = maximize
        self.teardown = teardown
        self.logger = logger
        self.optimized: list = []
        self.product_links: list = []
        self.product_data: list = []
        os.environ['PATH'] += ":" + driver_path
        options = Options()
        if headless:
            options.headless = True
            options.add_argument("--window-size=1920,1080")
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                         "Chrome/60.0.3112.50 Safari/537.36"
            options.add_argument(f'user-agent={user_agent}')
            options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
        super().__init__(options=options)
        self.implicitly_wait(wait)
        if self.maximize:
            self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.teardown:
            self.quit()

    def land_search_page(self, keyword: str, page: int) -> None:
        if page == 1:
            self.get('https://de.rs-online.com/web/c/?searchTerm='+keyword)
            try:
                self.find_element(By.ID, 'ensCloseBanner').click()
            except NoSuchElementException:
                pass
        elif page > 1:
            self.get('https://de.rs-online.com/web/c/?pn='+str(page)+'&searchTerm='+keyword)

    def get_product_pages(self, keyword: str, maxpages: int = None) -> None:
        for c in range(1, maxpages+1):
            time.sleep(random.randint(1, 3))
            self.land_search_page(keyword, c)
            try:
                product_list = self.find_element(By.CSS_SELECTOR, 'div[class="wrapper_2zZyTprJ loading-overlay results-wrapper"]')
                product_pages = product_list.find_elements(By.CSS_SELECTOR, 'div[data-qa="product-tile"]')
                for p in product_pages:
                    link = p.find_element(By.CSS_SELECTOR, 'a[class="link_3n-4Qpxf"]')
                    self.product_links.append(link.get_attribute('href'))
            except NoSuchElementException:
                self.logger.info(f"no data available for page {c} when searching for {keyword}")
                if self.check_load_error():
                    self.logger.info(f"load error - assuming that there are only {c-1} pages")
                    break
        self.product_links = list(dict.fromkeys(self.product_links))

    def check_load_error(self):
        load_error = False
        if self.find_element(By.ID, 'main-frame-error'):
            load_error = True
        return load_error

    def get_product_data(self):
        for pl in self.product_links:
            # add some randomness to the bot
            time.sleep(random.randint(0, 4))
            data: dict = {"url": pl}
            try:
                self.get(pl)
                data["name"] = self.find_element(By.CSS_SELECTOR, 'h1[data-testid="long-description"]').text
                data["code"] = self.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[1]/div[1]/div/div[1]/div/dl/dd[2]').text
                rsc_html = self.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                soup = BeautifulSoup(rsc_html, "html.parser")
                for item in soup.find_all("div", class_="sc-chPdSV gyouPk inc-vat"):
                    data["price"] = item.find_all("p")[0].text
                table = soup.find('table', attrs={'data-testid': 'specification-attributes'})
                body = table.find('tbody')
                for row in body.find_all('tr'):
                    attribute, value = row.find_all('td')
                    data[attribute.text] = value.text
                self.product_data.append(data)
                print(f"scraped {pl}")
                self.logger.info(f"scraped {pl}")
            except Exception:
                self.logger.info(f"skipped {pl}")
                print(f"skipped {pl}")
                pass

    def save_data(self):
        filename = "../data/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-rscomponents.json"
        with open(filename, "w") as f:
            json.dump(self.product_data, f, indent=4)

    def util_func(self, search_term, pages):
        self.get_product_pages(search_term, pages)
        self.get_product_data()
        self.save_data()


if __name__ == "__main__":
    # set up local logger
    rsc_logfile = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_rsc_scraper.log"
    rsc_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rsc_handler = logging.FileHandler(rsc_logfile)
    rsc_handler.setFormatter(rsc_formatter)
    rsc_logger = logging.getLogger(rsc_logfile.split(".")[0])
    rsc_logger.setLevel(logging.DEBUG)
    rsc_logger.addHandler(rsc_handler)

    cb = RsCompBot(logger=rsc_logger)
    cb.util_func(search_term="microcontroller", pages=5)
    print(*cb.product_data, sep="\n")
