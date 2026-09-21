from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Type', 'text/html; charset=UTF-8')
        super().end_headers()

HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()