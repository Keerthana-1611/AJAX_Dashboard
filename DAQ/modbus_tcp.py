from pymodbus.client.tcp import ModbusTcpClient

class ModbusTCPReader:
    def __init__(self, host: str = '127.0.0.1', port: int = 502):
        self.client = ModbusTcpClient(host=host, port=port)
        self.client.connect()
        self.status = self.client.connected
        if not self.status:
            raise ConnectionError(f"Failed to connect to Modbus TCP server at {host}:{port}")

    def read_coils(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_coils(address=address, count=count, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to read coils at address {address}")
            return result.bits[0:count]
        except Exception as e:
            raise RuntimeError(f"TCP Coil Read Error: {e}")

    def write_single_coil(self, address: int, value: bool, unit: int = 1):
        try:
            result = self.client.write_coil(address=address, value=value, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to write single coil at address {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"TCP Write Coil Error: {e}")

    def write_multi_coil(self, address: int, values: list[bool], unit: int = 1):
        try:
            result = self.client.write_coils(address=address, values=values, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to write multiple coils at address {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"TCP Write Coil Error: {e}")

    def read_discrete_inputs(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_discrete_inputs(address=address, count=count, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to read discrete inputs at address {address}")
            return result.bits
        except Exception as e:
            raise RuntimeError(f"TCP Discrete Input Read Error: {e}")

    def read_holding_registers(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_holding_registers(address=address, count=count, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to read holding registers at address {address}")
            return result.registers
        except Exception as e:
            raise RuntimeError(f"TCP Holding Register Read Error: {e}")

    def write_single_holding_registers(self, address: int, value: int = 1, unit: int = 1):
        try:
            result = self.client.write_register(address=address, value=value, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to write single holding register at address {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"TCP Holding Register Single Write Error: {e}")

    def write_multiple_holding_registers(self, address: int, value: list, unit: int = 1):
        try:
            result = self.client.write_registers(address=address, values=value, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to write multiple holding registers at address {address}")
            return True
        except Exception as e:
            raise RuntimeError(f"TCP Holding Register Multi Write Error: {e}")

    def read_input_registers(self, address: int, count: int = 1, unit: int = 1):
        try:
            result = self.client.read_input_registers(address=address, count=count, slave=unit)
            if result.isError() or not self.client.connected:
                raise RuntimeError(f"Failed to read input registers at address {address}")
            return result.registers
        except Exception as e:
            raise RuntimeError(f"TCP Input Register Read Error: {e}")

    def close(self):
        self.client.close()
