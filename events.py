from app import socketio

@socketio.on("connect")
def handle_connect():
    """handle clients(organizations and customers) connecting to server"""
    print('Client connected')