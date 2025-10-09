from src.ClientSide.client_app import ClientApp
from src.Client_Host_Link.send_and_receive import SendAndReceive

app = ClientApp()
sar = SendAndReceive("http://127.0.0.1:11434")
app.set_send_and_receive(sar)
sar.set_client_app(app)
app.mainloop()
