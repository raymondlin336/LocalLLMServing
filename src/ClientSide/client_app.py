import sys
import tkinter as tk
from tkinter import ttk
import socket
import psutil
import requests
import json
from src.Client_Host_Link.send_and_receive import SendAndReceive

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Local Helper")
        self.geometry("1300x900")
        self.minsize(420, 120)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        self.send_and_receive = SendAndReceive()

        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)

        # ---------- Rows ----------
        row0 = ttk.Frame(self)  # Connection row
        row0.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        for c in range(4):
            row0.columnconfigure(c, weight=(1 if c == 0 else 0))

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
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(50, 10))


        ttk.Label(row0, text="Host:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.ip_dropdown = ttk.Combobox(
            row0,
            values=self._detect_local_ips(),
            state="readonly",
            width=24,
        )
        # default to loopback; you can override below in launch_app.py too
        if "127.0.0.1" in self.ip_dropdown["values"]:
            self.ip_dropdown.set("127.0.0.1")
        elif self.ip_dropdown["values"]:
            self.ip_dropdown.current(0)
        self.ip_dropdown.grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.ip_dropdown.bind("<<ComboboxSelected>>", self.apply_host)

        ttk.Label(row0, text="Port:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.port_entry = ttk.Entry(row0, width=8)
        self.port_entry.insert(0, "11434")
        self.port_entry.grid(row=0, column=3, sticky="w")
        # Button to apply / (re)bind URL
        self.bind_btn = ttk.Button(row0, text="Set Host", command=self.apply_host)
        self.bind_btn.grid(row=0, column=4, sticky="w", padx=(10, 0))


        self.model_dropdown = ttk.Combobox(
            row1,
            values=["llama3.2-vision:11b", "deepseek-r1:7b", "deepseek-r1:14b"],
            state="readonly"
        )
        self.model_dropdown.grid(row=1, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.set_model)

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

        # Set initial URL based on defaults in the widgets
        self.apply_host()

        self.after(100, lambda: (self.search_bar.focus_set(), self.search_bar.icursor("end")))
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def _detect_local_ips(self):
        ips = set()
        ips.add("127.0.0.1")
        try:
            # psutil for interface addresses
            for ifname, addrs in psutil.net_if_addrs().items():
                for a in addrs:
                    if getattr(a, "family", None) == getattr(socket, "AF_INET", object()):
                        ip = a.address
                        # Basic filtering; keep all private/VPN addresses as options
                        if ip:
                            ips.add(ip)
        except Exception:
            pass
        # Also include hostname resolution if available
        try:
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
                ips.add(ip)
        except Exception:
            pass
        # Stable ordering: loopback first, then sorted
        ips = list(ips)
        ips_no_loop = [i for i in ips if i != "127.0.0.1"]
        return ["127.0.0.1"] + sorted(ips_no_loop)

    # ---------- NEW: apply selected host/port to SendAndReceive ----------
    def apply_host(self, event=None):
        host = self.ip_dropdown.get().strip() or "127.0.0.1"
        port = (self.port_entry.get().strip() or "11434")
        # Basic port validation
        if not port.isdigit():
            self.status.config(text=f"Invalid port: {port}")
            return
        self.send_and_receive.set_url(host, int(port))
        self.status.config(text=f"Server set to http://{host}:{port}")

    def set_model(self, event=None):
        self.send_and_receive.set_model(self.model_dropdown.get())

    def set_send_and_receive(self, sar: SendAndReceive):
        self.send_and_receive = sar
        # Re-apply the current host selectors to ensure URL is synced
        self.apply_host()

    def send_request(self, event=None):
        text = self.get_text()
        img = self.get_image()

        print(f"==================== QUERY")
        print(f"Text: {text}")
        if img != "":
            print(f"Image: {img}")
        print("==================== RESPONSE")
        self.clear_text()

        self.send_and_receive.send_request_to_model(text, img)

        self.search_bar.delete(0, "end")
        self.img_bar.delete(0, "end")

    def link_to_send_and_receive(self, sar: SendAndReceive):
        self.send_and_receive = sar

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
        payload = {"model": self.send_and_receive.selected_model, "keep_alive": 0}
        try:
            r = requests.post(f"{self.send_and_receive.url}/api/generate", json=payload, timeout=5)
            print("Model unloaded.")
        except Exception as e:
            print(f"Unloading error (ignored): {e}")
        self.destroy()
