"""
CoolCallPro Local Development Server
Serves the website at http://localhost:8080
"""
import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIRECTORY)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Only log errors, not every request
        if args and isinstance(args[0], str) and args[0].startswith('4') or args[0].startswith('5'):
            super().log_message(format, *args)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), QuietHandler) as httpd:
    print(f"CoolCallPro server running at http://localhost:{PORT}")
    print(f"Serving files from: {DIRECTORY}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
