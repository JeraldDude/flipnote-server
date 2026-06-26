# Nintendo Connection Test
# (c) Nintendo 2005

from flask import Response, request

CONNTEST_HOST = "conntest.nintendowifi.net"

def register_conntest(app):

    @app.route("/", host=CONNTEST_HOST)
    def conntest_root():
        print(f"[Conntest] {request.host}: {request.path}")

        html = (
            "<html>"
            "<head><title>HTML Page</title></head>"
            "<body bgcolor=\"#FFFFFF\">"
            "This is test.html page"
            "</body></html>"
        )

        resp = Response(html, mimetype="text/html")
        resp.headers["X-Organization"] = "Nintendo"
        return resp
