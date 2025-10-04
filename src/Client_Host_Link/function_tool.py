from typing import Callable, Any, Dict

def get_weather(location: str, time: str):
    print("Toronto is 20C today.")
    return ("Toronto is 20C today.")

class FunctionTool:


    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.function_map = {"get_weather": get_weather}
        self.function = self.function_map[name]
        self.kwargs = arguments

    def run(self):
        self.function(**self.kwargs)
