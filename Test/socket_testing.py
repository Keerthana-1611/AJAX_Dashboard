
from flask import Flask, request
from flask_socketio import SocketIO
import random
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

client_threads = {}  # Store thread flags per session ID

@app.route('/')
def index():
    return client_threads

# Background thread to emit random values
def background_thread(sid):
    while client_threads.get(sid, False):
        value = random.randint(1, 100)
        socketio.emit('random_value', {'value': value}, to=sid)
        print(value)
        socketio.sleep(2)
    print(f"Stopped thread for {sid}")

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    client_threads[sid] = True
    print(f"Client connected: {sid}")
    socketio.start_background_task(background_thread, sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    client_threads[sid] = False
    print(f"Client disconnected: {sid}")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)