from fastapi import FastAPI, HTTPException
from interaction import get_user_by_username
from pydantic import BaseModel

app = FastAPI()

class UserSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True  # ⚡ IMPORTANT pour pouvoir passer un objet SQLAlchemy


@app.get("/user")
def get_user_by_username_route(username: str):
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


# class RoomCreate(BaseModel):
#     name: str
#     description: str

# rooms = []

# @app.post("/rooms")
# async def create_room(room: RoomCreate):
#     room_id = len(rooms)
#     new_room = {
#         "id": room_id,
#         "name": room.name,
#         "description": room.description,
#     }
#     rooms.append(new_room)
#     return new_room


# @app.get("/rooms")
# async def get_rooms():
#     return rooms
