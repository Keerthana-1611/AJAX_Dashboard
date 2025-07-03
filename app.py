from flask import Flask
from Blueprints.frontend_routes import frontend  
from Blueprints.plc_communication_routes import plc_communication
from Blueprints.socket_routes import socket_communications,socketio
from db_handler import setup_database_and_tables
from modbus_handler import load_modbus_registry,start_thread
from db_backup_restore import backup_database,restore_database
from flask_cors import CORS
import os

import sys
import pystray
from PIL import Image
from threading import Thread
import webbrowser
import time


BASE_PATH = None

if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running as script or unpacked
    BASE_PATH = os.getcwd()

ICON_PATH = os.path.join(BASE_PATH,"logo","Ajax-Backend-logo.ico")
icon = None

def run_tray():
    global icon
    if icon is None:
        image = Image.open(ICON_PATH)
        menu = pystray.Menu(
            pystray.MenuItem("Open Ajax Editor", open_app),
            pystray.MenuItem("Exit", stop_app)
        )
        icon = pystray.Icon("Ajax", image, "Ajax RMC", menu)
        icon.run()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if icon:
            icon.stop()

def create_tray():
    tray = Thread(target=run_tray) 
    tray.daemon = True
    tray.start()

# Function to stop the app (optional)
def stop_app(icon, item):
    icon.stop()
    os._exit(0)

# Open browser
def open_app(icon, item):
    webbrowser.open("http://127.0.0.1:5000/frontend")
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ajax@backend'
CORS(app)

# Register blueprint with prefix (optional)
app.register_blueprint(frontend, url_prefix='/frontend')
app.register_blueprint(plc_communication, url_prefix='/plc_communication')
app.register_blueprint(socket_communications, url_prefix='/socket_communications')


if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        create_tray()
        load_modbus_registry()
        start_thread()
        # backup_database()
    # setup_database_and_tables()  # If needed
    socketio.init_app(app=app, cors_allowed_origins="*")
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
