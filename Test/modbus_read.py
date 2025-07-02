from modbus_handler import load_plc_config,create_modbus_connection
import time

load_plc_config()

while True:
    Instance = create_modbus_connection()
    print(Instance)
    if Instance:
        print(True)
        print(Instance.read_holding_registers(0,1,1))

    time.sleep(1)

