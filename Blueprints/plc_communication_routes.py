from flask import Blueprint, request, jsonify
from modbus_handler import create_modbus_connection,LOADCELL_REGISTER_MAP
from DAQ.Converstion import *
import os
import sys

if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running as script or unpacked
    BASE_PATH = os.getcwd()


plc_communication = Blueprint('plc_communication', __name__)

# ------------------------ Holding Registers ------------------------

# Single Read Holding Registers
@plc_communication.route('/read_single_holding', methods=['POST'])
def read_single_holding():
    data = request.get_json()
    address = data.get('address')

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        value = modbus.read_holding_registers(address, count=1)[0]
        
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Single Write Holding Registers
@plc_communication.route('/write_single_holding', methods=['POST'])
def write_single_holding():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        modbus.write_single_holding_registers(address, value)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Multiple Read Holding Registers
@plc_communication.route('/read_multiple_holding', methods=['POST'])
def read_multiple_holding():
    data = request.get_json()
    address = data.get('address')
    count = data.get('count', 1)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        values = modbus.read_holding_registers(address, count)
        
        return jsonify({'value': values, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Multiple Write Holding Registers
@plc_communication.route('/write_multiple_holding', methods=['POST'])
def write_multiple_holding():
    data = request.get_json()
    address = data.get('address')
    values = data.get('value')

    if address is None or not isinstance(values, list):
        return jsonify({'error': 'Missing address or value list', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        modbus.write_multiple_holding_registers(address, values)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# ------------------------ Coils ------------------------

# Single Read Coild Register
@plc_communication.route('/read_single_coil', methods=['POST'])
def read_single_coil():
    data = request.get_json()
    address = data.get('address')

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        value = modbus.read_coils(address, 1)[0]
        
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Single Write Coild Register
@plc_communication.route('/write_single_coil', methods=['POST'])
def write_single_coil():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        modbus.write_single_coil(address, bool(value))
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Multiple Read Coild Registers
@plc_communication.route('/read_multiple_coil', methods=['POST'])
def read_multiple_coil():
    data = request.get_json()
    address = data.get('address')
    count = data.get('count', 1)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        values = modbus.read_coils(address, count)
        
        return jsonify({'value': values, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Multiple Write Coild Registers
@plc_communication.route('/write_multiple_coil', methods=['POST'])
def write_multiple_coil():
    data = request.get_json()
    address = data.get('address')
    values = data.get('value')

    if address is None or not isinstance(values, list):
        return jsonify({'error': 'Missing address or value list', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        modbus.write_multi_coil(address, [bool(v) for v in values])
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ---------- FLOAT32 ----------
@plc_communication.route('/read_float32', methods=['POST'])
def read_float32():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 2)
        
        value = to_float32(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@plc_communication.route('/write_float32', methods=['POST'])
def write_float32():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_float32(float(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ---------- DOUBLE64 ----------
@plc_communication.route('/read_double64', methods=['POST'])
def read_double64():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 4)
        
        value = to_double64(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@plc_communication.route('/write_double64', methods=['POST'])
def write_double64():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_double64(float(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ---------- LONG64 ----------
@plc_communication.route('/read_long64', methods=['POST'])
def read_long64():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 4)
        
        value = to_long64(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@plc_communication.route('/write_long64', methods=['POST'])
def write_long64():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_long64(int(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ---------- ULONG64 ----------
@plc_communication.route('/read_ulong64', methods=['POST'])
def read_ulong64():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 4)
        
        value = to_ulong64(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@plc_communication.route('/write_ulong64', methods=['POST'])
def write_ulong64():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_ulong64(int(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ----------- INT32 -----------
@plc_communication.route('/read_int32', methods=['POST'])
def read_int32():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 2)
        
        value = to_int32(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@plc_communication.route('/write_int32', methods=['POST'])
def write_int32():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_int32(int(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# ----------- UINT32 -----------
@plc_communication.route('/read_uint32', methods=['POST'])
def read_uint32():
    data = request.get_json()
    address = data.get('address')
    inverse = data.get('inverse', True)

    if address is None:
        return jsonify({'error': 'Missing address', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(address, 2)
        
        value = to_uint32(regs, 0, inverse)
        return jsonify({'value': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@plc_communication.route('/write_uint32', methods=['POST'])
def write_uint32():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    inverse = data.get('inverse', True)

    if address is None or value is None:
        return jsonify({'error': 'Missing address or value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_uint32(int(value), inverse)
        modbus.write_multiple_holding_registers(address, words)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# Does the tare option for the load cell
@plc_communication.route('/tare_load', methods=['POST'])
def tare_load():
    data = request.get_json()
    if not data or 'loadcell_name' not in data:
        return jsonify({'error': 'Missing loadcell_name','success': False}), 400

    loadcell_name = data['loadcell_name']
    if loadcell_name not in LOADCELL_REGISTER_MAP:
        return jsonify({'error': 'Invalid loadcell_name','success': False}), 400

    register_address = LOADCELL_REGISTER_MAP[loadcell_name]
    modbus = None
    try:
        modbus = create_modbus_connection()
    
        #Modify the below code to the Tare operation based on the input required
        ##########################################################################################

        modbus.write_single_holding_registers(address=register_address, value=1, unit=1)

        ##########################################################################################


        

        return jsonify({'status': 'success', 'message': f'Tare command sent to {loadcell_name}'}), 200

    except Exception as e:
        return jsonify({'error': str(e),'success':False}), 500

# -------- MIX DESIGN at address 37768 --------

@plc_communication.route('/read_mix_design', methods=['GET'])
def read_mix_design():
    try:
        modbus = create_modbus_connection()
        regs = modbus.read_holding_registers(37768, 2)
        value = to_float32(regs, 0, True)  
        return jsonify({'mix_design': value, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@plc_communication.route('/write_mix_design', methods=['POST'])
def write_mix_design():
    data = request.get_json()
    value = data.get('value')
    inverse = data.get('inverse', True)

    if value is None:
        return jsonify({'error': 'Missing value', 'success': False}), 400

    try:
        modbus = create_modbus_connection()
        words = from_float32(float(value), inverse)
        modbus.write_multiple_holding_registers(37768, words)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500
