from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.router import Router
from src.Client_Host_Link.router_w_function import RouterF
from src.HostSide.llm_model import Model

app = ClientApp("http://100.68.67.70:11434")
router = RouterF("http://100.68.67.70:11434")
verified_model_list, verified_model_names = Model.load_verified_models()
app.set_send_and_receive(router)
app.load_potential_models(verified_model_names)
router.set_client_app(app)
app.mainloop()
