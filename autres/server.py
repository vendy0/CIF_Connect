import asyncio         # permet de faire des choses en "parallèle" sans bloquer le programme
import websockets      # bibliothèque pour gérer les WebSocket

# On crée une fonction qui gère chaque client
async def echo(websocket):
    # boucle infinie : on attend tous les messages du client
    async for message in websocket:
        print("Serveur a reçu :", message)       # on affiche le message
        await websocket.send(f"Echo: {message}") # on renvoie le même message au client

# Fonction principale du serveur
async def main():
    # "serve" = serveur, écoute les connexions sur localhost:8765
    async with websockets.serve(echo, "localhost", 8765):
        print("Serveur lancé, attente des clients...")
        await asyncio.Future()  # empêche le programme de s'arrêter

# Démarrage du serveur
asyncio.run(main())
