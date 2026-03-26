import random
from datetime import datetime, timedelta
from sqlalchemy import select
from models import SessionLocal, Message, User, Room


def seed_messages(count=200):
    db = SessionLocal()
    try:
        # 1. Vérifier que le salon 1 existe
        room = db.get(Room, 1)
        if not room:
            print("Erreur : Le salon avec l'ID 1 n'existe pas.")
            return

        # 2. Récupérer les utilisateurs disponibles pour varier les auteurs
        users = db.execute(select(User)).scalars().all()
        if not users:
            print("Erreur : Aucun utilisateur en base pour écrire des messages.")
            return

        print(f"Génération de {count} messages dans '{room.name}'...")

        # Liste de phrases aléatoires pour le test
        templates = [
            "Salut tout le monde !",
            "Est-ce que quelqu'un a testé la version 0.80.5 de Flet ?",
            "Le mode WAL de SQLite, c'est vraiment rapide.",
            "Test du message numéro {}",
            "Ceci est une simulation de chat intense.",
            "Python + FastAPI = ❤️",
            "Quelqu'un peut m'aider sur un bug ?",
            "On dirait que le scroll fonctionne bien.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "N'oubliez pas de tester les réactions !",
        ]

        now = datetime.now()

        for i in range(count):
            author = random.choice(users)
            # On décale le temps de création pour simuler un historique cohérent
            created_at = now - timedelta(minutes=(count - i))

            new_msg = Message(
                content=random.choice(templates).format(i + 1),
                author_id=author.id,
                room_id=room.id,
                author_display_name=author.pseudo,
                message_type="chat",
                created_at=created_at.replace(microsecond=0),
            )
            db.add(new_msg)

        db.commit()
        print(f"Succès ! {count} messages ont été ajoutés au salon ID 1.")

    except Exception as e:
        db.rollback()
        print(f"Une erreur est survenue : {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_messages()  # Tu peux changer le nombre ici
