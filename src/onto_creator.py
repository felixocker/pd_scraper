#!/usr/bin/env python3
"""create tboxes for ontologies to be populated with vendor catalog data"""

import ontor

CONRAD_DICT = {
    "product_name": ["name", "string"],
    "code": ["code", "string"],
    "price": ["price", "float"],
    "type": ["Typ", "string"],
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


def preprocess_conrad_data(data: list) -> list:
    raise NotImplementedError


def preprocess_infinity_data(data: list) -> list:
    raise NotImplementedError


def create_conrad_onto():
    conrad = ontor.OntoEditor("http://example.org/conrad.owl", "../data/conrad.owl")
    classes = [["microcontroller", None]]
    # TODO: add single-core attributes too
    dps = [[cd, None, True, "microcontroller", CONRAD_DICT[cd][1], None, None, None, None, None] for cd in CONRAD_DICT]
    conrad.add_taxo(classes)
    conrad.add_dps(dps)
    return conrad


def create_infinity_onto():
    infinity = ontor.OntoEditor("http://example.org/infinity.owl", "../data/infinity.owl")
    classes = [["microcontroller", None]]
    dps = [[cd, None, True, "microcontroller", INFINITY_DICT[cd][1], None, None, None, None, None] for cd in INFINITY_DICT]
    infinity.add_taxo(classes)
    infinity.add_dps(dps)
    return infinity


if __name__ == "__main__":
    conrad = create_conrad_onto()
    infinity = create_infinity_onto()
