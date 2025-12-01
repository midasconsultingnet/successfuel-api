from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.structures import Utilisateur
from services.rbac_service import get_permissions_for_user, check_user_permission
from utils.access_control import is_admin_or_super_admin, is_gerant_compagnie


def check_user_access_to_company_resource(
    db: Session, 
    current_user: Optional[Utilisateur], 
    resource_company_id: str
) -> bool:
    """
    Vérifie si l'utilisateur a accès à une ressource appartenant à une compagnie
    """
    if not current_user:
        return False

    # Les super administrateurs et administrateurs peuvent accéder à toutes les ressources
    if is_admin_or_super_admin(current_user.type_utilisateur):
        return True

    # Les utilisateurs ne peuvent accéder qu'aux ressources de leur propre compagnie
    return str(current_user.compagnie_id) == resource_company_id


def check_user_permission(
    db: Session,
    current_user: Optional[Utilisateur],
    permission: str
) -> bool:
    """
    Vérifie si l'utilisateur a la permission spécifiée
    """
    if not current_user:
        return False

    # Les super administrateurs ont toutes les permissions
    if current_user.type_utilisateur == "super_administrateur":
        return True

    # Les gérants de compagnie ont implicitement toutes les permissions pour leur compagnie
    if is_gerant_compagnie(current_user.type_utilisateur):
        return True

    # Pour les autres utilisateurs, vérifier explicitement la permission
    return check_user_permission(db, str(current_user.id), permission)


def filter_query_by_user_company(query, model, current_user: Optional[Utilisateur]):
    """
    Filtre une requête SQLAlchemy selon la compagnie de l'utilisateur
    """
    if not current_user:
        # S'il n'y a pas d'utilisateur authentifié, ne retourner aucune donnée
        return query.filter(model.id == None)  # Faux filtre pour retourner une liste vide

    # Les administrateurs peuvent voir toutes les données
    if is_admin_or_super_admin(current_user.type_utilisateur):
        return query

    # Les autres utilisateurs ne voient que les données de leur propre compagnie
    return query.filter(model.compagnie_id == current_user.compagnie_id)