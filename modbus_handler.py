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
                    result[name] = instance.read_single_holding_register(address=address ,count=1, unit=unit)
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

def read_grouped_data(grouped_keys: dict, unit: int = 1) -> dict:
    """
    Reads Modbus values using grouped key structure and returns nested results:
    {
        "BIN1": { "GET_VALUE": ..., "SET_VALUE": ..., ... },
        "MIXER": { "STATUS": ..., "GATE_STATUS": ... },
        "AUTO_MANUAL_STATUS": ...
    }
    """
    global MODBUS_REGISTRY
    result = {}
    instance = MODBUS_INSTANCE

    for group, sub_keys in grouped_keys.items():
        # Handle flat keys like AUTO_MANUAL_STATUS
        if not sub_keys:
            reg_info = MODBUS_REGISTRY.get(group)
            if not reg_info:
                result[group] = "Not found"
                continue

            reg_type = reg_info["register_type"]
            value_type = reg_info["value_type"]
            address = reg_info["address"]
            inverse = reg_info["inverse"]

            try:
                if reg_type == "coil":
                    result[group] = instance.read_coils(address=address, count=1, unit=unit)[0]
                elif reg_type == "input_register":
                    result[group] = instance.read_input_registers(address=address, count=1, unit=unit)[0]
                else:
                    result[group] = 0
            except Exception:
                result[group] = False if reg_type == "coil" else 0
        else:
            result[group] = {}
            for sub_key in sub_keys:
                full_key = f"{group}_{sub_key}"
                reg_info = MODBUS_REGISTRY.get(full_key)

                if not reg_info:
                    result[group][sub_key] = "Not found"
                    continue

                reg_type = reg_info["register_type"]
                value_type = reg_info["value_type"]
                address = reg_info["address"]
                inverse = reg_info["inverse"]

                try:
                    if reg_type == "coil":
                        result[group][sub_key] = instance.read_coils(address=address, count=1, unit=unit)[0]
                    elif reg_type == "discrete_input":
                        result[group][sub_key] = instance.read_discrete_inputs(address=address, count=1, unit=unit)[0]
                    elif reg_type == "holding_register":
                        if value_type == 'U16':
                            result[group][sub_key] = instance.read_single_holding_register(address=address, count=1, unit=unit)
                        elif value_type == 'Float':
                            result[group][sub_key] = instance.read_float_register(address=address, inverse=inverse, unit=unit)
                        elif value_type == 'U32':
                            result[group][sub_key] = instance.read_U32_register(address=address, inverse=inverse, unit=unit)
                        elif value_type == 'I32':
                            result[group][sub_key] = instance.read_I32_register(address=address, inverse=inverse, unit=unit)
                        elif value_type == 'Double':
                            result[group][sub_key] = instance.read_double_register(address=address, inverse=inverse, unit=unit)
                    elif reg_type == "input_register":
                        result[group][sub_key] = instance.read_input_registers(address=address, count=1, unit=unit)[0]
                    else:
                        result[group][sub_key] = False if reg_type == "coil" else 0
                except Exception:
                    result[group][sub_key] = False if reg_type == "coil" else 0

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
                    value = instance.read_single_holding_register(address=address, unit=1)
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

# Reads alarm coild and send its as dictionart
def read_alarm_sequential(alarm_list : list,unit : int = 1 ) -> dict:
    global MODBUS_REGISTRY
    result = {}
    size = len(alarm_list)
    instance = create_modbus_connection()
    starting_reg_details = MODBUS_REGISTRY.get(alarm_list[0])
    if starting_reg_details:
        starting_reg_address = starting_reg_details.get("address")
        data = instance.read_coils(address=starting_reg_address,count=size,unit=1)

        for i in range(size):
            result[alarm_list[i]] = data[i]
            
        return result
    else:
        return {}


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

    # data = read_data(names=alarm_lists,unit=1)
    data = read_alarm_sequential(alarm_list=alarm_lists,unit=1)
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
    
def write_plc_mode(mode):
    global MODBUS_REGISTRY
    try:
        instance = create_modbus_connection()
        value = 0 if mode == 'auto' else 1
        reg_details = MODBUS_REGISTRY.get('PLC_MODE')
        address = reg_details.get('address')
        instance.write_single_coil(address=address,value=value,unit=1)
        return True
    except Exception as e:
        return False

def write_truck_present(truck_present):
    global MODBUS_REGISTRY
    try:
        instance = create_modbus_connection()
        reg_details = MODBUS_REGISTRY.get('TRUCK_PRESENT')
        address = reg_details.get('address')
        instance.write_single_coil(address=address,value=truck_present,unit=1)
        return True
    except Exception as e:
        return False
    
def write_plant_parameters(data):
    global MODBUS_REGISTRY
    try:
        instance = create_modbus_connection()
        keys_map = {
            "stabilization_time":"scale_stabilization_time",
            "belt_transfer_time":"belt_transfer_time",
            "belt_pre_running_time":"belt_pre_running_time",
            "top_to_waiting_time":"top_to_waiting_time",
            "mixer_delta_on_time": "mixer_delta_on_time",
            "max_mixer_capacity":"max_mixer_capacity",
            "min_mixer_capacity":"min_mixer_capacity"
        }

        for key,value in data.items():
            if not isinstance(value,dict):
                reg_info = MODBUS_REGISTRY.get(key)
                if reg_info:
                    reg_type = reg_info.get("register_type")
                    value_type = reg_info.get("value_type")
                    address = reg_info.get("address")
                    inverse = reg_info.get("inverse", False)

                    if reg_type == "holding_register":
                        if value_type == "Float":
                            instance.write_float_register(address=address,value=value, inverse=inverse, unit=1)
                        elif value_type == "U16":
                            instance.write_single_holding_registers(address=address,value=value, unit=1)
                        elif value_type == "U32":
                            instance.write_U32_register(address=address,value=value, inverse=inverse, unit=1)
                        elif value_type == "I32":
                            instance.write_I32_register(address=address,value=value, inverse=inverse, unit=1)
                        elif value_type == "Double":
                            instance.write_double_register(address=address,value=value, inverse=inverse, unit=1)
                    elif reg_type == "coil":
                        instance.write_single_coil(address=address,value=value,unit=1)

        return True
    except Exception as e:
        # print(e)
        return False
    

