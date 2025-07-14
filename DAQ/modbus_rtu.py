from pymodbus.client.serial import ModbusSerialClient
from pymodbus import FramerType
from DAQ.Converstion import *

class ModbusSerialReader:
    def __init__(self, port='COM0', baudrate='9600', stopbit='1', type='rtu', databit='8', parity="N",slave_id='1'):
        try:
            self.client = ModbusSerialClient(
                framer=FramerType.ASCII if type == 'ascii' else FramerType.RTU,
                port=port,
                stopbits=int(stopbit),
                baudrate=int(baudrate),
                parity=parity,
                timeout=1,
                bytesize=int(databit)
            )
            self.slave_id = int(slave_id)
            self.client.connect()
            # self.status = self.client.connected
            # Verify device presence by reading 1 register from address 0
            result = self.client.read_holding_registers(address=37797, count=1, slave=self.slave_id)
            if result.isError():
                self.client.close()
                raise ConnectionError(f"Modbus device not responding at slave ID {self.slave_id}")
            
            self.status = True
            
        except Exception as e:
            self.client.close()
            raise e
    def read_coils(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_coils(address=address, count=count, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read coils at {address}")
            return result.bits[0:count]
        except Exception as e:
            raise RuntimeError(f"Serial Coil Read Error: {e}")

    def write_single_coil(self, address: int, value: bool, unit: int = 1):
        try:
            result = self.client.write_coil(address=address, value=value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write single coil at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Write Coil Error: {e}")

    def write_multi_coil(self, address: int, values: list[bool], unit: int = 1):
        try:
            result = self.client.write_coils(address=address, values=values, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write multiple coils at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Write Coil Error: {e}")

    def read_discrete_inputs(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_discrete_inputs(address=address, count=count, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read discrete inputs at {address}")
            return result.bits
        except Exception as e:
            raise RuntimeError(f"Serial Discrete Input Read Error: {e}")

    def read_holding_registers(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=count, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read holding registers at {address}")
            return result.registers
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Read Error: {e}")
    
    def read_single_holding_register(self, address: int, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address,count=1,slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read holding register at {address}")
            value = result.registers[0]
            return value
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Read Error: {e}")


    def write_single_holding_registers(self, address: int, value: int = 1, unit: int = 1):
        try:
            result = self.client.write_register(address=address, value=value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write single holding register at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Single Write Error: {e}")

    def write_multiple_holding_registers(self, address: int, value: list, unit: int = 1):
        try:
            result = self.client.write_registers(address=address, values=value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write multiple holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Multi Write Error: {e}")

    def read_input_registers(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_input_registers(address=address, count=count, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read input registers at {address}")
            return result.registers
        except Exception as e:
            raise RuntimeError(f"Serial Input Register Read Error: {e}")

    def read_float_register(self, address: int, inverse: bool = False, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=2, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read float value from holding registers at {address}")
            converted_result = to_float32(result.registers,0,inverse)
            return converted_result
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Read Error: {e}")
    
    def write_float_register(self, address: int, value: float, inverse: bool = False, unit: int = 1):
        try:
            converted_value = from_float32(value=float(value),inverse=inverse)
            result = self.client.write_registers(address=address, values=converted_value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write float value to holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Multi Write Error: {e}")
    
    def read_U32_register(self, address: int, inverse: bool = False, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=2, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read U32 value from holding registers at {address}")
            converted_result = to_uint32(result.registers,0,inverse)
            return converted_result
        except Exception as e:
            raise RuntimeError(f"Serial U32 Holding Register Read Error: {e}")
    
    def write_U32_register(self, address: int, value: int, inverse: bool = False, unit: int = 1):
        try:
            converted_value = from_uint32(value=int(value),inverse=inverse)
            result = self.client.write_registers(address=address, values=converted_value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write U32 value to holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial U32 Holding Register Multi Write Error: {e}")
    
    def read_I32_register(self, address: int, inverse: bool = False, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=2, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read I32 value from holding registers at {address}")
            converted_result = to_int32(result.registers,0,inverse)
            return converted_result
        except Exception as e:
            raise RuntimeError(f"Serial I32 Holding Register Read Error: {e}")
    
    def write_I32_register(self, address: int, value: int, inverse: bool = False, unit: int = 1):
        try:
            converted_value = from_int32(value=int(value),inverse=inverse)
            result = self.client.write_registers(address=address, values=converted_value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write I32 value to holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial I32 Holding Register Multi Write Error: {e}")
    
    def read_double_register(self, address: int, inverse: bool = False, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=4, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to read double value from holding registers at {address}")
            converted_result = to_double64(result.registers,0,inverse)
            return converted_result
        except Exception as e:
            raise RuntimeError(f"Serial double Holding Register Read Error: {e}")
    
    def write_double_register(self, address: int, value: int, inverse: bool = False, unit: int = 1):
        try:
            converted_value = from_double64(value=value,inverse=inverse)
            result = self.client.write_registers(address=address, values=converted_value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write double value to holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial double Holding Register Multi Write Error: {e}")
        
    def close(self):
        self.client.close()
