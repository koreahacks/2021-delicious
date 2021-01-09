from SeMalZip_web import app, db
from flask_socketio import SocketIO

socketio = SocketIO(app)

if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run(host="127.0.0.1")
    socketio.run(app, debug=True)