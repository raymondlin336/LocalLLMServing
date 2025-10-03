from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.send_and_receive import SendAndReceive

app = ClientApp("http://100.68.67.70:11434")
sar = SendAndReceive("http://100.68.67.70:11434")
app.set_send_and_receive(sar)
sar.set_client_app(app)
app.mainloop()
