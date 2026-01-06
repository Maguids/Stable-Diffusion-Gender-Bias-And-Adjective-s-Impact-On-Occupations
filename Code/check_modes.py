import requests

WEBUI = "http://127.0.0.1:7860"

samplers = requests.get(f"{WEBUI}/sdapi/v1/samplers").json()
for s in samplers:
    print("-",s["name"],"-")