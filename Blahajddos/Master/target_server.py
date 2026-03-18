import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime
import os

# Set console text to Light Blue (Color 01)
os.system('color 01')

app = FastAPI()

# Counter to track incoming beams
request_stats = {"hits": 0, "last_beam": "None"}

@app.get("/")
async def root(request: Request):
    request_stats["hits"] += 1
    request_stats["last_beam"] = datetime.now().strftime("%H:%M:%S")
    
    # Print status to console whenever a beam hits
    print(f"[#] REQUEST RECEIVED | Total: {request_stats['hits']} | Time: {request_stats['last_beam']}")
    
    return {
        "status": "online", 
        "total_hits": request_stats["hits"],
        "message": "Blahaj Server Standing By"
    }

# This endpoint handles the 'HEAD' method specifically if you chose it
@app.head("/")
async def root_head():
    request_stats["hits"] += 1
    return None

if __name__ == "__main__":
    print("--- TEST SERVER ---")
    print("Target Address: http://127.0.0.1:8000")
    print("--------------------------------------")
    # Bind to 0.0.0.0 so other devices on your Wi-Fi can see it
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")