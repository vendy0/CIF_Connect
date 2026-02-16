# sqlalchemy_full_demo_fixed.py
# Usage: python3 sqlalchemy_full_demo_fixed.py
# Testé pour Termux; supprime le fichier sqlite précédent pour une exécution propre.

import os
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Table,
    select, func, exists
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker, joinedload
)
from sqlalchemy.orm.exc import DetachedInstanceError

DB_FILENAME = "cif_connect_demo.db"

# --- (A) Reset DB file for a clean demo run ---
if os.path.exists(DB_FILENAME):
    try:
        os.remove(DB_FILENAME)
        print(f"[setup] Removed existing {DB_FILENAME} for a clean demo.")
    except Exception as e:
        print(f"[setup] Could not remove existing DB file: {e}")

# --- (B) Engine & Base ---
engine = create_engine(f"sqlite:///{DB_FILENAME}", echo=True, future=True)
Base = declarative_base()

# --- (C) Association table for many-to-many ---
user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)

# --- (D) Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=user_group, back_populates="users")

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r}>"

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r} user_id={self.user_id}>"

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    users = relationship("User", secondary=user_group, back_populates="groups")

    def __repr__(self):
        return f"<Group id={self.id} name={self.name!r}>"

# --- (E) Create tables ---
Base.metadata.create_all(engine)
print("[setup] Tables created.")

# --- (F) Session factory ---
SessionLocal = sessionmaker(bind=engine, future=True)

# ---------- DEMO FUNCTIONS ----------
def create_initial_data():
    """Crée users, groups, posts — montre add → flush → commit"""
    with SessionLocal() as session:
        print("\n[demo] create_initial_data: TRANSIENT -> PENDING -> FLUSH -> COMMIT")
        alice = User(name="Alice")
        bob = User(name="Bob")

        admins = Group(name="Admins")
        mods = Group(name="Moderators")

        p1 = Post(title="Alice Post 1", user=alice)
        p2 = Post(title="Alice Post 2", user=alice)
        p3 = Post(title="Bob Post 1", user=bob)

        # Many-to-Many relation setup (python side)
        alice.groups.extend([admins, mods])
        bob.groups.append(mods)

        # Add everything to session (pending)
        session.add_all([alice, bob, admins, mods, p1, p2, p3])

        # Flush (send SQL, get IDs) but still inside open transaction
        session.flush()
        print(f"[demo] after flush: alice.id={alice.id}, bob.id={bob.id}")

        # Modify before commit
        p2.title = "Alice Post 2 Updated"
        bob.name = "Robert"

        # Commit -> persistent confirmed
        session.commit()
        print("[demo] commit done. initial data saved.")

        # Return one object for further experiments (note: after context it becomes detached)
        return alice  # this will be a detached instance once context exits


def selects_and_queries():
    """Montre différents SELECT: simple, filter, join, aggregation, pagination, exists, eager loading"""
    with SessionLocal() as session:
        print("\n[demo] selects_and_queries")

        # simple select: get Alice (scalar returns object)
        stmt = select(User).where(User.name == "Alice").limit(1)
        alice = session.scalar(stmt)
        print("[select] simple:", alice, "posts count (lazy):", len(alice.posts))  # lazy will load posts

        # eager loading with joinedload (single query for users + posts)
        stmt = select(User).options(joinedload(User.posts))
        results = session.execute(stmt).unique().scalars().all()
        for u in results:
            print("[select eager] ", u.name, "-> posts:", [p.title for p in u.posts])
            
        # filter by relation content (join)
        stmt = select(User).join(User.posts).where(Post.title.like("%1%"))
        users_with_1 = session.scalars(stmt).all()
        print("[select join/filter] users with '1' in a post title:", [u.name for u in users_with_1])

        # aggregation: count posts per user
        stmt = select(User.name, func.count(Post.id)).join(User.posts).group_by(User.id)
        for name, count in session.execute(stmt).all():
            print("[agg] ", name, "has", count, "post(s)")

        # many-to-many filtering (users in Moderators)
        stmt = select(User).join(user_group).join(Group).where(Group.name == "Moderators")
        mods_users = session.scalars(stmt).all()
        print("[many-to-many] Moderators:", [u.name for u in mods_users])

        # pagination example
        stmt = select(User).order_by(User.id).offset(1).limit(2)
        page2 = session.scalars(stmt).all()
        print("[pagination] page2:", [u.name for u in page2])

        # exists clause
        stmt = select(User).where(exists(select(Post).where(Post.user_id == User.id)))
        has_posts = session.scalars(stmt).all()
        print("[exists] users with at least one post:", [u.name for u in has_posts])


