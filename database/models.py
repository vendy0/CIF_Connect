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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert
from flet import Icons

DB_FILENAME = "cif_connect_demo.db"

# ==============================================================================
# 1. CONFIGURATION MOTEUR & SESSION
# ==============================================================================

# echo=True utile pour voir les requêtes SQL dans la console en dev
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False, future=True)


# Active les Foreign Keys pour SQLite (désactivé par défaut)
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()


SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

# ==============================================================================
# 2. TABLES D'ASSOCIATION
# ==============================================================================

# Table de liaison Many-to-Many entre Users et Rooms (Membre d'un salon)
user_room = Table(
	"user_room",
	Base.metadata,
	Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
	Column("room_id", Integer, ForeignKey("rooms.id"), primary_key=True),
)

# ==============================================================================
# 3. MODÈLES (ENTITÉS)
# ==============================================================================


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	email = Column(String, nullable=False, unique=True, index=True)
	password = Column(String, nullable=False)
	pseudo = Column(String, nullable=False, unique=True, index=True)
	last_pseudo_update = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
	role = Column(String, default="eleve", nullable=False)

	# Gestion Ban
	is_banned = Column(Boolean, default=False, nullable=False)
	ban_expires_at = Column(DateTime, nullable=True)
	ban_reason = Column(String, nullable=True)

	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	# --- Relations ---
	created_rooms = relationship("Room", back_populates="creator")
	rooms = relationship("Room", secondary=user_room, back_populates="users")
	authored_messages = relationship(
		"Message", back_populates="author", cascade="all, delete-orphan"
	)
	reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")

	# Signalements
	reports_sent = relationship(
		"Report", back_populates="reporter", foreign_keys="Report.reporter_id"
	)
	reports_received = relationship(
		"Report", back_populates="reported", foreign_keys="Report.reported_id"
	)


class Room(Base):
	__tablename__ = "rooms"

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False, unique=True)
	description = Column(String, nullable=False)
	icon = Column(String, default=Icons.CHAT_BUBBLE_ROUNDED)
	access_key = Column(String, nullable=True)  # Null = Public

	created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	# --- Relations ---
	creator = relationship("User", back_populates="created_rooms")
	users = relationship("User", secondary=user_room, back_populates="rooms")
	messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = "messages"

	id = Column(Integer, primary_key=True)
	author_display_name = Column(String)  # Pseudo figé au moment de l'envoi
	content = Column(String, nullable=False)
	message_type = Column(String, default="chat")  # 'join', 'alert', etc.
	created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

	room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
	author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	parent_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)

	__table_args__ = (
		Index("ix_messages_room_id", "room_id"),
		Index("ix_messages_parent_id", "parent_id"),
	)

	# --- Relations ---
	author = relationship("User", back_populates="authored_messages")
	room = relationship("Room", back_populates="messages")
	# Auto-jointure pour les réponses
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

	# --- Relations ---
	user = relationship("User", back_populates="reactions")
	message = relationship("Message", back_populates="reactions")

	__table_args__ = (
		UniqueConstraint(
			"user_id", "message_id", name="uix_user_message_reaction"
		),  # Un seul emoji par msg par user ? À voir si tu veux autoriser plusieurs
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

	# --- Relations ---
	message = relationship("Message", back_populates="reported_message")
	reporter = relationship("User", back_populates="reports_sent", foreign_keys=[reporter_id])
	reported = relationship("User", back_populates="reports_received", foreign_keys=[reported_id])


# ==============================================================================
# 4. INITIALISATION DE LA BDD (Run once)
# ==============================================================================

if __name__ == "__main__":
	# Si besoin de tout reset (danger !) :
	# Base.metadata.drop_all(engine)

	Base.metadata.create_all(engine)
	print("=== Tables créées ou vérifiées ===")

	# Ajout du Salon Général par défaut
	with SessionLocal() as db:
		stmt = (
			insert(Room)
			.values(
				name="Salon Général",
				description="Discussion libre pour tous",
				icon=Icons.PUBLIC,
				access_key=None,
			)
			.on_conflict_do_nothing(
				index_elements=["name"]  # colonne unique
			)
		)

		db.execute(stmt)
		db.commit()
		print(" === Salon Général initié ===")
