# -*- coding: utf-8 -*-
#
# Taiwan Radio Frequency Allocations Spectrum Parser
#
# Copyright (C) 2021 Louie Lu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
import json
import pickle

import pandas as pd
import pdfplumber


LICENSE = "Copyright (C) 2021 Louie Lu / This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. / This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. / You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>."
FILENAME = "spectrum.pdf"

START_PAGE = 30
END_PAGE = 98


class Spectrum:
    def __init__(self, start, end, unit, page):
        self.start = start
        self.end = end
        self.unit = unit
        self.unit_factor = 0
        self.normalized_start = 0
        self.normalized_end = 0
        self.note = ""
        self.usage = []
        self.page_num = page

        self.normalize_Hz()

    def normalize_Hz(self):
        UNIT_FACTOR = {"KHz": 10e3, "MHz": 10e6, "GHz": 10e9}
        self.unit_factor = UNIT_FACTOR[self.unit]
        self.normalized_start = self.start * UNIT_FACTOR[self.unit]
        self.normalized_end = self.end * UNIT_FACTOR[self.unit]

    def to_json(self):
        return {
            "range": [self.start, self.end],
            "normalized_range": [self.normalized_start, self.normalized_end],
            "unit": self.unit,
            "unit_factor": self.unit_factor,
            "usage": self.usage,
            "note": self.note,
            "page_number": self.page_num,
        }

    def __repr__(self):
        return f"<{self.start} - {self.end} {self.unit}, usage: {len(self.usage)}, note: {self.note}>"


def parse_col(col, unit, page_num):
    result = []
    for r in col:
        if r is None:
            continue
        spectrum_start_end = re.findall(r"(\d+.\d+)\s?[-–]\s?(\d+.\d+)", r)
        if spectrum_start_end:
            result.append(Spectrum(*map(float, spectrum_start_end[0]), unit, page_num))
            usage = re.findall(r"(?<=\n).*?(?=\s\n|$)", r)
            if usage:
                result[-1].usage.extend(usage)
        else:
            result[-1].usage.append(r)
    return result


def parse_with_note(table, unit, page_num):
    result = []
    for r in table.iloc[:, 1:].iterrows():
        col = r[1]["頻段業務分配"]
        note = r[1]["備註"]
        if col is None:
            continue
        spectrum_start_end = re.findall(r"(\d+.\d+)\s?[-–]\s?(\d+.\d+)", col)
        if spectrum_start_end:
            result.append(Spectrum(*map(float, spectrum_start_end[0]), unit, page_num))
            usage = re.findall(r"(?<=\n).*?(?=\s\n|$)", col)
            if usage:
                result[-1].usage.extend(usage)
        else:
            result[-1].usage.append(col)
        if note:
            result[-1].note = note.replace("\n", "")
    return result


def parse_page(page, unit, page_num):
    COLUMNS = ["ITU無線電規則", "頻段業務分配", "備註"]

    table = pd.DataFrame(
        page.extract_tables({"merged_cell_fullfill": True})[0][2:], columns=COLUMNS
    )
    parse_col(table["ITU無線電規則"], unit, page_num)
    return parse_with_note(table, unit, page_num)


def main():
    pdf = pdfplumber.open(FILENAME)

    result = []
    prev_unit = "KHz"
    for p, page in enumerate(pdf.pages[START_PAGE - 1 : END_PAGE - 1]):
        print(page)

        unit = page.crop((0, 0, 595, 80)).extract_text().strip()
        if not unit.endswith("Hz"):
            unit = prev_unit
        result.extend(parse_page(page, unit, page.page_number))
        prev_unit = unit

    # Dumping
    d = {"license": LICENSE, "spectrum": result}
    pickle.dump(d, open("spectrum.pickle", "wb"))

    d["spectrum"] = list(map(lambda x: x.to_json(), d["spectrum"]))
    json.dump(
        d,
        open("spectrum.json", "w"),
        ensure_ascii=False,
        indent=4,
    )

    return pdf


if __name__ == "__main__":
    main()
