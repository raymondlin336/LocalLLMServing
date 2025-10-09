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
        self.send_second_req(request, img, [])

    def send_second_req(self, request, img, calls):
        img_path = img.replace("\\", "/")
        if self.selected_model is None:
            print("Error: model not selected.")
            return 0
        if request == "":
            pass
        elif img == "":
            self.message_history.append({"role": "user", "content": request})
        else:
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("ascii")
            self.message_history.append({"role": "user", "content": request, "images": [img_b64]})
        if calls != []:
            for call in calls:
                self.message_history.append({"role": "tool", "tool_name": call.get_name(), "content": str(call.run())})
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
        print(self.message_history)
        print("---------- New request sent")
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=False)
        calls = []
        print(json.loads(r.text))
        if "tool_calls" in json.loads(r.text)["message"]:
            print("---------- Function tool called")
            for call in json.loads(r.text)["message"]["tool_calls"]:
                call_object = FunctionTool(call["function"]["name"], call["function"]["arguments"])
                calls.append(call_object)
                call_object.run()
        if calls != []:
            self.send_second_req("", "", calls)
        self.client_app.append_and_show_text(json.loads(r.text)["message"]["content"])

        print()

    def check_model(self):
        print("==================== Model Testing")
        payload = {
            "model": self.selected_model,
            "messages": [{"role": "user",
                          "content": "You are a large language model. The next line will be a user starting a conversation with you, maybe asking a question, etc."}],
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600,
            "tools": self.tools
        }
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        # print(r.status_code)
        if r.ok:
            print("Model receives requests correctly.")
        else:
            print("Model is not receiving requests correctly.")
        return r.ok
