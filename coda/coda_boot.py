from network import WLAN
import time
from network import Server
import coda_common
import json, gc


coda_common.coda_init()

coda_common.led_r()

ap_list_fname = "/flash/coda/ap/list.json"
AP_LIST = []


def update_ap_list(SSID, PWD):
    item = {}
    item["SSID"] = SSID
    item["PWD"] = PWD
    if not item in AP_LIST:
        AP_LIST.append(item)
        f = open(ap_list_fname, 'w')
        f.write(json.dumps(AP_LIST))
        f.close()
    
        
def find_ap(ssid):
    for item in AP_LIST:
        if item["SSID"]==ssid:
            return item["PWD"]
    return ""

def load_ap_list():
    
    
    
    if coda_common.io_file_exists(ap_list_fname):
        try:
            f = open(ap_list_fname, 'r')
            global AP_LIST
            AP_LIST = json.loads(f.read())
            f.close()
        except:
            pass
    else:
        f = open(ap_list_fname, 'w')
        f.write(json.dumps(AP_LIST))
        f.close()
        


load_ap_list()


SSID = coda_common.CODA_CONFIG["lastssid"]
PWD = coda_common.CODA_CONFIG["lastappwd"]
print("Connecting to ", SSID)
wlan = WLAN(mode=WLAN.STA)


wlan.connect(SSID, auth=(WLAN.WPA2, PWD))
intTimeout = 0
while not wlan.isconnected():
    time.sleep_ms(50)
    intTimeout+=50
    if intTimeout>10000:
        break


if not wlan.isconnected():
    SCAN_LIST = WLAN().scan()
    time.sleep(3)
    gc.collect()
    SCAN_LIST = WLAN().scan()
    
    for item in SCAN_LIST:
        SSID =item[0]
        PWD=find_ap(SSID)
        if PWD > "":
           wlan.connect(SSID, auth=(WLAN.WPA2, PWD))
           intTimeout = 0
           while not wlan.isconnected():
                time.sleep_ms(50)
                intTimeout+=50
                if intTimeout>10000:
                    break
           if wlan.isconnected():
               coda_common.CODA_CONFIG["lastssid"] = SSID
               coda_common.CODA_CONFIG["lastappwd"] = PWD
               coda_common.coda_save_config()
               break
           else:
               pass
        else:
            pass
            

               
               
        
if wlan.isconnected():
    coda_common.led_g()
    update_ap_list(SSID, PWD)
    
    print("ip:", wlan.ifconfig()[0])
    server=Server()
    server.deinit()
    server.init(login=(coda_common.CODA_CONFIG["server_userid"], coda_common.CODA_CONFIG["server_pwd"]), timeout=60)
    
    
    time.sleep(1)
    coda_common.led_off()
    
    AP_LIST = None
    SCAN_LIST = None
    gc.collect()
    
    
    if coda_common.CODA_CONFIG["enable_app_main"] and  coda_common.CODA_CONFIG["app_main"] > "":
        execfile(coda_common.CODA_CONFIG["app_main"])
else:
    AP_LIST = None
    SCAN_LIST = None
    gc.collect()
    print("coda_boot end")
    try:
        WLAN().disconnect()
    except:
        pass
    execfile("/flash/coda/coda_wifi_manager.py")
    


