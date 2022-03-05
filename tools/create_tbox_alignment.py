#!/usr/bin/env python3
"""
create alignment for classes and datatype properties from manual comparison
"""

import csv


def reduce_to_matches(manual_comparison: str, output_file: str) -> None:
    with open(manual_comparison, "r") as inp:
        i = csv.reader(inp, delimiter=',')
        data = list(i)
    with open(output_file, "w") as outp:
        o = csv.writer(outp, quoting=csv.QUOTE_MINIMAL)
        con_prefix, inf_prefix = data[0]
        for row in data[1:]:
            if row[0] and row[1]:
                o.writerow([con_prefix + row[0], inf_prefix + row[1], "equivalence"])


def merge_alignments(inputs: list, output_file: str) -> None:
    with open(output_file, 'w') as o:
        for i in inputs:
            with open(i) as infile:
                o.write(infile.read())


if __name__ == "__main__":
    source_attrs = "../data/attribute_mapping.csv"
    source_cls = "../data/class_mapping_manual.csv"
    sink = "../data/attribute_mapping_manual.csv"
    integrated = "../data/tbox_mapping_manual.csv"
    reduce_to_matches(source_attrs, sink)
    merge_alignments([source_cls, sink], integrated)
