import asyncio
import random


# 1. Simulation d'une tâche : Récupérer les messages du serveur CIF
async def fetch_messages():
	print("📡 Connexion au serveur de messages...")
	await asyncio.sleep(2)  # Simule la latence réseau
	messages = ["Salut !", "Quelqu'un a fini le DM ?", "Anonyme: Test"]
	print("✅ Messages récupérés !")
	return messages


# 2. Simulation d'une tâche : Vérifier l'identité (anonymat)
async def check_user_status(user_id):
	print(f"🔍 Vérification du statut pour l'utilisateur {user_id}...")
	await asyncio.sleep(1.5)
	print(f"✅ Utilisateur {user_id} autorisé (Anonyme).")
	return True


# 3. Simulation d'une tâche : Charger les images de profil
async def load_avatars():
	print("🖼️ Chargement des avatars...")
	await asyncio.sleep(1)
	print("✅ Avatars chargés !")
	return "Avatars_OK"


# FONCTION PRINCIPALE (L'orchestre)
async def main():
	print("--- DÉMARRAGE DE CIF CONNECT ---")

	# On lance les 3 tâches EN MÊME TEMPS 🚀
	# Au lieu de prendre 2 + 1.5 + 1 = 4.5 secondes...
	# Cela prendra seulement le temps de la tâche la plus longue (2s) !

	resultats = await asyncio.gather(
		fetch_messages(), check_user_status("Eleve_42"), load_avatars()
	)

	messages, status, avatars = resultats

	print("\n--- ÉCRAN DE CHAT PRÊT ---")
	print(f"Messages du jour : {messages}")


# Lancer la boucle d'événements
if __name__ == "__main__":
	asyncio.run(main())


from fastapi import FastAPI
import uvicorn  # Le moteur qui fait tourner FastAPI

# 1. On crée l'application
app = FastAPI()


# 2. On définit une "Route" (l'adresse où l'app mobile enverra les messages)
# On utilise @app.post car l'app "poste" une information au serveur.
@app.post("/envoi-message")
async def recevoir_message(pseudo: str, contenu: str):
	print(f"--- NOUVEAU MESSAGE REÇU ---")

	# Ici, on simule une petite attente (ex: vérification anti-spam)
	# C'est ici que le 'await' est crucial !
	print(f"Traitement du message de {pseudo}...")

	# Imaginons qu'on vérifie si le pseudo est banni dans le futur
	# await verifier_bannissement(pseudo)

	print(f"Message : {contenu}")

	return {"status": "Success", "info": "Le serveur du CIF a bien reçu ton message !"}


# 3. Lancement du serveur (sur ton PC pour le moment)
if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000)


from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Notre base de données temporaire (une simple liste Python)
db_messages = []


class Message(BaseModel):
	pseudo: str
	contenu: str


# ROUTE 1 : Récupérer tous les messages (GET)
@app.get("/messages", response_model=List[Message])
async def lire_messages():
	return db_messages


# ROUTE 2 : Envoyer un message (POST)
@app.post("/messages")
async def creer_message(nouveau_msg: Message):
	db_messages.append(nouveau_msg)
	return {"status": "Message ajouté avec succès !"}


import aiosqlite
from fastapi import FastAPI

app = FastAPI()
DB_FILE = "cif_connect.db"


