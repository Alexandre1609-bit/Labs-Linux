import signal
import time
import os

def handle_sigterm(signum, frame):
    print("SIGTERM reçu : nettoyage en cours...", flush=True)
    time.sleep(10)
    print("Nettoyage terminé.", flush=True)
    exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

print(f"PID : {os.getpid()}", flush=True)

while True:
    time.sleep(1)