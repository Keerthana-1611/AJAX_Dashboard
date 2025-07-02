from DAQ.modbus_rtu import ModbusSerialReader
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
MODBUS_REGISTRY_KEYS = []


# Determine base path (for config file loading)
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS  # PyInstaller
else:
    BASE_PATH = os.getcwd()

# Loads PLC Connection informations
def load_plc_config(path=os.path.join(BASE_PATH, "data", "PLC_Data.json")):
    global PLC_CONNECTION_INFORMATION
    try:
        with open(path, 'r') as file:
            config = json.load(file)
            PLC_CONNECTION_INFORMATION = config['plc_connection_information']
            print("PLC config loaded.")
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error decoding JSON config: {e}")

# Read and loads the Modbus address and their types into Global Variable
def load_modbus_registry(filepath=os.path.join(BASE_PATH,"data","PLC_Address_registory.json")):
    global MODBUS_REGISTRY,MODBUS_REGISTRY_KEYS
    try:
        with open(filepath, 'r') as file:
            MODBUS_REGISTRY = json.load(file)
            MODBUS_REGISTRY_KEYS = MODBUS_REGISTRY.keys()
        print("Modbus registry loaded successfully.")
    except Exception as e:
        print(f"Failed to load registry: {e}")
        MODBUS_REGISTRY = {}

# Creates Modbus connection based on the previous loaded details
def create_modbus_connection():
    global MODBUS_INSTANCE
    # print("create_modbus_connection() CALLED")
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

'''
# Read values based on the key given which should match the key name in the Address registry file
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
                result[name] = reader.read(address=address, count=1, unit=unit)[0]
            elif reg_type == "input_registers":
                result[name] = reader.read_input_registers(address=address, count=1, unit=unit)[0]
            else:
                result[name] = f"Unsupported type: {reg_type}"
        except Exception as e:
            result[name] = f"Error: {str(e)}"

    return result
'''

# Main Thread which will be in constant communcation with PLC
# Used to get the Alarm and other default values and default operations
def main_thread():
    global MODBUS_INSTANCE
    print("Main thread started. Waiting for 5 seconds before polling...")
    time.sleep(5)

    while True:
        try:
            if MODBUS_INSTANCE:
                '''
                
                Functions need to be implemented here

                '''
                pass
            else:
                print("MODBUS_INSTANCE is None. Trying to reconnect...")
                MODBUS_INSTANCE = create_modbus_connection()

        except Exception as e:
            print(f"Exception in main_thread: {e}")
            print("Reconnecting Modbus...")
            MODBUS_INSTANCE = create_modbus_connection()

        time.sleep(1)

# Started the main thread
def start_thread():
    global MODBUS_INSTANCE
    print("start_thread() CALLED")
    load_plc_config()
    MODBUS_INSTANCE = create_modbus_connection()

    # Start polling thread
    main = Thread(target=main_thread, daemon=True)
    main.start()

# Read values based on the key given which should match the key name in the Address registry file
def read_data(names: list, unit: int = 1) -> dict:
    global MODBUS_REGISTRY,MODBUS_REGISTRY_KEYS,MODBUS_REGISTRY
    result = {}
    instance = MODBUS_INSTANCE
    for name in names:

        reg_info = MODBUS_REGISTRY.get(name)
        if not reg_info:
            result[name] = "Not found"
            continue

        reg_type = reg_info["register_type"]
        value_type = reg_info["value_type"]
        address = reg_info["address"]
        inverse = reg_info["inverse"]
        
        try:
            if reg_type == "coil":
                result[name] = instance.read_coils(address=address, count=1, unit=unit)[0]
            elif reg_type == "discrete_input":
                result[name] = instance.read_discrete_inputs(address=address, count=1, unit=unit)[0]
            elif reg_type == "holding_register":
                if value_type == 'U16':
                    result[name] = instance.read_holding_registers(address=address ,count=1, unit=unit)[0]
                if value_type == 'Float':
                    result[name] = instance.read_float_register(address=address, inverse=inverse, unit=unit)
                elif value_type == "U32":
                    result[name] = instance.read_U32_register(address=address, inverse=inverse, unit=unit)
                elif value_type == "I32":
                    result[name] = instance.read_I32_register(address=address, inverse=inverse,  unit=unit)
                elif value_type == "Double":
                    result[name] = instance.read_double_register(address=address, inverse=inverse, unit=unit)
            elif reg_type == "input_register":
                result[name] = instance.read_input_registers(address=address, count=1, unit=unit)[0]
            else:
                # result[name] = f"Unsupported type: {reg_type}"
                result[name] = False if reg_type == "coil" else 0
        except Exception as e:
            # result[name] = f"Error: {str(e)}"
            result[name] = False if reg_type == "coil" else 0
    return result

