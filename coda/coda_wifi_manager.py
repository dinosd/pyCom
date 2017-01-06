
#import machine

from network import WLAN
from network import Server
import time
import machine


import json
import gc


import coda_common

from coda_webserver import simpleHTTPServer
from coda_webserver import http_response

reboot = False
     

def hd_root(httpserver, request):
    request.RESOURCE = "/index.html"
    return httpserver.serve_static(request)
 


def hd_scan(server, request):
    response = http_response()
    response.content = json.dumps(nets)
    print(response.content)
    response.contentType ="application/json"
    response.status = "200 OK"
    return response
    
def hd_info(server, request):

    response = http_response()
    response.content = "{chipid:" + coda_common.get_chipid() + "}"
    response.status = "200 OK"
    response.contentType="application/json"
    return response
    
def hd_save(server, request):
    print(request.PARM)
    response = http_response()
    response.content = "{status:'ok'}"
    response.contentType ="application/json"
    response.status = "200 OK"
    
   
    coda_common.CODA_CONFIG["lastssid"] = request.PARM.split("&")[0] 
    coda_common.CODA_CONFIG["lastappwd"] = request.PARM.split("&")[1] 
    coda_common.coda_save_config()
#    
#    global conn_file
#    f = open(conn_file, "w")
#    f.write(ssid)
#    f.write(pwd)
#    f.close()
    global reboot
    reboot = True
    return response

def setup_ap():
    WLAN().init(mode=WLAN.AP, ssid=coda_common.CODA_CONFIG["wifi_manager_ssid"], auth=(WLAN.WPA2,coda_common.CODA_CONFIG["wifi_manager_pwd"],), channel=7, antenna=WLAN.INT_ANT)
    Server().deinit()
    Server().init(login=(coda_common.CODA_CONFIG["server_userid"], coda_common.CODA_CONFIG["server_pwd"]), timeout=60)
   


#begin code

server = Server()
gc.enable()

time.sleep(1)
wlan = WLAN()
try:
    wlan.disconnect()
except:
    pass
    
wlan.init(mode=WLAN.STA)

time.sleep(1)

nets = []
netlist = []
retries = 0
coda_common.led_off()

while True:
    retries+=1
    if retries>10:
        print("SCAN Error. Reboot.")
        machine.reset()
        
        
    coda_common.led_b()
    netlist = WLAN().scan()
    coda_common.led_off()
    
    if netlist and retries >= 3:
        break
    time.sleep(1)
    gc.collect()
        
for item in netlist:
    if item:
        ap = [item.ssid]
        if not ap in nets:
            nets.append(ap)
        print(item.ssid)


setup_ap()
#
##
webserver = simpleHTTPServer("/flash/httpd")
webserver.on("/", hd_root)
webserver.on("/info.svc", hd_info)
webserver.on("/ap.svc", hd_scan)
webserver.on("/save.svc", hd_save)
print('mem free:', gc.mem_free())

coda_common.led_b()
webserver.begin()
intTime = time.time() 
while True:
    
    webserver.update()
    if not reboot:
       reboot = time.time() - intTime > coda_common.CODA_CONFIG["wifi_manager_timeout"] * 10
    if reboot:
        coda_common.led_r()
        print("rebooting after 3 seconds")
        gc.collect()
        time.sleep(3)
        coda_common.led_off()
        machine.reset()
    pass


#print("end")
