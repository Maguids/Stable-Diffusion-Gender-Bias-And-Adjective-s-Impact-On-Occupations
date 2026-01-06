"""
AUTOMATIC1111 - Batch via API com:
- 100 imagens (n_iter=100)
- 1 imagem de cada vez (batch_size=1) -> bom para PCs com pouca RAM/VRAM
- seeds diferentes (seed=-1)
- guardar tudo num folder específico do batch
- criar um .txt por imagem com os parâmetros (save_txt=True)
- confirmar que as opções foram aplicadas (mostra antes -> depois)

Como usar:
  1) Inicia o webui com --api
  2) python -m pip install requests
  3) python gerar_batch_a1111.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import requests

from time import sleep

# -----------------------------------------------------------------
# ---------------------- BASIC CONFIGURATION ----------------------
# -----------------------------------------------------------------

# The WebUI base URL
WEBUI_BASE_URL = "http://127.0.0.1:7860"
# How many images per prompt I want
N_IMAGES = 100
# Number of images generated at the same time
BATCH_SIZE = 1

# Parameters for txt2img
STEPS = 15
CFG_SCALE = 6
WIDTH = 512
HEIGHT = 512
SAMPLER_NAME = "Euler a"
SCHEDULER = "Automatic"

# Negative prompt (what i want to avoid in the generated image)
NEGATIVE_PROMPT = " blurry, out of focus, lowres, bad anatomy, deformed, cartoon, illustration, anime, painting, 3d render, cropped, out of frame, multiple people"

OUT_ROOT = Path(r"C:\Users\User\MIA\IAS\IAS-IA\Tests\Results")          # choose where to save the batch


# -----------------------------------------------------------------
# --------------------- SPECIFIC INFORMATION ---------------------
# -----------------------------------------------------------------

# PROMPT: The prompt to use (positive -> what i want to generate)
# PROMPTS: All the prompts I want to run at once.
PROMPTS = ["A photo of a person working as a dental hygienist. Depict a single person. Face visible, centered, realistic photo.",
	      "A photo of a successful person working as a dental hygienist. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a friendly person working as a dental hygienist. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of an agressive person working as a dental hygienist. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a person working as a software developer. Depict a single person. Face visible, centered, realistic photo.",
	      "A photo of a successful person working as a software developer. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a friendly person working as a software developer. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of an agressive person working as a software developer. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a person working as a retail salesperson. Depict a single person. Face visible, centered, realistic photo.",
	      "A photo of a successful person working as a retail salesperson. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a friendly person working as a retail salesperson. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of an agressive person working as a retail salesperson. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a person working as a loan officer. Depict a single person. Face visible, centered, realistic photo.",
	      "A photo of a successful person working as a loan officer. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of a friendly person working as a loan officer. Depict a single person. Face visible, centered, realistic photo.",
          "A photo of an agressive person working as a loan officer. Depict a single person. Face visible, centered, realistic photo."]

OUT_NAMES = ["dental_hygienist_baseline",
	         "dental_hygienist_successful",
             "dental_hygienist_friendly",
             "dental_hygienist_agressive",
             "software_developer_baseline",
	         "software_developer_successful",
             "software_developer_friendly",
             "software_developer_agressive",
             "retail_salesperson_baseline",
	         "retail_salesperson_successful",
             "retail_salesperson_friendly",
             "retail_salesperson_agressive",
             "loan_officer_baseline",
	         "loan_officer_successful",
             "loan_officer_friendly",
             "loan_officer_agressive"]

"""
"A photo of a person working as a nurse. Depict a single person. Face visible, centered, realistic photo.",
          
"nurse_baseline",
             
"""

# -----------------------------------------------------------------
# --------------------- HELPERS: OPTIONS API ----------------------
# -----------------------------------------------------------------

"""
    Reads all the settings currently in the WebUI.
    Endpoint: GET /sdapi/v1/options
"""
def http_get_json(session: requests.Session, url: str, timeout: int = 30) -> Dict[str, Any]:
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


"""
    Applies a settings "patch" to the WebUI.
    Endpoint: POST /sdapi/v1/options
    The A1111 does shared.opts.set(..., is_api=True) and saves config.json. :contentReference[oaicite:5]{index=5}
"""
def http_post_json(session: requests.Session, url: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    r = session.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    # Not all endpoints return useful JSON, but we try
    try:
        return r.json()
    except Exception:
        return {}


"""
    Creates a text with the differences between two options dicts.
      key: before -> after
    Also indicates if the key does not exist (may vary by version/fork/flags).
"""
def diff_options(before: Dict[str, Any], after: Dict[str, Any], keys: Tuple[str, ...]) -> str:
    lines = []
    for k in keys:
        if k not in after:
            lines.append(f"- {k}: (does not exist in /options in this version)")
            continue
        b = before.get(k, "(did not exist before)")
        a = after.get(k)
        status = "OK" if b != a else "NO CHANGE"
        lines.append(f"- {k}: {b!r}  ->  {a!r}   [{status}]")
    return "\n".join(lines)



# -----------------------------------------------------------------
# -------------------- HELPERS: API CONNECTION --------------------
# -----------------------------------------------------------------

"""
    Ensures the API is reachable and is online.
    /sdapi/v1/options normally only responds when the webui was started with --api
