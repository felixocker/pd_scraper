#!/usr/bin/env python3
"""scraper for infinity-semiconductor.com"""

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


class InfinityBot(webdriver.Chrome):
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
            self.get('https://www.infinity-semiconductor.com/Integrated-Circuits(ICs)/'+keyword+'.aspx')
        elif page > 1:
            self.get('https://www.infinity-semiconductor.com/Integrated-Circuits(ICs)/'+keyword+'_page'+str(page)+'.aspx')

    def get_product_pages(self, keyword: str, maxpages: int = None) -> None:
        for c in range(1, maxpages+1):
            self.land_search_page(keyword, c)
            product_list = self.find_element(By.CSS_SELECTOR, 'div[class="products-list grid"]')
            product_pages = product_list.find_elements(By.TAG_NAME, 'dl')
            for p in product_pages:
                self.product_links.append(p.find_elements(By.XPATH, './/dd/a')[0].get_attribute('href'))
        self.product_links = list(dict.fromkeys(self.product_links))

    def get_product_data(self) -> None:
        for pl in self.product_links:
            # add some randomness to the bot
            time.sleep(random.randint(0, 4))
            data: dict = {}
            try:
                self.get(pl)
                data["name"] = self.find_element(By.CSS_SELECTOR, 'div[id="product-details"]').find_element(By.XPATH, './/div/h1').text
                print(data["name"])
                data["url"] = pl
                data["price"] = None
                try:
                    data["price"] = self.find_element(By.XPATH, '/html/body/div[4]/div/div[3]/form/div[2]/div[2]/dl[1]/dd').text
                except NoSuchElementException:
                    pass
                wait = WebDriverWait(self, 10)
                rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="product-details"]/div/div[4]/table/tbody/tr')))
                for row in rows:
                    attributes = row.find_elements(By.XPATH, './/th')
                    values = row.find_elements(By.XPATH, './/td')
                    for a, v in zip(attributes, values):
                        data[a.text] = v.text
                self.product_data.append(data)
                self.logger.info(f"scraped {pl}")
                print(f"scraped {pl}")
            except Exception:
                self.logger.info(f"skipped {pl}")
                print(f"skipped {pl}")
                pass

    def save_data(self) -> None:
        filename = "../data/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-infinity.json"
        with open(filename, "w") as f:
            json.dump(self.product_data, f, indent=4)

    def util_func(self, search_term: str, pages: int) -> None:
        self.get_product_pages(search_term, pages)
        self.get_product_data()
        self.save_data()


if __name__ == "__main__":
    infinity_logfile = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_infinity_scraper.log"
    infinity_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    infinity_handler = logging.FileHandler(infinity_logfile)
    infinity_handler.setFormatter(infinity_formatter)
    infinity_logger = logging.getLogger(infinity_logfile.split(".")[0])
    infinity_logger.setLevel(logging.DEBUG)
    infinity_logger.addHandler(infinity_handler)

    cb = InfinityBot(logger=infinity_logger)
    cb.util_func(search_term="Embedded-Microcontrollers", pages=3)
    print(*cb.product_data, sep="\n")
