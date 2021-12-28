#!/usr/bin/env python3
"""create tboxes for ontologies to be populated with vendor catalog data"""

import csv
import itertools
import json
import logging
import typing
import ontor
import owlready2

CONRAD_DICT = {
    "product_name": ["name", "string"],
    "code": ["code", "string"],
    "price": ["price", "float"],
    "prod_type": ["Typ", "string"],
    "manufacturer": ["Hersteller", "string"],
    "manuf_abbrev": ["Herst.-Abk.", "string"],
    "housing": ["Gehäuse", "string"],
    "clock_rate": ["Takt-Frequenz", "integer"],
    "series": ["Serie", "string"],
    "core_size_bit": ["Kerngröße", "integer"],
    "core_processor": ["Kern-Prozessor", "string"],
    "oscillator_type": ["Oszillator-Typ", "string"],
    "periphery_devices": ["Peripheriegeräte", "string"],
    "number_ios": ["Anzahl I/O", "integer"],
    "program_memory_type": ["Programmspeichertyp", "string"],
    "voltage_max": ["Versorgungsspannung max.", "float"],
    "voltage_min": ["Versorgungsspannung min.", "float"],
    "operating_temp_max": ["Betriebstemperatur (max.)", "integer"],
    "operating_temp_min": ["Betriebstemperatur (min.)", "integer"],
    "data_converter": ["Datenwandler (Embedded Mikrocontroller)", "string"],
    "eeprom": ["EEPROM Größe", "string"],
    "connectivity": ["Konnektivität", "string"],
    "program_memory_size_kb": ["Programmspeichergröße", "float"],
    "ram_size": ["RAM-Größe", "string"],
}

INFINITY_DICT = {
    "product_name": ["name", "string"],
    "price": ["price", "float"],
    "part_number": ["PART NUMBER", "string"],
    "manufacturer": ["MANUFACTURER", "string"],
    "description": ["DESCRIPTION", "string"],
    "lead_free_rohs": ["LEAD FREE STATUS / ROHS STATUS", "string"],
    "quantity_available": ["QUANTITY AVAILABLE", "integer"],
    "data_sheet": ["DATA SHEET", "string"],
    "voltage_max": ["VOLTAGE - SUPPLY (VCC/VDD) MAX", "integer"],
    "voltage_min": ["VOLTAGE - SUPPLY (VCC/VDD) MIN", "integer"],
    "supplier_device_package": ["SUPPLIER DEVICE PACKAGE", "string"],
    "speed_mhz": ["SPEED", "float"],
    "series": ["SERIES", "string"],
    "ram_size": ["RAM SIZE", "string"],
    "program_memory_type": ["PROGRAM MEMORY TYPE", "string"],
    "program_memory_size_kb": ["PROGRAM MEMORY SIZE", "float"],
    "peripherals": ["PERIPHERALS", "string"],
    "packaging": ["PACKAGING", "string"],
    "package": ["PACKAGE / CASE", "string"],
    "oscillator_type": ["OSCILLATOR TYPE", "string"],
    "operating_temp_max": ["OPERATING TEMPERATURE MAX", "integer"],
    "operating_temp_min": ["OPERATING TEMPERATURE MIN", "integer"],
    "number_ios": ["NUMBER OF I/O", "integer"],
    "moisture_sensitivity_level": ["MOISTURE SENSITIVITY LEVEL (MSL)", "string"],
    "eeprom_size": ["EEPROM SIZE", "string"],
    "detailed_description": ["DETAILED DESCRIPTION", "string"],
    "data_converters": ["DATA CONVERTERS", "string"],
    "core_size_bit": ["CORE SIZE", "integer"],
    "core_processor": ["CORE PROCESSOR", "string"],
    "connectivity": ["CONNECTIVITY", "string"],
}


def preprocess_conrad_data(data: list, logger: logging.Logger, pp_file: typing.Optional[str] = None) -> None:
    # TODO: also add attributes scraped for single-board computers, e.g., "Modell"
    for elem in data:
        elem["price"] = float(elem["price"].split()[0].replace(",", "."))
        for k in "clock_rate", "number_ios", "operating_temp_max", "operating_temp_min":
            try:
                elem[CONRAD_DICT[k][0]] = int(elem[CONRAD_DICT[k][0]])
            except KeyError:
                logger.info(f"no {k} available for {elem}")
        for k in "voltage_max", "voltage_min":
            try:
                elem[CONRAD_DICT[k][0]] = float(elem[CONRAD_DICT[k][0]])
            except KeyError:
                logger.info(f"no {k} available for {elem}")
        try:
            elem[CONRAD_DICT["core_size_bit"][0]] = int(elem[CONRAD_DICT["core_size_bit"][0]].split("-Bit")[0])
        except KeyError:
            logger.info(f"no core_size_bit available for {elem}")
        try:
            if "KB" in elem[CONRAD_DICT["program_memory_size_kb"][0]]:
                elem[CONRAD_DICT["program_memory_size_kb"][0]] = float(elem[CONRAD_DICT["program_memory_size_kb"][0]].split(" KB")[0])
            elif "B" in elem[CONRAD_DICT["program_memory_size_kb"][0]]:
                elem[CONRAD_DICT["program_memory_size_kb"][0]] = float(elem[CONRAD_DICT["program_memory_size_kb"][0]].split(" B")[0])/1000
            else:
                logger.info(f"unexpected memory unit in {elem[CONRAD_DICT['program_memory_size_kb'][0]]} for {elem[CONRAD_DICT['product_name'][0]]}")
        except KeyError:
            logger.info(f"no program_memory_size_kb available for {elem}")
    if pp_file:
        with open(pp_file, "w") as ppf:
            json.dump(data, ppf, indent=4)


