#!/usr/bin/env python3
"""
main module for scraping data and creating ontologies
"""

import datetime
import logging
from src import conrad_scraper
from src import infinity_scraper
from src import onto_creator


PDS_LOGFILE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+"_pd_scraper.log"
pds_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
pds_handler = logging.FileHandler(PDS_LOGFILE)
pds_handler.setFormatter(pds_formatter)
pds_logger = logging.getLogger(PDS_LOGFILE.split(".")[0])
pds_logger.setLevel(logging.DEBUG)
pds_logger.addHandler(pds_handler)


def main(scrape_new: bool, search_terms: dict, pages: int) -> None:
    if scrape_new:
        cb = conrad_scraper.ConradBot(pds_logger)
        cb.util_func(search_term=search_terms["conrad"], pages=pages)
        ib = infinity_scraper.InfinityBot(pds_logger)
        ib.util_func(search_term=search_terms["infinity"], pages=pages)
    onto_creator.create_ontos(pds_logger)


if __name__ == "__main__":
    search_terms = {
        "conrad": "microcontroller",
        "infinity": "Embedded-Microcontrollers",
    }
    main(scrape_new=True, search_terms=search_terms, pages=1)
