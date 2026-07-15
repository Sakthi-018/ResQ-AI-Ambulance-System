from app.websocket.manager import manager


async def notify_driver(message: str):
    await manager.broadcast({
        "type": "notification",
        "message": message
    })


async def broadcast_location(
    ambulance_id: int,
    latitude: float,
    longitude: float
):
    await manager.broadcast({
        "type": "location",
        "ambulance_id": ambulance_id,
        "latitude": latitude,
        "longitude": longitude
    })

async def broadcast_status(
    emergency_id: int,
    status: str
):
    await manager.broadcast({
        "type": "status",
        "emergency_id": emergency_id,
        "status": status
    })