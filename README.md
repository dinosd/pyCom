# pyCom
pyCom CODA library

1. Supports WIFI Manager like ESP8266. Default AP Name: "your_pycom_device", default PWD: "www.pycom.io". Server() username:"micro" and PWD: "python"
   After initialization it starts as an AP. Then you connect to this AP with your mobile phone and hit http://192.168.4.1. You select an existing AP from the GUI.
   If a connection is done then the library keeps the AP in list. So if you carry your device it will remember the AP password.
   
 2. Supports WEB Server but it needs more development. Library can server html static files.
 
 3. Supports web client.
 


Copy coda and httpd folders to  /flash