def rollback_demo():
    """Montre rollback et ce qu'il arrive aux objets pending/persistent"""
    with SessionLocal() as session:
        print("\n[demo] rollback_demo")
        # take Alice from db
        alice = session.scalars(select(User).where(User.name == "Alice")).one()
        temp_post = Post(title="TEMP Post", user=alice)
        session.add(temp_post)
        print("[rollback_demo] temp_post pending in session:", temp_post in session)
        # Now rollback - this will remove pending changes
        session.rollback()
        print("[rollback_demo] after rollback, temp_post in session?:", temp_post in session)
        # note: temp_post is now transient/detached depending on internal state


def detached_handling_demo(alice_detached):
    """
    Montre correctement comment rattacher un objet detached:
      - mauvaise méthode (on montre l'erreur capturée)
      - méthode 1: merge()
      - méthode 2: re-query depuis nouvelle session
    """
    print("\n[demo] detached_handling_demo")
    # alice_detached is detached because returned from create_initial_data (session closed)
    # BAD: trying to access lazy relationship or append will raise DetachedInstanceError
    try:
        print("[bad] Attempting to access alice_detached.posts (lazy) -> should raise DetachedInstanceError")
        # If posts was loaded with eager earlier, access might work; here we assume lazy to show the error.
        _ = alice_detached.posts  # may raise
    except DetachedInstanceError as e:
        print("[bad] Caught DetachedInstanceError (expected):", e)

    # Method A: merge()
    with SessionLocal() as session:
        print("[good] Reattaching via merge()")
        alice_att = session.merge(alice_detached)  # returns an attached instance
        new_post = Post(title="Alice via merge()")
        alice_att.posts.append(new_post)
        session.commit()
        print("[good] merged, appended post, and committed:", new_post)

    # Method B: re-query from DB
    with SessionLocal() as session:
        print("[good] Re-querying alice from DB and using that attached instance")
        alice_att = session.scalar(select(User).where(User.name == "Alice"))  # fresh attached instance
        another_post = Post(title="Alice via re-query")
        alice_att.posts.append(another_post)
        session.commit()
        print("[good] re-queried, appended post, committed:", another_post)


def detached_merge_subtlety_demo():
    """
    Montre la subtilité: merge() retourne UNE VERSION attachée;
    l'objet detached d'origine NE devient PAS attaché automatiquement.
    """
    print("\n[demo] detached_merge_subtlety_demo")
    with SessionLocal() as session:
        # get Alice attached
        alice = session.scalar(select(User).where(User.name == "Alice"))
        session.expunge(alice)  # explicit detach -> alice is detached now
        print("[subtle] alice detached explicit:", alice)

        # Merge into new session
        alice_merged = session.merge(alice)  # attaches a *copy* (or the state) to session
        print("[subtle] alice_merged is attached:", alice_merged in session)

        # Modify merged, commit
        alice_merged.name = alice_merged.name + " (merged)"
        session.commit()
        print("[subtle] committed merged change; detached original still detached object in memory:", alice)


# ---------- RUN DEMOS ----------
if __name__ == "__main__":
    # 1) create initial data and obtain a detached alice instance (function returns after session closes)
    alice_detached = create_initial_data()

    # 2) run various selects & queries demonstrating eager/lazy/joins/agg/pagination/exists
    selects_and_queries()

    # 3) show rollback behaviour
    rollback_demo()

    # 4) detached handling (BAD attempt is caught; then two correct ways are shown)
    detached_handling_demo(alice_detached)

    # 5) subtlety about merge (original detached object stays detached)
    detached_merge_subtlety_demo()

    print("\n[done] Demo complete. DB file:", DB_FILENAME)
