import sys
import tkinter as tk
from tkinter import ttk
import requests
import json
import base64

import psutil
import subprocess
import os

# (Optional) make text crisp on high-DPI Windows displays
if sys.platform.startswith("win"):
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI awareness

class ClientApp(tk.Tk):
    def __init__(self, url):
        # General setup
        super().__init__()
        self.title("Local Helper") # App name
        self.geometry("700x300")
        self.minsize(420, 120)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.message_history = []
        self.selected_model = None
        self.url = url
        self.response_text = ""

        # Title

        # Forming a new row for search bar and buttons
        row0 = ttk.Frame(self)
        row0.grid(row=0, column=0, sticky="ew", padx=10)
        row0.columnconfigure(0, weight=1)

        row1 = ttk.Frame(self)
        row1.grid(row=1, column=0, sticky="ew", padx=10)
        row1.columnconfigure(0, weight=1)

        row2 = ttk.Frame(self)
        row2.grid(row=2, column=0, sticky="ew", padx=10)
        row2.columnconfigure(0, weight=1)

        row3 = ttk.Frame(self)
        row3.grid(row=3, column=0, sticky="ew", padx=10)
        row3.columnconfigure(0, weight=1)

        header = ttk.Label(self, text="Query", font=("Segoe UI", 11, "bold"))
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 10))

        self.model_dropdown = ttk.Combobox(row1, values=["llama3.2-vision:11b", "deepseek-r1:7b", "deepseek-r1:14b"])
        self.model_dropdown.grid(row=1, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.set_model)

        # Sets up
        self.search_bar = ttk.Entry(row2, font=("Segoe UI", 11))
        self.search_bar.grid(row=2, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.search_bar.bind("<Return>", self.send_request)

        self.search_btn = ttk.Button(row2, text="Ask", command=self.send_request)
        self.search_btn.grid(row=2, column=1, sticky="e")

        self.img_bar = ttk.Entry(row3, font=("Segoe UI", 11))
        self.img_bar.grid(row=3, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.img_bar.bind("<Return>", self.send_request)

        # ----- Output / status
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.grid(row=4, column=0, sticky="ew", padx=14, pady=(8, 10))

        # Focus caret into the entry for instant typing
        self.after(100, lambda: (self.search_bar.focus_set(), self.search_bar.icursor("end")))

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def send_request(self, event=None):
        text = self.get_text()
        img = self.get_image()

        # 👉 This is where your program "reads" the input.
        # For now we just print it and show it in the status.
        print(f"==================== QUERY")
        print(f"Text: {text}")
        if img != "":
            print(f"Image: {img}")
        print("==================== RESPONSE")
        self.clear_text()
        response = self.send_request_to_model(self.selected_model, text, img)

        # Clear the box for the next query (optional)
        self.search_bar.delete(0, "end")
        self.img_bar.delete(0, "end")

    def get_text(self) -> str:
        return self.search_bar.get().strip()

    def get_image(self) -> str:
        return self.img_bar.get().strip()

    def append_and_show_text(self, text: str):
        self.response_text += text
        self.status.config(text=self.response_text)

    def clear_text(self):
        self.response_text = ""
        self.status.config(text=self.response_text)

    def set_model(self, event=None):
        self.check_vpn()
        self.selected_model = self.model_dropdown.get()
        self.pull_model()
        self.check_model()

    def check_vpn(self, vpn_path = "tailscale-ipn.exe"):
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
            "messages": {"role": "user", "content": "You are a helpful assistant."},
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600
        }
        r = requests.post(f"{self.url}/api/pull", json=payload, timeout=1000, stream=True)
        if r.ok:
            print("Model receives requests correctly.")
        else:
            print("Model is not receiving requests correctly.")
        return r.ok


    def send_request_to_model(self, model, request, img, event=None):
        url = "http://100.68.67.70:11434/api/chat"
        img_path = img.replace("\\", "/")
        if model == None:
            print("Error: model not selected.")
            return 0
        if img == "":
            self.message_history.append({"role": "user", "content": request})
        else:
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("ascii")
            self.message_history.append({"role": "user", "content": request, "images": [img_b64]})
        payload = {
            "model": model,
            "messages": self.message_history,
            "stream": True,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600
        }

        self.message_history.append({"role": "assistant", "content": ""})
        with requests.post(url, json=payload, stream=True) as response:
            for line in response.iter_lines(decode_unicode=True):
                data = json.loads(line)
                self.message_history[-1]["content"] += data["message"]["content"]
                #print(data)
                if data["message"]["content"] != "" and "<" != data["message"]["content"][0]:
                    self.append_and_show_text(data["message"]["content"])
                    print(data["message"]["content"], end="")

        print()
        #print(self.message_history)

    def pull_model(self):
        print("==================== Model Loading")
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
                    print(f"Loading model: {completed}/{total}, {round(completed / total * 100)}%")
                if line_dict["status"] == "success":
                    print("Model loaded successfully.")

    def on_close(self):
        print("Client app is closed.")
        payload = {"model": self.selected_model, "keep_alive": 0}
        r = requests.post(f"{self.url}/api/generate", json=payload, timeout=1000)
        print("Model unloaded.")
        self.destroy()

def check_available_models(url="http://100.68.67.70:11434/api/tags"):
    with requests.get(url, timeout=1000) as response:
        for line in response.iter_lines(decode_unicode=True):
            for model in json.loads(line)["models"]:
                print(model["name"], model["size"])

def remove_model(model_name, url):
    payload = {"model": model_name}
    r = requests.delete(f"{url}/api/delete", json=payload, timeout=1000)
    print(r.text)

if __name__ == "__main__":
    # remove_model(model, url)
    # check_available_models()
    app = ClientApp("http://100.68.67.70:11434")
    app.mainloop()
