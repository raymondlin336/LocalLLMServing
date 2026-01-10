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

def web_search(search_terms: str):
    API = "51b5d3964006010f3b3ff4c817022ab4ecee485a6ee65c5a0d6a2e8e7d20818c"
    url = "https://serpapi.com/search"
    parameters = {
        "q": search_terms,
        "engine": "google",
        "api_key": API
    }
    data = requests.get(url, params=parameters).json()
    returned_text = []
    if "answer_box" in data:
        returned_text.append(data["answer_box"])
    if "organic_results" in data:
        returned_text.append(data["organic_results"])
    if "knowledge_graph" in data:
        returned_text.append(data["knowledge_graph"])
    if returned_text == []:
        returned_text.append("No relevant data retrieved.")
    return returned_text

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
