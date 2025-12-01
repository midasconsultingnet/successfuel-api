from typing import Optional
from fastapi import Request
from database.database import SessionLocal
from models.structures import Utilisateur
from services.auth_service import get_user_by_id
from utils.security import verify_token
from strawberry.fastapi import BaseContext

class GraphQLContext(BaseContext):
    def __init__(self, db_session=None, current_user: Optional[Utilisateur] = None):
        super().__init__()
        self.db_session = db_session
        self.current_user = current_user

async def get_context(request: Request) -> GraphQLContext:
    db_session = SessionLocal()
    try:
        # Récupérer le token JWT de l'en-tête Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    # Récupérer l'utilisateur depuis la base de données
                    user = get_user_by_id(db_session, user_id)
                    # Vérifier que l'utilisateur est actif
                    if user and user.statut == "Actif":
                        return GraphQLContext(db_session=db_session, current_user=user)

        # Si pas d'utilisateur authentifié ou utilisateur invalide
        return GraphQLContext(db_session=db_session)
    except Exception:
        db_session.close()
        raise