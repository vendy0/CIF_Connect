import asyncio
import websockets

# -----------------------------
# Serveur WebSocket
# -----------------------------
async def echo_server(ws):
    """
    Serveur simple qui renvoie tout message reçu à l'expéditeur
    """
    try:
        async for message in ws:
            print(f"[Serveur] Message reçu : {message}")
            await ws.send(f"Echo: {message}")
    except websockets.ConnectionClosedOK:
        print("[Serveur] Connexion fermée normalement")
    except Exception as e:
        print(f"[Serveur] Erreur : {e}")


# -----------------------------
# Client WebSocket
# -----------------------------
async def client(name, messages):
    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            for msg in messages:
                print(f"[{name}] Envoi : {msg}")
                await ws.send(msg)
                response = await ws.recv()
                print(f"[{name}] Réponse du serveur : {response}")
                await asyncio.sleep(0.5)
    except Exception as e:
        print(f"[{name}] Erreur client : {e}")


# -----------------------------
# Fonction principale
# -----------------------------
async def main():
    # Lancer le serveur
    server = await websockets.serve(echo_server, "localhost", 8765)
    print("[Main] Serveur WebSocket démarré sur ws://localhost:8765")

    # Messages clients
    messages_client1 = ["Salut", "Comment ça va ?", "Bye"]
    messages_client2 = ["Hello", "Ça va bien ?", "Au revoir"]

    # Donner un peu de temps au serveur pour démarrer
    await asyncio.sleep(0.1)

    # Lancer les clients
    await asyncio.gather(
        client("Client1", messages_client1),
        client("Client2", messages_client2)
    )

    # Fermer le serveur
    server.close()
    await server.wait_closed()
    print("[Main] Serveur arrêté")


# -----------------------------
# Entrée principale
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
