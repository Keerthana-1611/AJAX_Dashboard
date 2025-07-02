from DAQ.modbus_rtu import ModbusSerialReader


instance = ModbusSerialReader(
    port='COM2', baudrate='9600', stopbit='1', type='ascii', databit='8', parity="N",slave_id='1'

)

print(instance.read_float_register(0,True,1))
instance.close()