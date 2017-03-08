### Arduino combatibility library
from utime import ticks_ms, sleep_ms, sleep_us
import machine
from machine import Pin

myPins = {}    
adc =  machine.ADC()
HIGH = 1
LOW = 2
def delay(milliseconds):
    sleep_ms(milliseconds)

def delayMicroseconds(micros):
    sleep_us(micros)
    
def millis():
    return ticks_ms()
    
def reset():
    machine.reset()
    
def toHexString(num):
    return "{0:#0{1}x}".format(num,4).replace("0x","")
    
class SoftwareSerial:
    def __init__(self):
        self.uart = machine.UART(1, 115200)
    def available(self):
        return self.uart.any()
    def read(self, bytesToRead = 1):
        return self.uart.read(bytesToRead)
    def readall(self):
        return self.uart.readall()
    def write(self, buf):
        self.uart.write(buf)
        


#adc 0: available analog pins    13,14,15,16,17,18,19,20
#       available digital pins   8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23
def pinMode(pinNumber, mode="OUTPUT"):
    pinName = "P" + str(pinNumber)
    pMode = Pin.OUT
    pPull = None
    isAnalog = False
    if mode=="INPUT": 
        pMode = Pin.IN
        pPull = None
    if  mode=="INPUT_PULLUP":
        pMode = Pin.IN
        pPull = Pin.PULL_UP
    if  mode=="INPUT_PULLDOWN":
        pMode = Pin.IN
        pPull = Pin.PULL_DOWN 
    if mode == "OUTPUT":
        pMode = Pin.OUT
        pPull = None
    if mode == "OPEN_DRAIN":
        pMode = Pin.OPEN_DRAIN
        pPull = None
    if mode == "ANALOG_INPUT" or mode=="ANALOG_IN":
        isAnalog = True
    if isAnalog:
        pin = adc.channel(pin=pinName)
        myPins[pinName] = pin
    else:
        pin = Pin(pinName, mode=pMode, pull=pPull)
        myPins[pinName] = pin
  
def analogRead(pinNumber):
    pinName = "P" + str(pinNumber)
    pin = myPins[pinName]
    return pin()
  
def digitalRead(pinNumber):
    pinName = "P" + str(pinNumber)
    pin = myPins[pinName]
    return pin.value()

def digitalWrite(pinNumber, pinValue):
    pinName = "P" + str(pinNumber)
    pin = myPins[pinName]
    value = pin.value()
    pin.value(pinValue)
    return value

def attachInterrupt(pinNumber, eventType, handler):
    pinName = "P" + str(pinNumber)
    pin = myPins[pinName]
    pTrigger = None
    if eventType=="FALLING": pTrigger = Pin.IRQ_FALLING
    if eventType=="RISING": pTrigger = Pin.IRQ_RISING 
    if eventType=="LOW": pTrigger = Pin.IRQ_LOW_LEVEL
    if eventType=="HIGH": pTrigger = Pin.IRQ_HIGH_LEVEL
    if eventType=="CHANGE": pTrigger = Pin.IRQ_FALLING | Pin.IRQ_RISING 
    pin.callback(pTrigger, handler)
    
def detachInterrupt(pinNumber):
    pinName = "P" + str(pinNumber)
    pin = myPins[pinName]
    pin.callback(handler=None)
    
def onTimer_seconds(seconds, handler):
    machine.Timer.Alarm(handler, seconds, periodic=True)

def onTimer_millis(mil, handler):
     machine.Timer.Alarm(handler, ms=mil, periodic=True)
