# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Import depuis tes fichiers
from database.models import SessionLocal
import database.crud as db_inter
from database.shemas import *

app = FastAPI(title="CIF Connect API")


# --- Dépendance BDD ---
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


# --- Endpoints ---

"""
===== Users =====
"""


@app.post("/login", response_model=UserSchema)
def login(data: LoginRequest, db: Session = Depends(get_db)):
	# On utilise la fonction de interactions.py
	user = db_inter.get_user_by_email(db, data.email)

	# Vérification basique (mdp en clair pour l'instant)
	if not user or user.password != data.password:
		raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

	if user.is_banned:
		raise HTTPException(status_code=403, detail="Ce compte est banni.")

	return user


@app.post("/register", response_model=UserSchema)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
	user = db_inter.new_user(db, data)
	return user


@app.get("/users", response_model=list[UserSchema])
def list_all_users(db: Session = Depends(get_db)):
	return db_inter.get_all_users(db)


@app.put("/users/{user_id}/pseudo")
def change_pseudo(user_id: int, data: PseudoUpdateRequest, db: Session = Depends(get_db)):
	user = db_inter.update_user_pseudo(db, user_id, data.new_pseudo)

	if not user:
		raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

	return {"detail": "Pseudo changé avec succès !", "new_pseudo": user.pseudo}


"""
===== Rooms =====
"""


@app.get("/rooms", response_model=list[RoomSchema])
def list_all_rooms(db: Session = Depends(get_db)):
	return db_inter.get_all_rooms(db)


@app.post("/rooms", response_model=RoomSchema)  # On utilise le pluriel pour les ressources
def create_a_room(data: CreateRoomSchema, db: Session = Depends(get_db)):
	# On passe l'ID du créateur directement depuis les données reçues
	return db_inter.create_room(db, data, creator_id=data.creator.id)


@app.get("/user/rooms", response_model=list[RoomSchema])
def get_my_rooms(email: str, db: Session = Depends(get_db)):
	rooms = db_inter.get_user_rooms(db, email)
	if rooms is None:
		return []  # Retourne une liste vide si pas de salons
	return rooms


"""
===== Messages =====
"""


@app.get("/room/{room_id}/messages", response_model=list[MessageSchema])
def read_messages(room_id: int, db: Session = Depends(get_db)):
	return db_inter.get_messages(db, room_id)


@app.post("/room/{room_id}/messages", response_model=MessageSchema)
def send_message(room_id: int, message_data: MessageCreate, db: Session = Depends(get_db)):
	return db_inter.create_message(db, room_id, message_data)


"""
===== Réactions =====
"""


@app.post("/message/{message_id}/reaction", response_model=ReactionSchema)
def send_reaction(
	message_id: int, reaction_data: ReactionCreateSchema, db: Session = Depends(get_db)
):
	return db_inter.reagir(db, message_id, reaction_data)


@app.delete("/message/{reaction_id}/reaction")
def remove_reaction(reaction_id: int, db: Session = Depends(get_db)):
	if db_inter.dereagir(db, reaction_id):
		return {"detail": "Réaction supprimé !"}
	else:
		return {"detail": "Erreur lors de la suppression !"}


"""
- Quand est ce qu'on passe les données dans la route ou dans un path variable ?
- Comment est ce qu'on organise le code généralement ? Les get avant, les post avant ou bien jsp ?
"""
