import requests

WEBUI="http://127.0.0.1:7860"

payload = {
  "prompt": "test",
  "steps": 10,
  "width": 512,
  "height": 512,
  "batch_size": 1,
  "n_iter": 1,
  "seed": 1,
  "sampler_name": "Euler a",
  "scheduler": "Automatic",
  "save_images": True,
  "send_images": False
}

r = requests.post(f"{WEBUI}/sdapi/v1/txt2img", json=payload, timeout=3600)
r.raise_for_status()
print("ok")