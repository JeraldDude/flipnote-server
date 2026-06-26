# Flipnote Hatena - flipnote.post endpoint written by JeraldDude
# --------------------------------------------------------------
# seen at /ds/v2-us/post/flipnote.post meaning an endpoint where ppm files are carried and posted to the server
# -------------------------------------------------------------------------------------------------------------
def register_flipnote_post(app):
    @app.route("/ds/v2-xx/post/flipnote.post", methods=["POST"])
    def flipnote_post():
        # DSi console ID from header
        dsi_id = request.headers.get("X-DSi-ID", "UNKNOWN-DSI")

        # Flipnote filename (DSi usually sends it as form-data)
        flipname = (
            request.form.get("flipnote_filename")
            or request.args.get("flipnote_filename")
            or "unknown.ppm"
        )

        # Build DS-era plain text response
        line_user = f"User: {dsi_id} has sent a flipnote named {flipname}"
        line_save = f"Saved at: /ppm/{dsi_id}/{flipname}"

        response_text = line_user + "\n" + line_save + "\n"

        return Response(response_text, mimetype="text/plain")
