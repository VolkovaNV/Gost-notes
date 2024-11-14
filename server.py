from http.server import HTTPServer, CGIHTTPRequestHandler

server_adress = ("127.0.0.1", 5501)
httpd = HTTPServer(server_adress, CGIHTTPRequestHandler)
httpd.serve_forever()

