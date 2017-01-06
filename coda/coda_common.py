import uos
from network import WLAN
import json
import gc
import machine
import pycom
CODA_CONFIG = None
CODA_LED_DIM = 30

coda_json_fname = "/flash/coda/coda_config.json"
def io_file_exists(fname):
    try:
        intFileSize = uos.stat(fname)[6]
    except:
        intFileSize = 0
    
    if intFileSize>0:
        return True
        
    return False

def get_chipid():
    intCHIPID = WLAN().mac()[0]
    intCHIPID = intCHIPID << 8 
    intCHIPID += WLAN().mac()[1]
    intCHIPID = intCHIPID << 8 
    intCHIPID += WLAN().mac()[2]
    intCHIPID = intCHIPID << 8 
    intCHIPID += WLAN().mac()[3]
    intCHIPID = intCHIPID << 8 
    intCHIPID += WLAN().mac()[4]
    ret = str(intCHIPID)
    return ret
 
def io_read_all_lines(fname):
    try:
        intFileSize = uos.stat(fname)[6]
    except:
        intFileSize = 0
        return []
        
    print("FileSize: ", intFileSize)    
    if intFileSize > 0:
        f = open(fname)
        lines = f.readlines()
        
        f.close()
        index = 0
        for line in lines:
            line = line.replace('\r\n', '')
            lines[index ] = line
            index += 1
        return lines

def io_get_json(fname):
    try:
        uos.stat(fname)[6]
    except:
        
        return {}
        
    f = open(fname)
    s = f.read()
    f.close()
    gc.collect()
    return json.loads(s)
    


def io_save_json(fname, obj):
    f = open(fname, 'w')
    
    f.write( json.dumps(obj) )
    f.close()
    
def coda_init():
    pycom.heartbeat(False)
    global CODA_CONFIG
    try:
        CODA_CONFIG = io_get_json(coda_json_fname)
        if CODA_CONFIG["wifi_manager_ssid"] == "": CODA_CONFIG["wifi_manager_ssid"] = "your_pycom_device"
        if CODA_CONFIG["wifi_manager_pwd"] == "": CODA_CONFIG["wifi_manager_pwd"] = "www.pycom.io"
        
    except:
        CODA_CONFIG = {}
        CODA_CONFIG["lastssid"] = "NONE"
        CODA_CONFIG["lastappwd"] = "NONE"
        CODA_CONFIG["wifi_manager_ssid"] = "your_pycom_device"
        CODA_CONFIG["wifi_manager_pwd"] = "www.pycom.io"
        CODA_CONFIG["wifi_manager_timeout"] = 240
        CODA_CONFIG["server_userid"] = "micro"
        CODA_CONFIG["server_pwd"] = "python"
        CODA_CONFIG["app_main"] = ""
        CODA_CONFIG["enable_app_main"] = 0
        
    
def coda_save_config():
    io_save_json(coda_json_fname, CODA_CONFIG)

def autostart_true():
    CODA_CONFIG["enable_app_main"] = 1
    coda_save_config()
    autostart_info()
    
def autostart_false():
    CODA_CONFIG["enable_app_main"] = 0
    coda_save_config()
    autostart_info()
    
def autostart_set(fname):
    CODA_CONFIG["app_main"] = fname
    coda_save_config()
    autostart_info()
    
def autostart_info():
    print("auto start app   :",  CODA_CONFIG["app_main"])
    print("auto start enable:",  CODA_CONFIG["enable_app_main"])

def ap_set(ssid, pwd):
    CODA_CONFIG["lastssid"] = ssid
    CODA_CONFIG["lastappwd"] = pwd
    coda_save_config()
    machine.reset()
    
def led_dim(byteDim):
    global CODA_LED_DIM
    CODA_LED_DIM = byteDim
    
def led_off():
    global CODA_LED_DIM
    pycom.rgbled(0x000000)

def led_r():
    global CODA_LED_DIM
    pycom.rgbled(CODA_LED_DIM << 16)
    
def led_g():
    global CODA_LED_DIM
    pycom.rgbled(CODA_LED_DIM << 8)
    
def led_b():
    global CODA_LED_DIM
    pycom.rgbled(CODA_LED_DIM)

def reboot():
    machine.reset()
