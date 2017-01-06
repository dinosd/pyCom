import pycom
import json
import gc
import socket

class webreponse:
    def __init__(self):
        self.status = 0
        self.lines = []
    def append(self, data):
        self.lines.append(data)
    def tojson(self):
        if len(self.lines)==0:
            return json.loads("{'dbstatus':'error'}")
        if not self.lines[0]:
            return json.loads("{'dbstatus':'error'}")
        return json.loads(self.lines[0])
        

def webclient(url, data=None, method="GET"):
    pycom.rgbled(0xff0000) 
    if data is not None and method == "GET":
        method = "POST"
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]
    s = socket.socket()
    s.connect(addr)
    if proto == "https:":
        s = ussl.wrap_socket(s)

    s.write(method)
    s.write(b" /")
    s.write(path)
    s.write(b" HTTP/1.0\r\nHost: ")
    s.write(host)
    s.write(b"\r\n")
    s.write(b"User-Agent: pycom;ESP32\r\n")
    if data:
        s.write(b"Content-Length: ")
        s.write(str(len(data)))
        s.write(b"\r\n")
    s.write(b"\r\n")
    if data:
        s.write(data)

    pycom.rgbled(0x00ff00) 
    l = s.readline()
    protover, status, msg = l.split(None, 2)
    status = int(status)
    ret = webreponse()
    ret.status = status
    #ret.append(l)
    while True:
        l = s.readline()
        if not l :
            break
        
        if l.startswith(b"Transfer-Encoding:"):
            if b"chunked" in l:
                raise ValueError("Unsupported " + l)
        elif l.startswith(b"Location:"):
            raise NotImplementedError("Redirects not yet supported")
            
        if ":" in l and "{" in l and "}" in l:
            ret.append(l.decode('ASCII'))
    gc.mem_free()        
    pycom.rgbled(0x000000)    
    return ret

