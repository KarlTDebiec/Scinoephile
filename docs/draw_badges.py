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
        <text x="19" y="15" fill="#010101" fill-opacity=".3">build</text>
        <text x="19" y="14">build</text>
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
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
        <text x="31.5" y="14">coverage</text>
        <text x="80" y="15" fill="#010101" fill-opacity=".3">VALUE</text>
        <text x="80" y="14">VALUE</text>
    </g>
</svg>
"""
license_template = """
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="78" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="78" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h47v20H0z"/>
        <path fill="#97ca00" d="M47 0h31v20H47z"/>
        <path fill="url(#b)" d="M0 0h78v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" 
       font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="24.5" y="15" fill="#010101" fill-opacity=".3">license</text>
        <text x="24.5" y="14">license</text>
        <text x="61.5" y="15" fill="#010101" fill-opacity=".3">MIT</text>
        <text x="61.5" y="14">MIT</text>
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


    def get_build_color(passing):
        if build == "passing":
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


    # Read test log
    with open(f"{root}/test/test.log", "r") as infile:
        for line in infile.readlines():
            match_build = re.match(re_build, line.strip())
            if match_build:
                if match_build.groupdict()["failed"] is None:
                    build = "passing"
                else:
                    build = "failing"
            match_coverage = re.match(re_coverage, line.strip())
            if match_coverage:
                coverage = int(match_coverage.groupdict()['coverage'])

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

    # Write license badge
    with open(f"{root}/docs/static/license.svg", "w") as outfile:
        outfile.write(license_template.strip())
        outfile.write("\n")
