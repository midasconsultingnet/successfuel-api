from typing import Callable, Any
from functools import wraps
from strawberry.types import Info
from fastapi import HTTPException
from .utils import check_user_permission, check_user_access_to_company_resource
from .context import GraphQLContext


def require_auth():
    """
    Décorateur pour exiger qu'un utilisateur soit authentifié
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, info: Info, **kwargs):
            context: GraphQLContext = info.context
            if not context.current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            return func(*args, info=info, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    Décorateur pour exiger qu'un utilisateur ait une permission spécifique
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, info: Info, **kwargs):
            context: GraphQLContext = info.context
            if not context.current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            has_permission = check_user_permission(
                context.db_session, 
                context.current_user, 
                permission
            )
            
            if not has_permission:
                raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
                
            return func(*args, info=info, **kwargs)
        return wrapper
    return decorator


def protect_company_data(model_field_name: str = "compagnie_id"):
    """
    Décorateur pour protéger les données par la compagnie de l'utilisateur
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, info: Info, **kwargs):
            context: GraphQLContext = info.context
            if not context.current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            result = func(*args, info=info, **kwargs)
            
            # Vérifier que l'utilisateur a accès aux données retournées
            # Selon le type de résultat (instance unique ou liste)
            if result is None:
                return result
            
            # Pour une liste de résultats
            if isinstance(result, list):
                filtered_result = []
                for item in result:
                    if hasattr(item, model_field_name):
                        resource_company_id = getattr(item, model_field_name)
                        has_access = check_user_access_to_company_resource(
                            context.db_session,
                            context.current_user,
                            str(resource_company_id)
                        )
                        if has_access:
                            filtered_result.append(item)
                return filtered_result
            # Pour un seul résultat
            else:
                if hasattr(result, model_field_name):
                    resource_company_id = getattr(result, model_field_name)
                    has_access = check_user_access_to_company_resource(
                        context.db_session,
                        context.current_user,
                        str(resource_company_id)
                    )
                    if not has_access:
                        raise HTTPException(status_code=403, detail="Access denied to this resource")
                return result
                
        return wrapper
    return decorator