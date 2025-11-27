from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.structures import Utilisateur
from services.auth_service import get_user_by_id
from utils.security import verify_token
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer


security = HTTPBearer()

async def get_token_from_header(credentials: HTTPBearer = Depends(security)):
    """
    Extract and return the token from the Authorization header
    """
    if not credentials or not credentials.credentials:
        return None
    return credentials.credentials


def get_current_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """
    Get the current user from the token
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_with_company_access(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """
    Get the current user from the token and verify they have access to the requested company.
    This is used for operations that need company-level filtering.
    """
    user = get_current_user(token, db)

    # For gérants de compagnie, verify they have a company assigned
    if user.type_utilisateur == 'gerant_compagnie':
        if not user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Gérant de compagnie must be associated with a company"
            )

    return user