# Write Order_Config
def write_order_config_to_plc(name: str, total_bins: int, bins: list = None) -> bool:
    try:
        name = name.upper()

        name_to_modbus_key = {
            "AGGREGATE": "No_Bin_AGG",
            "CEMENT": "No_Bin_CEM",
            "ADMIXTURES": "No_Bin_ADMIX",
            "WATER": "No_Bin_WATER"
        }

        modbus_key = name_to_modbus_key.get(name)
        if not modbus_key:
            print(f"[SKIPPED] No PLC mapping found for name: {name}")
            return False

        plc_data = {modbus_key: total_bins}
        print(f"[PLC WRITE] {modbus_key} = {total_bins}")

        if bins and isinstance(bins, list):
            for bin in bins:
                bin_name = bin.get("bin_name")
                order_number = bin.get("order_number")

                if not bin_name or order_number is None:
                    print(f"[SKIPPED] Invalid bin entry: {bin}")
                    continue

                order_modbus_key = f"Order_Bin_{name} {bin_name}".upper()

                if order_modbus_key not in MODBUS_REGISTRY:
                    print(f"[SKIPPED] Modbus key not found: {order_modbus_key}")
                    continue

                plc_data[order_modbus_key] = order_number
                print(f"[PLC WRITE] {order_modbus_key} = {order_number}")

        return write_db_values_to_plc(plc_data)

    except Exception as e:
        print(f"[ERROR] write_total_bins_to_plc: {e}")
        return False


# PLC_Mode_Register
def update_plc_mode_registers(updates: list) -> bool:
    global MODBUS_REGISTRY
    sales_name_to_modbus_key = {
        "AGGREGATE BIN 1": "Mode_AGG BIN 1",
        "AGGREGATE BIN 2": "Mode_AGG BIN 2",
        "AGGREGATE BIN 3": "Mode_AGG BIN 3",
        "AGGREGATE BIN 4": "Mode_AGG BIN 4",
        "AGGREGATE BIN 5": "Mode_AGG BIN 5",
        "AGGREGATE BIN 6": "Mode_AGG BIN 6",
        "CEMENT BIN 1": "Mode_CEM BIN 1",
        "CEMENT BIN 2": "Mode_CEM BIN 2",
        "CEMENT BIN 3": "Mode_CEM BIN 3",
        "CEMENT BIN 4": "Mode_CEM BIN 4",
        "ADMIXTURES BIN 1": "Mode_ADMIX 1",
        "ADMIXTURES BIN 2": "Mode_ADMIX 2",
        "WATER BIN 1": "Mode_WATER 1",
        "WATER BIN 2": "Mode_WATER 2",
    }

    mode_type_to_value = {
        "AUTOINFLIGHT": 0,
        "FIXEDJOG": 1,
        "AUTOJOG": 2,
    }

    plc_data_to_write = {}

    for item in updates:
        sales_name = item.get("sales_name")
        mode_type = item.get("mode_type")
        correction_type = item.get("correction_type")

        if not sales_name or not mode_type or not correction_type:
            # print(f"[SKIPPED] Incomplete item: {item}")
            continue

        # Main mode write (e.g., Mode_AGG BIN 1)
        modbus_key = sales_name_to_modbus_key.get(sales_name)
        plc_value = mode_type_to_value.get(mode_type.upper())
        if modbus_key and plc_value is not None:
            plc_data_to_write[modbus_key] = plc_value
            # print(f"[PLC WRITE] {modbus_key} = {plc_value}")
        else:
            pass
            #print(f"[SKIPPED] Could not map {sales_name} or mode_type")

        # Additional write to Mean_Correction
        if "Mean_Correction" in MODBUS_REGISTRY:
            correction_value = 0 if correction_type.upper() == "BATCH" else 1
            plc_data_to_write["Mean_Correction"] = correction_value
            print(f"[PLC WRITE] Mean_Correction = {correction_value}")

    # Final call to Modbus writer
    if plc_data_to_write:
        return write_db_values_to_plc(plc_data_to_write)

    return True


def read_mimic_value() -> dict:
    grouped_keys = {
    "BIN1": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "BIN2": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "BIN3": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "BIN4": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "BIN5": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "BIN6": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    
    "CMT1": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "CMT2": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    "CMT3": ["GET_VALUE", "SET_VALUE", "ACTUAL_VALUE", "GATE_STATUS"],
    
    "WTR1": ["GET_VALUE", "SET_VALUE", "GATE_STATUS"],
    "WTR2": ["GET_VALUE", "SET_VALUE", "GATE_STATUS"],
    
    "ADM1": ["GET_VALUE", "SET_VALUE", "GATE_STATUS"],
    "ADM2": ["GET_VALUE", "SET_VALUE", "GATE_STATUS"],
    "ADM3": ["GET_VALUE", "SET_VALUE", "GATE_STATUS"],
    
    "MIXER": ["STATUS", "GATE_STATUS"],
    
    "AUTO_MANUAL_STATUS": [],
    "SKIP":["STATUS", "BOTTOM_STATUS", "WAITING_STATUS", "TOP_STATUS", "EMG_STATUS"]
    }
    return read_grouped_data(grouped_keys=grouped_keys, unit=1)
