from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.router import Router
from src.Client_Host_Link.router_w_function import RouterF

app = ClientApp("http://100.68.67.70:11434")
sar = RouterF("http://100.68.67.70:11434")
app.set_send_and_receive(sar)
sar.set_client_app(app)
app.mainloop()
