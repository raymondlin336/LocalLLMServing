from src.ClientSide.UI.client_app_info import ClientAppInfo
from src.ClientSide.UI.client_app import ClientApp
from src.ClientSide.Serving.router import Router

app_info = ClientAppInfo("LocalLLM", "ClientSide/Serving/verified_models.json")
app = ClientApp(app_info)
router = Router("http://100.68.67.70:11434", "ClientSide/Serving/function_tools.json")
router.set_client_app(app)
app.set_router(router)
app.mainloop()
