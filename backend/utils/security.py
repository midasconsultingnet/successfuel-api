from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.structures import Utilisateur
from models.securite import AuthToken
from config.config import settings
from jose import JWTError, jwt
from database.database import get_db

# Configuration pour l'authentification JWT
security = HTTPBearer()
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Dépendance FastAPI pour récupérer l'utilisateur connecté à partir du JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    utilisateur = db.query(Utilisateur).filter(Utilisateur.login == login).first()
    if utilisateur is None:
        raise credentials_exception

    return utilisateur