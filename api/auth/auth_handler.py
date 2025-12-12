from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..models import User, TokenSession
from ..rbac_utils import get_modules_utilisateur
from ..database import get_db
import os
from sqlalchemy import and_
import uuid

# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key and algorithm from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed password.
    Truncates password to 72 bytes if longer, as bcrypt has a 72-byte password limit.
    """
    try:
        # Truncate password to 72 bytes if longer, as bcrypt has a 72-byte password limit
        truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
        return pwd_context.verify(truncated_password, hashed_password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            # Even after truncation, if there's still an issue, we handle it gracefully
            # This shouldn't happen with our truncation, but added as additional safety
            return False
        else:
            raise e


def get_password_hash(password):
    """
    Generate a hash for a plain password.
    Truncates password to 72 bytes if longer, as bcrypt has a 72-byte password limit.
    """
    try:
        # Truncate password to 72 bytes if longer, as bcrypt has a 72-byte password limit
        truncated_password = password[:72] if len(password) > 72 else password
        return pwd_context.hash(truncated_password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            # Handle the edge case where there's still an issue after truncation
            truncated_password = password[:72]
            return pwd_context.hash(truncated_password[:72])
        else:
            raise e


def authenticate_user(db: Session, login: str, password: str):
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.mot_de_passe_hash):
        return False

    # Update last login time
    user.date_derniere_connexion = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        token_type: str = payload.get("type")

        # Verify it's an access token
        if token_type != "access":
            raise credentials_exception

        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception

    # Récupérer les modules autorisés pour cet utilisateur
    modules_autorises = get_modules_utilisateur(db, user.id)

    # Créer un objet Pydantic UserWithPermissions au lieu de modifier l'objet SQLAlchemy
    from .schemas import UserWithPermissions
    user_with_permissions = UserWithPermissions(
        id=user.id,
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        login=user.login,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
        date_derniere_connexion=user.date_derniere_connexion,
        actif=user.actif,
        compagnie_id=user.compagnie_id,
        modules_autorises=modules_autorises
    )

    return user_with_permissions


def get_current_user_security(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    """
    Nouvelle version de get_current_user qui retourne un objet Pydantic UserWithPermissions
    pour éviter les problèmes de sérialisation avec les objets SQLAlchemy modifiés
    """
    from .schemas import UserWithPermissions

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        token_type: str = payload.get("type")

        # Verify it's an access token
        if token_type != "access":
            raise credentials_exception

        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception

    # Récupérer les modules autorisés pour cet utilisateur
    modules_autorises = get_modules_utilisateur(db, uuid.UUID(str(user.id)))

    # Créer un objet Pydantic UserWithPermissions au lieu de modifier l'objet SQLAlchemy
    user_with_permissions = UserWithPermissions(
        id=user.id,
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        login=user.login,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at,
        date_derniere_connexion=user.date_derniere_connexion,
        actif=user.actif,
        compagnie_id=user.compagnie_id,
        modules_autorises=modules_autorises
    )

    return user_with_permissions


def get_user_from_refresh_token(db: Session, refresh_token: str) -> tuple:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        token_type: str = payload.get("type")

        # Verify it's a refresh token
        if token_type != "refresh":
            raise credentials_exception

        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception

    # Check if the refresh token exists in the database
    token_entry = db.query(TokenSession).filter(
        and_(
            TokenSession.utilisateur_id == user.id,
            TokenSession.token_refresh == refresh_token,
            TokenSession.actif == True,
            TokenSession.date_expiration > datetime.utcnow()
        )
    ).first()

    if not token_entry:
        raise credentials_exception

    return user, token_entry


def create_tokens_for_user(db: Session, user: User):
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        data={"sub": user.login}
    )

    # Store the refresh token in database
    token_session = TokenSession(
        utilisateur_id=user.id,
        token=access_token,
        token_refresh=refresh_token,
        date_expiration=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(token_session)
    db.commit()

    return access_token, refresh_token