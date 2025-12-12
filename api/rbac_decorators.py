from fastapi import Depends, HTTPException, status
from .auth.auth_handler import get_current_user_security
from .auth.schemas import UserWithPermissions
from .rbac_utils import check_permission
import uuid

def require_permission(module_nom: str):
    """
    Dépendance pour vérifier les permissions
    Utilise la fonction get_current_user_security qui retourne un objet Pydantic
    """
    def permission_dependency(current_user: UserWithPermissions = Depends(get_current_user_security)):
        # Vérifier si l'utilisateur est un gérant
        if current_user.role == "gerant_compagnie":
            return  # Permission accordée

        # Vérifier si le module est dans les modules autorisés
        if module_nom not in current_user.modules_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé : permission nécessaire pour {module_nom}"
            )

    # Enlever les annotations pour éviter les problèmes d'analyse
    if hasattr(permission_dependency, '__annotations__'):
        permission_dependency.__annotations__ = {}

    return permission_dependency