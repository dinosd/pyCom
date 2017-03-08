import arduino


estado = 0
estado2 = 0
cont = 0
A = 10
B = 11
C = 12
D = 13
E = 14
def setup():
    arduino.pinMode(15, "ANALOG_INPUT")  #PIN P13,  there is no mode analog input in arduino but pycom need it
    arduino.pinMode(8, "INPUT")          # modes are "INPUT","OUTPUT","INPUT_PULLUP","INPUT_PULLDOWN","ANALOG_INPUT"
    arduino.pinMode(7, "INPUT")     
    arduino.pinMode(A, "OUTPUT")     
    arduino.pinMode(B, "OUTPUT")     
    arduino.pinMode(C, "OUTPUT")     
    arduino.pinMode(D, "OUTPUT")     
    arduino.pinMode(E, "OUTPUT")     
    
    
def loop():
    global estado, estado2, cont
    
    value = arduino.analogRead(13)
    millivolts = 1100 * value / 1.1      #max volts for analog in is 1.1V
    db = millivolts / 10
    print(db, "DB")
    estado2 = arduino.digitalRead(8)
    if estado2:   #this means high  or you can write if estado2==1
        estado = arduino.digitalRead(7)
        if estado:
            arduino.delay(500)
        cont += 1
    if cont==1:
        arduino.digitalWrite(A, 1)
        arduino.digitalWrite(B, 1)
        arduino.digitalWrite(C, 1)
        arduino.digitalWrite(D, 1)
        arduino.digitalWrite(E, 1)
        
        
