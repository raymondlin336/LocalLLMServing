import sys
import tkinter as tk
from tkinter import ttk
import requests
import json
from src.Client_Host_Link.router import Router

class ClientApp(tk.Tk):
    def __init__(self, url):
        # General setup
        super().__init__()
        self.title("Local Helper") # App name
        self.geometry("700x300")
        self.minsize(420, 120)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.router = Router()

        # (Optional) make text crisp on high-DPI Windows displays
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI awareness

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

        self.model_dropdown = ttk.Combobox(row1, values=[])
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

    def load_potential_models(self, model_list: list[str]):
        self.model_dropdown["values"] = model_list

    def set_model(self, event=None):
        self.router.set_model(self.model_dropdown.get())

    def set_router(self, sar: Router):
        self.router = sar

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

        self.router.send_request_to_model(text, img)

        self.search_bar.delete(0, "end")
        self.img_bar.delete(0, "end")

    def link_to_send_and_receive(self, sar: Router):
        self.router = sar

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

    def on_close(self):
        print("Client app is closed.")
        payload = {"model": self.router.selected_model, "keep_alive": 0}
        r = requests.post(f"{self.router.url}/api/generate", json=payload, timeout=1000)
        print("Model unloaded.")
        self.destroy()
