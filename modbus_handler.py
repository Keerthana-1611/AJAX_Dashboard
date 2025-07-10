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
ACTIVE_ALARMS = set()
PREVIOUS_ALARM_STATE = {} 

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

def update_values_to_plc(data : dict):
    global MODBUS_REGISTRY
    '''
    "mixer_capacity": {
        "register_type": "holding_register",
        "address": 37912,
        "value_type": "Float",
        "inverse": false
    },
    '''
    try:
        instance = create_modbus_connection()
        for key,value in data.items():
            reg_details = MODBUS_REGISTRY.get(key)
            if reg_details == None:
                continue
        
            reg_type = reg_details.get("register_type")
            value_type = reg_details.get("value_type")
            reg_address = reg_details.get("address")
            inverse = reg_details.get('inverse')
            if reg_type == "holding_register":
                if value_type == "Float":
                    instance.write_float_register(address=reg_address,value=float(value),inverse=inverse,unit=1)
                elif value_type == "U16":
                    instance.write_single_holding_registers(address=reg_address,value=int(value),unit=1)
                elif value_type == "U32":
                    instance.write_U32_register(address=reg_address,value=int(value),inverse=inverse,unit=1)
                elif value_type == "I32":
                    instance.write_I32_register(address=reg_address,value=int(value),inverse=inverse,unit=1)            
            elif reg_type == "coil":
                instance.write_single_coil(address=reg_address,value=bool(value),unit=1)
        return True
    except Exception as e:
        error = e
        return False

def write_db_values_to_plc(db_data: dict):
    global MODBUS_REGISTRY
    try:
        print("[DEBUG] Entering write_db_values_to_plc")
        print("[DEBUG] Input Data:", db_data)
        print("[DEBUG] MODBUS_REGISTRY Keys:", list(MODBUS_REGISTRY.keys()))

        instance = create_modbus_connection()
        if not instance:
            print("[ERROR] Failed to create Modbus connection instance")
            return False

        for key, value in db_data.items():
            print(f"[DEBUG] Attempting to write key: {key}, value: {value}")
            reg_info = MODBUS_REGISTRY.get(key)
            if not reg_info:
                print(f"[SKIPPED] Key '{key}' not found in MODBUS_REGISTRY")
                continue

            reg_type = reg_info.get("register_type")
            value_type = reg_info.get("value_type")
            address = reg_info.get("address")
            inverse = reg_info.get("inverse", False)

            print(f"[WRITE] Key: {key}, Addr: {address}, Type: {value_type}, Val: {value}")

            if reg_type == "holding_register":
                if value_type == "Float":
                    instance.write_float_register(address=address, value=float(value), inverse=inverse, unit=1)
                elif value_type == "U16":
                    instance.write_single_holding_registers(address=address, value=int(value), unit=1)
                elif value_type == "U32":
                    instance.write_U32_register(address=address, value=int(value), inverse=inverse, unit=1)
                elif value_type == "I32":
                    instance.write_I32_register(address=address, value=int(value), inverse=inverse, unit=1)
                elif value_type == "Double":
                    instance.write_double_register(address=address, value=float(value), inverse=inverse, unit=1)
                else:
                    print(f"[UNSUPPORTED] Value type '{value_type}' for key '{key}'")
            elif reg_type == "coil":
                instance.write_single_coil(address=address, value=bool(value), unit=1)
            else:
                print(f"[UNSUPPORTED] Register type '{reg_type}' for key '{key}'")

        return True
    except Exception as e:
        print(f"[ERROR] write_db_values_to_plc: {e}")
        return False

# Read_PLC_Values_to_DB
def read_plc_values_to_db(keys_to_read: list = None):
    global MODBUS_REGISTRY
    try:
        print("[DEBUG] Entering read_plc_values_to_db")

        instance = create_modbus_connection()
        if not instance:
            print("[ERROR] Failed to create Modbus connection instance")
            return None

        read_data = {}

        keys = keys_to_read if keys_to_read else MODBUS_REGISTRY.keys()

        for key in keys:
            reg_info = MODBUS_REGISTRY.get(key)
            if not reg_info:
                print(f"[SKIPPED] Key '{key}' not found in MODBUS_REGISTRY")
                continue

            reg_type = reg_info.get("register_type")
            value_type = reg_info.get("value_type")
            address = reg_info.get("address")
            inverse = reg_info.get("inverse", False)

            print(f"[READ] Key: {key}, Addr: {address}, Type: {value_type}")

            if reg_type == "holding_register":
                if value_type == "Float":
                    value = instance.read_float_register(address=address, inverse=inverse, unit=1)
                elif value_type == "U16":
                    value = instance.read_single_holding_registers(address=address, unit=1)
                elif value_type == "U32":
                    value = instance.read_U32_register(address=address, inverse=inverse, unit=1)
                elif value_type == "I32":
                    value = instance.read_I32_register(address=address, inverse=inverse, unit=1)
                elif value_type == "Double":
                    value = instance.read_double_register(address=address, inverse=inverse, unit=1)
                else:
                    print(f"[UNSUPPORTED] Value type '{value_type}' for key '{key}'")
                    continue
            elif reg_type == "coil":
                value = instance.read_single_coil(address=address, unit=1)
            else:
                print(f"[UNSUPPORTED] Register type '{reg_type}' for key '{key}'")
                continue

            read_data[key] = value

        print("[DEBUG] Completed reading PLC values")
        return read_data

    except Exception as e:
        print(f"[ERROR] read_plc_values_to_db: {e}")
        return None



