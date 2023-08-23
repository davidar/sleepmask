def format(run):
    line = run["text"]
    style = run["style"]
    if style == "header" or style == "subheader" or style == "alert":
        return f"**{line}**"
    elif style == "input":
        return ""
    elif style == "normal" or style == "preformatted":
        return line
    elif style == "emphasized":
        return f"*{line}*"
    elif style == "user1":
        return f"_{line}_"
    elif style == "user2":
        return f"[{line}]"
    else:
        return f"<{style}>{line}</{style}>"


class RemHandler:
    def __init__(self):
        self.gen = None
        self.windows = {}
        self.inputs = []

    def process(self, obj):
        if obj.get("type") == "pass":
            return

        if "gen" in obj:
            self.gen = obj["gen"]

        if obj.get("type") == "error":
            raise Exception(f"Error: {obj['message']}")

        if obj.get("type") != "update":
            raise Exception(f"Unknown event type: {obj.get('type')}")

        if "windows" in obj:
            for window in obj["windows"]:
                self.windows[window["id"]] = window
                if window["type"] == "grid":
                    self.windows[window["id"]]["grid"] = [
                        " " * window["width"]
                    ] * window["height"]
                else:
                    self.windows[window["id"]]["buffer"] = []

        if "content" in obj:
            for content in obj["content"]:
                window = self.windows[content["id"]]
                if window["type"] == "grid":
                    for line in content["lines"]:
                        window["grid"][line["line"]] = ""
                        for run in line["content"]:
                            window["grid"][line["line"]] += format(run)
                    print("] " + "\n] ".join(window["grid"]))
                else:
                    if content.get("clear"):
                        window["buffer"] = []
                    if content.get("text"):
                        for text in content["text"]:
                            s = ""
                            if "content" in text:
                                if len(text["content"]) == 1:
                                    s = format(text["content"][0])
                                else:
                                    for run in text["content"]:
                                        s += format(run)

                            if text.get("append"):
                                window["buffer"].append("")
                                window["buffer"][-1] += s
                            else:
                                window["buffer"].append(s)

                    print("\n".join(window["buffer"]))
                    window["buffer"] = [window["buffer"][-1]]

        if "specialinput" in obj:
            self.inputs = [obj["specialinput"]]
            self.inputs[0]["gen"] = self.gen
            print(
                f"Enter a {obj['specialinput']['filetype']} filename to {obj['specialinput']['filemode']}:"
            )
        elif "input" in obj:
            self.inputs = obj["input"]
        else:
            raise Exception("No input found")

    def send_input(self, msg):
        input_id = None
        gen = None
        msgtype = "line"
        msgdetail = None

        if self.inputs:
            for input_item in self.inputs:
                if input_item["type"] == "line":
                    input_id = input_item["id"]
                    gen = input_item["gen"]
                    break
                elif input_item["type"] == "char":
                    msgtype = "char"
                    input_id = input_item["id"]
                    gen = input_item["gen"]
                    break
                elif input_item["type"] == "fileref_prompt":
                    msgtype = "specialresponse"
                    msgdetail = input_item["type"]
                    gen = input_item["gen"]

        if input_id is not None:
            if msgtype == "char":
                if not msg:
                    value = "return"
                elif msg[0] == "/":
                    parts = msg.split(" ")
                    if len(parts) == 1:
                        value = msg[1:]
                    else:
                        value = parts[1]
                    if value == "space":
                        value = " "
                else:
                    value = msg[0]
            else:
                value = msg

            return {
                "type": msgtype,
                "gen": int(gen),
                "window": int(input_id),
                "value": str(value),
            }

        elif msgdetail == "fileref_prompt":
            return {
                "type": msgtype,
                "gen": int(gen),
                "response": "fileref_prompt",
                "value": str(msg),
            }

        else:
            raise Exception(f"Couldn't send: {msg}")
