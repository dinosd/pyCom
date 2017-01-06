import socket
import time

def highbyte(word):
    return word >> 8
    
def lowbyte(word):
    return word - (highbyte(word)<<8)
    
        
class modBusDevice:
    def __init__(self, ip, port=502):
        self.ip = ip
        self.port = port
    def readRegister(self, unitID, functionCode, firstReg, countOfRegs):
        sendbuf = bytes([0, 1, 0, 0, 0, 6, unitID, functionCode,highbyte(firstReg),lowbyte(firstReg),highbyte(countOfRegs),lowbyte(countOfRegs)])
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ai = socket.getaddrinfo(self.ip, self.port)
        addr = ai[0][4]
        s.connect(addr)
        s.write(sendbuf)
        retbuf = []
        timespend = 0
        while True:
            retbuf = s.recv(28)
            if len(retbuf)>0:
                break
            timespend += 1
            time.sleep(1)
            if timespend > 5:
                break
            
        s.close()
        if len(retbuf)==0:
            return 0
      
        
        return self.getNumber(retbuf, 9, countOfRegs)
    def getNumber(self, buff, offset, words):
        ret = 0
        word_size = words * 2
        for i in range(1, word_size+1):
            temp = buff[offset+i-1] << (word_size-i) * 8
            ret += temp
        return ret
            
        
        


