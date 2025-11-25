from typing import Optional
from database.database import SessionLocal
from strawberry.fastapi import BaseContext

class GraphQLContext(BaseContext):
    def __init__(self, db_session=None, current_user=None):
        super().__init__()
        self.db_session = db_session
        self.current_user = current_user

async def get_context() -> GraphQLContext:
    db_session = SessionLocal()
    try:
        # Vous pouvez ajouter la logique d'authentification ici
        # selon votre système de JWT actuel
        return GraphQLContext(db_session=db_session)
    except Exception:
        db_session.close()
        raise