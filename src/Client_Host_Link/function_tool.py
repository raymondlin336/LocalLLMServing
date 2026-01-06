from typing import Any, Dict
import requests


def get_weather(location: str):
    parameters = {'key': 'td5wfyspfmkftx0ls7wsxlugqokof39kpz4ve8y9',
                  'place_id': location}
    url = "https://www.meteosource.com/api/v1/free/point"
    data = requests.get(url, parameters).json()
    return f"Current info: {data['current']} Hourly info: {data['hourly']} Daily info: {data['daily']}"

def get_weather_place_id(location: str):
    parameters = {'key': 'td5wfyspfmkftx0ls7wsxlugqokof39kpz4ve8y9',
                  'text': location}
    url = "https://www.meteosource.com/api/v1/free/find_places"
    data = requests.get(url, parameters).json()
    return data

def web_search():
    # TODO: implement web search algorithm
    return ""

class FunctionTool:
    function_map = {"get_weather": get_weather,
                    "get_weather_place_id": get_weather_place_id,
                    "web_search": web_search}
    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.function = self.function_map[name]
        self.kwargs = arguments
        self.fn_name = name

    def run(self):
        return self.function(**self.kwargs)

    def get_name(self):
        return self.fn_name
