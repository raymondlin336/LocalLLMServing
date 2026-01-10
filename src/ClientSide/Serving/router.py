import base64
import psutil
import requests
import json
from src.ClientSide.Serving.model_info import ModelInfo
from src.ClientSide.Development.log import Log
from src.ClientSide.Serving.function_tool import FunctionTool

class Router:
    def __init__(self, url="", tools_path=""):
        self.message_history = []
        self.selected_model = None
        self.url = url
        self.response_text = ""
        self.tools = json.load(open(tools_path))
        self.use_tools = True
        self.client_app = None

    def set_client_app(self, app):
        self.client_app = app

    def set_model(self, model):
        self.check_vpn()
        self.selected_model = model
        self.pull_model()
        self.check_model()

    def send_request(self, request, last_call_tools):
        if self.selected_model is None:
            Log.print_message("Error: model not selected.")
            return 0

        self.message_history.append({"role": "user", "content": request})
        if last_call_tools != []:
            for use in last_call_tools:
                self.message_history.append({"role": "tool", "tool_name": use.get_name(), "content": str(use.run())})

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

        # Add tools section to request if function calling is enabled
        if self.client_app.use_fn_calling.get():
            payload["tools"] = self.tools
            Log.print_subtitle(f"New request sent (function calling enabled)")
        else:
            Log.print_subtitle(f"New request sent (function calling disabled)")

        # Set up message history, send new request
        self.message_history.append({"role": "assistant", "content": ""})
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=False)
        Log.print_message("Model responded")

        next_call_tools = []
        # If function tools were called last round:
        if "tool_calls" in json.loads(r.text)["message"]:
            Log.print_message(json.loads(r.text)["message"])
            Log.print_message("Function tool called")
            for call in json.loads(r.text)["message"]["tool_calls"]:
                call_object = FunctionTool(call["function"]["name"], call["function"]["arguments"])
                next_call_tools.append(call_object)
            self.send_request("", next_call_tools)
        # If function tools were not called last round
        else:
            output = json.loads(r.text)["message"]["content"]
            Log.print_title("RESPONSE")
            Log.print_model_output(output)
            self.client_app.append_and_show_text(Log.return_model_output(output))

    def check_vpn(self, vpn_path="tailscale-ipn.exe"):
        Log.print_subtitle("Checking VPN connection")
        for process in psutil.process_iter(["name"]):
            try:
                if process.info["name"] == vpn_path:
                    print("Client side VPN running.")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        Log.print_message("Client side VPN is not running.")
        return False

    def check_model(self):
        Log.print_title("MODEL TESTING")
        payload = {
            "model": self.selected_model,
            "messages": [{"role": "user",
                          "content": "You are a large language model. The next line will be a user starting a conversation with you, maybe asking a question, etc."}],
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600
        }
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        if r.ok:
            Log.print_message("Model receives requests correctly.")
        else:
            Log.print_message("Model is not receiving requests correctly.")
            return r.ok

    def pull_model(self):
        Log.print_title("MODEL LOADING")
        payload = {"model": self.selected_model}
        with requests.post(f"{self.url}/api/pull", json=payload, timeout=1000, stream=True) as response:
            total = 0
            completed = 0
            for line in response.iter_lines(decode_unicode=True):
                line_dict = json.loads(line)
                if "total" in line_dict.keys() and line_dict["total"] != total:
                    total = line_dict["total"]
                if "completed" in line_dict.keys():
                    completed = line_dict["completed"]
                if total != 0:
                    Log.print_message(f"Loading model: {completed}/{total}, {round(completed / total * 100)}%")
                if line_dict["status"] == "success":
                    Log.print_message("Model loaded successfully.")

    def unload_all_models(self):
        _, models = ModelInfo.load_verified_models("ClientSide/Serving/verified_models.json")
        for model in models:
            payload = {"model": model, "prompt": "", "keep_alive": 0}
            r = requests.post(f"{self.url}/api/chat", json=payload, timeout=1000)
            Log.print_model_output(r.text)