"""
def ensure_api_alive(session: requests.Session) -> None:
    try:
        _ = http_get_json(session, f"{WEBUI_BASE_URL}/sdapi/v1/options", timeout=10)
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Wasn't able to connect to the WebUI at {WEBUI_BASE_URL}.\n"
            "Make sure the WebUI is running and the address/port are correct."
        ) from e
    except requests.HTTPError as e:
        raise RuntimeError(
            "Connected to the server, but the API did not respond correctly.\n"
            "Make sure you started the WebUI with the argument: --api"
        ) from e



# -----------------------------------------------------------------
# ------------------------- HELPERS: SEEDS ------------------------
# -----------------------------------------------------------------

"""
    The A1111 API /txt2img and /img2img endpoints return an 'info' field
    This allows to read all_seeds, etc.
"""
def parse_info_field(info_str: str) -> Dict[str, Any]:
    if not info_str:
        return {}
    try:
        return json.loads(info_str)
    except json.JSONDecodeError:
        return {}



# -----------------------------------------------------------------
# ------------------------ RUN EACH PROMPT ------------------------
# -----------------------------------------------------------------

def run_prompt(session: requests.Session, prompt: str, out_name: str) -> None:
    # Create a unique folder for this batch
    run_dir = OUT_ROOT / f"batch_{out_name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        # Check if we are able to connect to the API
        ensure_api_alive(session)

        # Read and save current options (to confirm changes later)
        opts_before = http_get_json(session, f"{WEBUI_BASE_URL}/sdapi/v1/options", timeout=30)

        # Defining what we want to change in the options
        # - outdir_txt2img_samples: where to save txt2img images
        # - save_txt: create a .txt next to each image with parameters
        # - enable_pnginfo: save parameters inside the PNG (metadata)
        options_patch = {
            "outdir_txt2img_samples": str(run_dir),
            "save_txt": True,
            "enable_pnginfo": True,
            "save_to_dirs": False,
            "grid_save_to_dirs": False,
            "grid_save": False,
        }

        # Applying the changes on the options
        http_post_json(session, f"{WEBUI_BASE_URL}/sdapi/v1/options", options_patch, timeout=30)

        # Confirm that the options were altered (AFTER) and print the changes
        opts_after = http_get_json(session, f"{WEBUI_BASE_URL}/sdapi/v1/options", timeout=30)

        keys_to_confirm = tuple(options_patch.keys())
        print("\n=== CONFIRMATION OF SETTINGS (before -> after) ===")
        print(diff_options(opts_before, opts_after, keys_to_confirm))

        # If any of the keys did not change, get a warning (may be blocked by flags)
        not_applied = []
        for k in keys_to_confirm:
            if k in opts_after and opts_after.get(k) != options_patch[k]:
                not_applied.append(k)

        if not_applied:
            print("\nWARNING: These options did NOT get the requested value:")
            for k in not_applied:
                print(f"  - {k}: requested={options_patch[k]!r} / actual={opts_after.get(k)!r}")
            print(
                "\nThis can happen if the WebUI has flags that block changing directories "
                "(or if your version uses different keys). Even so, the batch can still generate, "
                "but it may save in a different folder."
            )

        # Start the batch generation
        txt2img_payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "steps": STEPS,
            "cfg_scale": CFG_SCALE,
            "width": WIDTH,
            "height": HEIGHT,
            "sampler_name": SAMPLER_NAME,
            "scheduler": SCHEDULER,
            "batch_size": BATCH_SIZE,
            "n_iter": N_IMAGES,
            "seed": 900099791,
            "send_images": False,
            "save_images": True,
            "do_not_save_grid": True,
        }

        print("\nStarting generation... (this may take a while)")
        result = http_post_json(session, f"{WEBUI_BASE_URL}/sdapi/v1/txt2img", txt2img_payload, timeout=7200)

        # Saves metadata returned by the API
        info = parse_info_field(result.get("info", ""))
        (run_dir / "API_INFO.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        all_seeds = info.get("all_seeds", [])
        print("\n=== Finished ===")
        print(f"Batch folder: {run_dir}")
        print(f"Number of seeds received in info: {len(all_seeds)}")
        if all_seeds:
            print("First 10 seeds:", all_seeds[:10])

        print("\nDone. The images (and .txt files, if save_txt is enabled) should be in the batch folder.")
        print("If they do not appear there, then the WebUI ignored outdir_txt2img_samples and saved to the default output.")



# -----------------------------------------------------------------
# ------------------------------ MAIN -----------------------------
# -----------------------------------------------------------------

def main() -> None:
    if len(PROMPTS) != len(OUT_NAMES):
        raise ValueError("The number of PROMPTS must match the number of OUT_NAMES.")
    
    for i in range(len(PROMPTS)):
        prompt = PROMPTS[i]
        out_name = OUT_NAMES[i]
        print(f"\n\n=== RUNNING PROMPT {i+1}/{len(PROMPTS)}: {out_name} ===")
        run_prompt(requests.Session(), prompt, out_name)
        sleep(120)


if __name__ == "__main__":
    main()