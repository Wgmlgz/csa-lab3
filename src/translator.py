# translator.py

import logging
from lang.module import Module
from json import dumps
from utils import config
import re
import sys

USAGE_STR = """
Usage: python translator.py <input_file> [target_file] [-d/--debug]
  Flags:
    -d/--debug enables debug output
"""


def main(input_file: str, target_file: str):
    if config["debug"]:
        logging.debug("Translation completed successfully.")
    try:
        mod = Module(input_file)
        mod.link()
        executable = mod.exe
        if executable is None:
            raise Exception("No executable")
        dict = executable.to_dict()
        formatted_json = dumps(dict, indent=2)

        # Regex for pairs of a string and a number.
        formatted_json = re.sub(
            r'\[\n\s+("[^"]+",)\n\s+(-?\d+)\n\s+\]', r"[\1 \2]", formatted_json
        )
        # Regex for single-element arrays containing a string.
        formatted_json = re.sub(r'\[\n\s+("[^"]+")\n\s+\]', r"[\1]", formatted_json)
        # Regex for single-element arrays containing a number.
        formatted_json = re.sub(r"\[\n\s+(\d+)\n\s+\]", r"[\1]", formatted_json)

        with open(target_file, "w") as f:
            f.write(formatted_json)

        if config["debug"]:
            logging.debug("Translation completed successfully.")
    except Exception as err:
        logging.error("Translation failed:")
        if config["debug"]:
            raise err
        logging.error(err)
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE_STR)
        exit(1)

    input_file = sys.argv[1]

    target_file = (
        sys.argv[2]
        if len(sys.argv) > 2 and not sys.argv[2].startswith("-")
        else "out.o.json"
    )
    config["debug"] = "-d" in sys.argv or "--debug" in sys.argv
    if config["debug"]:
        logging.getLogger().setLevel(logging.DEBUG)
    main(input_file, target_file)
