#ADXL362 SPI Library
#written  by Constantinos Dafalias cdafalias@gmail.com
from machine import SPI
from machine import Pin
import time

class ADXL362:
    def _init__(self, cspin):
        self.cspin = Pin(cspin, mode=Pin.OUT)
        self.cspin.value(1)
        self.x = 0
        self.y = 0
        self.z = 0
        self.t = 0
        self.spi = SPI(0, mode=SPI.MASTER, baudrate=1000000, polarity=0, phase=0, firstbit=SPI.MSB)
        time.sleep_ms(1000)
        self.SPIwriteOneRegister(0x1F, 0x52)  #RESET
        time.sleep_ms(10)
        self.DEVICEID = self.SPIreadOneRegister(0x00)
        self.DEVID_MST = self.SPIreadOneRegister(0x01)
        self.PART_ID = self.SPIreadOneRegister(0x02)
        self.REV_ID = self.SPIreadOneRegister(0x03)
        self.STATUS = self.getStatus()
        
    def getStatus(self):
        return self.SPIreadOneRegister(0x0B)
    def beginMeasure(self):
        temp = self.SPIreadOneRegister(0x2D)
        tempwrite = temp | 0x02
        self.SPIwriteOneRegister(0x2D, tempwrite)
        time.sleep_ms(10)
    def readXData(self):
        XDATA = self.SPIreadTwoRegisters(0x0E)
        return XDATA
    def readYData(self):
        YDATA = self.SPIreadTwoRegisters(0x10)
        return YDATA
    def readZData(self):
        ZDATA = self.SPIreadTwoRegisters(0x12)
        return ZDATA
    def readTemp(self):
        TEMP = self.SPIreadTwoRegisters(0x14)
        return TEMP
    def readXYZTData(self):
        ret = {}
        self.select()
        self.spi.write(0x0B)
        self.spi.write(0x0E)
        ret['x'] = self.spi.read(1)
        ret['x'] += self.spi.read(1) << 8
        ret['y'] = self.spi.read(1)
        ret['y'] += self.spi.read(1) << 8
        ret['z'] = self.spi.read(1)
        ret['z'] += self.spi.read(1) << 8
        ret['t'] = self.spi.read(1)
        ret['t'] += self.spi.read(1) << 8
        self.deselect()
        self.x = ret['x']
        self.y = ret['y']
        self.z = ret['z']
        self.t = ret['t']
        return ret
        
    def setupACActivityInterrupt(self, threshold, time):
        self.SPIwriteTwoRegisters(0x20, threshold)
        self.SPIwriteOneRegister(0x22, time);
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        ACT_INACT_CTL_Reg = ACT_INACT_CTL_Reg | (0x03)
        self.SPIwriteOneRegister(0x27, ACT_INACT_CTL_Reg)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        
    def setupACInactivityInterrupt(self, threshold, time):
        self.SPIwriteTwoRegisters(0x23, threshold)
        self.SPIwriteTwoRegisters(0x25, time)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        ACT_INACT_CTL_Reg = ACT_INACT_CTL_Reg | (0x0C)
        self.SPIwriteOneRegister(0x27, ACT_INACT_CTL_Reg)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
    def setupDCActivityInterrupt(self, threshold, time):
        self.SPIwriteTwoRegisters(0x20, threshold)
        self.SPIwriteOneRegister(0x22, time)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        ACT_INACT_CTL_Reg = ACT_INACT_CTL_Reg | (0x01)
        self.SPIwriteOneRegister(0x27, ACT_INACT_CTL_Reg)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        
    def setupDCInactivityInterrupt(self, threshold, time):
        self.SPIwriteTwoRegisters(0x23, threshold)
        self.SPIwriteTwoRegisters(0x25, time)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        ACT_INACT_CTL_Reg = ACT_INACT_CTL_Reg | (0x04)
        self.SPIwriteOneRegister(0x27, ACT_INACT_CTL_Reg)
        ACT_INACT_CTL_Reg = self.SPIreadOneRegister(0x27)
        
    def SPIreadOneRegister(self, regAddress):
        self.select()
        self.spi.write(0x0B)
        self.spi.write(regAddress)
        regValue = self.spi.read(1)
        self.deselect()
        return regValue
    def SPIwriteOneRegister(self, regAddress, regValue):
        self.select()
        self.spi.write(0x0A)
        self.spi.write(regAddress)
        self.spi.write(regValue)
        self.deselect()
    def SPIwriteTwoRegisters(self, regAddress, twoRegValue):
        twoRegValueH = twoRegValue >> 8
        twoRegValueL = twoRegValue
        self.select()
        self.spi.write(0x0A)
        self.spi.write(regAddress)
        self.spi.write(twoRegValueL)
        self.spi.write(twoRegValueH)
        self.deselect()
    def SPIreadTwoRegisters(self, regAddress):        
        self.select()
        self.spi.write(0x0B)
        self.spi.write(regAddress)
        twoRegValue = self.read(1)
        twoRegValue += self.read(1) << 8
        self.deselect()
        return twoRegValue
        
    def select(self):
        self.cspin.value(0)
    def deselect(self):
        self.cspin.value(1)
        
        
class ADXL362_MotionSensor(ADXL362):
    def __init__(self, csPIN, ISRPin, ActivityThreshold=70, ActivityTime=5, InactivityThreshold=1000, InactivityTime=5):
        self.steps = 0
        ADXL362.__init__(self, csPIN)
        self.isrpin = Pin(ISRPin, mode=Pin.IN)
        self.isrpin.callback(trigger=Pin.IRQ_RISING, handler=self._isr_handler)
     
        self.setupDCActivityInterrupt(ActivityThreshold, ActivityTime)
        self.setupDCInactivityInterrupt(InactivityThreshold, InactivityTime)
        
        #ACTIVITY/INACTIVITY CONTROL REGISTER
        self.SPIwriteOneRegister(0x27, 0B111111)  #B111111  Link/Loop:11 (Loop Mode), Inactive Ref Mode:1,Inactive Enable (under threshold):1,Active Ref Mode:1, Active Enable (over threshold):1
        
        #MAP INTERRUPT 1 REGISTER.
        self.SPIwriteOneRegister(0x2A,0B10010000) #B00010000 0=HIGH on ISR,AWAKE:0,INACT:0,ACT:1,FIFO_OVERRUN:0,FIFO_WATERMARK:0,FIFO_READY:0,DATA_READY:0
  
        #POWER CONTROL REGISTER
        self.SPIwriteOneRegister(0x2D, 0B1110)    #B1011 Wake-up:1,Autosleep:0,measure:11=Reserved (Maybe works better)
        self.beginMeasure()
        time.sleep_ms(100)
        
    def _isr_handler(self, id):
        self.steps += 1
        
