import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CITIES = [
    {"city": "New York", "lat": 40.7128, "lng": -74.0060},
    {"city": "London", "lat": 51.5074, "lng": -0.1278},
    {"city": "Tokyo", "lat": 35.6762, "lng": 139.6503},
    {"city": "Frankfurt", "lat": 50.1109, "lng": 8.6821},
    {"city": "Singapore", "lat": 1.3521, "lng": 103.8198},
    {"city": "São Paulo", "lat": -23.5505, "lng": -46.6333},
    {"city": "Sydney", "lat": -33.8688, "lng": 151.2093},
    {"city": "Mumbai", "lat": 19.0760, "lng": 72.8777},
]

ATTACK_TYPES = ["SYN Flood", "UDP Amplification", "HTTP DDoS", "DNS Flood"]

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/attacks")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            origin = random.choice(CITIES)
            target = random.choice(CITIES)
            while origin == target:
                target = random.choice(CITIES)
                
            attack_data = {
                "origin_city": origin["city"],
                "origin": [origin["lat"], origin["lng"]],
                "target_city": target["city"],
                "target": [target["lat"], target["lng"]],
                "type": random.choice(ATTACK_TYPES),
                "gbps": round(random.uniform(10.5, 450.0), 2)
            }
            
            await manager.broadcast(json.dumps(attack_data))
            await asyncio.sleep(random.uniform(0.5, 1.5))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
