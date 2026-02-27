# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import des modules locaux
from database.models import SessionLocal
import database.crud as db_inter
from database.shemas import *
from security import create_access_token, verify_password, SECRET_KEY, ALGORITHM

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError


app = FastAPI(title="CIF Connect API", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==============================================================================
# DEPENDANCE DATABASE
# ==============================================================================


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # 1. On tente de décoder le jeton avec notre SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception
        return user_id  # On retourne l'ID pour que la route sache qui appelle
    except JWTError:
        # Si le jeton est expiré ou falsifié, on lève une erreur 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton invalide ou expiré",
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# UTILISATEURS (USERS)
# ==============================================================================


@app.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["Users"])
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur"""
    user = db_inter.new_user(db, data)
    access_token = create_access_token(data={"sub": user.id, "pseudo": user.pseudo, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token, tags=["Users"])
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authentification simple (Email + Password)"""
    user = db_inter.get_user_by_email(db, data.email)

    # Vérification (Attention: MDP en clair ici, à hasfer en prod !)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable !")
    elif not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect !")

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Compte banni.")
    # ... après avoir vérifié que l'utilisateur existe et que le MDP est bon ...
    access_token = create_access_token(data={"sub": user.id, "pseudo": user.pseudo, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users", response_model=List[UserSchema], tags=["Users"])
def list_all_users(db: Session = Depends(get_db)):
    """Admin only: Liste tous les utilisateurs"""
    return db_inter.get_all_users(db)


@app.put("/users/{user_id}/pseudo", tags=["Users"])
def change_pseudo(user_id: int, data: PseudoUpdateRequest, db: Session = Depends(get_db)):
    """Changer son pseudo"""
    user = db_inter.update_user_pseudo(db, user_id, data.new_pseudo)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"detail": "Pseudo modifié", "new_pseudo": user.pseudo}


# ==============================================================================
# SALONS (ROOMS)
# ==============================================================================


@app.get("/rooms", response_model=List[RoomSchema], tags=["Rooms"])
def list_rooms(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),  # Le verrou est ici !
):
    """Liste publique des salons"""
    # Logique pour chercher les salons en base de données
    return db_inter.get_all_rooms(db)


@app.post("/rooms", response_model=RoomSchema, status_code=status.HTTP_201_CREATED, tags=["Rooms"])
def create_room(data: CreateRoomSchema, db: Session = Depends(get_db)):
    """Créer un nouveau salon"""
    # L'ID du créateur est dans le body (data.creator_id)
    return db_inter.create_room(db, data, creator_id=data.creator_id)


@app.put("/rooms/{room_id}", response_model=RoomSchema, tags=["Rooms"])
def update_room_info(
    room_id: int,
    update_data: RoomUpdateSchema,
    user_id: int,  # On demande l'ID de l'user (idéalement via token, ici via query pour la démo)
    db: Session = Depends(get_db),
):
    """
    Modifier un salon (Nom, description, icône).
    Seul le créateur peut le faire.
    """
    return db_inter.update_room(db, room_id, user_id, update_data)


@app.delete("/rooms/{room_id}", response_model=RoomReturnSchema, tags=["Rooms"])
def delete_room(room_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Supprimer définitivement un salon.
    Seul le créateur peut le faire.
    """
    return db_inter.delete_room_func(db, room_id, user_id)


@app.get("/user/rooms", response_model=List[RoomSchema], tags=["Rooms"])
def get_my_rooms(email: str, db: Session = Depends(get_db)):
    """Récupère les salons d'un utilisateur spécifique"""
    return db_inter.get_user_rooms(db, email)


@app.post("/user/rooms/join", response_model=RoomSchema, tags=["Rooms"])
def join_room(data: JoinRoomSchema, db: Session = Depends(get_db)):
    """Rejoindre un salon existant"""
    return db_inter.join_new_room(db, data)


@app.post("/user/rooms/{room_id}/quit", response_model=RoomSchema, tags=["Rooms"])
def quit_room(room_id: int, user_id: int, db: Session = Depends(get_db)):
    """Quitter un salon"""
    return db_inter.quit_room_func(db, user_id=user_id, room_id=room_id)


# ==============================================================================
# MESSAGES
# ==============================================================================


@app.get("/room/{room_id}/messages", response_model=List[MessageSchema], tags=["Messages"])
def read_messages(room_id: int, db: Session = Depends(get_db)):
    """Lire l'historique d'un salon"""
    return db_inter.get_messages(db, room_id)


@app.post(
    "/room/{room_id}/messages",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
)
def send_message(room_id: int, message_data: MessageCreate, db: Session = Depends(get_db)):
    """Poster un message dans un salon"""
    return db_inter.create_message(db, room_id, message_data)


# MODÉRATION DES MESSAGES


@app.delete("/message/{message_id}", tags=["Messages"])
def delete_message(message_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un message.
    Possible si on est l'auteur OU si on est Admin.
    """
    return db_inter.delete_message_func(db, message_id, user_id)


# ==============================================================================
# RÉACTIONS
# ==============================================================================


@app.post("/message/{message_id}/reaction", response_model=ReactionSchema, tags=["Reactions"])
def add_reaction(message_id: int, reaction_data: ReactionCreateSchema, db: Session = Depends(get_db)):
    """Ajouter un emoji à un message"""
    return db_inter.reagir(db, message_id, reaction_data)


@app.delete("/reaction/{reaction_id}", response_model=ReactionReturnSchema, tags=["Reactions"])
def remove_reaction(reaction_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une réaction.
    On demande user_id en query param pour vérifier que c'est bien l'auteur.
    """
    return db_inter.dereagir(db, user_id, reaction_id)


# ==============================================================================
# SIGNALEMENTS (REPORTS)
# ==============================================================================


@app.post("/reports", response_model=ReportSchema, status_code=status.HTTP_201_CREATED, tags=["Reports"])
def send_report(data: ReportCreateSchema, db: Session = Depends(get_db)):
    """
    Créer un nouveau signalement.
    Il suffit de donner l'ID du message et la raison.
    """
    return db_inter.create_report(db, data)


@app.get("/reports", response_model=List[ReportFullSchema], tags=["Reports"])
def list_reports(db: Session = Depends(get_db)):
    """
    (Admin) Voir tous les signalements.
    """
    return db_inter.get_all_reports(db)


@app.post("/reports/{report_id}/resolve", response_model=ReportSchema, tags=["Reports"])
def resolve_report(report_id: int, resolution_data: ReportResolutionSchema, db: Session = Depends(get_db)):
    """
    (Admin) Résoudre un signalement avec action optionnelle (Ban).

    - status: 'resolved', 'dismissed', etc.
    - ban_user: true/false
    - ban_duration_hours: int (si vide = définitif)
    """
    # Ici, tu devrais vérifier si l'user connecté est admin (via dépendance ou check manuel)
    return db_inter.process_report_resolution(db, report_id, resolution_data)
