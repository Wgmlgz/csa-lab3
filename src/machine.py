import logging
from typing import Optional
from computer.computer import Machine
from computer.runner import Runner
import sys
import json
from utils import config

USAGE_STR = """
Usage: python machine.py <machine_code_file> [input_file] [-d/--debug] [-i/--interactive] [-c/--clear] [-m/--memory]
  Flags:
    -d/--debug enables debug output
    -i/--interactive enables interactive mode
    -c/--clear clears the memory before execution
    -m/--memory shows memory debug output
"""


def main(machine_code_file: str, input_file: Optional[str]):
    try:
        machine = Machine()

        # Loading machine code
        with open(machine_code_file, "r") as f:
            instructions = json.load(f)
        machine.memory.memory.load_instructions(
            instructions["instructions"], machine.word_size
        )

        # Load input data if an input file is provided; use empty input otherwise
        if input_file is not None:
            try:
                with open(input_file, "r") as f:
                    input_data = f.read().encode()
            except IOError:
                logging.warning(
                    f"Could not read input file '{input_file}'. Using empty input."
                )
                input_data = "".encode()
        else:
            input_data = "".encode()

        machine.stdin.data = input_data

        runner = Runner(machine)
        runner.run()
        # print(runner.m.stdout.data.decode())

    except Exception as err:
        logging.error("Execution failed:")
        if config["debug"]:
            raise err
        logging.error(err)
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE_STR)
        exit(1)

    machine_code_file = sys.argv[1]
    input_file = (
        sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else None
    )
    config["debug"] = "-d" in sys.argv or "--debug" in sys.argv
    if config["debug"]:
        logging.getLogger().setLevel(logging.DEBUG)

    config["interactive"] = "-i" in sys.argv or "--interactive" in sys.argv
    config["clear"] = "-c" in sys.argv or "--clear" in sys.argv
    config["debug-mem"] = "-m" in sys.argv or "--memory" in sys.argv
    main(machine_code_file, input_file)
