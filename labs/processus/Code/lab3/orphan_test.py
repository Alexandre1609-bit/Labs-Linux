import os
import time

pid = os.fork()

if pid == 0:
    print(
        f"Enfant : PID={os.getpid()}, "
        f"PPID initial={os.getppid()}",
        flush=True
    )

    time.sleep(60)

    print(
        f"Enfant : nouveau PPID={os.getppid()}",
        flush=True
    )

    time.sleep(30)
    os._exit(0)

else:
    print(f"Parent : PID={os.getpid()}", flush=True)
    print(f"Enfant : PID={pid}", flush=True)
    time.sleep(60)