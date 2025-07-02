from DAQ.modbus_rtu import ModbusSerialReader  # Adjust the import based on your structure
import sys
import json
import os
from threading import Thread
import time

# Globals
LOADCELL_REGISTER_MAP = None
PLC_CONNECTION_INFORMATION = None
MODBUS_INSTANCE = None
PLC_CONNECTION_STATUS = False
MODBUS_REGISTRY = {}

# Determine base path (for config file loading)
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS  # PyInstaller
else:
    BASE_PATH = os.getcwd()


def load_plc_config(path=os.path.join(BASE_PATH, "data", "PLC_Data.json")):
    global LOADCELL_REGISTER_MAP, PLC_CONNECTION_INFORMATION
    try:
        with open(path, 'r') as file:
            config = json.load(file)
            LOADCELL_REGISTER_MAP = config['loadcell_register_map']
            PLC_CONNECTION_INFORMATION = config['plc_connection_information']
            print("PLC config loaded.")
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error decoding JSON config: {e}")

def load_modbus_registry(filepath=os.path.join(BASE_PATH,"data","PLC_Address_registory.json")):
    global MODBUS_REGISTRY
    try:
        with open(filepath, 'r') as file:
            MODBUS_REGISTRY = json.load(file)
        print("Modbus registry loaded successfully.")
    except Exception as e:
        print(f"Failed to load registry: {e}")
        MODBUS_REGISTRY = {}

def create_modbus_connection():
    global MODBUS_INSTANCE
    print("create_modbus_connection() CALLED")

    # # If an existing instance exists, close and cleanup
    # if MODBUS_INSTANCE is not None:
    #     try:
    #         MODBUS_INSTANCE.client.close()  # Ensure COM port is closed
    #         print("Existing Modbus connection closed.")
    #     except Exception as e:
    #         print(f"Error closing existing Modbus connection: {e}")
    #     finally:
    #         MODBUS_INSTANCE = None

    # Attempt to create a new connection
    try:
        if MODBUS_INSTANCE:
            return MODBUS_INSTANCE
        
        MODBUS_INSTANCE = ModbusSerialReader(
            port=PLC_CONNECTION_INFORMATION['port'],
            baudrate=PLC_CONNECTION_INFORMATION['baudrate'],
            stopbit=PLC_CONNECTION_INFORMATION['stopbit'],
            databit=PLC_CONNECTION_INFORMATION['databit'],
            parity=PLC_CONNECTION_INFORMATION['parity'],
            type=PLC_CONNECTION_INFORMATION['type'],
            slave_id=PLC_CONNECTION_INFORMATION['slave_id']
        )
        print("New Modbus connection established.")
        return MODBUS_INSTANCE
    except Exception as e:
        print(f"Error creating Modbus connection: {e}")
        return None

def read_by_names(reader, registry: dict, names: list, unit: int = 1) -> dict:
    result = {}

    for name in names:
        reg_info = registry.get(name)
        if not reg_info:
            result[name] = "Not found"
            continue

        reg_type = reg_info["type"]
        address = reg_info["address"]

        try:
            if reg_type == "coils":
                result[name] = reader.read_coils(address=address, count=1, unit=unit)[0]
            elif reg_type == "discrete_inputs":
                result[name] = reader.read_discrete_inputs(address=address, count=1, unit=unit)[0]
            elif reg_type == "holding_registers":
                result[name] = reader.read_holding_registers(address=address, count=1, unit=unit)[0]
            elif reg_type == "input_registers":
                result[name] = reader.read_input_registers(address=address, count=1, unit=unit)[0]
            else:
                result[name] = f"Unsupported type: {reg_type}"
        except Exception as e:
            result[name] = f"Error: {str(e)}"

    return result

def main_thread():
    global MODBUS_INSTANCE
    print("Main thread started. Waiting for 5 seconds before polling...")
    time.sleep(5)

    while True:
        try:
            if MODBUS_INSTANCE:
                result = MODBUS_INSTANCE.read_holding_registers(0, 1, 1)
                print("Read Result:", result)
                pass
            else:
                print("MODBUS_INSTANCE is None. Trying to reconnect...")
                MODBUS_INSTANCE = create_modbus_connection()

        except Exception as e:
            print(f"Exception in main_thread: {e}")
            print("Reconnecting Modbus...")
            MODBUS_INSTANCE = create_modbus_connection()

        time.sleep(1)

def start_thread():
    global MODBUS_INSTANCE
    print("start_thread() CALLED")
    load_plc_config()
    MODBUS_INSTANCE = create_modbus_connection()

    # Start polling thread
    main = Thread(target=main_thread, daemon=True)
    main.start()

def write_demo_value(address, x,id):
    instance = create_modbus_connection()
    instance.write_float_to_registers(1,34.99,1)
    return instance.read_float_from_registers(1,2,True,1)
