#!/usr/bin/python
# -*- coding: utf-8 -*-
#   draw_badges.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################## VARIABLES ##################################
build_template = """
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="88" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="88" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h37v20H0z"/>
        <path fill="COLOR" d="M37 0h51v20H37z"/>
        <path fill="url(#b)" d="M0 0h88v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" 
       font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="19" y="15" fill="#010101" fill-opacity=".3">Build</text>
        <text x="19" y="14">Build</text>
        <text x="62" y="15" fill="#010101" fill-opacity=".3">VALUE</text>
        <text x="62" y="14">VALUE</text>
    </g>
</svg>
"""
coverage_template = """
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="99" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="99" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="COLOR" d="M63 0h36v20H63z"/>
        <path fill="url(#b)" d="M0 0h99v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" 
       font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="31" y="15" fill="#010101" fill-opacity=".3">Coverage</text>
        <text x="31" y="14">Coverage</text>
        <text x="81" y="15" fill="#010101" fill-opacity=".3">VALUE</text>
        <text x="81" y="14">VALUE</text>
    </g>
</svg>
"""
docs_template = """
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="70" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="70" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h35v20H0z"/>
        <path fill="COLOR" d="M35 0h35v20H35z"/>
        <path fill="url(#b)" d="M0 0h70v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle"
       font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="18" y="15" fill="#010101" fill-opacity=".3">Docs</text>
        <text x="18" y="14">Docs</text>
        <text x="52" y="15" fill="#010101" fill-opacity=".3">VALUE</text>
        <text x="52" y="14">VALUE</text>
    </g>
</svg>
"""
license_template = """
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="136" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="136" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h51v20H0z"/>
        <path fill="#fe7d37" d="M51 0h85v20H51z"/>
        <path fill="url(#b)" d="M0 0h136v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" 
       font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="26" y="15" fill="#010101" fill-opacity=".3">License</text>
        <text x="26" y="14">License</text>
        <text x="93" y="15" fill="#010101" fill-opacity=".3">BSD 3-Clause</text>
        <text x="93" y="14">BSD 3-Clause</text>
    </g>
</svg>
"""
#################################### MAIN #####################################
if __name__ == "__main__":
    import re
    from inspect import currentframe, getframeinfo
    from os.path import dirname, realpath

    root = dirname(dirname(realpath(getframeinfo(currentframe()).filename)))
    re_build = re.compile("^=+ "
                          "((?P<failed>\d+) failed)?,? ?"
                          "((?P<passed>\d+) passed)?,? ?"
                          "((?P<warnings>\d+) warnings)? in "
                          "(?P<duration>\d+\.?\d*)? seconds =+$")
    re_coverage = re.compile(r"^TOTAL\s+"
                             r"(?P<statements>\d+)+\s+"
                             r"(?P<missed>\d+)+\s+"
                             r"(?P<coverage>\d+)+%$")
    re_coverage_html = re.compile(r"^\s*<span class=\"pc_cov\">"
                                  r"(?P<coverage>\d+)%</span>$")
    re_docs = re.compile(r"^\| TOTAL\s+\|\s+"
                         r"(?P<docs>\d+\.?\d+)%\s+\|\s+"
                         r"(?P<undocumented>\d+\s+|$)")


    # | TOTAL           | 76.19%   | 5            |

    def get_build_color(passing):
        if build == "Passing":
            return "#4c1"
        else:
            return "#e05d44"


    def get_coverage_color(coverage):
        if coverage >= 95:
            return "#4c1"
        elif coverage >= 90:
            return "#97CA00"
        elif coverage >= 75:
            return "#a4a61d"
        elif coverage >= 60:
            return "#dfb317"
        elif coverage >= 40:
            return "#fe7d37"
        else:
            return "#e05d44"


    # Read test log, and html coverage is necessary
    coverage = None
    with open(f"{root}/test/test.log", "r") as infile:
        for line in infile.readlines():
            match_build = re.match(re_build, line.strip())
            if match_build:
                if match_build.groupdict()["failed"] is None:
                    build = "Passing"
                else:
                    build = "Failing"
            match_coverage = re.match(re_coverage, line.strip())
            if match_coverage:
                coverage = int(match_coverage.groupdict()["coverage"])
    if coverage is None:
        with open(f"{root}/test/htmlcov/index.html", "r") as infile:
            for line in infile.readlines():
                match_coverage = re.match(re_coverage_html, line.strip())
                if match_coverage:
                    coverage = int(match_coverage.groupdict()["coverage"])
    docs = 10
    with open(f"{root}/docs/html/python.txt", "r") as infile:
        for line in infile.readlines():
            print(line.strip())
            match_docs = re.match(re_docs, line.strip())
            if match_docs:
                docs = int(float(match_docs.groupdict()["docs"]))
    # Write build badge
    with open(f"{root}/docs/static/build.svg", "w") as outfile:
        outfile.write(build_template.strip().replace(
            "VALUE", f"{build}").replace(
            "COLOR", get_build_color(build)))
        outfile.write("\n")

    # Write coverage badge
    with open(f"{root}/docs/static/coverage.svg", "w") as outfile:
        outfile.write(coverage_template.strip().replace(
            "VALUE", f"{coverage}%").replace(
            "COLOR", get_coverage_color(coverage)))
        outfile.write("\n")

    # Write documentation badge
    with open(f"{root}/docs/static/docs.svg", "w") as outfile:
        outfile.write(docs_template.strip().replace(
            "VALUE", f"{docs}%").replace(
            "COLOR", get_coverage_color(docs)))
        outfile.write("\n")

    # Write license badge
    with open(f"{root}/docs/static/license.svg", "w") as outfile:
        outfile.write(license_template.strip())
        outfile.write("\n")
