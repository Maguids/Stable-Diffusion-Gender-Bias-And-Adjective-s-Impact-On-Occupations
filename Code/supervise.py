import time, requests

WEBUI = "http://127.0.0.1:7860"

while True:
    p = requests.get(f"{WEBUI}/sdapi/v1/progress?skip_current_image=true", timeout=5).json()
    st = p.get("state", {}) or {}

    print(
        f"job={st.get('job_no')}/{st.get('job_count')}  "
        f"step={st.get('sampling_step')}/{st.get('sampling_steps')}  "
        f"progress={p.get('progress'):.4f}  eta={p.get('eta_relative')}"
    )
    time.sleep(2)