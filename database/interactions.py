# database/interactions.py
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from database.initialisation import User, Room


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
    stmt = select(User).options(joinedload(User.rooms).joinedload(Room.creator)).where(User.email == email)
    user = db.execute(stmt).scalars().first()

    if not user:
        return []
    return user.rooms


# Récupérer TOUS les salons (pour la liste publique)
def get_all_rooms(db: Session):
    stmt = select(Room).options(joinedload(Room.creator))
    return db.execute(stmt).scalars().all()


def new_user(db: Session, user_data: dict):
    try:
        user = User(**user_data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("Utilisateur déjà existant")
