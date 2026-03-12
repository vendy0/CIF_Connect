from sqlalchemy import select, delete, insert, func, desc, case
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from database.models import User, Room, Message, Reaction, user_room, Report
from database.shemas import *
from fastapi import HTTPException
from datetime import datetime, timedelta
from security import get_password_hash, verify_password


# ==============================================================================
# UTILITAIRES
# ==============================================================================
def verify_user_room(db: Session, user_id: int, room_id: int):
	stmt = select(User).join(User.rooms).where(User.id == user_id, Room.id == room_id)
	if not db.execute(stmt).first():
		return False
	return True


# ==============================================================================
# GESTION DES UTILISATEURS
# ==============================================================================


def get_all_users(db: Session):
	stmt = select(User)
	return db.execute(stmt).scalars().all()


def get_user_by_email(db: Session, email: str):
	stmt = select(User).where(User.email == email)
	return db.execute(stmt).scalars().first()


def new_user(db: Session, user_data: RegisterRequest):
	try:
		# 1. Création de l'objet utilisateur
		# On transforme le Pydantic en dict
		user_dict = user_data.model_dump()

		# On Vérifie la longueur du mot de passe
		if len(user_dict["password"]) < 8:
			raise HTTPException(status_code=403, detail="Le mot de pass est trop court !")

		user_dict["password"] = get_password_hash(user_dict["password"])
		user = User(**user_dict)

		# 2. Ajout au Salon Général par défaut s'il existe
		stmt = select(Room).where(Room.name == "Salon Général")
		general_room = db.execute(stmt).scalars().first()

		if general_room:
			# SQLAlchemy gère la table de liaison automatiquement avec .append
			user.rooms.append(general_room)

		db.add(user)
		db.commit()
		db.refresh(user)  # Important pour avoir l'ID généré

		# 3. Message de bienvenue automatique (Optionnel)
		if general_room:
			try:
				welcome_msg = Message(
					content=f"{user.pseudo} a rejoint le chat !",
					author_id=user.id,
					room_id=general_room.id,
					message_type="join",
					author_display_name=user.pseudo,
				)
				db.add(welcome_msg)
				db.commit()
			except Exception as e:
				print(f"Erreur message bienvenue: {e}")
				# Pas grave si le message échoue, l'user est créé

		return user

	except IntegrityError as IntE:
		print(f"Erreur : {IntE}")
		db.rollback()
		raise HTTPException(status_code=400, detail="Email ou Pseudo déjà utilisé !")
	except HTTPException:
		raise
	except Exception as e:
		db.rollback()
		print(f"Erreur new_user: {e}")
		raise HTTPException(status_code=500, detail="Erreur serveur")


def update_user_pseudo(db: Session, user_id: int, new_pseudo: str):
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		return None

	if user.pseudo == new_pseudo:
		raise HTTPException(status_code=400, detail="Vous utilisez déjà ce pseudo !")

	user.pseudo = new_pseudo
	user.last_pseudo_update = func.current_timestamp()

	try:
		db.commit()
		db.refresh(user)
		return user
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=409, detail="Ce pseudo est déjà utilisé ! Choisissez un autre.")


# ==============================================================================
# GESTION DES SALONS (ROOMS)
# ==============================================================================


def get_all_rooms(db: Session):
	# Sous-requête pour la date du dernier message
	last_msg_sub = select(Message.room_id, func.max(Message.created_at).label("last_message_date")).group_by(Message.room_id).subquery()

	stmt = (
		select(Room)
		.options(joinedload(Room.creator))
		.outerjoin(last_msg_sub, Room.id == last_msg_sub.c.room_id)
		.order_by(
			# Critère 1 : Force l'ID 1 en haut (True > False en SQL)
			desc(Room.id == 1),
			# Critère 2 : Dernier message
			desc(last_msg_sub.c.last_message_date),
			# Critère 3 : Date de création du salon (fallback)
			desc(Room.created_at),
		)
	)

	return db.execute(stmt).scalars().all()


