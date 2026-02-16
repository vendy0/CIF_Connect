import sqlalchemy
from initialisation import Session, User


def get_user_by_username(username):
    with Session() as session:
        stmt = select(User).where(User.username == username).first()
        session.execute(stmt)
