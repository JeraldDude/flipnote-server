from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/ds/v2-xx/post/flipnote.post", methods=["POST"])
def flipnote_post():
    # Get DSi ID from header
    dsi_id = request.headers.get("X-DSi-ID", "UNKNOWN-DSI")

    # Get flipnote filename from form or query (adjust to your protocol)
    flipnote_filename = request.form.get("flipnote_filename") or request.args.get("flipnote_filename")
    if not flipnote_filename:
        flipnote_filename = "unknown_flipnote.ppm"

    # Build response text
    user_line = f"User: {dsi_id} has sent a flipnote named {flipnote_filename}"
    saved_line = f"Saved at: /ppm/{dsi_id}/{flipnote_filename}"

    body = user_line + "\n" + saved_line + "\n"

    # Return plain text response (DS/Wii-era style)
    return Response(body, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
