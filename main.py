import sys
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app, async_mode="gevent")

sessions = {}

@app.route('/')
def app_index():
    return render_template('index.html')

@app.route('/push/<room>', methods=['POST'])
def app_push(room=None):
  print("%s %s" %(room, request.get_json()), file=sys.stderr)
  content = request.get_json().copy()
  if request.is_json and 'message' in content:
    msg = content['message']
    
    print("PUSHED: to %s" % msg, file=sys.stderr)
    socketio.emit('output', msg, room=room, namespace='/notification')

    return jsonify({'status': 'OK'}), 200
  else: 
    return jsonify({
      'error': 'Must push json formated data and message!'
    }), 400

@socketio.on('subscribe', namespace='/notification')
def subscribe(payload):
  print(payload, file=sys.stderr)
  room = payload['room']
  join_room(room)
  
@socketio.on('unsubscribe', namespace='/notification')
def unsubscribe(payload):
  print(payload, file=sys.stderr)
  room = payload['room']
  socketio.leave_room(room)

@socketio.on('push', namespace='/notification')
def push(payload):
  print(payload, file=sys.stderr)
  room = payload['room']
  msg = payload['message']
  socketio.emit('output', msg, room=room, namespace='/notification')
  

if __name__ == '__main__':
    socketio.run(app)
