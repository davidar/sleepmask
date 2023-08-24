import json
import subprocess

from handler import RemHandler


class Game:
    def __init__(self, args):
        self.process = subprocess.Popen(
            args,
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
        self.process.stdin.write(json.dumps(init_data) + "\n")

        self.handler = RemHandler()
        self.process_output()

    def send_input(self, msg=""):
        self.process.stdin.write(json.dumps(self.handler.send_input(msg)) + "\n")
        self.process_output()

    def process_output(self):
        buffer = ""
        while self.process.poll() is None:
            line = self.process.stdout.readline()
            if line.strip() == "":
                self.handler.process(json.loads(buffer))
                break
            else:
                buffer += line
