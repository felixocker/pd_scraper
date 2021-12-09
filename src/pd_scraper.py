#!/usr/bin/env python3
"""main module for scraping data and creating ontologies"""

import datetime
import json
import logging
import os
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


def main(scrape_new: bool):
    # scrape data
    if scrape_new:
        cb = conrad_scraper.ConradBot()
        cb.util_func()
        ib = infinity_scraper.InfinityBot()
        ib.util_func()
    # access data scraped
    scraped_files = os.listdir("../data/")
    with open("../data/"+sorted(sf for sf in scraped_files if "conrad.json" in sf)[-1], "r") as conrad_file:
        conrad_data = json.load(conrad_file)
    # TODO: set position to -1 to load large data set
    with open("../data/"+sorted(sf for sf in scraped_files if "infinity.json" in sf)[-1]) as infinity_file:
        infinity_data = json.load(infinity_file)

    # data preprocessing
    con_dict = onto_creator.CONRAD_DICT
    # TODO: also add attributes scraped for single-board computers
    for elem in conrad_data:
        elem["price"] = float(elem["price"].split()[0].replace(",", "."))
        for k in "clock_rate", "number_ios", "operating_temp_max", "operating_temp_min":
            try:
                elem[con_dict[k][0]] = int(elem[con_dict[k][0]])
            except KeyError:
                pds_logger.info(f"no {k} available for {elem}")
        for k in "voltage_max", "voltage_min":
            try:
                elem[con_dict[k][0]] = float(elem[con_dict[k][0]])
            except KeyError:
                pds_logger.info(f"no {k} available for {elem}")
        try:
            elem[con_dict["core_size_bit"][0]] = int(elem[con_dict["core_size_bit"][0]].split("-Bit")[0])
        except KeyError:
            pds_logger.info(f"no core_size_bit available for {elem}")
        try:
            if "KB" in elem[con_dict["program_memory_size_kb"][0]]:
                elem[con_dict["program_memory_size_kb"][0]] = float(elem[con_dict["program_memory_size_kb"][0]].split(" KB")[0])
            elif "B" in elem[con_dict["program_memory_size_kb"][0]]:
                elem[con_dict["program_memory_size_kb"][0]] = float(elem[con_dict["program_memory_size_kb"][0]].split(" B")[0])/1000
            else:
                pds_logger.info(f"unexpected memory unit in {elem[con_dict['program_memory_size_kb'][0]]} for {elem[con_dict['product_name'][0]]}")
        except KeyError:
            pds_logger.info(f"no program_memory_size_kb available for {elem}")

    inf_dict = onto_creator.INFINITY_DICT
    # TODO: do not treat ram info as string? - same for conrad data
    for elem in infinity_data:
        try:
            elem["price"] = float(elem["price"][1:])
        except TypeError:
            pds_logger.info(f"issue with the price for {elem[inf_dict['product_name'][0]]}")
            elem.pop("price")
        try:
            elem[inf_dict["number_ios"][0]] = int(elem[inf_dict["number_ios"][0]])
        except KeyError:
            pds_logger.info(f"no number_ios available for {elem[inf_dict['product_name'][0]]}")
        elem[inf_dict["quantity_available"][0]] = int(elem[inf_dict["quantity_available"][0]].split(" pcs")[0])
        try:
            elem[inf_dict["core_size_bit"][0]] = int(elem[inf_dict["core_size_bit"][0]].split("-Bit")[0])
        except KeyError:
            pds_logger.info(f"no core_size_bit available for {elem[inf_dict['product_name'][0]]}")
        except ValueError:
            pds_logger.info(f"unexpected value in {elem[inf_dict['core_size_bit'][0]]} for {elem[inf_dict['product_name'][0]]}")
            elem.pop(inf_dict['core_size_bit'][0])
        try:
            if "MHz" in elem[inf_dict["speed_mhz"][0]]:
                elem[inf_dict["speed_mhz"][0]] = float(elem[inf_dict["speed_mhz"][0]].split("MHz")[0])
            else:
                pds_logger.info(f"unexpected unit in {elem[inf_dict['speed_mhz'][0]]} for {elem[inf_dict['product_name'][0]]}")
                elem.pop(inf_dict['speed_mhz'][0])
        except KeyError:
            pds_logger.info(f"no speed_mhz available for {elem[inf_dict['product_name'][0]]}")
        try:
            if "KB" in elem[inf_dict["program_memory_size_kb"][0]]:
                elem[inf_dict["program_memory_size_kb"][0]] = float(elem[inf_dict["program_memory_size_kb"][0]].split("KB")[0])
            elif "MB" in elem[inf_dict["program_memory_size_kb"][0]]:
                elem[inf_dict["program_memory_size_kb"][0]] = float(elem[inf_dict["program_memory_size_kb"][0]].split("MB")[0]*1000)
            else:
                pds_logger.info(f"unexpected unit in {elem[inf_dict['program_memory_size_kb'][0]]} for {elem[inf_dict['product_name'][0]]}")
                elem.pop(inf_dict['program_memory_size_kb'][0])
        except KeyError:
            pds_logger.info(f"no program_memory_size_kb available for {elem[inf_dict['product_name'][0]]}")
        # split up temperature values
        try:
            elem[inf_dict["operating_temp_max"][0]] = int(elem["OPERATING TEMPERATURE"].split(" ~ ")[1].split("°")[0])
            elem[inf_dict["operating_temp_min"][0]] = int(elem["OPERATING TEMPERATURE"].split(" ~ ")[0].split("°")[0])
        except KeyError:
            pds_logger.info(f"no operating_temp available for {elem[inf_dict['product_name'][0]]}")
        # split up voltage values
        try:
            print(elem["VOLTAGE - SUPPLY (VCC/VDD)"])
            elem[inf_dict["voltage_max"][0]] = float(elem["VOLTAGE - SUPPLY (VCC/VDD)"].split(" ~ ")[1].split(" V")[0])
            elem[inf_dict["voltage_min"][0]] = float(elem["VOLTAGE - SUPPLY (VCC/VDD)"].split(" ~ ")[0].split(" V")[0])
        except IndexError:
            pds_logger.info(f"issue with voltage for {elem[inf_dict['product_name'][0]]}")
        except KeyError:
            pds_logger.info(f"no voltage available for {elem[inf_dict['product_name'][0]]}")

    # create ontologies
    conrad_ontor = onto_creator.create_conrad_onto()
    for c, prod in enumerate(conrad_data):
        instance_name = "conrad_" + "0"*(3-len(str(c))) + str(c)
        prod_ins_data = [[instance_name, "microcontroller", None, None, None]]
        for key in con_dict:
            try:
                prod_ins_data.append([instance_name, "microcontroller", key, prod[con_dict[key][0]], con_dict[key][1]])
            except KeyError:
                pds_logger.info(f"{key} not available for product number {instance_name}")
        conrad_ontor.add_instances(prod_ins_data)

    infinity_ontor = onto_creator.create_infinity_onto()
    for c, prod in enumerate(infinity_data):
        instance_name = "infinity_" + "0"*(3-len(str(c))) + str(c)
        prod_ins_data = [[instance_name, "microcontroller", None, None, None]]
        for key in inf_dict:
            try:
                prod_ins_data.append([instance_name, "microcontroller", key, prod[inf_dict[key][0]], inf_dict[key][1]])
            except KeyError:
                pds_logger.info(f"{key} not available for product number {instance_name}")
        infinity_ontor.add_instances(prod_ins_data)

    # TODO: refactor - move preprocessing and onto creation to respective file
    # TODO: create gold standard for alignment - EAN or part number unique?


if __name__ == "__main__":
    main(scrape_new=False)
