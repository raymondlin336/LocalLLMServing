from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.router_w_function import RouterF

app = ClientApp("HostSide/verified_models.json")
app.load_potential_models()
router = RouterF("http://100.68.67.70:11434", "Client_Host_Link/function_tools.json")
router.set_client_app(app)
app.set_router(router)
app.mainloop()
