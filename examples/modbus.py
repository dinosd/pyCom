import coda_modbus
reg=modBusDevice("127.0.0.1").readRegister(2, 3, 30057, 2)
print(reg)
