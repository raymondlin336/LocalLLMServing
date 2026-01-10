# LocalLLMServing v0.1

This project aims to create a simple and user friendly program that pools computing resources of you and your friends' PCs to host LLMs. This enables you to send queries to LLMs from your laptop / phone on a different network to your PC.

## Features

- Launch LLMs and send queries from laptop client to a PC
- Basic UI to choose a model (qwen3:14b) to send and receive requests
- Implemented conversational context so the model remembers what you just said
- Implemented function calling features such as web searches and live weather data

## Set up

### Windows 11

Host:
- Download Tailscale VPN https://tailscale.com/
- Sign up / log in
- Download Ollama https://ollama.com/download/windows
- Download start-ollama.bat. (src/HostSide/start-ollama.bat) Modify the file to match the file path to Ollama to the path in your host machine. Modify the port if the current port is occupied.
- Run start-ollama.bat on the host side

Client:
- Download Tailscale VPN https://tailscale.com/
- Sign up / log in

Launch program:
- Configure the VPNs and connect the two devices
- Run ui_test.py on the client side

## Latest Additions

- Added web searching with a free API and function calling

## Future Steps 

- Improveing the UI
- Implement the launch of the VPN app and automatically check for connection to host
- Improve the current code structure to better enable future development
- Implement load balancing among multiple clients and multiple hosts
- Test and add more models
