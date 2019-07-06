#!/usr/bin/python
# -*- coding: utf-8 -*-
#   update_badges.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
#################################### MAIN #####################################
if __name__ == "__main__":
    import re
    from inspect import currentframe, getframeinfo
    from os import devnull
    from os.path import dirname, realpath
    from subprocess import Popen, PIPE

    root = dirname(dirname(
        dirname(dirname(realpath(getframeinfo(currentframe()).filename)))))
    print(root)

    re_usage = re.compile(r"((?P<block_1>.*:name: derasterizer_usage\n\n))"
                          r"((?P<derasterizer_usage>.*?(?=^\S+)))"
                          r"((?P<block_2>.*:name: compositor_usage\n\n))"
                          r"((?P<compositor_usage>.*?(?=^\S+)))"
                          r"((?P<block_3>.*))",
                          re.M | re.S)

    # Read current README and split into sections
    with open(f"{root}/README.rst", "r") as infile:
        readme = infile.read()
    readme_sections = re.match(re_usage, readme).groupdict()

    # Read current Derasterizer.py usage
    with open(devnull, "w") as fnull:
        derasterizer_usage = Popen(
            f"python {root}/scinoephile/Derasterizer.py -h",
            stdout=PIPE, stderr=fnull, shell=True).stdout.read().decode(
            "utf-8")

    # Read current Compositor.py usage
    with open(devnull, "w") as fnull:
        compositor_usage = Popen(
            f"python {root}/scinoephile/Compositor.py -h",
            stdout=PIPE, stderr=fnull, shell=True).stdout.read().decode(
            "utf-8")

    # Write updated README
    with open(f"{root}/README.rst", "w") as outfile:
        outfile.write(readme_sections["block_1"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", derasterizer_usage))
        outfile.write("\n")
        outfile.write(readme_sections["block_2"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", compositor_usage))
        outfile.write("\n")
        outfile.write(readme_sections["block_3"])
