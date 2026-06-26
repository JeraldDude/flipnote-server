import os
from flask import Blueprint, request, make_response

flipnote_post_bp = Blueprint("flipnote_post", __name__)

SAVE_DIR = "src/database/ppm"


@flipnote_post_bp.route("/ds/v2-xx/post/flipnote.post", methods=["POST"])
def flipnote_post():
    print("\n==============================")
    print("   Flipnote Upload Received")
    print("==============================")

    # ---------------------------------------------------------
    # 1. Print DSi headers
    # ---------------------------------------------------------
    print("\n[DSi Headers]")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

    # ---------------------------------------------------------
    # 2. Print form fields (title, description, etc.)
    # ---------------------------------------------------------
    print("\n[Form Fields]")
    for key in request.form:
        print(f"{key}: {request.form[key]}")

    # ---------------------------------------------------------
    # 3. Extract uploaded .ppm file
    # ---------------------------------------------------------
    ppm_file = request.files.get("file")

    if not ppm_file:
        print("\nERROR: No .ppm file found in upload!")
        return make_response("ERROR", 400)

    filename = ppm_file.filename or "unknown.ppm"
    ppm_data = ppm_file.read()

    print("\n[Flipnote File]")
    print(f"Filename: {filename}")
    print(f"Size: {len(ppm_data)} bytes")

    # ---------------------------------------------------------
    # 4. Parse Flipnote ID + Creator FSID
    # ---------------------------------------------------------
    # Example filename:
    #   4F11EB_18662D11D8A13_001.ppm
    parts = filename.replace(".ppm", "").split("_")

    creator_fsid = parts[0]
    flipnote_id = filename.replace(".ppm", "")

    print(f"Creator FSID: {creator_fsid}")
    print(f"Flipnote ID: {flipnote_id}")

    # ---------------------------------------------------------
    # 5. Save Flipnote to /src/database/ppm/
    # ---------------------------------------------------------
    os.makedirs(SAVE_DIR, exist_ok=True)
    save_path = os.path.join(SAVE_DIR, filename)

    with open(save_path, "wb") as f:
        f.write(ppm_data)

    print(f"Saved to: {save_path}")

    # ---------------------------------------------------------
    # 6. Prepare metadata for movie page
    # ---------------------------------------------------------
    metadata = {
        "id": flipnote_id,
        "filename": filename,
        "creator_fsid": creator_fsid,
        "title": request.form.get("title", "Untitled"),
        "description": request.form.get("description", ""),
        "green_stars": 0,
        "red_stars": 0,
        "comment_count": 0,
        "views": 0,
        "downloads": 0,
        "updated_at": "Now",
        "channel_id": "0",
        "channel_name": "Unassigned",
        "command": "",
        "numeric_id": 0
    }

    # Save metadata JSON
    meta_dir = "src/database/meta"
    os.makedirs(meta_dir, exist_ok=True)

    meta_path = os.path.join(meta_dir, f"{flipnote_id}.json")

    import json
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved: {meta_path}")

    print("\nUpload complete.\n")

    # ---------------------------------------------------------
    # 7. Respond to the DSi
    # ---------------------------------------------------------
    return make_response("OK", 200)
