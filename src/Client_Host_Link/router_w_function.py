from src.Client_Host_Link.router import Router
import base64
import json
import requests

class RouterF(Router):
    def __init__(self, url="", use_tools = True):
        super().__init__(url)
        self.usetools = True

    def send_request_to_model(self, request, img):
        if self.usetools:
            self.send_request_to_model_with_tools(request, img)
        else:
            super().send_request_to_model(request, img)

    def send_request_to_model_with_tools(self, request, img):
        self.send_first_req(request, img)

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
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the weather for a location at a specific time.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City or place name, e.g., 'Toronto, Canada'."
                                },
                                "time": {
                                    "type": "string",
                                    "description": "Time for which to get the weather, e.g., 'now', 'tomorrow', or '2025-10-05 09:00'."
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }

            ]
        }
        self.message_history.append({"role": "assistant", "content": ""})
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        print(json.loads(r.text)["message"])
        calls = []
        if "tool_calls" in json.loads(r.text)["message"]:
            print("Tool called")
            print(json.loads(r.text)["message"]["tool_calls"])
            for call in json.loads(r.text)["message"]["tool_calls"]:
                print(f"Function: {call["function"]["name"]}")
                print(f"Kwargs: {call["function"]["arguments"]}")
                call_object = FunctionCall(call["function"]["name"], call["function"]["arguments"])
                calls.append(call_object)
                call_object.run()

        if calls != []:
            self.send_second_req(request, img, calls)
        else:
            self.client_app.append_and_show_text(json.loads(r.text)["message"]["content"])


    def send_second_req(self, request, img, calls):
        self.message_history.append({"role": "tool", "tool_name": "get_weather", "content": "Toronto is 20C today."})
        payload = {
            "model": self.selected_model,
            "messages": self.message_history,
            "stream": False,
            "options": {
                "num_predict": -1
            },
            "keep_alive": 3600,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the weather for a location at a specific time.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City or place name, e.g., 'Toronto, Canada'."
                                },
                                "time": {
                                    "type": "string",
                                    "description": "Time for which to get the weather, e.g., 'now', 'tomorrow', or '2025-10-05 09:00'."
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }

            ]
        }
        self.message_history.append({"role": "assistant", "content": ""})
        r = requests.post(f"{self.url}/api/chat", json=payload, stream=True)
        print(json.loads(r.text)["message"]["content"])
        self.client_app.append_and_show_text(json.loads(r.text)["message"]["content"])

from typing import Callable, Any, Dict

def get_weather(location: str, time: str):
    print("Toronto is 20C today.")
    return ("Toronto is 20C today.")

class FunctionCall:


    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.function_map = {"get_weather": get_weather}
        self.function = self.function_map[name]
        self.kwargs = arguments

    def run(self):
        self.function(**self.kwargs)
