# socket_routes.py
from flask import request, Blueprint
from threading import Lock
from modbus_handler import start_thread as plc_thread
from modbus_handler import ACTIVE_ALARMS,PREVIOUS_ALARM_STATE
from db_handler import insert_alarm
import random
import sys
import os
from flask_socketio import SocketIO
from modbus_handler import read_alarm

if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running as script or unpacked
    BASE_PATH = os.getcwd()


# Create Blueprint
socket_communications = Blueprint('socket_communications', __name__)
socketio = SocketIO(manage_session=False, cors_allowed_origins='*')

# Client tracking
client_threads = {}
thread_lock = Lock()

# ---------------- PLC SOCKET EVENTS ----------------

@socketio.on('connect', namespace='/plc_socket')
def handle_plc_connect():
    sid = request.sid
    print(f"✅ PLC Client connected: {sid}")
    client_threads[sid] = True
    socketio.start_background_task(plc_thread, sid)


@socketio.on('disconnect', namespace='/plc_socket')
def handle_plc_disconnect():
    sid = request.sid
    client_threads[sid] = False
    print(f"❌ PLC Client disconnected: {sid}")


# ---------------- RANDOM SOCKET EVENTS ----------------

@socketio.on('connect', namespace='/random_socket')
def handle_random_connect():
    sid = request.sid
    print(f"✅ Random Client connected: {sid}")
    client_threads[sid] = True
    socketio.start_background_task(random_thread, sid)


@socketio.on('disconnect', namespace='/random_socket')
def handle_random_disconnect():
    sid = request.sid
    client_threads[sid] = False
    print(f"❌ Random Client disconnected: {sid}")


# Background thread for /random_socket
def random_thread(sid):
    while client_threads.get(sid, False):
        value = random.randint(1, 100)
        # print(value)
        socketio.emit('random_value', {'value': value,
                                       "somthing": 23}, to=sid, namespace='/random_socket')
        socketio.sleep(0.0)
    print(f"🛑 Random thread stopped for {sid}")


# ---------------- ALARM SOCKET EVENTS ----------------

def process_alarms(data: dict, user: str = 'Unknown'):
    global ACTIVE_ALARMS, PREVIOUS_ALARM_STATE

    new_alarms = []

    for key, value in data.items():
        prev_value = PREVIOUS_ALARM_STATE.get(key, False)

        # Only insert if the value changes from False → True
        if value is True and prev_value is False:
            alarm_record = insert_alarm(key, user=user)
            new_alarms.append(alarm_record)
            ACTIVE_ALARMS.add(key)

        # Update the stored value
        PREVIOUS_ALARM_STATE[key] = value

    return new_alarms

def alarm_manager(sid, username):
    global ACTIVE_ALARMS
    while client_threads.get(sid, False):
        try:
            data = read_alarm()
            new_alarms= process_alarms(data, username)
            # new_alarms = []
        
            if new_alarms:
                socketio.emit('alarm_data', {
                    "new_alarms": new_alarms
                }, to=sid, namespace='/alarm_events')

            # socketio.sleep(0.2)
        except Exception as e:
            break
    
    print(f"🛑 Alarm thread stopped for {sid}")

@socketio.on('connect', namespace='/alarm_events')
def handle_plc_connect():
    username = request.args.get('username', 'Unknown')
    sid = request.sid
    print(f"✅ Alarm thread Client connected: {sid}")
    client_threads[sid] = True
    socketio.start_background_task(alarm_manager, sid,username)

@socketio.on('disconnect', namespace='/alarm_events')
def handle_plc_disconnect():
    sid = request.sid
    client_threads[sid] = False
    client_threads.pop(sid, None) 
    print(f"❌ Alarm thread Client disconnected: {sid}")