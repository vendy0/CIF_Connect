from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# --- Schémas Pydantic ---
class UserMinimalSchema(BaseModel):
	id: int
	pseudo: Optional[str] = None

	class Config:
		from_attributes = True


class UserSchema(BaseModel):
	id: int
	email: str
	pseudo: str
	role: str
	is_banned: bool
	created_at: datetime
	last_pseudo_update: datetime

	class Config:
		from_attributes = True


class RoomSchema(BaseModel):
	id: int
	name: str
	description: str
	icon: str
	created_at: datetime
	creator: Optional[UserMinimalSchema]
	messages: List["MessageSchema"] = []

	class Config:
		from_attributes = True


class CreateRoomSchema(BaseModel):
	name: str
	description: str
	icon: str
	access_key: str
	creator: UserMinimalSchema

	class Config:
		from_attributes = True


class JoinRoomSchema(BaseModel):
	user_id: int
	room_id: int
	access_key: str

	class Config:
		from_attributes = True


class LoginRequest(BaseModel):
	email: str
	password: str

	class Config:
		from_attributes = True


class RegisterRequest(BaseModel):
	email: str
	password: str
	pseudo: str
	role: str | None = "eleve"

	class Config:
		from_attributes = True


class PseudoUpdateRequest(BaseModel):
	new_pseudo: str


class ReactionSchema(BaseModel):
	id: int
	user_id: int
	message_id: int
	emoji: str
	created_at: datetime

	user: UserMinimalSchema

	class Config:
		from_attributes = True


class MessageSchema(BaseModel):
	id: int
	author_display_name: str
	content: str
	message_type: str
	created_at: datetime
	# room_id suffit souvent, mais tu peux mettre RoomSchema si besoin
	room_id: int
	parent: Optional["MessageSchema"] = None

	author: UserMinimalSchema

	reactions: List[ReactionSchema] = []

	class Config:
		from_attributes = True


class MessageCreate(BaseModel):
	content: str
	author_id: int
	parent_id: Optional[int] = None
	# Pour les réponses


class ReactionCreateSchema(BaseModel):
	user_id: int
	emoji: str


class ReactionReturnSchema(BaseModel):
	id: int
	emoji: str
	message: MessageCreate
