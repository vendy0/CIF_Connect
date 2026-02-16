# database/models.py (anciennement initialisation.py)
from sqlalchemy import (
	create_engine,
	Column,
	Integer,
	String,
	Boolean,
	DateTime,
	ForeignKey,
	Table,
	func,
	event,
	Index,
	UniqueConstraint,
)

from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from flet import Icons

DB_FILENAME = "cif_connect_demo.db"

# --- 1. Moteur & Session ---
# echo=False en prod pour ne pas polluer les logs, True en dev pour debug
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False, future=True)


# Indispensable pour SQLite : active la vérification des clés étrangères
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()


SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

# --- 2. Tables de liaison ---
user_room = Table(
	"user_room",
	Base.metadata,
	Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
	Column("room_id", Integer, ForeignKey("rooms.id"), primary_key=True),
)

# --- 3. Modèles (Classes) ---


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	email = Column(
		String, nullable=False, unique=True, index=True
	)  # Index pour recherche rapide au login
	password = Column(String, nullable=False)
	pseudo = Column(
		String, nullable=False, unique=True, index=True
	)  # Index pour recherche de profil
	last_pseudo_update = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
	role = Column(String, default="eleve", nullable=False)
	is_banned = Column(Boolean, default=False, nullable=False)
	ban_expires_at = Column(DateTime)
	ban_reason = Column(String)
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	# Relations
	created_rooms = relationship("Room", back_populates="creator")
	rooms = relationship("Room", secondary=user_room, back_populates="users")
	authored_messages = relationship(
		"Message", back_populates="author", cascade="all, delete-orphan"
	)
	reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")

	reports_sent = relationship(
		"Report",
		back_populates="reporter",
		foreign_keys="Report.reporter_id",
		cascade="all, delete-orphan",
	)
	reports_received = relationship(
		"Report",
		back_populates="reported",
		foreign_keys="Report.reported_id",
		cascade="all, delete-orphan",
	)


class Room(Base):
	__tablename__ = "rooms"

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False, unique=True)
	description = Column(String, nullable=False)
	icon = Column(String, default=Icons.CHAT_BUBBLE_ROUNDED)
	access_key = Column(String)  # Clé pour rejoindre un salon privé
	created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	# Relations
	creator = relationship("User", back_populates="created_rooms")
	users = relationship("User", secondary=user_room, back_populates="rooms")
	messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True)
	author_display_name = Column(String, nullable=False)
	# Copie du pseudo au moment de l'envoi (historique)
	content = Column(String, nullable=False)
	message_type = Column(String, default="chat_message")
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
	author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	parent_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)

	__table_args__ = (
		Index("ix_messages_room_id", "room_id"),
		Index("ix_messages_parent_id", "parent_id"),
	)
	# Relations
	author = relationship("User", back_populates="authored_messages")
	room = relationship("Room", back_populates="messages")
	parent = relationship("Message", remote_side=[id], backref="replies")
	reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")
	reported_message = relationship("Report", back_populates="message")


class Reaction(Base):
	__tablename__ = "reactions"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
	emoji = Column(String, nullable=False)
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	# Relations
	user = relationship("User", back_populates="reactions")
	message = relationship("Message", back_populates="reactions")

	# Contrainte unique : Un user ne peut mettre qu'une fois le même emoji sur un message
	__table_args__ = (
		UniqueConstraint("user_id", "message_id", name="uix_user_message_reaction"),
		Index("ix_reactions_message_id", "message_id"),
	)


class Report(Base):
	__tablename__ = "reports"

	id = Column(Integer, primary_key=True, autoincrement=True)
	raison = Column(String)
	status = Column(String, default="pending", nullable=False)  # pending, resolved, dismissed
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	reported_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)

	# Relations
	message = relationship("Message", back_populates="reported_message")
	reporter = relationship("User", back_populates="reports_sent", foreign_keys=[reporter_id])
	reported = relationship("User", back_populates="reports_received", foreign_keys=[reported_id])

	# Index pour le dashboard admin
	__table_args__ = (
		Index("ix_reports_status", "status"),
		Index("ix_reports_reported_id", "reported_id"),
	)


# --- 4. Script de création (ne s'exécute que manuellement) ---
if __name__ == "__main__":
	# Si tu veux réinitialiser la BDD complètement, décommente la ligne suivante :
	# Base.metadata.drop_all(engine)

	Base.metadata.create_all(engine)
	print(" === Base de données et Tables mises à jour avec succès === ")

	# Tu peux ajouter ici tes scripts d'insertion de test si nécessaire
	# mais il vaut mieux utiliser l'API pour créer des données maintenant.
