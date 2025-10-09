import base64
import psutil
import requests
import json

class SendAndReceive:
    def __init__(self, url="http://127.0.0.1:11434"):  # default stays loopback
        self.message_history = []
        self.selected_model = None
        self.url = url
        self.response_text = ""
        self.client_app = None

    def set_client_app(self, app):
        self.client_app = app

    # NEW: called by the GUI when user picks a host/port
    def set_url(self, host: str, port: int):
        self.url = f"http://{host}:{port}"
        print(f"=== Server URL set to {self.url}")

    def set_model(self, model):
        self.check_vpn()
        self.selected_model = model
        self.pull_model()
        self.check_model()

    def send_request_to_model(self, request, img):
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
            "stream": True,
            "options": {"num_predict": -1},
            "keep_alive": 3600
        }

        self.message_history.append({"role": "assistant", "content": ""})
        with requests.post(f"{self.url}/api/chat", json=payload, stream=True) as response:
            for line in response.iter_lines(decode_unicode=True):
                data = json.loads(line)
                self.message_history[-1]["content"] += data["message"]["content"]
                if data["message"]["content"] != "" and "<" != data["message"]["content"][0]:
                    if self.client_app:
                        self.client_app.append_and_show_text(data["message"]["content"])
                    print(data["message"]["content"], end="")
        print()

    def check_vpn(self, vpn_path="tailscale-ipn.exe"):
        print("==================== Checking VPN connection")
        for process in psutil.process_iter(["name"]):
            try:
                if process.info["name"] == vpn_path:
                    print("Client side VPN running.")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        print("Client side VPN is not running.")
        return False

    def check_model(self):
        print("==================== Model Testing")
        payload = {
            "model": self.selected_model,
            "messages": [{"role": "user", "content": "You are a large language model. The next line will be a user starting a conversation with you, maybe asking a question, etc."}],
            "stream": True,
            "options": {"num_predict": -1},
            "keep_alive": 3600
        }
        try:
            r = requests.post(f"{self.url}/api/chat", json=payload, stream=True, timeout=10)
            if r.ok:
                print("Model receives requests correctly.")
            else:
                print("Model is not receiving requests correctly.")
            return r.ok
        except Exception as e:
            print(f"Model test failed: {e}")
            return False

    def pull_model(self):
        print("==================== Model Loading")
        payload = {"model": self.selected_model}
        with requests.post(f"{self.url}/api/pull", json=payload, timeout=1000, stream=True) as response:
            total = 0
            completed = 0
            for line in response.iter_lines(decode_unicode=True):
                line_dict = json.loads(line)
                if "total" in line_dict and line_dict["total"] != total:
                    total = line_dict["total"]
                if "completed" in line_dict:
                    completed = line_dict["completed"]
                if total:
                    print(f"Loading model: {completed}/{total}, {round(completed / total * 100)}%")
                if line_dict.get("status") == "success":
                    print("Model loaded successfully.")
