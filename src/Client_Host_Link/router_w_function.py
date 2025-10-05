from src.Client_Host_Link.router import Router
import base64
import json
import requests
from src.Client_Host_Link.function_tool import FunctionTool

class RouterF(Router):
    def __init__(self, url="", tools_path="Client_Host_Link/function_tools.json"):
        super().__init__(url)
        self.tools = json.load(open(tools_path))

    def send_request_to_model(self, request, img):
        r, calls = self.send_first_req(request, img)
        if calls == []:
            self.client_app.append_and_show_text(json.loads(r.text)["message"]["content"])
            # for line in r.iter_lines(decode_unicode=True):
            #     data = json.loads(line)
            #     self.message_history[-1]["content"] += data["message"]["content"]
            #     if data["message"]["content"] != "" and "<" != data["message"]["content"][0]:
            #         self.client_app.append_and_show_text(data["message"]["content"])
            #         print(data["message"]["content"], end="")
            # print()
        else:
            self.send_second_req(calls)

    def send_first_req(self, request, img):
        img_path = img.replace("\\", "/")
        if self.selected_model is None:
            print("Error: model not selected.")
            return 0
        if img == "":
            self.message_history.append({"role": "user", "content": request})
        else:
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("ascii")
            self.message_history.append({"role": "user", "content": request, "images": [img_b64]})
        payload = {
            "model": self.selected_model,
            "messages": self.message_history,
            "stream": False,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600,
            "tools": self.tools
        }
        self.message_history.append({"role": "assistant", "content": ""})
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        calls = []
        if "tool_calls" in json.loads(r.text)["message"]:
            print("---------- Function tool called")
            for call in json.loads(r.text)["message"]["tool_calls"]:
                call_object = FunctionTool(call["function"]["name"], call["function"]["arguments"])
                calls.append(call_object)
                call_object.run()

        return r, calls

    def send_second_req(self, calls):
        for call in calls:
            self.message_history.append({"role": "tool", "tool_name": "get_weather", "content": call.run()})
        payload = {
            "model": self.selected_model,
            "messages": self.message_history,
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600,
            "tools": self.tools
        }
        self.message_history.append({"role": "assistant", "content": ""})
        with requests.post(f"{self.url}/api/chat", json=payload, stream=True) as response:
            for line in response.iter_lines(decode_unicode=True):
                data = json.loads(line)
                self.message_history[-1]["content"] += data["message"]["content"]
                if data["message"]["content"] != "" and "<" != data["message"]["content"][0]:
                    self.client_app.append_and_show_text(data["message"]["content"])
                    print(data["message"]["content"], end="")

        print()
