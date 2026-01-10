import json
from src.ClientSide.Serving.model_info import ModelInfo


class ClientAppInfo():
    def __init__(self, window_title, models_json_path):
        # UI Info
        self.window_title = window_title
        # Backend Info
        self.selected_model = ModelInfo("")
        self.model_objects_dict = dict()
        self.models_dropdown_options = []
        self.models_json_path = models_json_path
        self.load_potential_models()

    def load_potential_models(self):
        models_json = json.load(open(self.models_json_path))
        for m in models_json:
            self.model_objects_dict[m["Model Tag"]] = ModelInfo(m["Model Tag"], m["Image Compatibility"],
                                                      m["Function Compatibility"])
            self.models_dropdown_options.append(m["Model Tag"])

    def get_model_options(self):
        return self.models_dropdown_options
