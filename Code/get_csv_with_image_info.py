from pathlib import Path
import csv
import re

IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"]

"""
    Find an image in the same folder with the same stem as the txt file.
"""
def find_matching_image(txt_path: Path) -> Path | None:
    for ext in IMAGE_EXTS:
        candidate = txt_path.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None

"""
    Regex to find key/value pairs in the metadata line(s).
"""
KV_PATTERN = re.compile(r"([^:]+):\s*([^,]+)(?:,|$)")


"""
    Parses files of the form:
      <prompt line>
      Negative prompt: <...>
      Steps: ..., Sampler: ..., ...
"""
def parse_txt_content(text: str) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out = {}

    if not lines:
        return out

    # Prompt == first non-empty line
    out["prompt"] = lines[0]

    # Next. get the Negative prompt line (if present)
    neg_idx = None
    for i, ln in enumerate(lines[1:], start=1):
        if ln.lower().startswith("negative prompt:"):
            out["negative_prompt"] = ln.split(":", 1)[1].strip()
            neg_idx = i
            break
    if "negative_prompt" not in out:
        out["negative_prompt"] = ""

    # Next is the metadata key/value pairs, which can be in various formats:
    # If format is slightly different, we just parse any later line containing ":".
    meta_lines = []
    if neg_idx is not None and neg_idx + 1 < len(lines):
        meta_lines = lines[neg_idx + 1:]
    else:
        meta_lines = lines[1:]

    # Join meta lines in case it's wrapped across multiple lines
    meta_text = " ".join([ln for ln in meta_lines if ":" in ln])

    for key, val in KV_PATTERN.findall(meta_text):
        key = key.strip()
        val = val.strip()
        # Normalize key names slightly (optional)
        out[key] = val

    return out

"""
    Main function to build the CSV.
"""
def build_csv(main_dir: str, output_csv: str):
    main_path = Path(main_dir)
    rows = []
    all_keys = set(["folder", "base_name", "txt_path", "image_path", "prompt", "negative_prompt"])

    for txt_path in main_path.rglob("*.txt"):
        img_path = find_matching_image(txt_path)

        text = txt_path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_txt_content(text)

        row = {
            "folder": txt_path.parent.name,
            "base_name": txt_path.stem,
            "txt_path": str(txt_path),
            "image_path": str(img_path) if img_path else "",
            **parsed,
        }

        rows.append(row)
        all_keys.update(row.keys())

    # Order columns: stable, with known columns first
    preferred = [
        "folder", "base_name", "image_path", "txt_path",
        "prompt", "negative_prompt",
        "Steps", "Sampler", "Schedule type", "CFG scale", "Seed", "Size",
        "Model hash", "Model", "Version",
    ]
    # Add any extra keys discovered
    extras = [k for k in sorted(all_keys) if k not in preferred]
    fieldnames = [k for k in preferred if k in all_keys] + extras

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_csv}")

if __name__ == "__main__":
    # CHANGE THESE:
    MAIN_FOLDER = r"C:\Users\magda.costa\MIA\IAS\IndividualAssignment\Code\Results_Extra"
    OUTPUT_CSV  = r"C:\Users\magda.costa\MIA\IAS\IndividualAssignment\Code\Results_Extra\image_info.csv"

    build_csv(MAIN_FOLDER, OUTPUT_CSV)