def get_user_rooms(db: Session, user_id: int):
	last_msg_sub = select(Message.room_id, func.max(Message.created_at).label("last_message_date")).group_by(Message.room_id).subquery()

	stmt = (
		select(Room)
		.options(joinedload(Room.creator))
		.join(user_room, Room.id == user_room.c.room_id)
		.outerjoin(last_msg_sub, Room.id == last_msg_sub.c.room_id)
		.where(user_room.c.user_id == user_id, Room.active == True)
		.order_by(
			desc(Room.id == 1),  # Toujours le salon 1 en premier
			desc(last_msg_sub.c.last_message_date),
			desc(Room.created_at),
		)
	)

	return db.execute(stmt).scalars().all()


def create_room(db: Session, room_data: CreateRoomSchema, creator_id: int):
	try:
		# 1. Création de la room
		# On exclut creator_id car on va le passer manuellement à la colonne created_by
		data = room_data.model_dump()

		# 3. Logique Toggle (Ajout/Suppression)
		existing_room = db.execute(select(Room).where(Room.access_key == data["access_key"])).scalar_one_or_none()

		if existing_room:
			db.rollback()
			raise HTTPException(status_code=409, detail="Réessayez dans un instant !")
			return

		# On crée l'objet Room
		new_room = Room(**data, created_by=creator_id)
		db.add(new_room)
		db.flush()  # Flush pour obtenir l'ID de la room avant commit final

		# 2. Ajouter le créateur comme membre de la room
		creator = db.query(User).filter(User.id == creator_id).first()
		if creator:
			new_room.users.append(creator)

		db.refresh(new_room)

		# Message système
		sys_msg = Message(
			content=f"{creator.pseudo} a créé le salon.",
			author_id=creator.id,
			room_id=new_room.id,
			message_type="join",
			author_display_name=creator.pseudo,
		)
		db.add(sys_msg)

		db.commit()
		return new_room

	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=409, detail="Ce nom de salon existe déjà !")

	except HTTPException:
		raise

	except Exception as e:
		db.rollback()
		print(f"Erreur create_room: {e}")
		raise HTTPException(status_code=500, detail="Erreur création salon")


def join_new_room(db: Session, join_data: JoinRoomSchema, user_id: int):
	# 1. Vérif Room et Clé
	stmt = select(Room).where(Room.access_key == join_data.access_key, Room.active == True)
	room = db.execute(stmt).scalars().first()

	if not room:
		raise HTTPException(status_code=404, detail="Salon introuvable")

	# 2. Vérif User
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="Utilisateur introuvable")

	# 3. Ajout membre
	if room not in user.rooms:
		user.rooms.append(room)

		# Message système
		sys_msg = Message(
			content=f"{user.pseudo} a rejoint le salon.",
			author_id=user.id,
			room_id=room.id,
			message_type="join",
			author_display_name=user.pseudo,
		)
		db.add(sys_msg)

		db.commit()
		db.refresh(room)

	return room


def quit_room_func(db: Session, user_id: int, room_id: int):
	# Récupère l'user (doit exister)
	user = db.execute(select(User).where(User.id == user_id)).scalar_one()

	# Récupère la room uniquement si l'user y est (protection)
	room = db.execute(select(Room).where(Room.id == room_id, Room.users.any(User.id == user_id))).scalar_one_or_none()

	if not room:
		raise HTTPException(status_code=404, detail="Vous ne faites pas partie de ce salon !")

	if room.id == 1 or room.name == "Salon Général":
		raise HTTPException(status_code=403, detail="Vous ne pouvez pas quitter le Salon Général !")
	# Retire l'utilisateur de la relation many-to-many
	room.users.remove(user)
	db.flush()  # applique la suppression dans la session / DB

	# Compte fiable des membres restants dans la room via la table d'association
	remaining = db.execute(select(func.count()).select_from(user_room).where(user_room.c.room_id == room_id)).scalar_one()

	# Si plus personne, on désactive la room
	if remaining == 0:
		room.active = False

	# Message système
	sys_msg = Message(
		content=f"{user.pseudo} a quitté le salon.",
		author_id=user.id,
		room_id=room.id,
		message_type="quit",
		author_display_name=user.pseudo,
	)
	db.add(sys_msg)

	db.commit()
	db.refresh(room)

	return room


