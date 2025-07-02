from webapp import app, socketio
from webapp.app import bp

app.register_blueprint(bp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
