# database/interactions.py
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from database.models import User, Room, Message, Reaction
from database.shemas import *
from fastapi import HTTPException


# Récupérer trous les users
def get_all_users(db: Session):
	stmt = select(User)
	return db.execute(stmt).scalars().all()


# Récupérer un user par son Pseudo
def get_user_by_username(db: Session, pseudo: str):
	stmt = select(User).where(User.pseudo == pseudo)
	return db.execute(stmt).scalars().first()


# Récupérer un user par son Email (pour le Login)
def get_user_by_email(db: Session, email: str):
	stmt = select(User).where(User.email == email)
	return db.execute(stmt).scalars().first()


# Récupérer les salons d'un user
def get_user_rooms(db: Session, email: str):
	# On charge l'user ET ses rooms ET les créateurs des rooms
	stmt = (
		select(User)
		.options(joinedload(User.rooms).joinedload(Room.creator))
		.where(User.email == email)
	)
	user = db.execute(stmt).scalars().first()

	if not user:
		return []
	return user.rooms


def create_room(db: Session, room_data: RoomSchema, creator_id: int):
	# 1. On transforme le schéma en dict, mais on retire 'creator' car
	# en BDD on veut juste l'ID du créateur (created_by)
	data = room_data.model_dump(exclude={"creator"})

	# 2. On crée l'objet Room
	db_room = Room(**data, created_by=creator_id)

	db.add(db_room)
	db.commit()
	db.refresh(db_room)
	return db_room


# Récupérer TOUS les salons (pour la liste publique)
def get_all_rooms(db: Session):
	stmt = select(Room).options(joinedload(Room.creator))
	return db.execute(stmt).scalars().all()


# database/crud.py


def new_user(db: Session, user_data: UserSchema):
	# : RegisterRequest):  # Utilise le schéma Pydantic pour le type
	try:
		# 1. Création de l'objet utilisateur
		user = User(**user_data.model_dump())

		# 2. Récupération du "Salon Général"
		# On cherche le salon qui a été créé par défaut lors de l'initialisation
		stmt = select(Room).where(Room.name == "Salon Général")
		general_room = db.execute(stmt).scalars().first()

		# 3. Si le salon existe, on l'ajoute à l'utilisateur
		if general_room:
			user.rooms.append(general_room)

		db.add(user)
		db.commit()
		db.refresh(user)
		return user
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=400, detail="Email ou Pseudo déjà utilisé !")


def update_user_pseudo(db: Session, user_id: int, new_pseudo: str):
	# 1. On récupère l'utilisateur
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		return None

	# 2. On change le pseudo et on met à jour la date de modif
	if user.pseudo == new_pseudo:
		raise HTTPException(status_code=401, detail="Vous utilisez déjà ce pseudo !")
	user.pseudo = new_pseudo
	user.last_pseudo_update = func.current_timestamp()

	try:
		db.commit()
		db.refresh(user)
		return user
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=401, detail="Ce pseudo est déjà utilisé.")
	except:
		db.rollback()
		raise HTTPException(status_code=400, detail="Une erreur est survenu !")


def get_messages(db: Session, room_id: int):
	try:
		# On utilise .where() pour filtrer
		# On utilise selectinload pour charger les réactions (car c'est une liste)
		# On utilise joinedload pour l'auteur (un seul objet)
		stmt = (
			select(Message)
			.options(joinedload(Message.author), selectinload(Message.reactions))
			.where(Message.room_id == room_id)
			.order_by(Message.created_at.asc())  # Les plus vieux en premier pour le chat
			.limit(500)
		)
		messages = db.execute(stmt).scalars().all()
		if not messages:
			return []
		return messages
	except Exception as e:
		# Il est préférable de logger l'erreur réelle pour le dev
		print(f"Erreur get_messages: {e}")
		db.rollback()
		raise HTTPException(status_code=500, detail="Impossible de récupérer les messages")


def create_message(db: Session, room_id: int, message_data: MessageCreate):
	# 1. On récupère l'utilisateur pour avoir son pseudo actuel
	stmt = select(User).where(User.id == message_data.author_id)
	user = db.execute(stmt).scalars().first()
	if not user:
		raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

	# 2. On crée le message avec le pseudo "figé" (author_display_name)
	try:
		db_message = Message(
			author_display_name=user.pseudo,  # On enregistre le pseudo du moment
			content=message_data.content,
			author_id=message_data.author_id,
			room_id=room_id,
			parent_id=message_data.parent_id,
		)

		db.add(db_message)
		db.commit()
	except Exception as e:
		print(f"Erreur lors de l'envoi : {e}")
		db.rollback()
		raise HTTPException(status_code=400, detail="Erreur lors de l'envoi !")
	return db_message


def reagir(db, message_id: int, reaction_data: ReactionCreateSchema):
	reaction = Reaction(**reaction_data.model_dump())
	reaction.message_id = message_id
	db.add(reaction)
	db.commit()
	db.refresh(reaction)
	return reaction


def dereagir(db: Session, reaction_id: int):
	try:
		stmt = delete(Reaction).where(Reaction.id == reaction_id)
		db.execute(stmt)
		db.commit()
		return True
	except Exception as e:
		print(f"Erreur : {e}")
		return False