# ==============================================================================
# GESTION DES SALONS (SUITE)
# ==============================================================================


def update_room(db: Session, room_id: int, user_id: int, update_data: RoomUpdateSchema):
	# 1. On récupère le salon
	stmt = select(Room).where(Room.id == room_id)
	room = db.execute(stmt).scalars().first()

	if not room:
		raise HTTPException(status_code=404, detail="Salon introuvable")

	# 2. Vérification des droits (Seul le créateur peut modifier)
	if room.created_by != user_id:
		raise HTTPException(status_code=403, detail="Seul le créateur peut modifier ce salon")

	# 3. Mise à jour dynamique des champs présents
	# exclude_unset=True permet de ne pas écraser avec None si le champ n'est pas envoyé
	for key, value in update_data.model_dump(exclude_unset=True).items():
		setattr(room, key, value)

	try:
		db.commit()
		db.refresh(room)
		return room
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=409, detail="Ce nom de salon est déjà pris.")


def delete_room_func(db: Session, room_id: int, user_id: int):
	# 1. On récupère le salon
	stmt = select(Room).where(Room.id == room_id)
	room = db.execute(stmt).scalars().first()

	if not room:
		raise HTTPException(status_code=404, detail="Salon introuvable")

	# 2. Vérification des droits
	if room.created_by != user_id:
		raise HTTPException(status_code=403, detail="Seul le créateur peut supprimer ce salon")

	# 3. Suppression
	try:
		room.active = False
		db.add(room)
		db.commit()
		return {"detail": "Salon supprimé avec succès", "room_id": room_id}
	except Exception as e:
		db.rollback()
		print(f"Erreur delete_room: {e}")
		raise HTTPException(status_code=500, detail="Erreur serveur lors de la suppression")


# ==============================================================================
# GESTION DES SIGNALEMENTS (REPORTS)
# ==============================================================================
def create_report(db: Session, report_data: ReportCreateSchema, reporter_id: int):
	"""
	Crée un signalement.
	"""
	# 1. Récupérer le message pour savoir QUI on signale
	stmt_msg = select(Message).where(Message.id == report_data.message_id)
	message = db.execute(stmt_msg).scalar_one_or_none()

	if not message:
		raise HTTPException(status_code=404, detail="Message signalé introuvable")

	# On ne peut pas signaler un message système
	if message.message_type in ["join", "quit"]:
		raise HTTPException(status_code=400, detail="Inutile de signaler un message système.")

	# 2. Création de l'objet Report
	# reported_id devient l'auteur du message
	new_report = Report(
		reporter_id=reporter_id,
		reported_id=message.author_id,
		message_id=report_data.message_id,
		raison=report_data.raison,
		status="pending",
	)

	try:
		db.add(new_report)
		db.commit()
		db.refresh(new_report)
		return new_report
	except Exception as e:
		db.rollback()
		print(f"Erreur create_report: {e}")
		raise HTTPException(status_code=500, detail="Erreur lors du signalement")


def get_all_reports(db: Session):
	"""Récupère tous les signalements avec les relations chargées (pour l'admin)."""
	stmt = (
		select(Report)
		.options(
			joinedload(Report.reporter),  # Charge qui a signalé
			joinedload(Report.reported),  # Charge qui est signalé
			joinedload(Report.message),  # Charge le message concerné
		)
		.order_by(Report.created_at.desc())
	)
	return db.execute(stmt).scalars().all()


