import socket
from coda_common import io_file_exists
import gc

class simpleHTTPServer:
  
    def __init__(self, mp):
        self.started = False
        self.mount_point = mp
        print("httpd mount point:", self.mount_point)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 80))
        self.callbacks = []
    def get_content_type(self, resource):  
        atok = resource.split(".")
        ext = atok[len(atok)-1].lower()
        if ext=="html": return "text/html"
        if ext=="htm": return "text/html"
        if ext=="png": return "image/PNG"
        if ext=="jpg": return "image/jpg"
        if ext=="jpeg": return "image/jpeg"
        
    def serve_static(self, request):
        resource = self.mount_point + request.RESOURCE 
        response = http_response()
    
        if io_file_exists(resource):
         
            response.contentType=self.get_content_type(resource)
            response.status = "200 OK"
            f = open(resource, 'r')
            response.content = f.read()
            f.close()
                    
        return response
        
    def begin(self):
       self.started = True
       self.socket.listen(0)
    def on(self, resource, fn):
        self.callbacks.append([resource, fn])
    def update(self):
        conn, addr = self.socket.accept()
        request = http_request(conn.recv(1024).decode('ASCII'))
    
        response = self.serve_static(request)
        if response.status != "200 OK":
            for item in self.callbacks:
                if item[0]==request.RESOURCE:
                    response = item[1](self, request)
                    break
        if response.status=="200 OK":
            conn.sendall(response.toString())
            conn.sendall(response.content)
        conn.sendall('\n')
        conn.close()
        gc.collect()

        
class http_response:
    def __init__(self):
        self.status = "404 Not Found"
        self.contentType = "text/html"
        self.content = []
       
      
    def toString(self):
        return "HTTP/1.1 " + self.status + "\nConnection: close\nServer: nanoWiPy\nContent-Type: " + self.contentType + "\n" + "Content-Length: " + str(len(self.content)) + "\n\n"
    def getContent(self):
        return self.content
    
    
class http_request:
    def __init__(self, req_str):
        req_str=req_str.replace('\r\n',  '|')
        alines = req_str.split('|')
 
        self.METHOD = ""
        self.RESOURCE = ""
        self.PROTOCOL = ""
        self.REMOTE_ADDR = ""
        self.PARM= ""
        for line in alines:
            if len(line)==0: break

            awords = line.split()
            print("line:", line)
            if awords[0]=='GET':
                self.METHOD = 'GET'
                self.RESOURCE = awords[1]
                self.PROTOCOL = awords[2]
                parms = self.RESOURCE.split("?")
                if len(parms) > 1:
                    self.RESOURCE=parms[0]
                    self.PARM = parms[1]
                break
                
            if awords[0]=='Host:':
                self.REMOTE_ADDR = awords[1]
                break

