#RFM69 Library for pyCOM
from coda_rfm69_regs import RFM69_CONST_VARS
from machine import SPI
from machine import Pin
import utime
from machine import disable_irq
from machine import enable_irq

_irqsts = 0
def millis():
    return utime.ticks_ms()

def interrupts():
    enable_irq(_irqsts)

def noInterrupts():
    _irqsts=disable_irq()
    return _irqsts
   
class RFM69(RFM69_CONST_VARS):
    
    def __init__(self, cspin, ISRPin, nodeID, networkID, freqBand=868, isRFM69HW=False):
        RFM69_CONST_VARS.__init__(self)
        self._isRFM69HW = isRFM69HW
        
        tREG_FRFMSB = self.RF_FRFMSB_868
        tREG_FRFMID = self.RF_FRFMID_868
        tREG_FRFLSB = self.RF_FRFLSB_868
        if freqBand==433:
            tREG_FRFMSB = self.RF_FRFMSB_433
            tREG_FRFMID = self.RF_FRFMID_433
            tREG_FRFLSB = self.RF_FRFLSB_433
        
        if freqBand==315:
            tREG_FRFMSB = self.RF_FRFMSB_315
            tREG_FRFMID = self.RF_FRFMID_315
            tREG_FRFLSB = self.RF_FRFLSB_315
        
        if freqBand==915:
            tREG_FRFMSB = self.RF_FRFMSB_915
            tREG_FRFMID = self.RF_FRFMID_915
            tREG_FRFLSB = self.RF_FRFLSB_915
            
        self.CONFIG = [[self.REG_OPMODE, self.RF_OPMODE_SEQUENCER_ON | self.RF_OPMODE_LISTEN_OFF | self.RF_OPMODE_STANDBY], 
              [self.REG_DATAMODUL, self.RF_DATAMODUL_DATAMODE_PACKET | self.RF_DATAMODUL_MODULATIONTYPE_FSK | self.RF_DATAMODUL_MODULATIONSHAPING_00], 
              [self.REG_BITRATEMSB, self.RF_BITRATEMSB_55555], 
              [self.REG_BITRATELSB, self.RF_BITRATELSB_55555], 
              [self.REG_FDEVMSB, self.RF_FDEVMSB_50000], 
              [self.REG_FDEVLSB, self.RF_FDEVLSB_50000], 
              [self.REG_FRFMSB, tREG_FRFMSB ], 
              [self.REG_FRFMID, tREG_FRFMID], 
              [self.REG_FRFLSB, tREG_FRFLSB], 
              [self.REG_RXBW, self.RF_RXBW_DCCFREQ_010 | self.RF_RXBW_MANT_16 | self.RF_RXBW_EXP_2 ], 
              [self.REG_DIOMAPPING1, self.RF_DIOMAPPING1_DIO0_01], 
              [self.REG_DIOMAPPING2, self.RF_DIOMAPPING2_CLKOUT_OFF], 
              [self.REG_IRQFLAGS2, self.RF_IRQFLAGS2_FIFOOVERRUN], 
              [self.REG_RSSITHRESH, 220], 
              [self.REG_SYNCCONFIG, self.RF_SYNC_ON | self.RF_SYNC_FIFOFILL_AUTO | self.RF_SYNC_SIZE_2 | self.RF_SYNC_TOL_0], 
              [self.REG_SYNCVALUE1, 0x2D], 
              [self.REG_SYNCVALUE2, networkID ], 
              [self.REG_PACKETCONFIG1, self.RF_PACKET1_FORMAT_VARIABLE | self.RF_PACKET1_DCFREE_OFF | self.RF_PACKET1_CRC_ON | self.RF_PACKET1_CRCAUTOCLEAR_ON | self.RF_PACKET1_ADRSFILTERING_OFF], 
              [self.REG_FIFOTHRESH, self.RF_FIFOTHRESH_TXSTART_FIFONOTEMPTY | self.RF_FIFOTHRESH_VALUE], 
              [self.REG_PACKETCONFIG2, self.RF_PACKET2_RXRESTARTDELAY_2BITS | self.RF_PACKET2_AUTORXRESTART_ON | self.RF_PACKET2_AES_OFF], 
              [self.REG_TESTDAGC, self.RF_DAGC_IMPROVED_LOWBETA0]]
              
        self.cspin = Pin(cspin, mode=Pin.OUT)
        self.cspin.value(1)
        self.isrpin = Pin(ISRPin, mode=Pin.IN)
        
        self.isrpin.callback(trigger=Pin.IRQ_RISING, handler=self.isr0)
        self.spi = SPI(0, mode=SPI.MASTER, baudrate=1000000, polarity=0, phase=0, firstbit=SPI.MSB)
    
        start = millis()
        timeout = 50
        while millis()-start < timeout:
            self.writeReg(self.REG_SYNCVALUE1, 0xAA)
            if self.readReg(self.REG_SYNCVALUE1) == 0xaa:
                break
        
        start = utime.ticks_ms()
        while utime.ticks_ms()-start < timeout:
            self.writeReg(self.REG_SYNCVALUE1, 0x55)
            if self.readReg(self.REG_SYNCVALUE1) == 0x55:
                break
        for item in self.CONFIG:
            self.writeReg(item[0], item[1])
            
        self.encrypt(0)
        
    def getFrequency(self):
        return self.RF69_FSTEP * (self.readReg(self.REG_FRFMSB) << 16) + self.readReg(self.REG_FRFMID) + self.readReg(self.REG_FRFLSB)
            
    def setFrequency(self, freqHz):
        oldMode = self._mode
        if oldMode == self.RF69_MODE_TX:
            self.setMode(self.RF69_MODE_RX)
            
        freqHz /= self.RF69_FSTEP
        self.writeReg(self.REG_FRFMSB, freqHz >> 16)
        self.writeReg(self.REG_FRFMID, freqHz >> 8)
        self.writeReg(self.REG_FRFLSB, freqHz)
        if oldMode == self.RF69_MODE_RX:
            self.setMode(self.RF69_MODE_SYNTH)
            
        self.setMode(oldMode)
    def setMode(self, new_mode):
        if self._mode == new_mode:
            return
        
        if new_mode == self.RF69_MODE_TX:
            self.writeReg(self.REG_OPMODE, (self.readReg(self.REG_OPMODE) & 0xE3) | self.RF_OPMODE_TRANSMITTER)
            if self._isRFM69HW:
                self.setHighPowerRegs(True)
                
        if new_mode == self.RF69_MODE_RX:
            self.writeReg(self.REG_OPMODE, (self.readReg(self.REG_OPMODE) & 0xE3) | self.RF_OPMODE_RECEIVER)
            if self._isRFM69HW:
                self.setHighPowerRegs(False)

        if new_mode == self.RF69_MODE_SYNTH:
            self.writeReg(self.REG_OPMODE, (self.readReg(self.REG_OPMODE) & 0xE3) | self.RF_OPMODE_SYNTHESIZER)

        if new_mode == self.RF69_MODE_STANDBY:
            self.writeReg(self.REG_OPMODE, (self.readReg(self.REG_OPMODE) & 0xE3) | self.RF_OPMODE_STANDBY)
        
        if new_mode == self.RF69_MODE_SLEEP:
            self.writeReg(self.REG_OPMODE, (self.readReg(self.REG_OPMODE) & 0xE3) | self.RF_OPMODE_SLEEP)
            while self._mode == self.RF69_MODE_SLEEP and (self.readReg(self.REG_IRQFLAGS1) & self.RF_IRQFLAGS1_MODEREADY) == 0x00:
                pass
        self._mode = new_mode

    def sleep(self):
        self.setMode(self.RF69_MODE_SLEEP)
    def setAddress(self, addr):
        self._address = addr;
        self.writeReg(self.REG_NODEADRS, self._address)
    def setNetwork(self, networkID):
        self.writeReg(self.REG_SYNCVALUE2, networkID)

    def setPowerLevel(self, powerLevel):
        self._powerLevel = powerLevel
        if self._powerLevel > 31:
            self._powerLevel = 31
        self.writeReg(self.REG_PALEVEL, (self.readReg(self.REG_PALEVEL) & 0xE0) | self._powerLevel);
        
    def canSend(self):
        if self._mode == self.RF69_MODE_RX and self.PAYLOADLEN == 0 and self.readRSSI() < self.CSMA_LIMIT:
            self.setMode(self.RF69_MODE_STANDBY)
            return True
        return False
    def send(self, toAddress, buffer, bufferSize, requestACK):
        self.writeReg(self.REG_PACKETCONFIG2, (self.readReg(self.REG_PACKETCONFIG2) & 0xFB) | self.RF_PACKET2_RXRESTART)
        now = millis()
        while self.canSend()==False and millis() - now < self.RF69_CSMA_LIMIT_MS:
            self.receiveDone()
        self.sendFrame(toAddress, buffer, bufferSize, requestACK, False)
        
    def sendWithRetry(self, toAddress, buffer, bufferSize, retries, retryWaitTime):
        for i in range(retries+1):
            self.send(toAddress, buffer, bufferSize, False)
            sentTime = millis()
            while millis() - sentTime < retryWaitTime:
                if self.ACKReceived(toAddress):
                    return True
            return False
    def ACKReceived(self, fromNodeID):
        if self.receiveDone():
            return (self.SENDERID == fromNodeID or fromNodeID == self.RF69_BROADCAST_ADDR) and self.ACK_RECEIVED
        return False
    def ACKRequested(self):
        return self.ACK_REQUESTED and (self.TARGETID != self.RF69_BROADCAST_ADDR)
    def sendACK(self, buffer, bufferSize):
        self.ACK_REQUESTED = 0
        sender = self.SENDERID
        _RSSI = self.RSSI
        self.writeReg(self.REG_PACKETCONFIG2, (self.readReg(self.REG_PACKETCONFIG2) & 0xFB) | self.RF_PACKET2_RXRESTART)
        now = millis()
        while not self.canSend() and millis() - now < self.RF69_CSMA_LIMIT_MS:
           self.receiveDone()
        self.SENDERID = sender
        self.sendFrame(sender, buffer, bufferSize, False, True)
        self.RSSI = _RSSI
    def sendFrame(self, toAddress, buffer, bufferSize, requestACK, sendACK):
      
        self.setMode(self.RF69_MODE_STANDBY)
        while self.readReg(self.REG_IRQFLAGS1) & self.RF_IRQFLAGS1_MODEREADY == 0x00:
            pass
        
        self.writeReg(self.REG_DIOMAPPING1, self.RF_DIOMAPPING1_DIO0_00)
        if bufferSize > self.RF69_MAX_DATA_LEN:
            bufferSize = self.RF69_MAX_DATA_LEN

        CTLbyte = 0x00;
        if sendACK:
            CTLbyte = self.RFM69_CTL_SENDACK
        else:
            if requestACK:
                CTLbyte = self.RFM69_CTL_REQACK

        self.select();
        self.spi.write(self.REG_FIFO | 0x80)
        self.spi.write(bufferSize + 3)
        self.spi.write(toAddress)
        self.spi.write(self._address)
        self.spi.write(CTLbyte)
        for i in range(bufferSize):
            self.spi.write(buffer[i])
        self.unselect()

        self.setMode(self.RF69_MODE_TX)
        txStart = millis();
        while (self.isrpin.value() == 0 and millis() - txStart < self.RF69_TX_LIMIT_MS):
            pass
        self.setMode(self.RF69_MODE_STANDBY);
        
    def interruptHandler(self, id):
       
        if self._mode == self.RF69_MODE_RX and (self.readReg(self.REG_IRQFLAGS2) & self.RF_IRQFLAGS2_PAYLOADREADY):
            self.setMode(self.RF69_MODE_STANDBY)
            self.select()
            self.spi.write(self.REG_FIFO & 0x7F)
            self.PAYLOADLEN = self.spi.read(1)
            self.PAYLOADLEN = self.PAYLOADLEN
            if self.PAYLOADLEN > 66: self.PAYLOADLEN = 66
            self.TARGETID = self.spi.read(1)
            if not (self._promiscuousMode or self.TARGETID == self._address or self.TARGETID == self.RF69_BROADCAST_ADDR) or self.PAYLOADLEN < 3:
                self.PAYLOADLEN = 0
                self.unselect()
                self.receiveBegin()
                return
            self.DATALEN = self.PAYLOADLEN - 3
            self.SENDERID = self.spi.read(1)
            CTLbyte = self.spi.read(1)
            self.ACK_RECEIVED = CTLbyte & self.RFM69_CTL_SENDACK
            self.ACK_REQUESTED = CTLbyte & self.RFM69_CTL_REQACK
            self.interruptHook(CTLbyte)
            for i in range(self.DATALEN):
                self.DATA[i] = self.spi.read(1)
            if self.DATALEN < self.RF69_MAX_DATA_LEN: self.DATA[self.DATALEN] = 0
            self.unselect()
            self.setMode(self.RF69_MODE_RX)
            
        self.RSSI = self.readRSSI()

    def isr0(self, id):
        self._inISR=True
        self.interruptHandler(id)
        self._inISR=False
    def receiveBegin(self):
        self.DATALEN = 0
        self.SENDERID = 0
        self.TARGETID = 0
        self.PAYLOADLEN = 0
        self.ACK_REQUESTED = 0
        self.ACK_RECEIVED = 0
        self.RSSI = 0
        if self.readReg(self.REG_IRQFLAGS2) & self.RF_IRQFLAGS2_PAYLOADREADY:
            self.writeReg(self.REG_PACKETCONFIG2, (self.readReg(self.REG_PACKETCONFIG2) & 0xFB) |self.RF_PACKET2_RXRESTART)
        self.writeReg(self.REG_DIOMAPPING1, self.RF_DIOMAPPING1_DIO0_01)
        self.setMode(self.RF69_MODE_RX)
    def receiveDone(self):
        noInterrupts()
        if self._mode == self.RF69_MODE_RX and self.PAYLOADLEN > 0:
            self.setMode(self.RF69_MODE_STANDBY) 
            return True
        else:
            if self._mode==self.RF69_MODE_RX:
                interrupts()
                return False
                
        self.receiveBegin()
        return False
    def encrypt(self, key):
        self.setMode(self.RF69_MODE_STANDBY)
        if key != 0:
            self.select()
            self.spi.write(self.REG_AESKEY1 | 0x80)
            for i in range(16):
                self.spi.write(key[i])
            self.unselect()
            
        val = 1
        if key==None:
            val = 0
            
        self.writeReg(self.REG_PACKETCONFIG2, (self.readReg(self.REG_PACKETCONFIG2) & 0xFE) | val)
        
    def readRSSI(self, forceTrigger):
        rssi = 0
        if forceTrigger:
            self.writeReg(self.REG_RSSICONFIG, self.RF_RSSI_START)
            while (self.readReg(self.REG_RSSICONFIG) & self.RF_RSSI_DONE) == 0x00:
                pass
        rssi = -self.readReg(self.REG_RSSIVALUE)
        rssi = rssi >> 1
        return rssi
    def readReg(self, addr):
        self.select()
        self.spi.write(addr & 0x7F)
        regValue = self.spi.read(1)
        self.unselect()
        return regValue    
    def writeReg(self, addr, value):
        self.select()
        self.spi.write(addr | 0x80)
        self.spi.write(value)
        self.unselect()
         
    def select(self):
        self.cspin.value(0)
    def unselect(self):
        self.cspin.value(1)    
    def promiscuous(self, onOff):
        self._promiscuousMode = onOff
        
    def setHighPower(self, onOff):
        self._isRFM69HW = onOff
        if self._isRFM69HW:
            self.writeReg(self.REG_OCP, self.RF_OCP_OFF)
            self.writeReg(self.REG_PALEVEL, (self.readReg(self.REG_PALEVEL) & 0x1F) | self.RF_PALEVEL_PA1_ON | self.RF_PALEVEL_PA2_ON)
            
        else:
            self.writeReg(self.REG_OCP, self.RF_OCP_ON)
            self.writeReg(self.REG_PALEVEL, self.RF_PALEVEL_PA0_ON | self.RF_PALEVEL_PA1_OFF | self.RF_PALEVEL_PA2_OFF | self._powerLevel)
        
    def setHighPowerRegs(self, onOff):
        if onOff:
            self.writeReg(self.REG_TESTPA1, 0x5D)
            self.writeReg(self.REG_TESTPA2, 0x7C)
        else:    
            self.writeReg(self.REG_TESTPA1, 0x55)
            self.writeReg(self.REG_TESTPA2, 0x70)
            
    def setCS(self, newSPISlaveSelect):
        self._slaveSelectPin = newSPISlaveSelect  
        self.cspin = Pin(self._slaveSelectPin, mode=Pin.OUT)
        self.cspin.value(1)
    def readAllRegs(self):
        regVal = 0
       
        print("Address - HEX - BIN")
        for regAddr in range(1, 0x4F):
            self.select()
            self.spi.write(regAddr & 0x7F)
            regVal = self.spi.read(1)
            self.unselect()
            print(regAddr, " - ", regVal)
           
    def readTemperature(self, calFactor):
        self.setMode(self.RF69_MODE_STANDBY);
        self.writeReg(self.REG_TEMP1, self.RF_TEMP1_MEAS_START)
        while self.readReg(self.REG_TEMP1) & self.RF_TEMP1_MEAS_RUNNING:
            pass
        return ~self.readReg(self.REG_TEMP2) + self.COURSE_TEMP_COEF + calFactor
    def rcCalibration(self):
        self.writeReg(self.REG_OSC1, self.RF_OSC1_RCCAL_START)
        while (self.readReg(self.REG_OSC1) & self.RF_OSC1_RCCAL_DONE) == 0x00: pass
    def maybeInterrupts(self):
        if not self._inISR:
           interrupts()
    def initialize(self):
        pass    
        
obj = RFM69('P9', 'P10', 1, 2)
