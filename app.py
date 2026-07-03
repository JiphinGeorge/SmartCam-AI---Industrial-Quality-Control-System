from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    from app.services.database import DatabaseService
    DatabaseService.initialize()
    # Run with eventlet/gevent if installed, otherwise uses standard threading for SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
