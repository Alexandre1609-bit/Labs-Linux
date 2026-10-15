import os
import time

pid = os.fork()

if pid == 0:
    # Processus enfant
    print(f"Enfant : PID={os.getpid()}, fin immédiate.", flush=True)
    os._exit(0)

else:
    # Processus parent
    print(f"Parent : PID={os.getpid()}", flush=True)
    print(f"Enfant : PID={pid}", flush=True)
    print("Le parent attend 60 secondes sans récupérer le statut de l'enfant.", flush=True)
    time.sleep(60)