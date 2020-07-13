#!/usr/bin/env python3
#   update_helptext.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
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

    root = dirname(dirname(dirname(dirname(realpath(
        getframeinfo(currentframe()).filename)))))
    re_helptext = re.compile(
        r"(?P<block_1>.*:name: derasterizer_helptext\n\n)"
        r"(?P<derasterizer_helptext>.*?(?=^\S+))"
        r"(?P<block_2>.*:name: compositor_helptext\n\n)"
        r"(?P<compositor_helptext>.*?(?=^\S+))"
        r"(?P<block_3>.*)",
        re.M | re.S)

    # Read current README and split into sections
    with open(f"{root}/README.rst", "r") as infile:
        readme = infile.read()
    readme_sections = re.match(re_helptext, readme).groupdict()

    # Read current cltools.rst and split into sections
    with open(f"{root}/docs/cltools.rst", "r") as infile:
        cltools = infile.read()
    cltools_sections = re.match(re_helptext, cltools).groupdict()

    # Read current Derasterizer.py usage
    with open(devnull, "w") as fnull:
        derasterizer_helptext = Popen(
            f"python {root}/scinoephile/Derasterizer.py -h",
            stdout=PIPE, stderr=fnull, shell=True).stdout.read().decode(
            "utf-8")

    # Read current Compositor.py usage
    with open(devnull, "w") as fnull:
        compositor_helptext = Popen(
            f"python {root}/scinoephile/Compositor.py -h",
            stdout=PIPE, stderr=fnull, shell=True).stdout.read().decode(
            "utf-8")

    # Write updated README
    with open(f"{root}/README.rst", "w") as outfile:
        outfile.write(readme_sections["block_1"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", derasterizer_helptext))
        outfile.write("\n")
        outfile.write(readme_sections["block_2"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", compositor_helptext))
        outfile.write("\n")
        outfile.write(readme_sections["block_3"])

    # Write updated cltools.rst
    with open(f"{root}/docs/cltools.rst", "w") as outfile:
        outfile.write(cltools_sections["block_1"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", derasterizer_helptext))
        outfile.write("\n")
        outfile.write(cltools_sections["block_2"])
        outfile.write("    ")
        outfile.write(re.sub(r"\n(.+)", "\n    \\1", compositor_helptext))
        outfile.write("\n")
        outfile.write(cltools_sections["block_3"])
