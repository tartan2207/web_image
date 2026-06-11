import json
from http.server import BaseHTTPRequestHandler

from backend.utils.encoders import AppJSONEncoder


class BaseHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(json.dumps(data, cls=AppJSONEncoder).encode('utf-8'))

    def _send_error(self, status_code: int, message: str):
        self._send_json(status_code, {"error": message})