def process_report_resolution(db: Session, report_id: int, resolution_data: ReportResolutionSchema):
	"""
	Résout un signalement et applique une sanction si demandée (Ban).
	"""
	# 1. Récupérer le signalement
	stmt = select(Report).where(Report.id == report_id)
	report = db.execute(stmt).scalar_one_or_none()

	if not report:
		raise HTTPException(status_code=404, detail="Signalement introuvable")

	# 2. Appliquer la sanction (Ban) si demandée
	if resolution_data.ban_user and report.reported_id:
		stmt_user = select(User).where(User.id == report.reported_id)
		user_to_ban = db.execute(stmt_user).scalar_one_or_none()

		if user_to_ban:
			user_to_ban.is_banned = True
			user_to_ban.ban_reason = resolution_data.ban_reason or report.raison

			# Gestion de la durée (Definitif ou Temporaire)
			if resolution_data.ban_duration_hours:
				user_to_ban.ban_expires_at = datetime.utcnow() + timedelta(hours=resolution_data.ban_duration_hours)
			else:
				user_to_ban.ban_expires_at = None  # Infini

	# 3. Mettre à jour le statut du report
	report.status = resolution_data.status

	try:
		db.commit()
		db.refresh(report)
		return report
	except Exception as e:
		db.rollback()
		print(f"Erreur resolution report: {e}")
		raise HTTPException(status_code=500, detail="Erreur lors de la résolution")


def update_report_status(db: Session, report_id: int, new_status: str):
	"""Met à jour le statut d'un signalement (ex: 'pending' -> 'resolved')."""
	stmt = select(Report).where(Report.id == report_id)
	report = db.execute(stmt).scalar_one_or_none()

	if not report:
		raise HTTPException(status_code=404, detail="Signalement introuvable")

	report.status = new_status

	try:
		db.commit()
		db.refresh(report)
		return report
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500, detail="Erreur mise à jour signalement")


# ==============================================================================
# GESTION DES MESSAGES
# ==============================================================================


def get_messages(db: Session, room_id: int, user_id: int):
	if not verify_user_room(db, user_id, room_id):
		raise HTTPException(status_code=401, detail="Vous ne faites pas partie de ce salon !")
	try:
		stmt = (
			select(Message)
			.options(
				joinedload(Message.author),  # Charge l'auteur
				selectinload(Message.reactions).joinedload(Reaction.user),  # Charge les réactions ET qui a réagi
				joinedload(Message.parent).joinedload(Message.author),  # Charge le message parent et son auteur (pour l'affichage "réponse à X")
			)
			.where(Message.room_id == room_id)
			.order_by(Message.created_at.asc())
			.limit(100)  # Limite pour éviter de charger trop d'un coup
		)
		messages = db.execute(stmt).scalars().all()
		return messages
	except Exception as e:
		print(f"Erreur get_messages: {e}")
		raise HTTPException(status_code=500, detail="Impossible de récupérer les messages")


def create_message(db: Session, room_id: int, message_data: MessageCreate, author_id, message_type="chat"):
	# 1. Pseudo actuel de l'auteur
	# user = db.query(User).filter(User.id == message_data.author_id).first()
	user = db.execute(select(User).where(User.id == author_id)).scalars().first()
	if not user:
		raise HTTPException(status_code=404, detail="Utilisateur introuvable")

	# 1.5 Vérifie si l'utilisateur est dans le salon
	if not verify_user_room(db, author_id, room_id):
		raise HTTPException(status_code=401, detail="Vous n'avez pas rejoint le salon !")

	try:
		new_msg = Message(
			content=message_data.content,
			author_id=author_id,
			room_id=room_id,
			parent_id=message_data.parent_id,
			message_type=message_type,
			author_display_name=user.pseudo,  # Snapshot du pseudo
		)
		db.add(new_msg)
		db.commit()
		db.refresh(new_msg)
		return new_msg
	except Exception as e:
		db.rollback()
		print(f"Erreur create_message: {e}")
		raise HTTPException(status_code=400, detail="Erreur lors de l'envoi")


def edit_message_func(db: Session, message_id: int, data: EditMessageSchema, user_id: int):
	"""
	Modifier un message.
	"""
	# 1. Récupérer le message
	stmt = select(Message).where(Message.id == message_id)
	message = db.execute(stmt).scalar_one_or_none()

	if not message:
		raise HTTPException(status_code=404, detail="Message introuvable")

	if (datetime.now() - timedelta(minutes=15)) > message.created_at:
		raise HTTPException(status_code=401, detail="Impossible de modifier un message après 15 minutes.")

	# 2. Protection des messages système
	if message.message_type in ["join", "quit"]:
		raise HTTPException(status_code=403, detail="Impossible de modifier un message système.")

	# 3. Vérification des droits (Auteur)
	user_stmt = select(User).where(User.id == user_id)
	user = db.execute(user_stmt).scalar_one_or_none()

	is_author = message.author_id == user_id

	if not is_author:
		raise HTTPException(status_code=403, detail="Vous n'avez pas le droit de supprimer ce message.")

	# 4. Suppression
	try:
		message.content = data.content
		message.modified = True

		db.commit()
		db.refresh(message)
		return message
	except Exception as e:
		db.rollback()
		print(f"Erreur edit_message: {e}")
		raise HTTPException(status_code=500, detail="Impossible de modifier le message")


