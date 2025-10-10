import json
import requests

class Model:
    def __init__(self, model_tag, use_images=False, use_functions=False):
        self.model_tag = model_tag
        self.use_images = use_images
        self.use_functions = use_functions

    @staticmethod
    def load_verified_models(json_path="HostSide/verified_models.json"):
        models_json = json.load(open(json_path))
        model_objects = {}
        model_tags = []
        for m in models_json:
            model_objects[m["Model Tag"]] = Model(m["Model Tag"], m["Image Compatibility"], m["Function Compatibility"])
            model_tags.append(m["Model Tag"])
        return model_objects, model_tags

    def get_tag(self):
        return self.model_tag

    def get_use_image(self):
        return self.use_images

    def get_use_function(self):
        return self.use_functions
