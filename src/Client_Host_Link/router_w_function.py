from src.Client_Host_Link.router import Router
import base64
import json
import requests
from src.Client_Host_Link.function_tool import FunctionTool
from src.ClientSide.log import Log


class RouterF(Router):
    def __init__(self, url="", tools_path=""):
        super().__init__(url)
        self.tools = json.load(open(tools_path))
        self.use_tools = True

    def send_request_to_model(self, request, img):
        self.send_second_req(request, img, [])

    def send_second_req(self, request, img, calls):
        img_path = img.replace("\\", "/")
        if self.selected_model is None:
            Log.print_message("Error: model not selected.")
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
            "think": False
        }
        fn_call = ""
        if self.client_app.use_fn_calling.get():
            fn_call = "enabled"
            payload["tools"] = self.tools
        else:
            fn_call = "disabled"
        self.message_history.append({"role": "assistant", "content": ""})
        Log.print_subtitle(f"New request sent (function calling {fn_call})")
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=False)
        calls = []
        if "tool_calls" in json.loads(r.text)["message"]:
            Log.print_message("Function tool called")
            for call in json.loads(r.text)["message"]["tool_calls"]:
                call_object = FunctionTool(call["function"]["name"], call["function"]["arguments"])
                calls.append(call_object)
        Log.print_message("Model responded")
        if calls != []:
            self.send_second_req("", "", calls)
        else:
            output = json.loads(r.text)["message"]["content"]
            Log.print_title("RESPONSE")
            Log.print_model_output(output)
            self.client_app.append_and_show_text(Log.return_model_output(output))

    def check_model(self):
        Log.print_title("MODEL TESTING")
        request = "You are a large language model. The next line will be a user starting a conversation with you, maybe asking a question, etc. You may be provided function tools. If no function tools are used, do not mention the function tools to the user."
        self.message_history.append({"role": "user", "content": request})
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
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        Log.print_message(f"Status code: {r.status_code}")
        if r.ok:
            Log.print_message("Model receives requests correctly.")
        else:
            Log.print_message("Model is not receiving requests correctly.")
        return r.ok
