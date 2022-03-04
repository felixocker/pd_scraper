#!/usr/bin/env python3
"""scraper for conrad.de"""

import os
import datetime
import json
import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src import constants as const


class ConradBot(webdriver.Chrome):
    def __init__(self, logger: logging.Logger, wait: int = 60, headless: bool = const.HEADLESS, maximize: bool = False,
                 driver_path: str = const.CHROME_DRIVER_PATH, teardown: bool = True) -> None:
        self.logger = logger
        self.maximize = maximize
        self.teardown = teardown
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
            self.get('https://www.conrad.de/de/search.html?search='+keyword)
            try:
                self.find_element(By.CSS_SELECTOR, 'div[class="cmsCookieNotification__button cmsCookieNotification__button--accept"]').click()
            except NoSuchElementException:
                pass
        elif page > 1:
            self.get('https://www.conrad.de/de/search.html?search='+keyword+'&page='+str(page))

    def get_product_pages(self, keyword: str, maxpages: int = None) -> None:
        for c in range(1, maxpages+1):
            self.land_search_page(keyword, c)
            product_list = self.find_element(By.ID, 'scroller')
            product_pages = product_list.find_elements(By.CSS_SELECTOR, 'a[class="product__title"]')
            for p in product_pages:
                self.product_links.append(p.get_attribute('href'))
        self.product_links = list(dict.fromkeys(self.product_links))

    def get_product_data(self) -> None:
        for pl in self.product_links:
            # add some randomness to the bot
            time.sleep(random.randint(0, 4))
            data: dict = {}
            try:
                self.get(pl)
                data["name"] = self.find_element(By.CSS_SELECTOR, 'h1[id="ProductTitle"]').text
                data["url"] = pl
                data["ean"] = self.find_element(By.CSS_SELECTOR, 'dd[id="eanCode"]').text
                data["code"] = self.find_element(By.CSS_SELECTOR, 'dd[id="manufacturerCode"]').text
                data["price"] = None
                for ps in 'p[id="productPriceUnitPrice"]', 'span[id="productPriceUnitPrice"]':
                    try:
                        data["price"] = self.find_element(By.CSS_SELECTOR, ps).text
                    except NoSuchElementException:
                        pass
                wait = WebDriverWait(self, 10)
                rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'dl[class="productTechData__list"]')))
                for row in rows:
                    attribute = row.find_element(By.TAG_NAME, 'dt').text
                    values = [v.text for v in row.find_elements(By.TAG_NAME, 'span')]
                    if len(values) == 1:
                        data[attribute] = values[0]
                    elif len(values) > 1:
                        data[attribute] = values
                self.product_data.append(data)
                self.logger.info(f"scraped {pl}")
                print(f"scraped {pl}")
            except Exception:
                self.logger.info(f"skipped {pl}")
                print(f"skipped {pl}")
                pass

    def filter_product_type(self, product_types: list) -> None:
        inter = [pd for pd in self.product_data if "Produkt-Art" in pd]
        self.product_data = [pd for pd in inter if pd["Produkt-Art"] in product_types]

    def save_data(self) -> None:
        filename = "../data/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-conrad.json"
        with open(filename, "w") as f:
            json.dump(self.product_data, f, indent=4)

    def util_func(self, search_term: str, pages: int) -> None:
        self.get_product_pages(search_term, pages)
        self.get_product_data()
        self.filter_product_type(['Embedded-Mikrocontroller', 'Single-Board-Computer'])
        self.save_data()


if __name__ == "__main__":
    conrad_logfile = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_conrad_scraper.log"
    conrad_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    conrad_handler = logging.FileHandler(conrad_logfile)
    conrad_handler.setFormatter(conrad_formatter)
    conrad_logger = logging.getLogger(conrad_logfile.split(".")[0])
    conrad_logger.setLevel(logging.DEBUG)
    conrad_logger.addHandler(conrad_handler)

    cb = ConradBot(logger=conrad_logger)
    cb.util_func(search_term="microcontroller", pages=3)
    print(*cb.product_data, sep="\n")