def preprocess_infinity_data(data: list, logger: logging.Logger, pp_file: typing.Optional[str] = None) -> None:
    # TODO: do not treat ram info as string? - same for conrad data
    for elem in data:
        try:
            elem["price"] = float(elem["price"][1:])
        except TypeError:
            logger.info(f"issue with the price for {elem[INFINITY_DICT['product_name'][0]]}")
            elem.pop("price")
        try:
            elem[INFINITY_DICT["number_ios"][0]] = int(elem[INFINITY_DICT["number_ios"][0]])
        except KeyError:
            logger.info(f"no number_ios available for {elem[INFINITY_DICT['product_name'][0]]}")
        elem[INFINITY_DICT["quantity_available"][0]] = int(elem[INFINITY_DICT["quantity_available"][0]].split(" pcs")[0])
        try:
            elem[INFINITY_DICT["core_size_bit"][0]] = int(elem[INFINITY_DICT["core_size_bit"][0]].split("-Bit")[0])
        except KeyError:
            logger.info(f"no core_size_bit available for {elem[INFINITY_DICT['product_name'][0]]}")
        except ValueError:
            logger.info(f"unexpected value in {elem[INFINITY_DICT['core_size_bit'][0]]} for {elem[INFINITY_DICT['product_name'][0]]}")
            elem.pop(INFINITY_DICT['core_size_bit'][0])
        try:
            if "MHz" in elem[INFINITY_DICT["speed_mhz"][0]]:
                elem[INFINITY_DICT["speed_mhz"][0]] = float(elem[INFINITY_DICT["speed_mhz"][0]].split("MHz")[0])
            else:
                logger.info(f"unexpected unit in {elem[INFINITY_DICT['speed_mhz'][0]]} for {elem[INFINITY_DICT['product_name'][0]]}")
                elem.pop(INFINITY_DICT['speed_mhz'][0])
        except KeyError:
            logger.info(f"no speed_mhz available for {elem[INFINITY_DICT['product_name'][0]]}")
        try:
            if "KB" in elem[INFINITY_DICT["program_memory_size_kb"][0]]:
                elem[INFINITY_DICT["program_memory_size_kb"][0]] = float(elem[INFINITY_DICT["program_memory_size_kb"][0]].split("KB")[0])
            elif "MB" in elem[INFINITY_DICT["program_memory_size_kb"][0]]:
                elem[INFINITY_DICT["program_memory_size_kb"][0]] = float(elem[INFINITY_DICT["program_memory_size_kb"][0]].split("MB")[0]*1000)
            else:
                logger.info(f"unexpected unit in {elem[INFINITY_DICT['program_memory_size_kb'][0]]} for {elem[INFINITY_DICT['product_name'][0]]}")
                elem.pop(INFINITY_DICT['program_memory_size_kb'][0])
        except KeyError:
            logger.info(f"no program_memory_size_kb available for {elem[INFINITY_DICT['product_name'][0]]}")
        # split up temperature values
        try:
            elem[INFINITY_DICT["operating_temp_max"][0]] = int(elem["OPERATING TEMPERATURE"].split(" ~ ")[1].split("°")[0])
            elem[INFINITY_DICT["operating_temp_min"][0]] = int(elem["OPERATING TEMPERATURE"].split(" ~ ")[0].split("°")[0])
        except KeyError:
            logger.info(f"no operating_temp available for {elem[INFINITY_DICT['product_name'][0]]}")
        # split up voltage values
        try:
            print(elem["VOLTAGE - SUPPLY (VCC/VDD)"])
            elem[INFINITY_DICT["voltage_max"][0]] = float(elem["VOLTAGE - SUPPLY (VCC/VDD)"].split(" ~ ")[1].split(" V")[0])
            elem[INFINITY_DICT["voltage_min"][0]] = float(elem["VOLTAGE - SUPPLY (VCC/VDD)"].split(" ~ ")[0].split(" V")[0])
        except IndexError:
            logger.info(f"issue with voltage for {elem[INFINITY_DICT['product_name'][0]]}")
        except KeyError:
            logger.info(f"no voltage available for {elem[INFINITY_DICT['product_name'][0]]}")
    if pp_file:
        with open(pp_file, "w") as ppf:
            json.dump(data, ppf, indent=4)


