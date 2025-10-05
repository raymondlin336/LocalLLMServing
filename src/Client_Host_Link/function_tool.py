from typing import Callable, Any, Dict

def get_weather(location: str, time: str):
    return (f"{location} is 20C today.")

class FunctionTool:
    function_map = {"get_weather": get_weather}
    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.function = self.function_map[name]
        self.kwargs = arguments

    def run(self):
        return self.function(**self.kwargs)
