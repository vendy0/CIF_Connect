# demo_sqlalchemy_full.py

import logging
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, select, func
)
from sqlalchemy.orm import (
    declarative_base, relationship, Session, selectinload
)
from sqlalchemy.exc import SQLAlchemyError

# 🔹 Config log
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 🔹 Base et moteur
Base = declarative_base()
engine = create_engine("sqlite:///:memory:", echo=False, future=True)

# 🔹 Tables
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", secondary="user_group", back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("User", secondary="user_group", back_populates="groups")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")

class UserGroup(Base):
    __tablename__ = "user_group"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)

# 🔹 Création de la base
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
logger.info("[setup] Tables created")

# 🔹 Fonctions CRUD avec transactions et logs
def create_user(session: Session, name: str) -> User:
    try:
        with session.begin_nested():
            user = User(name=name)
            session.add(user)
            logger.info(f"[CREATE] User '{name}' added")
            return user
    except SQLAlchemyError as e:
        logger.error(f"[ERROR CREATE] {e}")
        session.rollback()
        raise

def create_group(session: Session, name: str) -> Group:
    try:
        with session.begin_nested():
            group = Group(name=name)
            session.add(group)
            logger.info(f"[CREATE] Group '{name}' added")
            return group
    except SQLAlchemyError as e:
        logger.error(f"[ERROR CREATE] {e}")
        session.rollback()
        raise

def create_post(session: Session, title: str, user: User) -> Post:
    try:
        with session.begin_nested():
            post = Post(title=title, user=user)
            session.add(post)
            logger.info(f"[CREATE] Post '{title}' for user '{user.name}' added")
            return post
    except SQLAlchemyError as e:
        logger.error(f"[ERROR CREATE POST] {e}")
        session.rollback()
        raise

def assign_user_to_group(session: Session, user: User, group: Group):
    try:
        with session.begin_nested():
            user.groups.append(group)
            logger.info(f"[ASSIGN] User '{user.name}' added to group '{group.name}'")
    except SQLAlchemyError as e:
        logger.error(f"[ERROR ASSIGN] {e}")
        session.rollback()
        raise

def read_users(session: Session, eager=False):
    stmt = select(User)
    if eager:
        stmt = stmt.options(selectinload(User.groups), selectinload(User.posts))
    users = session.scalars(stmt).all()
    for u in users:
        groups = [g.name for g in u.groups]
        posts = [p.title for p in u.posts]
        logger.info(f"[READ] {u.name} -> Groups: {groups}, Posts: {posts}")
    return users

def update_user_name(session: Session, user: User, new_name: str):
    with session.begin_nested() as nested:
        try:
                old_name = user.name
                user.name = new_name
                logger.info(f"[UPDATE] User '{old_name}' renamed to '{new_name}'")
        except SQLAlchemyError as e:
            logger.error(f"[ERROR UPDATE] {e}")
            session.rollback()

def delete_user(session: Session, user: User):
    try:
        with session.begin_nested() as nested:
            session.delete(user)
            logger.info(f"[DELETE] User '{user.name}' deleted")
    except SQLAlchemyError as e:
        logger.error(f"[ERROR DELETE] {e}")
        session.rollback()
        raise

# 🔹 Démo complète
with Session(engine) as session:
    with session.begin():
        # Création
        alice = create_user(session, "Alice")
        bob = create_user(session, "Bob")
        admin = create_group(session, "Admins")
        mod = create_group(session, "Moderators")
        assign_user_to_group(session, alice, admin)
        assign_user_to_group(session, alice, mod)
        assign_user_to_group(session, bob, mod)
        create_post(session, "Alice Post 1", alice)
        create_post(session, "Alice Post 2", alice)
        create_post(session, "Bob Post 1", bob)
    
        # Lecture eager
        read_users(session, eager=True)
    
        # Update
        update_user_name(session, bob, "Robert")
    
        # Filtrage / agrégations
        stmt = select(User.name, func.count(Post.id)).join(User.posts).group_by(User.id)
        for name, count in session.execute(stmt):
            logger.info(f"[AGG] {name} has {count} post(s)")
    
        # Delete
        delete_user(session, alice)
    
        # Lecture finale
        read_users(session, eager=True)

logger.info("[done] Demo complete")