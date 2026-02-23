import asyncio
import websockets

async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("Who are you ?")
        response = await websocket.recv()
        print("Réponse du serveur :", response)

asyncio.run(main())
