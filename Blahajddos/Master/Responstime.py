import asyncio
import httpx
import time
import os
import sys
from datetime import datetime

# --- CONFIGURATION ---
CHECK_INTERVAL = 1  # Updated to 1 second
TIMEOUT = 5.0      # Reduced timeout for faster reporting

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

async def monitor_site():
    clear_screen()
    print("\033[94m--- BLAHAJ REAL-TIME MONITOR ---\033[0m")
    
    try:
        target_url = input("Enter the Website URL (e.g., google.com): ").strip()
        if not target_url:
            print("No URL entered. Exiting.")
            return
            
        if not target_url.startswith("http"):
            target_url = "https://" + target_url

        print(f"\n[*] Monitoring: {target_url}")
        print(f"[*] Update Frequency: {CHECK_INTERVAL}s")
        print("-" * 60)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        # Optimized client for high-frequency polling
        async with httpx.AsyncClient(verify=True, headers=headers, follow_redirects=True) as client:
            while True:
                timestamp = datetime.now().strftime('%H:%M:%S')
                try:
                    start_time = time.perf_counter()
                    response = await client.get(target_url, timeout=TIMEOUT)
                    end_time = time.perf_counter()
                    
                    latency = round((end_time - start_time) * 1000, 2)
                    status = response.status_code
                    size = len(response.content)
                    
                    if status == 200:
                        color = "\033[92m" # Green
                    elif 300 <= status < 400:
                        color = "\033[94m" # Blue
                    else:
                        color = "\033[93m" # Yellow
                        
                    output = f"[{timestamp}] Status: {color}{status}\033[0m | Latency: {latency:>7}ms | Size: {size:>7}B"
                    print(output)
                    sys.stdout.flush()

                except httpx.ConnectTimeout:
                    print(f"[{timestamp}] \033[91mFAILED: Timeout\033[0m")
                except httpx.ConnectError:
                    print(f"[{timestamp}] \033[91mFAILED: DNS/Connection Error\033[0m")
                except Exception as e:
                    print(f"[{timestamp}] \033[91mERROR: {type(e).__name__}\033[0m")

                await asyncio.sleep(CHECK_INTERVAL)
                
    except EOFError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(monitor_site())
    except KeyboardInterrupt:
        print("\n[*] Monitor stopped.")