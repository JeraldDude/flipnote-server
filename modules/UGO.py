import json
import base64
import os


def b64_label(text: str) -> str:
    """Encode label as Base64 UTF-16LE (no null terminator)."""
    return base64.b64encode(text.encode("utf-16le")).decode("ascii")


def build_toc(json_obj: dict) -> str:
    """
    Build the Table of Contents text section.
    Each entry is a line with tab-separated fields.
    """
    lines = []

    # Layout (optional)
    if "layout" in json_obj:
        layout_values = "\t".join(str(v) for v in json_obj["layout"])
        lines.append("0\t" + layout_values)

    # Items
    for item in json_obj["items"]:
        if item["type"] == "button":
            url = item["url"]
            icon = item["icon"]
            label = b64_label(item["label"])
            trait = "0"  # always 0 for normal buttons

            # Format EXACTLY like pbsds:
            # 4 <url> <icon> <labelBase64> 0
            line = f"4\t{url}\t{icon}\t{label}\t{trait}"
            lines.append(line)

        else:
            raise ValueError(f"Unsupported item type: {item['type']}")

    return "\n".join(lines)


def pack_ugo(json_obj: dict) -> bytes:
    """
    Build a complete UGO file matching pbsds's format exactly.
    """
    toc = build_toc(json_obj).encode("utf-8")
    toc_len = len(toc)

    # Pad TOC to 4-byte alignment
    if toc_len % 4 != 0:
        toc += b"\x00" * (4 - (toc_len % 4))

    # Header:
    # "UGAR"
    # uint32 sections (always 1 for TOC-only)
    # uint32 toc_length
    header = b"UGAR"
    header += (1).to_bytes(4, "big")       # Sections = 1
    header += toc_len.to_bytes(4, "big")   # TOC length

    return header + toc


def convert_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ugo = pack_ugo(data)

    with open(output_path, "wb") as f:
        f.write(ugo)

    print(f"[UGO] Converted {input_path} → {output_path} ({len(data['items'])} entries)")

# Path Folder

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    assets_ds = os.path.join(base, "assets", "ds")

    region_folder = None
    for name in os.listdir(assets_ds):
        if name.startswith("v2-"):
            region_folder = os.path.join(assets_ds, name)
            break

    if region_folder is None:
        print("[UGO] ERROR: No /src/assets/ds/v2-xx/ folder found.")
        exit(1)

    json_path = os.path.join(region_folder, "index.json")
    ugo_path = os.path.join(region_folder, "index.ugo")

    if not os.path.isfile(json_path):
        print(f"[UGO] ERROR: {json_path} not found.")
        exit(1)

    convert_file(json_path, ugo_path)
