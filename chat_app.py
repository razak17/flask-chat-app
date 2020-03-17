from app import create_app
from flask_socketio import SocketIO, join_room, leave_room
from app.models import save_message
from datetime import datetime

app = create_app()
socketio = SocketIO(app)

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} in room {} said {}".format(data['username'], data['room'], data['message'] ))
    data['date_sent'] = datetime.utcnow().strftime("%b %d, %H:%M")
    save_message(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