async def init_db():
	async with aiosqlite.connect(DB_FILE) as db:
		# Création de la table des messages
		await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                contenu TEXT NOT NULL
            )
        """)
		await db.commit()


# On lance l'initialisation au démarrage du serveur
@app.on_event("startup")
async def startup():
	await init_db()


@app.post("/messages")
async def creer_message(msg: Message):
	async with aiosqlite.connect(DB_FILE) as db:
		# Insertion du message
		await db.execute(
			"INSERT INTO messages (pseudo, contenu) VALUES (?, ?)", (msg.pseudo, msg.contenido)
		)
		await db.commit()
	return {"status": "Enregistré dans SQLite !"}


@app.get("/messages")
async def lire_messages():
	async with aiosqlite.connect(DB_FILE) as db:
		async with db.execute("SELECT pseudo, contenu FROM messages") as cursor:
			rows = await cursor.fetchall()
			# On transforme les tuples en dictionnaires pour le JSON
			return [{"pseudo": r[0], "contenu": r[1]} for r in rows]


# Dans un fichier database.py (inspiré de ton connexion.py)
import aiosqlite


async def get_db():
	# On utilise 'async with' pour garantir une connexion propre
	async with aiosqlite.connect("cif_connect.db") as db:
		db.row_factory = aiosqlite.Row  # Pour accéder aux données par nom de colonne
		yield db  # 'yield' permet d'utiliser cette fonction comme une "dépendance"


import aiosqlite
from fastapi import FastAPI, Depends

app = FastAPI()


# 1. La "Fontaine" à connexion (Gestionnaire de ressource)
async def get_db():
	# 'async with' ouvre la porte du fichier .db
	async with aiosqlite.connect("interpam.db") as db:
		db.row_factory = aiosqlite.Row
		print("🔓 Connexion ouverte")

		yield db  # On "donne" la connexion à la route

		# Le code revient ICI une fois que la route a fini
		print("🔒 Connexion fermée automatiquement")


# 2. La Route qui utilise la connexion
@app.post("/envoyer")
async def envoyer_message(pseudo: str, texte: str, db=Depends(get_db)):
	# On utilise 'await' car l'écriture disque est lente
	await db.execute("INSERT INTO messages (pseudo, contenu) VALUES (?, ?)", (pseudo, texte))
	await db.commit()
	return {"info": "Message enregistré !"}


from database import DB_NAME  # On récupère le nom depuis ton fichier
import aiosqlite


async def init_db():
	async with aiosqlite.connect(DB_NAME) as db:
		# On crée la table si elle n'existe pas encore
		await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                contenu TEXT NOT NULL,
                date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
		await db.commit()
		print("✅ Base de données prête et table 'messages' vérifiée.")


@app.on_event("startup")
async def startup():
	await init_db()


from fastapi import FastAPI, Depends
from database import get_db
from pydantic import BaseModel

app = FastAPI()


class MessageSchema(BaseModel):
	pseudo: str
	contenu: str


@app.post("/envoyer")
async def envoyer_msg(data: MessageSchema, db=Depends(get_db)):
	# On insère les données de l'objet 'data' dans la DB
	await db.execute(
		"INSERT INTO messages (pseudo, contenu) VALUES (?, ?)", (data.pseudo, data.contenu)
	)
	await db.commit()  # On valide l'écriture
	return {"status": "success"}


# Je vais créer deux fichiers qui stockent ces adjectifs en json
import random

ADJECTIFS = ["Rapide", "Joyeux", "Invisible", "Savant", "Brave"]
ANIMAUX = ["Lion", "Aigle", "Dauphin", "Loup", "Hibou"]


def generer_pseudo():
	adj = random.choice(ADJECTIFS)
	ani = random.choice(ANIMAUX)
	numero = random.randint(10, 99)  # Un petit nombre pour l'unicité
	return f"{ani}-{adj}-{numero}"


@app.post("/connexion")
async def connexion_anonyme():
	pseudo_final = generer_pseudo()
	return {"pseudo": pseudo_final, "message": "Bienvenue sur InterPam !"}


async def obtenir_pseudo_unique(db):
	while True:
		# 1. On génère un pseudo au hasard
		pseudo_propose = generer_pseudo()

		# 2. On vérifie s'il est déjà pris dans la base
		async with db.execute(
			"SELECT 1 FROM messages WHERE pseudo = ?", (pseudo_propose,)
		) as cursor:
			existe = await cursor.fetchone()

			# 3. Si 'existe' est None, c'est que le pseudo est libre !
			if not existe:
				return pseudo_propose


await db.execute("""
    CREATE TABLE IF NOT EXISTS validations (
        email TEXT PRIMARY KEY,
        code TEXT NOT NULL,
        expire_at TIMESTAMP NOT NULL
    )
