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
            self.slave_id = slave_id
            self.client.connect()
            # self.status = self.client.connected
             # Verify device presence by reading 1 register from address 0
            result = self.client.read_holding_registers(address=0, count=1, slave=self.slave_id)
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

    def write_float_to_registers(self, address: int, value: float, inverse: bool = False ,unit: int = 1):
        try:
            converted_value = from_float32(value=value,inverse=inverse)
            result = self.client.write_registers(address=address, values=converted_value, slave=unit)
            if result.isError():
                raise RuntimeError(f"Failed to write multiple holding registers at {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Multi Write Error: {e}")

    def read_float_from_registers(self, address: int, count: int = 2, inverse: bool = False,unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=count, slave=unit)
            converted_result = to_float32(result.registers,0,inverse)
            if result.isError():
                raise RuntimeError(f"Failed to read holding registers at {address}")
            return converted_result
        except Exception as e:
            raise RuntimeError(f"Serial Holding Register Read Error: {e}")
        
    def read_mix_design(self, address: int = 37768, num_floats: int = 10, inverse: bool = False, unit: int = 1):
        try:
            registers_to_read = num_floats * 2
            
            result_registers = self.read_holding_registers(address=address, count=registers_to_read, unit=unit)
            
            mix_design_data = []
            for i in range(num_floats):
              
                float_value = to_float32(result_registers, i * 2, inverse)
                mix_design_data.append(float_value)
            return mix_design_data
        except Exception as e:
            raise RuntimeError(f"Failed to read mix design from address {address}: {e}")

    def write_mix_design(self, mix_design_data: list[float], address: int = 37768, inverse: bool = False, unit: int = 1):

        try:
            all_registers_to_write = []
            for value in mix_design_data:
                converted_registers = from_float32(value=value, inverse=inverse)
                all_registers_to_write.extend(converted_registers)
            
            self.write_multiple_holding_registers(address=address, value=all_registers_to_write, unit=unit)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to write mix design to address {address}: {e}")    
            
    def close(self):
        self.client.close()

