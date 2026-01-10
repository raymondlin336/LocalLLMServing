import sys
import tkinter as tk
from tkinter import ttk
from src.ClientSide.Serving.router import Router
from src.ClientSide.Development.log import Log

class ClientApp(tk.Tk):
    def __init__(self, client_app_info):
        # General setup
        super().__init__()
        self.client_app_info = client_app_info
        self.title("Local Helper")
        self.geometry("700x300")
        self.minsize(400, 300)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.router = None
        self.model_object_dict = {}
        self.use_fn_calling = tk.BooleanVar(value=False)

        # Improves text on Windows
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)

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

        row4 = ttk.Frame(self)
        row4.grid(row=3, column=0, sticky="ew", padx=10)
        row4.columnconfigure(0, weight=1)

        header = ttk.Label(self, text="Query", font=("Segoe UI", 11, "bold"))
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 10))

        self.model_dropdown = ttk.Combobox(row1, values=[])
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

        self.fn_calling_checkbox = ttk.Checkbutton(row3, text="Enable function calling",variable=self.use_fn_calling)
        self.fn_calling_checkbox.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=10)

        self.model_output = ttk.Label(self, text="", anchor="w", justify="left", wraplength=700)
        self.model_output.grid(row=4, column=0, sticky="ew", padx=14, pady=(8, 10))
        self.bind("<Configure>", lambda e: self.model_output.configure(wraplength=e.width - 40))

        self.after(100, lambda: (self.search_bar.focus_set(), self.search_bar.icursor("end")))

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Get the list of models from the client app info
        self.model_dropdown["values"] = self.client_app_info.get_model_options()

    def set_model(self, event=None):
        self.router.unload_all_models()
        model_tag = self.model_dropdown.get()
        self.model = self.client_app_info.model_objects_dict[model_tag]
        self.router.set_model(model_tag)
        if self.model.get_use_image():
            self.img_bar.configure(state="normal")
        else:
            self.img_bar.configure(state="disabled")
        if self.model.get_use_function():
            self.use_fn_calling.set(True)
            self.fn_calling_checkbox.configure(state="normal")
        else:
            self.use_fn_calling.set(False)
            self.fn_calling_checkbox.configure(state="disabled")

    def set_router(self, sar: Router):
        self.router = sar

    def send_request(self, event=None):
        text = self.get_text()
        img = self.get_image()

        # 👉 This is where your program "reads" the input.
        # For now we just print it and show it in the status.
        Log.print_title("QUERY")
        print(f"Text: {text}")
        if img != "":
            print(f"Image: {img}")
        Log.print_title("PROCESSING")
        self.clear_text()

        self.router.send_request(text, [])

        self.search_bar.delete(0, "end")
        self.img_bar.delete(0, "end")

    def link_to_send_and_receive(self, sar: Router):
        self.router = sar

    def get_text(self) -> str:
        return self.search_bar.get().strip()

    def get_image(self) -> str:
        return self.img_bar.get().strip()

    def get_function_calling_usage(self) -> bool:
        return self.use_fn_calling.get()

    def append_and_show_text(self, text: str):
        self.response_text += text
        self.model_output.config(text=self.response_text)

    def clear_text(self):
        self.response_text = ""
        self.model_output.config(text=self.response_text)

    def on_close(self):
        Log.print_message("Client app is closed.")
        self.router.unload_all_models()
        Log.print_message("Model unloaded.")
        self.destroy()
