#!/usr/bin/env python3
"""
helper functions for data exploration
"""

import csv
import itertools
import json
import matplotlib.pyplot as plt
from rapidfuzz.distance import Indel


def load_pp_dump(pp_file: str) -> list:
    """load data dumps w preprocessed data"""
    with open(pp_file, "r") as pp_dump:
        pp_data = json.load(pp_dump)
    return pp_data


def check_duplicate_attributes(pp_file: str) -> set:
    data = load_pp_dump(pp_file)
    same_val = set()
    for entry in data:
        for a1, a2 in itertools.combinations(entry, 2):
            if entry[a1] == entry[a2]:
                same_val.add((a1, a2))
            if entry[a1] != entry[a2] and (a1, a2) in same_val:
                same_val.remove((a1, a2))
    return same_val


def find_matches(pp_file_conrad: str, pp_file_infinity: str) -> tuple:
    """ find matches between products, relevant keys are Typ (Modell for raspis) and PART NUMBER for conrad and
    infinity, respectively
    """
    exact_matches: list = []
    sim_matches: list = []
    ids_conrad: list = []
    for entry in load_pp_dump(pp_file_conrad):
        if "Typ" in entry:
            # print((entry["name"], entry["Typ"]))
            ids_conrad.append((entry["name"], entry["Typ"]))
        elif "Modell" in entry:
            ids_conrad.append((entry["name"], entry["Modell"]))
        else:
            print(f"no identifier for {entry}")
    ids_i1 = [(e["name"], e["PART NUMBER"]) for e in load_pp_dump(pp_file_infinity)]
    ids_i2 = []
    for e in load_pp_dump(pp_file_infinity):
        if "OTHER NAMES" in e:
            ids_i2.extend([(e["name"], on) for on in e["OTHER NAMES"]])
    ids_infinity = ids_i1 + ids_i2
    for id_c, id_i in itertools.product(ids_conrad, ids_infinity):
        if id_c[1] == id_i[1]:
            exact_matches.append((id_c, id_i))
        if Indel.normalized_similarity(id_c[1], id_i[1]) > .8:
            sim_matches.append((id_c, id_i))
    return exact_matches, sim_matches


def find_possible_classes(pp_file: str) -> dict:
    """ check which attributes may be suitable as subclasses for structuring individuals
    """
    data = load_pp_dump(pp_file)
    entries_per_key = {k: [] for k in data[0].keys()}
    for e in data:
        for k in entries_per_key:
            if k in e:
                # only consider functional attributes to avoid multiple inheritance
                if not isinstance(e[k], list):
                    entries_per_key[k].append(e[k])
    entries_per_key = {k: (len(set(entries_per_key[k])), len(entries_per_key[k])) for k in entries_per_key}
    return entries_per_key


def attribute_overlap(manual_comparison: str) -> dict:
    """ check relative overlap of the attributes used to describe components
    """
    occurrences = {"conrad only": 0, "both": 0, "infinity only": 0}
    with open(manual_comparison, "r") as f:
        r = csv.reader(f)
        for row in r:
            if row[0] and row[1]:
                occurrences["both"] += 1
            elif not row[0] and row[1]:
                occurrences["conrad only"] += 1
            elif row[0] and not row[1]:
                occurrences["infinity only"] += 1
    return occurrences


def clock_rate_ranges(pp_file: str) -> dict:
    """ check the value ranges of the clock rate parameters for deriving sensible classes
    """
    occurrences = {0: 0}
    speed_keys = {
        "../data/conrad_data_dump.json": "Takt-Frequenz",
        "../data/infinity_data_dump.json": "SPEED",
    }
    data = load_pp_dump(pp_file)
    for e in data:
        if speed_keys[pp_file] in e:
            if e[speed_keys[pp_file]] in occurrences:
                occurrences[e[speed_keys[pp_file]]] += 1
            else:
                occurrences[e[speed_keys[pp_file]]] = 1
        else:
            occurrences[0] += 1
    return dict(sorted(occurrences.items()))


def plot_ranges(occurrences: dict) -> None:
    """ plot value ranges
    """
    plt.bar(list(occurrences.keys()), occurrences.values(), color='b')
    plt.show()


if __name__ == "__main__":
    data_dumps = "../data/conrad_data_dump.json", "../data/infinity_data_dump.json"
    print("product catalog size:")
    for data_dump in data_dumps:
        print(data_dump, ":", len(load_pp_dump(data_dump)))
    print("\nredundant attributes:")
    for data_dump in data_dumps:
        print(data_dump, ":", check_duplicate_attributes(data_dump))
    print("\noccurrences of attributes:")
    for data_dump in data_dumps:
        print(data_dump, ":", find_possible_classes(data_dump))
    exact_matches, sim_matches = find_matches(*data_dumps)
    for name, matches in ("exact_matches", exact_matches), ("sim_matches", sim_matches):
        print(f"\n{len(matches)} {name}:")
        print(*matches, sep="\n")
    print("\nattribute overlap:")
    print(attribute_overlap("../data/attribute_mapping_manual.csv"))
    print("\nrange of clock rates:")
    for data_dump in data_dumps:
        crr = clock_rate_ranges(data_dump)
        print(crr)
        plot_ranges(crr)
