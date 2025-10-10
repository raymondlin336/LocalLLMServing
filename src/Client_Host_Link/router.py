import base64
import psutil
import requests
import json
from src.HostSide.llm_model import Model
from src.ClientSide.log import Log

class Router:
    def __init__(self, url=""):
        self.message_history = []
        self.selected_model = None
        self.url = url
        self.response_text = ""

        self.client_app = None

    def set_client_app(self, app):
        self.client_app = app

    def set_model(self, model):
        self.check_vpn()
        self.selected_model = model
        self.pull_model()
        self.check_model()

    def send_request_to_model(self, request, img):
        img_path = img.replace("\\", "/")
        if self.selected_model is None:
            Log.print_message("Error: model not selected.")
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
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600
        }

        # print(payload)

        self.message_history.append({"role": "assistant", "content": ""})
        with requests.post(f"{self.url}/api/chat", json=payload, stream=True) as response:
            # print(response.status_code)
            for line in response.iter_lines(decode_unicode=True):
                data = json.loads(line)
                self.message_history[-1]["content"] += data["message"]["content"]
                if data["message"]["content"] != "" and "<" != data["message"]["content"][0]:
                    self.client_app.append_and_show_text(data["message"]["content"])
                    print(data["message"]["content"], end="")

        print()

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
        # print(r.status_code)
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
                # print(line)
                line_dict = json.loads(line)
                if "total" in line_dict.keys() and line_dict["total"] != total:
                    total = line_dict["total"]
                if "completed" in line_dict.keys():
                    completed = line_dict["completed"]
                if total != 0:
                    Log.print_message(f"Loading model: {completed}/{total}, {round(completed / total * 100)}%")
                if line_dict["status"] == "success":
                    Log.print_message("Model loaded successfully.")

    def check_available_models(self):
        with requests.get(f"{self.url}/api/tags", timeout=1000) as response:
            for line in response.iter_lines(decode_unicode=True):
                for model in json.loads(line)["models"]:
                    print(model["name"], model["size"])

    def unload_all_models(self):
        _, models = Model.load_verified_models()
        for model in models:
            payload = {"model": model, "prompt": "", "keep_alive": 0}
            r = requests.post(f"{self.url}/api/chat", json=payload, timeout=1000)
            Log.print_model_output(r.text)
