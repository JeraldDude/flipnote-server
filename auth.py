# Nintendo Authentication Server + Hatena Auth written by JeraldDude
# (c) Nintendo, Hatena

import time
import base64
import hashlib
import urllib.parse
from flask import request, Response

XOR_KEY_AUTH = bytes([0xFF, 0xCC, 0x73, 0xFE, 0xEC, 0xF3, 0x57, 0xA8])

def auth_challenge(fsid: str, challenge: str) -> str:
    fsid_bytes = bytes.fromhex(fsid)[-6:]
    fsid_xored = bytearray(fsid_bytes)

    for i in range(len(fsid_xored)):
        fsid_xored[i] ^= XOR_KEY_AUTH[i % 4]

    challenge_bytes = bytearray(challenge.encode("ascii"))
    for i in range(8):
        challenge_bytes[i] ^= XOR_KEY_AUTH[i]

    token = bytes([
        fsid_xored[0], challenge_bytes[0],
        fsid_xored[1], challenge_bytes[1],
        fsid_xored[2], challenge_bytes[2],
        fsid_xored[3], challenge_bytes[3],
        fsid_xored[4], 0x55, 0x67, fsid_xored[5],
        challenge_bytes[4], challenge_bytes[5],
        challenge_bytes[6], challenge_bytes[7],
    ])

    md5_hash = hashlib.md5(token).digest()
    return bytes(md5_hash[i] for i in range(0, 16, 2)).hex()

def b64_star_encode(s: str) -> str:
    return base64.b64encode(s.encode()).decode().replace("=", "*")

def b64_star_decode(s: str) -> str:
    return base64.b64decode(s.replace("*", "=")).decode()

def parse_b64_star_form(body: str) -> dict:
    raw = urllib.parse.parse_qs(body)
    out = {}
    for k, v in raw.items():
        if v:
            out[k] = b64_star_decode(v[0])
    return out

def build_b64_star_form(d: dict) -> str:
    return "&".join(f"{k}={b64_star_encode(v)}" for k, v in d.items())

sessions = {}      # SID → session data
nas_challenges = {}  # FSID → challenge

def register_nas(app):

    @app.route("/ac", methods=["POST"])
    def nas_ac():
        form = parse_b64_star_form(request.get_data(as_text=True))

        fsid = form.get("userid", "0000000000000000")
        challenge = str(int(time.time()))[-8:]

        nas_challenges[fsid] = challenge

        token = f"NDS/0/{challenge}/no-gsbrcd/{request.remote_addr}|tok/tok"

        resp = {
            "challenge": challenge,
            "locator": "gamespy.com",
            "retry": "0",
            "returncd": "001",
            "token": token,
            "datetime": time.strftime("%Y%m%d%H%M%S", time.gmtime())
        }

        return Response(build_b64_star_form(resp), mimetype="text/plain")

    @app.route("/pr", methods=["POST"])
    def nas_pr():
        resp = {
            "prwords": "0",
            "returncd": "000",
            "datetime": time.strftime("%Y%m%d%H%M%S", time.gmtime())
        }
        return Response(build_b64_star_form(resp), mimetype="text/plain")

    @app.route("/ds/v2-us/auth", methods=["GET"])
    def hatena_auth_get():
        sid = f"SID-{int(time.time())}"
        challenge = str(int(time.time()))[-8:]

        sessions[sid] = {"challenge": challenge}

        resp = Response("", mimetype="text/plain")
        resp.headers["X-DSi-Auth-Challenge"] = challenge
        resp.headers["X-DSi-SID"] = sid
        resp.headers["X-DSi-New-Notices"] = "0"
        resp.headers["X-DSi-Unread-Notices"] = "0"
        return resp

    @app.route("/ds/v2-us/auth", methods=["POST"])
    def hatena_auth_post():
        sid = request.headers.get("X-DSi-SID", "")
        fsid = request.headers.get("X-DSi-ID", "")
        auth_resp = request.headers.get("X-DSi-Auth-Response", "")

        if sid not in sessions:
            return Response("Invalid SID", status=400)

        challenge = sessions[sid]["challenge"]
        expected = auth_challenge(fsid, challenge)

        if auth_resp != expected:
            return Response("Auth failed", status=403)

        resp = Response("", mimetype="text/plain")
        resp.headers["X-DSi-SID"] = sid
        resp.headers["X-DSi-New-Notices"] = "0"
        resp.headers["X-DSi-Unread-Notices"] = "0"
        return resp
