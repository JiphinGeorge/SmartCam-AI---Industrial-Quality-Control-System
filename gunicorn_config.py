import multiprocessing

# Bind to 0.0.0.0:5000 inside the container
bind = "0.0.0.0:5000"

# Use gevent workers for WebSocket (SocketIO) support
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"

# Workers calculation
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Timeouts
timeout = 120
keepalive = 5