'''

# Testing Manual Read 
def read_manual_values(unit=1):
    instance = create_modbus_connection()
    result = {}

    try:
        result["motor_start"] = instance.read_coils(address=0, count=1, unit=unit)[0]
        result["valve_open"] = instance.read_coils(address=1, count=1, unit=unit)[0]
        result["emergency_stop"] = instance.read_coils(address=2, count=1, unit=unit)[0]

        result["temperature_setpoint"] = instance.read_holding_registers(address=0, count=1, unit=unit)[0]
        result["pressure_limit"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Lower Pressure"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["Upper pressure"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["temperature_actual"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["under Lower"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Under Upper"] = instance.read_float_register(address=2, inverse=True, unit=unit)

        result["motor_1start"] = instance.read_coils(address=0, count=1, unit=unit)[0]
        result["valve_2open"] = instance.read_coils(address=1, count=1, unit=unit)[0]
        result["emergency_3stop"] = instance.read_coils(address=2, count=1, unit=unit)[0]

        result["temperature_1setpoint"] = instance.read_holding_registers(address=0, count=1, unit=unit)[0]
        result["pressure_2limit"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Lower 3Pressure"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["Upper 12pressure"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["temperature_231actual"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["under 12Lower"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]

        result["valv1_open"] = instance.read_coils(address=1, count=1, unit=unit)[0]
        result["emerg1ency_stop"] = instance.read_coils(address=2, count=1, unit=unit)[0]

        result["tempe1rature_setpoint"] = instance.read_holding_registers(address=0, count=1, unit=unit)[0]
        result["pressu1re_limit"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Lowe1r Pressure"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["Upper 1pressure"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["temper1ature_actual"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["under L1ower"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Under Up1per"] = instance.read_float_register(address=2, inverse=True, unit=unit)

        result["motor_1st1art"] = instance.read_coils(address=0, count=1, unit=unit)[0]
        result["valve_21open"] = instance.read_coils(address=1, count=1, unit=unit)[0]
        result["emergency_3s1top"] = instance.read_coils(address=2, count=1, unit=unit)[0]

        result["temperature11_1setpoint"] = instance.read_holding_registers(address=0, count=1, unit=unit)[0]
        result["pressure_2limi1t"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Lower 3Pressu1re"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["Upper 12pres1sure"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["temperature_231ac1tual"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["under 12L2ower"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["Lowaer 3Pressu1re"] = instance.read_float_register(address=2, inverse=True, unit=unit)
        result["Uppser 12pres1sure"] = instance.read_holding_registers(address=1, count=1, unit=unit)[0]
        result["tempserature_231ac1tual"] = instance.read_float_register(address=2, inverse=True, unit=unit)

    except Exception as e:
        print(f"Error during manual read: {e}")

    return result

load_modbus_registry()
load_plc_config()
print(len(MODBUS_REGISTRY_KEYS))
time.sleep(2)
while True:
    start = time.time()
    auto_values = read_data(MODBUS_REGISTRY_KEYS,1)
    auto_read_time = f"Auto Read time : {time.time() - start} sec"
    manual_start = time.time()
    manula_values = read_manual_values()
    manual_read_time = f"Manual Read time : {time.time() - manual_start} sec"
    print(f"{auto_read_time}\n{manual_read_time}")
'''