""")


from datetime import datetime, timedelta
import secrets


@app.post("/demander-code")
async def demander_code(email: str, db=Depends(get_db)):
	# 1. Vérifier si c'est un email du collège
	if not email.endswith("@cifamilia.fr"):  # Exemple de domaine
		return {"erreur": "Email non autorisé"}

	# 2. Générer un code à 6 chiffres sécurisé
	code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
	expiration = datetime.now() + timedelta(minutes=10)

	# 3. Stocker ou mettre à jour le code pour cet email
	await db.execute(
		"""
        INSERT INTO validations (email, code, expire_at) 
        VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET code=excluded.code, expire_at=excluded.expire_at
    """,
		(email, code, expiration),
	)

	await db.commit()
	# Ici, on enverrait normalement l'email. Pour l'instant, on le simule :
	print(f"📧 Email envoyé à {email} avec le code {code}")
	return {"status": "Code envoyé !"}

from fastapi import HTTPException

@app.post("/verifier-code")
async def verifier_code(email: str, code_entre: str, db = Depends(get_db)):
    # 1. Chercher les infos pour cet email
    async with db.execute(
        "SELECT code, expire_at FROM validations WHERE email = ?", 
        (email,)
    ) as cursor:
        resultat = await cursor.fetchone()

    # 2. Vérifications de sécurité
    if not resultat:
        raise HTTPException(status_code=404, detail="Aucun code demandé pour cet email")

    code_stocke = resultat["code"]
    expiration = datetime.fromisoformat(resultat["expire_at"])

    # 3. Comparaison du code et de l'heure
    if code_entre != code_stocke:
        raise HTTPException(status_code=400, detail="Code incorrect")
    
    if datetime.now() > expiration:
        raise HTTPException(status_code=400, detail="Code expiré (10 min écoulées)")

    # 4. Succès ! On peut maintenant générer le pseudo unique
    pseudo = await obtenir_pseudo_unique(db)
    return {"status": "valide", "pseudo": pseudo}


import flet as ft

def main(page: ft.Page):
    page.title = "CIF Connect - Stockage"
    
    # 1. Tentative de récupération du pseudo stocké
    pseudo_stocke = page.client_storage.get("user_pseudo")

    def enregistrer_pseudo(e):
        if champ_pseudo.value:
            # Sauvegarde physique dans le téléphone 📥
            page.client_storage.set("user_pseudo", champ_pseudo.value)
            label_info.value = f"Pseudo '{champ_pseudo.value}' enregistré !"
            page.update()

    def effacer_pseudo(e):
        # Supprimer la donnée du téléphone 🗑️
        page.client_storage.remove("user_pseudo")
        label_info.value = "Stockage vidé."
        page.update()

    # --- Interface Graphique ---
    champ_pseudo = ft.TextField(label="Ton Pseudo", value=pseudo_stocke if pseudo_stocke else "")
    label_info = ft.Text(f"Pseudo actuel en mémoire : {pseudo_stocke}")
    
    btn_save = ft.ElevatedButton("Sauvegarder localement", on_click=enregistrer_pseudo)
    btn_clear = ft.ElevatedButton("Effacer la mémoire", on_click=effacer_pseudo)

    page.add(
        ft.Text("Test du stockage local (InterPam)", size=20, weight="bold"),
        label_info,
        champ_pseudo,
        ft.Row([btn_save, btn_clear])
    )

ft.app(target=main)



import flet as ft

def main(page: ft.Page):
    # C'est ici qu'on configure notre "tableau blanc"
    page.title = "CIF Connect"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER # Centre le contenu
    
    # On crée un composant texte
    texte_bienvenue = ft.Text("Bienvenue sur InterPam !", size=30, color="blue")
    
    # On l'ajoute à la page
    page.add(texte_bienvenue)

# On lance l'application
ft.app(target=main)