def create_conrad_onto(scraped_data: list, logger: logging.Logger) -> None:
    conrad = ontor.OntoEditor("http://example.org/conrad.owl", "../data/conrad.owl")
    classes = [["microcontroller", None]]
    # TODO: add single-core attributes too
    dps = [[cd, None, True, "microcontroller", CONRAD_DICT[cd][1], None, None, None, None, None] for cd in CONRAD_DICT]
    conrad.add_taxo(classes)
    conrad.add_dps(dps)
    preprocess_conrad_data(scraped_data, logger, "../data/conrad_data_dump.json")
    populate_with_scraped_data(conrad, scraped_data, logger, CONRAD_DICT)


def create_infinity_onto(scraped_data: list, logger: logging.Logger) -> None:
    infinity = ontor.OntoEditor("http://example.org/infinity.owl", "../data/infinity.owl")
    classes = [["microcontroller", None]]
    dps = [[cd, None, True, "microcontroller", INFINITY_DICT[cd][1], None, None, None, None, None] for cd in INFINITY_DICT]
    infinity.add_taxo(classes)
    infinity.add_dps(dps)
    preprocess_infinity_data(scraped_data, logger, "../data/infinity_data_dump.json")
    populate_with_scraped_data(infinity, scraped_data, logger, INFINITY_DICT)


def populate_with_scraped_data(pd_ontor: ontor.OntoEditor, scraped_data: list, logger: logging.Logger, pd_dict: dict) -> None:
    for c, prod in enumerate(scraped_data):
        instance_name = "infinity_" + "0"*(3-len(str(c))) + str(c)
        prod_ins_data = [[instance_name, "microcontroller", None, None, None]]
        for key in pd_dict:
            try:
                prod_ins_data.append([instance_name, "microcontroller", key, prod[pd_dict[key][0]], pd_dict[key][1]])
            except KeyError:
                logger.info(f"{key} not available for product number {instance_name}")
        pd_ontor.add_instances(prod_ins_data)


def save_reference_alignment_as_csv(alignment_file: str) -> None:
    with open(alignment_file, "w") as af:
        writer = csv.writer(af, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for line in create_reference_alignment():
            writer.writerow(line)


def create_reference_alignment(conrad_iri: str = "http://example.org/conrad.owl",
                               infinity_iri: str = "http://example.org/infinity.owl") -> list:
    """ create reference alignment based on infinity part number and conrad typ

    :return: nested list with expected correspondences [elem1, elem2, relationship]
    """
    matches = find_matches("../data/conrad_data_dump.json", "../data/infinity_data_dump.json")
    correspondences: list = []
    owlready2.onto_path.append("../data/")
    conrad_onto = owlready2.get_ontology(conrad_iri).load()
    infinity_onto = owlready2.get_ontology(infinity_iri).load()
    for m in matches:
        conrad_iri = conrad_onto.search_one(prod_type = m[0][1])
        infinity_iri = infinity_onto.search_one(part_number = m[1][1])
        correspondences.append([conrad_iri.iri, infinity_iri.iri, "equivalence"])
    return correspondences


def find_matches(pp_file_conrad: str, pp_file_infinity: str) -> list:
    """ find matches between products, relevant keys are Typ (Modell for raspis) and PART NUMBER for conrad and
    infinity, respectively
    """
    matches: list = []
    ids_conrad: list = []
    for entry in load_pp_dump(pp_file_conrad):
        if "Typ" in entry:
            ids_conrad.append((entry["name"], entry["Typ"]))
        elif "Modell" in entry:
            ids_conrad.append((entry["name"], entry["Modell"]))
        else:
            print(f"conrad: no identifier for {entry}")
    ids_infinity: list = []
    for entry in load_pp_dump(pp_file_infinity):
        if "PART NUMBER" in entry:
            ids_infinity.append((entry["name"], entry["PART NUMBER"]))
        else:
            print(f"infinity: no identifier for {entry}")
    for id_c, id_i in itertools.product(ids_conrad, ids_infinity):
        if id_c[1] == id_i[1]:
            matches.append((id_c, id_i))
    return matches


def load_pp_dump(pp_file: str) -> list:
    """load data dumps w preprocessed data"""
    with open(pp_file, "r") as pp_dump:
        pp_data = json.load(pp_dump)
    return pp_data


if __name__ == "__main__":
    print(create_reference_alignment())
    save_reference_alignment_as_csv("test.csv")