# Abstract function to ready the list of alarm in the array defined as constant
def read_alarm() -> dict:
    alarm_lists = [
    "AGGREGATE CALIBRATION FAULT",
    "CEMENT CALIBRATION FAULT",
    "WATER CALIBRATION FAULT",
    "ADMIXTURE CALIBRATION FAULT",
    "AGGREGATE FILLING FAULT",
    "CEMENT FILLING FAULT",
    "WATER FILLING FAULT",
    "ADMIXTURE FILLING FAULT",
    "AGGREGATE DISCHARGE FAULT",
    "CEMENT DISCHARGE FAULT",
    "WATER DISCHARGE FAULT",
    "ADMIXTURE DISCHARGE FAULT",
    "AGGREGATE DEAD WEIGHT FAULT",
    "CEMENT DEAD WEIGHT FAULT",
    "WATER DEAD WEIGHT FAULT",
    "ADMIXTURE DEAD WEIGHT FAULT",
    "AGGREGATE BIN-1 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-1 TOLERANCE FAULT-- LT",
    "AGGREGATE BIN-2 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-2 TOLERANCE FAULT-- LT",
    "AGGREGATE BIN-3 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-3 TOLERANCE FAULT-- LT",
    "AGGREGATE BIN-4 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-4 TOLERANCE FAULT-- LT",
    "AGGREGATE BIN-5 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-5 TOLERANCE FAULT-- LT",
    "AGGREGATE BIN-6 TOLERANCE FAULT-- GT",
    "AGGREGATE BIN-6 TOLERANCE FAULT-- LT",
    "CEMENT TOLERANCE FAULT C-1 GT",
    "CEMENT TOLERANCE FAULT C-1 LT",
    "CEMENT TOLERANCE FAULT C-2 GT",
    "CEMENT TOLERANCE FAULT C-2 LT",
    "CEMENT TOLERANCE FAULT C-3 GT",
    "CEMENT TOLERANCE FAULT C-3 LT",
    "CEMENT TOLERANCE FAULT C-4 GT",
    "CEMENT TOLERANCE FAULT C-4 LT",
    "WATER TOLERANCE FAULT W-1 GT",
    "WATER TOLERANCE FAULT W-1 LT",
    "WATER TOLERANCE FAULT W-2 GT",
    "WATER TOLERANCE FAULT W-2 LT",
    "ADMIXTURE-1 TOLERANCE FAULT GT",
    "ADMIXTURE-1 TOLERANCE FAULT LT",
    "ADMIXTURE-2 TOLERANCE FAULT GT",
    "ADMIXTURE-2 TOLERANCE FAULT LT",
    "SKIP DOWN TO WAITING FAULT",
    "SKIP WAITING TO TOP FAULT",
    "CLOSE ON"
    ]

    data = read_data(names=alarm_lists,unit=1)
    return data

# Clean Alarm function clears the alarm with Alarm Key in the Modbus Address registry
def clear_alarm(alarm_key):
    global ACTIVE_ALARMS, MODBUS_REGISTRY
    try:
        # Safely remove from ACTIVE_ALARMS
        ACTIVE_ALARMS.discard(alarm_key)

        reg_details = MODBUS_REGISTRY.get(alarm_key)
        if not reg_details:
            print(f"⚠️ No Modbus registry entry found for alarm key: {alarm_key}")
            return False

        instance = create_modbus_connection()
        reg_type = reg_details.get("register_type")
        value_type = reg_details.get("value_type")
        reg_address = reg_details.get("address")
        inverse = reg_details.get("inverse")

        if reg_type == "holding_register":
            if value_type == "Float":
                instance.write_float_register(address=reg_address, value=0.0, inverse=inverse, unit=1)
            elif value_type == "U16":
                instance.write_single_holding_registers(address=reg_address, value=0, unit=1)
            elif value_type == "U32":
                instance.write_U32_register(address=reg_address, value=0, inverse=inverse, unit=1)
            elif value_type == "I32":
                instance.write_I32_register(address=reg_address, value=0, inverse=inverse, unit=1)
        elif reg_type == "coil":
            instance.write_single_coil(address=reg_address, value=False, unit=1)

        return True

    except Exception as e:
        print(f"❌ Error clearing alarm '{alarm_key}': {e}")
        return False

# Write Accept and Terminate functions write as pulse in the their address
def write_accept():
    global MODBUS_REGISTRY
    try:
        instance = create_modbus_connection()

        reg_details = MODBUS_REGISTRY.get("Alarm_ACCEPT")
        address = reg_details.get("address")
        instance.write_single_coil(address=address,value=True,unit=1)
        time.sleep(0.2)
        instance.write_single_coil(address=address,value=False,unit=1)
        return True
    except Exception as e:
        return False

def write_terminate():
    global MODBUS_REGISTRY
    try:
        instance = create_modbus_connection()

        reg_details = MODBUS_REGISTRY.get("Alarm_TERMINATE")
        address = reg_details.get("address")
        instance.write_single_coil(address=address,value=True,unit=1)
        time.sleep(0.2)
        instance.write_single_coil(address=address,value=False,unit=1)
        return True
    except Exception as e:
        print(e)
        return False