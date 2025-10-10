from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.router import Router
from src.Client_Host_Link.router_w_function import RouterF
from src.HostSide.llm_model import Model

app = ClientApp()
router = RouterF("http://100.68.67.70:11434", "Client_Host_Link/function_tools.json")
model_object_dict, model_tag_list = Model.load_verified_models()
app.set_router(router)
app.load_potential_models(model_object_dict, model_tag_list)
router.set_client_app(app)
app.mainloop()
