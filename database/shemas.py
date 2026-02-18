from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ==============================================================================
# SCHÉMAS DE BASE (Partagés)
# ==============================================================================


class UserMinimalSchema(BaseModel):
	"""Utilisé pour afficher un user imbriqué (sans mdp/email)"""

	id: int
	pseudo: Optional[str] = None

	class Config:
		from_attributes = True


# ==============================================================================
# UTILISATEURS (USERS)
# ==============================================================================


class UserSchema(BaseModel):
	"""Schéma complet renvoyé au client"""

	id: int
	email: str
	pseudo: str
	role: str
	is_banned: bool
	created_at: datetime
	last_pseudo_update: datetime

	class Config:
		from_attributes = True


class LoginRequest(BaseModel):
	email: str
	password: str


class RegisterRequest(BaseModel):
	email: str
	password: str
	pseudo: str
	role: Optional[str] = None


class PseudoUpdateRequest(BaseModel):
	new_pseudo: str


# ==============================================================================
# MESSAGES & RÉACTIONS
# ==============================================================================


class ReactionCreateSchema(BaseModel):
	user_id: int
	emoji: str


class ReactionSchema(BaseModel):
	"""Lecture d'une réaction"""

	id: int
	user_id: int
	message_id: int
	emoji: str
	created_at: datetime
	# On inclut qui a réagi
	user: UserMinimalSchema

	class Config:
		from_attributes = True


class MessageCreate(BaseModel):
	"""Payload pour envoyer un message"""

	content: str
	author_id: int
	parent_id: Optional[int] = None


class MessageSchema(BaseModel):
	"""Lecture d'un message"""

	id: int
	author_display_name: str
	content: str
	message_type: str
	created_at: datetime
	room_id: int
	parent_id: Optional[int] = None  # ID du message parent si réponse

	author: UserMinimalSchema
	reactions: List[ReactionSchema] = []

	class Config:
		from_attributes = True


class ReactionReturnSchema(BaseModel):
	"""Retour spécifique après suppression d'une réaction"""

	detail: str
	reaction_id: int


class RoomReturnSchema(BaseModel):
	"""Retour spécifique après suppression d'un salon"""

	detail: str
	room_id: int


# ==============================================================================
# SALONS (ROOMS)
# ==============================================================================


class RoomSchema(BaseModel):
	"""Lecture d'un salon"""

	id: int
	name: str
	description: str
	icon: str
	created_at: datetime
	creator: Optional[UserMinimalSchema]  # Optional car le créateur peut avoir été supprimé
	# On n'inclut pas toujours les messages par défaut pour ne pas alourdir

	class Config:
		from_attributes = True


class CreateRoomSchema(BaseModel):
	"""Création d'un salon"""

	name: str
	description: str
	icon: str
	access_key: Optional[str] = None  # Optionnel si public
	creator_id: int  # On passe l'ID, pas tout l'objet user


class JoinRoomSchema(BaseModel):
	user_id: int
	room_id: int
	access_key: Optional[str] = None


# ... (à la suite des autres classes Room)


class RoomUpdateSchema(BaseModel):
	"""Payload pour modifier un salon (tous champs optionnels)"""

	name: Optional[str] = None
	description: Optional[str] = None
	icon: Optional[str] = None
	access_key: Optional[str] = None


# ==============================================================================
# SIGNALEMENTS (REPORTS)
# ==============================================================================


class ReportCreateSchema(BaseModel):
	"""
	Création d'un signalement.
	NOTE: On ne demande plus reported_id, le back-end le trouvera via le message_id.
	"""

	reporter_id: int
	message_id: int  # Obligatoire maintenant pour identifier l'auteur
	raison: str


class ReportResolutionSchema(BaseModel):
	"""
	Payload pour résoudre un signalement avec une action concrète.
	"""

	status: str  # ex: 'resolved', 'dismissed', 'warning_sent'

	# Options de bannissement (si l'admin décide de sévir)
	ban_user: bool = False
	ban_duration_hours: Optional[int] = None  # Si None et ban_user=True -> Ban définitif
	ban_reason: Optional[str] = None


class ReportSchema(BaseModel):
	"""Lecture d'un signalement (Vue Admin)"""

	id: int
	raison: str
	status: str
	created_at: datetime
	reporter_id: Optional[int]
	reported_id: Optional[int]
	message_id: Optional[int]

	class Config:
		from_attributes = True


# ... Garde ReportFullSchema tel quel ...


class ReportStatusUpdate(BaseModel):
	"""Pour qu'un admin change le statut d'un signalement"""

	status: str  # ex: 'resolved', 'dismissed'


class ReportFullSchema(ReportSchema):
	"""
	Vue complète d'un signalement pour l'admin.
	On inclut les infos minimales des personnes impliquées.
	"""

	reporter: Optional[UserMinimalSchema]
	reported: Optional[UserMinimalSchema]
	# On pourrait aussi inclure le contenu du message signalé si besoin

	class Config:
		from_attributes = True
