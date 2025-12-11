#!/usr/bin/env python3
"""
Simple WebSocket chat server for local network
Run: python server.py
"""

import asyncio
import websockets
import json
from datetime import datetime
import sys

# Store connected clients
clients = set()
chat_history = []

async def handle_client(websocket, path):
    """Handle incoming WebSocket connections"""
    clients.add(websocket)
    print(f"New client connected. Total: {len(clients)}")
    
    # Send chat history to new client
    if chat_history:
        await websocket.send(json.dumps({
            "type": "history",
            "data": chat_history[-50:]  # Last 50 messages
        }))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "message":
                # Add timestamp and ID
                msg_data = {
                    "id": len(chat_history),
                    "user": data.get("user", "Anonymous"),
                    "text": data["text"],
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                chat_history.append(msg_data)
                print(f"Message from {msg_data['user']}: {msg_data['text']}")
                
                # Broadcast to all clients
                broadcast_msg = json.dumps({
                    "type": "message",
                    "data": msg_data
                })
                
                # Send to all connected clients
                await asyncio.gather(
                    *[client.send(broadcast_msg) for client in clients]
                )
                
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        clients.remove(websocket)
        print(f"Client removed. Total: {len(clients)}")

async def main():
    """Start WebSocket server"""
    port = 8765
    server = await websockets.serve(handle_client, "0.0.0.0", port)
    
    print(f"WebSocket chat server running on:")
    print(f"  ws://localhost:{port}")
    print(f"  ws://{get_ip()}:{port}")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("\nServer shutting down...")

def get_ip():
    """Get local IP address"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    # Check if websockets is installed
    try:
        import websockets
    except ImportError:
        print("Error: websockets module not installed.")
        print("Install it with: pip install websockets")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")