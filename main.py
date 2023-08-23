#!/usr/bin/env python3

import json
import subprocess
import sys

from handler import RemHandler


def main():
    process = subprocess.Popen(
        sys.argv[1:],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
    )

    init_data = {
        "type": "init",
        "gen": 0,
        "metrics": {"width": 70, "height": 24},
    }
    process.stdin.write(json.dumps(init_data) + "\n")

    remhandler = RemHandler()
    buffer = ""

    while process.poll() is None:
        line = process.stdout.readline()
        if line.strip() == "":
            remhandler.process(json.loads(buffer))
            buffer = ""
            msg = input()
            process.stdin.write(json.dumps(remhandler.send_input(msg)) + "\n")
        else:
            buffer += line


if __name__ == "__main__":
    main()
