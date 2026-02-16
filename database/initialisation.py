# # database/initialisation.py
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table, func, event, Index, UniqueConstraint
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker
# from flet import Icons

# DB_FILENAME = "cif_connect_demo.db"

# # --- Moteur & Session ---
# engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=False, future=True)

# @event.listens_for(engine, "connect")
# def enable_foreign_keys(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

# SessionLocal = sessionmaker(bind=engine, future=True)
# Base = declarative_base()

# # --- Tables ---
# user_room = Table(
#     "user_room",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
#     Column("room_id", Integer, ForeignKey("rooms.id"), primary_key=True),
# )

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     pseudo = Column(String, nullable=False, unique=True)
#     last_pseudo_update = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
#     role = Column(String, default="eleve", nullable=False)
#     is_banned = Column(Boolean, default=False, nullable=False)
#     ban_expires_at = Column(DateTime)
#     ban_reason = Column(String)
#     created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

#     created_rooms = relationship("Room", back_populates="creator")
#     rooms = relationship("Room", secondary=user_room, back_populates="users")
#     authored_messages = relationship("Message", back_populates="author", cascade="all, delete-orphan")
#     reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
#     reports_sent = relationship("Report", back_populates="reporter", foreign_keys="Report.reporter_id", cascade="all, delete-orphan")
#     reports_received = relationship("Report", back_populates="reported", foreign_keys="Report.reported_id", cascade="all, delete-orphan")

# class Room(Base):
#     __tablename__ = "rooms"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#     description = Column(String, nullable=False)
#     icon = Column(String, default=Icons.CHAT_BUBBLE_ROUNDED)
#     access_key = Column(String)
#     created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
#     created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

#     creator = relationship("User", back_populates="created_rooms")
#     users = relationship("User", secondary=user_room, back_populates="rooms")
#     messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")

# class Message(Base):
#     __tablename__ = "messages"
#     id = Column(Integer, primary_key=True)
#     author_display_name = Column(String, nullable=False)
#     content = Column(String, nullable=False)
#     message_type = Column(String, default="chat_message")
#     created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
#     room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
#     author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     parent_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)

#     author = relationship("User", back_populates="authored_messages")
#     room = relationship("Room", back_populates="messages")
#     parent = relationship("Message", remote_side=[id], backref="replies")
#     reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")
#     reported_message = relationship("Report", back_populates="message")

# class Reaction(Base):
#     __tablename__ = "reactions"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
#     emoji = Column(String, nullable=False)
#     created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
#     user = relationship("User", back_populates="reactions")
#     message = relationship("Message", back_populates="reactions")

# class Report(Base):
#     __tablename__ = "reports"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     raison = Column(String)
#     status = Column(String, default="pending", nullable=False)
#     created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
#     reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
#     reported_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
#     message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)

#     message = relationship("Message", back_populates="reported_message")
#     reporter = relationship("User", back_populates="reports_sent", foreign_keys=[reporter_id])
#     reported = relationship("User", back_populates="reports_received", foreign_keys=[reported_id])

# # --- Initialisation (ne s'exécute que si on lance ce fichier manuellement) ---
# if __name__ == "__main__":
#     from sqlalchemy.dialects.sqlite import insert
#     Base.metadata.create_all(engine)
#     with SessionLocal() as session:
#         # Création des données de démo (Vendy, etc.) ici...
#         # ... (ton code d'insertion existant)
#         print("Base de données initialisée.")

# SessionLocal = sessionmaker(bind=engine, future=True)

# with SessionLocal() as session:
#     stmt = insert(Room).values(name="Salon Général", description="Discussion libre pour tous", icon=Icons.PUBLIC).on_conflict_do_nothing(index_elements=["name"])
#     session.execute(stmt)

#     andy = User(email="aaaa@gmail.com", password="1234", pseudo="Vendy")
#     session.add(andy)
#     session.flush()
#     room = Room(name="Salon 1", description="Test de Salon", icon=Icons.CODE, creator=andy, access_key="zy2u")
#     session.add(room)

#     session.commit()


# database/initialisation.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table, func, event, Index, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from flet import Icons

DB_FILENAME = "cif_connect_demo.db"

# --- Moteur & Session ---
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=True, future=True)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

# --- Tables ---
user_room = Table(
    "user_room",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("room_id", Integer, ForeignKey("rooms.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    pseudo = Column(String, nullable=False, unique=True)
    last_pseudo_update = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    role = Column(String, default="eleve", nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    ban_expires_at = Column(DateTime)
    ban_reason = Column(String)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    created_rooms = relationship("Room", back_populates="creator")
    rooms = relationship("Room", secondary=user_room, back_populates="users")
    authored_messages = relationship("Message", back_populates="author", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
    reports_sent = relationship("Report", back_populates="reporter", foreign_keys="Report.reporter_id", cascade="all, delete-orphan")
    reports_received = relationship("Report", back_populates="reported", foreign_keys="Report.reported_id", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    icon = Column(String, default=Icons.CHAT_BUBBLE_ROUNDED)
    access_key = Column(String)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    creator = relationship("User", back_populates="created_rooms")
    users = relationship("User", secondary=user_room, back_populates="rooms")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    author_display_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    message_type = Column(String, default="chat_message")
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)

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
    user = relationship("User", back_populates="reactions")
    message = relationship("Message", back_populates="reactions")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    raison = Column(String)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reported_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)

    message = relationship("Message", back_populates="reported_message")
    reporter = relationship("User", back_populates="reports_sent", foreign_keys=[reporter_id])
    reported = relationship("User", back_populates="reports_received", foreign_keys=[reported_id])


# --- Initialisation (ne s'exécute que si on lance ce fichier manuellement) ---
if __name__ == "__main__":
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    from sqlalchemy.dialects.sqlite import insert

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        # stmt = insert(Room).values(name="Salon Général", description="Discussion libre pour tous", icon=Icons.PUBLIC).on_conflict_do_nothing(index_elements=["name"])
        # session.execute(stmt)

        # andy = User(email="aaaa@gmail.com", password="1234", pseudo="Vendy")
        # session.add(andy)
        # session.flush()
        # room = Room(name="Salon 1", description="Test de Salon", icon=Icons.CODE, creator=andy, access_key="zy2u")
        # session.add(room)
        # session.flush()

        # andy.rooms.append(room)
        # session.add(andy)

        # session.commit()

        stmt = select(User).options(joinedload(User.rooms).joinedload(Room.creator)).where(User.email == "aaaa@gmail.com")
        andy = session.execute(stmt).scalars().first()
        room = Room(name="Salon 2", description="Test de Salon, une deuxième fois !", icon=Icons.ACCESSIBLE, creator=andy, access_key="z2uu")
        andy.email = "aaaa"
        andy.rooms.append(room)
        session.add_all([andy, room])
        session.commit()
    print("Base de données initialisée.")
