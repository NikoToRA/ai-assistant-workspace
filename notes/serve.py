#!/usr/bin/env python3
"""Simple livereload server for moriyama-proposal.html"""
import os, time, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8765
WATCH = os.path.join(os.path.dirname(__file__), 'moriyama-proposal.html')

clients = []
last_mtime = os.path.getmtime(WATCH)

def watcher():
    global last_mtime
    while True:
        time.sleep(0.5)
        try:
            m = os.path.getmtime(WATCH)
            if m != last_mtime:
                last_mtime = m
                for q in list(clients):
                    try: q.put('reload')
                    except: pass
        except: pass

import queue

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/livereload':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            q = queue.Queue()
            clients.append(q)
            try:
                while True:
                    try:
                        q.get(timeout=25)
                        self.wfile.write(b'data: reload\n\n')
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b': ping\n\n')
                        self.wfile.flush()
            except:
                clients.remove(q)
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        if '/livereload' not in (args[0] if args else ''):
            super().log_message(fmt, *args)

threading.Thread(target=watcher, daemon=True).start()
os.chdir(os.path.dirname(__file__))
print(f'http://localhost:{PORT}/moriyama-proposal.html')
HTTPServer(('', PORT), Handler).serve_forever()
