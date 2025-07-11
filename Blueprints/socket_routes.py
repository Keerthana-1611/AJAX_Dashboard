# socket_routes.py
from flask import request, Blueprint
from threading import Lock
from modbus_handler import start_thread as plc_thread
from modbus_handler import MODBUS_REGISTRY
import random
import sys
import os
from flask_socketio import SocketIO


if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running as script or unpacked
    BASE_PATH = os.getcwd()


# Create Blueprint
socket_communications = Blueprint('socket_communications', __name__)
socketio = SocketIO()

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
        print(value)
        socketio.emit('random_value', {'value': value,
                                       "somthing": 23}, to=sid, namespace='/random_socket')
        socketio.sleep(0.0)
    print(f"🛑 Random thread stopped for {sid}")
