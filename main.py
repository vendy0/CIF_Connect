# from fastapi import FastAPI, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy import select
# from sqlalchemy.orm import Session
# from database.initialisation import User, SessionLocal
# from database.interactions import get_user_by_username, get_user_rooms
# from datetime import datetime

# app = FastAPI(title="Demo Users API")


# # 🔹 Dépendance pour la session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # 🔹 Pydantic model
# class UserSchema(BaseModel):
#     id: int
#     email: str
#     pseudo: str
#     role: str
#     created_at: datetime
#     is_banned: bool
#     ban_expires_at: datetime | None = None

#     class Config:
#         from_attributes = True  # Permet de renvoyer un objet SQLAlchemy directement


# # 🔹 Pydantic model
# class UserMinimalSchema(BaseModel):
#     id: int
#     pseudo: str

#     class Config:
#         from_attributes = True


# class RoomSchema(BaseModel):
#     id: int
#     name: str
#     description: str
#     icon: str
#     created_at: datetime
#     # On utilise la relation 'creator' définie dans Room (SQLAlchemy)
#     creator: UserMinimalSchema | None

#     class Config:
#         from_attributes = True


# # 🔹 Endpoint GET
# @app.get("/user", response_model=UserSchema)
# def get_user_by_username_route(username: str):
#     user = get_user_by_username(username)
#     if not user:
#         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
#     return user


# # # 🔹 Endpoint GET
# # @app.get("/rooms", response_model=UserSchema)
# # def get_user_by_username_route(username: str):
# #     user = get_user_by_username(username)
# #     if not user:
# #         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
# #     return user


# @app.get("/user/rooms")
# def get_user_rooms_route(email: str):
#     rooms = get_user_rooms(email)
#     if not rooms:
#         raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
#     # 2. On retourne la liste des salons (RoomSchema devra être défini)
#     return rooms


# # class RoomCreate(BaseModel):
# #     name: str
# #     description: str

# # rooms = []

# # @app.post("/rooms")
# # async def create_room(room: RoomCreate):
# #     room_id = len(rooms)
# #     new_room = {
# #         "id": room_id,
# #         "name": room.name,
# #         "description": room.description,
# #     }
# #     rooms.append(new_room)
# #     return new_room


# # @app.get("/rooms")
# # async def get_rooms():
# #     return rooms


# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

# Import depuis tes fichiers
from database.initialisation import SessionLocal
import database.interactions as db_inter

app = FastAPI(title="CIF Connect API")


# --- Dépendance BDD ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Schémas Pydantic ---
class UserMinimalSchema(BaseModel):
    id: int
    pseudo: str

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: int
    email: str
    pseudo: str
    role: str
    is_banned: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoomSchema(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    created_at: datetime
    creator: UserMinimalSchema | None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    pseudo: str
    role: str | None = "eleve"


# --- Endpoints ---


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


@app.get("/user/rooms", response_model=list[RoomSchema])
def get_my_rooms(email: str, db: Session = Depends(get_db)):
    rooms = db_inter.get_user_rooms(db, email)
    if rooms is None:
        return []  # Retourne une liste vide si pas de salons
    return rooms


@app.get("/rooms", response_model=list[RoomSchema])
def list_all_rooms(db: Session = Depends(get_db)):
    return db_inter.get_all_rooms(db)
