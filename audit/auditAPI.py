from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import os
sys.path.append(os.path.abspath("."))
print(os.path.abspath("."))

import bupt_funcs

def processlogic(source_data):
    # 处理逻辑，最终返回服务端响应值到变量rpdata
    method,para=source_data.split("=")
    if method=="get":
        rpdata=bupt_funcs.getPages(para)
    elif method=="delete":
        rpdata=bupt_funcs.delPages(para)
    elif method=="remain":
        rpdata=bupt_funcs.rmnPages(para)

    return rpdata

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        source_data = self.rfile.read(length).decode('utf-8')
        #读取了post报文到source_data变量
        resposedata = processlogic(source_data)
        respose = resposedata.encode('utf-8')   
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(respose)       
    
server_address = ('', 8000)
httpd = HTTPServer(server_address, RequestHandler)
print('Starting server')
httpd.serve_forever()