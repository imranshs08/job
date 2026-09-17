import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Mock data for Kubeshark to intercept
MOCK_DATA = {
    "status": "success",
    "metrics": {
        "cpu_usage": "45%",
        "memory_usage": "1.2GB",
        "active_connections": 154
    },
    "user_session": {
        "user_id": "usr_9824xyz",
        "role": "admin",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('X-App-Version', 'v1.0.0')
        self.end_headers()
        
        # When Kubeshark taps this, you will see this rich JSON payload
        self.wfile.write(json.dumps(MOCK_DATA).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"message": "Payload received!", "bytes": content_length}
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting Python API on port 8080...')
    httpd.serve_forever()
