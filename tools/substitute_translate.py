# Automatically modify the files generated from pyuic5

import re
import argparse


def substitute_translate_in_generated_ui_py_script(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    with open(path, 'w') as f:
        f.writelines([
"""# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object,unused-import
""",
            *lines[1:7],
            "from anki.lang import _\n"
        ])
        re1 = re.compile(r"(?:QtGui\.QApplication\.translate|_translate)\(\".*\", ")
        re2 = re.compile(r", None.*")
        f.writelines((re2.sub("))", re1.sub("_(", l)) for l in lines[7:]))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_file", type=str)
    args = argparser.parse_args()

    substitute_translate_in_generated_ui_py_script(args.in_file)
