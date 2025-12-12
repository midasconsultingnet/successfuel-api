from sqlalchemy.orm import Session
from .rbac_models import UtilisateurProfil, ProfilModule
import uuid

def check_permission(db: Session, utilisateur_id: uuid.UUID, module_nom: str) -> bool:
    """
    Vérifie si un utilisateur a la permission d'accéder à un module spécifique
    """
    result = db.query(UtilisateurProfil).filter(
        UtilisateurProfil.utilisateur_id == utilisateur_id
    ).first()
    
    if not result:
        return False  # L'utilisateur n'a pas de profil attribué
    
    # Vérifier si le module est dans les modules autorisés pour le profil de l'utilisateur
    module_associe = db.query(ProfilModule).filter(
        ProfilModule.profil_id == result.profil_id,
        ProfilModule.module_nom == module_nom
    ).first()
    
    return module_associe is not None

def get_modules_utilisateur(db: Session, utilisateur_id: uuid.UUID) -> list[str]:
    """
    Récupère la liste des modules autorisés pour un utilisateur spécifique
    """
    utilisateur_profil = db.query(UtilisateurProfil).filter(
        UtilisateurProfil.utilisateur_id == utilisateur_id
    ).first()
    
    if not utilisateur_profil:
        return []  # L'utilisateur n'a pas de profil attribué
    
    # Récupérer tous les modules associés au profil de l'utilisateur
    modules_associes = db.query(ProfilModule).filter(
        ProfilModule.profil_id == utilisateur_profil.profil_id
    ).all()
    
    return [module.module_nom for module in modules_associes]