def delete_message_func(db: Session, message_id: int, user_id: int):
	"""
	Supprime un message.
	"""
	# 1. Récupérer le message
	stmt = select(Message).where(Message.id == message_id)
	message = db.execute(stmt).scalar_one_or_none()

	if not message:
		raise HTTPException(status_code=404, detail="Message introuvable")

	if (datetime.now() - timedelta(days=3)) > message.created_at:
		raise HTTPException(status_code=403, detail="Impossible de supprimer un message envoyé depuis plus de 3 jours.")

	# 2. Protection des messages système
	if message.message_type in ["join", "quit"]:
		raise HTTPException(status_code=403, detail="Impossible de supprimer un message système.")

	# 3. Vérification des droits (Auteur ou Admin)
	user_stmt = select(User).where(User.id == user_id)
	user = db.execute(user_stmt).scalar_one_or_none()

	is_admin = (user.role == "admin") if user else False
	is_author = message.author_id == user_id

	if not (is_author or is_admin):
		raise HTTPException(status_code=403, detail="Vous n'avez pas le droit de supprimer ce message.")

	# 4. Suppression
	try:
		message.message_type = "delete"
		db.add(message)
		db.commit()
		return message
	except Exception as e:
		db.rollback()
		print(f"Erreur delete_message: {e}")
		raise HTTPException(status_code=500, detail="Impossible de supprimer le message")


# ==============================================================================
# GESTION DES RÉACTIONS
# ==============================================================================
def reagir(db: Session, message_id: int, reaction_data: ReactionCreateSchema, user_id):
	"""
	Ajoute ou supprime une réaction.
	"""
	# 1. Vérif du message
	stmt_msg = select(Message).where(Message.id == message_id)
	message = db.execute(stmt_msg).scalar_one_or_none()

	if not message:
		raise HTTPException(status_code=404, detail="Message introuvable")

	# 2. Protection : Pas de réaction sur les messages système
	if message.message_type in ["join", "quit"]:
		raise HTTPException(status_code=400, detail="On ne peut pas réagir aux messages système.")

	# 3. Logique Toggle (Ajout/Suppression)
	existing_reaction = db.execute(
		select(Reaction).where(
			Reaction.user_id == user_id,
			Reaction.message_id == message_id,
		)
	).scalar_one_or_none()

	if existing_reaction:
		db.delete(existing_reaction)
		db.commit()
		# On renvoie un objet vide ou simulé pour dire "supprimé" au front,
		# ou on gère ça via un code HTTP spécifique. Ici on retourne l'objet supprimé.
		# return existing_reaction

	# Sinon création
	reaction = Reaction(
		user_id=user_id,
		message_id=message_id,
		emoji=reaction_data.emoji,
	)

	db.add(reaction)
	db.commit()
	db.refresh(reaction)
	return reaction


def dereagir(db: Session, user_id: int, reaction_id: int):
	# 1. On récupère la réaction
	reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()

	if not reaction:
		raise HTTPException(status_code=404, detail="Réaction introuvable")

	if reaction.user_id != user_id:
		raise HTTPException(status_code=403, detail="Ce n'est pas votre réaction")

	try:
		# 2. Suppression
		db.delete(reaction)
		db.commit()

		# 3. Retourne un message simple (l'objet n'existe plus)
		return {"detail": "Réaction supprimée", "reaction_id": reaction_id}

	except Exception as e:
		db.rollback()
		print(f"Erreur suppression réaction: {e}")
		raise HTTPException(status_code=500, detail="Erreur serveur")
