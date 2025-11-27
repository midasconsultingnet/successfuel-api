from typing import List, Optional
from sqlalchemy.orm import Session
from models.structures import Profil, Permission, Module, ProfilPermission, Utilisateur
from datetime import datetime


def create_module(db: Session, libelle: str, statut: str = "ACTIF") -> Module:
    """
    Create a new module
    """
    existing_module = db.query(Module).filter(Module.libelle == libelle).first()
    if existing_module:
        raise ValueError("Module already exists")
    
    db_module = Module(libelle=libelle, statut=statut)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    
    return db_module


def get_module_by_id(db: Session, module_id: str) -> Optional[Module]:
    """
    Get a module by ID
    """
    return db.query(Module).filter(Module.id == module_id).first()


def get_module_by_libelle(db: Session, libelle: str) -> Optional[Module]:
    """
    Get a module by its libelle
    """
    return db.query(Module).filter(Module.libelle == libelle).first()


def create_permission(db: Session, libelle: str, module_id: str, description: Optional[str] = None, 
                      statut: str = "ACTIF") -> Permission:
    """
    Create a new permission
    """
    existing_permission = db.query(Permission).filter(Permission.libelle == libelle).first()
    if existing_permission:
        raise ValueError("Permission already exists")
    
    db_permission = Permission(
        libelle=libelle,
        module_id=module_id,
        description=description,
        statut=statut
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    
    return db_permission


def get_permission_by_id(db: Session, permission_id: str) -> Optional[Permission]:
    """
    Get a permission by ID
    """
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_libelle(db: Session, libelle: str) -> Optional[Permission]:
    """
    Get a permission by its libelle
    """
    return db.query(Permission).filter(Permission.libelle == libelle).first()


def create_profil(db: Session, code: str, libelle: str, description: Optional[str] = None,
                  compagnie_id: Optional[str] = None, type_profil: str = "utilisateur_compagnie") -> Profil:
    """
    Create a new profile
    """
    existing_profil = db.query(Profil).filter(Profil.code == code).first()
    if existing_profil:
        raise ValueError("Profile with this code already exists")

    db_profil = Profil(
        code=code,
        libelle=libelle,
        description=description,
        compagnie_id=compagnie_id,
        type_profil=type_profil
    )
    db.add(db_profil)
    db.commit()
    db.refresh(db_profil)

    return db_profil


def get_profil_by_id(db: Session, profil_id: str) -> Optional[Profil]:
    """
    Get a profile by ID
    """
    return db.query(Profil).filter(Profil.id == profil_id).first()


def get_profil_by_code(db: Session, code: str) -> Optional[Profil]:
    """
    Get a profile by its code
    """
    return db.query(Profil).filter(Profil.code == code).first()


def assign_permissions_to_profil(db: Session, profil_id: str, permission_ids: List[str]) -> Profil:
    """
    Assign permissions to a profile
    """
    profil = get_profil_by_id(db, profil_id)
    if not profil:
        raise ValueError("Profile not found")

    # For 'gerant_compagnie' profiles, we automatically assign all permissions
    if profil.type_profil == "gerant_compagnie":
        # Get all available permissions
        all_permissions = get_all_permissions(db)
        permission_ids = [str(perm.id) for perm in all_permissions if perm.statut == "Actif"]

    # First remove all existing permissions for this profile
    db.query(ProfilPermission).filter(ProfilPermission.profil_id == profil_id).delete()

    # Then add the new permissions
    for perm_id in permission_ids:
        permission = get_permission_by_id(db, perm_id)
        if not permission:
            raise ValueError(f"Permission with ID {perm_id} not found")

        profil_permission = ProfilPermission(
            profil_id=profil_id,
            permission_id=perm_id
        )
        db.add(profil_permission)

    db.commit()
    db.refresh(profil)

    return profil


def get_permissions_for_profil(db: Session, profil_id: str) -> List[Permission]:
    """
    Get all permissions for a specific profile
    """
    profil = get_profil_by_id(db, profil_id)
    if not profil:
        return []

    # For 'gerant_compagnie' profiles, return all permissions
    if profil.type_profil == "gerant_compagnie":
        return get_all_permissions(db)

    # For other profiles, return only assigned permissions
    permissions = (
        db.query(Permission)
        .join(ProfilPermission, Permission.id == ProfilPermission.permission_id)
        .filter(ProfilPermission.profil_id == profil_id)
        .filter(Permission.statut == "Actif")
        .all()
    )

    return permissions


def get_permissions_for_user(db: Session, user_id: str) -> List[Permission]:
    """
    Get all permissions for a user through their profile
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return []

    # For 'gerant_compagnie' users, return all permissions regardless of profile
    if user.type_utilisateur == "gerant_compagnie":
        return get_all_permissions(db)

    if not user.profil_id:
        return []

    permissions = (
        db.query(Permission)
        .join(ProfilPermission, Permission.id == ProfilPermission.permission_id)
        .filter(ProfilPermission.profil_id == user.profil_id)
        .filter(Permission.statut == "Actif")
        .all()
    )

    return permissions


def get_permissions_for_profil(db: Session, profil_id: str) -> List[Permission]:
    """
    Get all permissions for a specific profile
    """
    permissions = (
        db.query(Permission)
        .join(ProfilPermission, Permission.id == ProfilPermission.permission_id)
        .filter(ProfilPermission.profil_id == profil_id)
        .filter(Permission.statut == "Actif")
        .all()
    )

    return permissions


def check_user_permission(db: Session, user_id: str, permission_libelle: str) -> bool:
    """
    Check if a user has a specific permission
    """
    # Get user to check their type
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        return False

    # Gérants de compagnie have all permissions for their company
    if user.type_utilisateur == "gerant_compagnie":
        return True

    permissions = get_permissions_for_user(db, user_id)
    return any(perm.libelle == permission_libelle for perm in permissions)


def get_all_profils(db: Session) -> List[Profil]:
    """
    Get all profiles
    """
    return db.query(Profil).all()


def get_all_permissions(db: Session) -> List[Permission]:
    """
    Get all permissions
    """
    return db.query(Permission).all()


def get_all_modules(db: Session) -> List[Module]:
    """
    Get all modules
    """
    return db.query(Module).all()


def update_profil(db: Session, profil_id: str, **kwargs) -> Optional[Profil]:
    """
    Update profile information
    """
    profil = db.query(Profil).filter(Profil.id == profil_id).first()
    if not profil:
        return None

    for key, value in kwargs.items():
        if hasattr(profil, key):
            setattr(profil, key, value)

    # Special handling for type_profil: if changing to 'gerant_compagnie', assign all permissions
    if 'type_profil' in kwargs and kwargs['type_profil'] == 'gerant_compagnie':
        # Get all available permissions and assign them
        all_permissions = get_all_permissions(db)
        permission_ids = [str(perm.id) for perm in all_permissions if perm.statut == "Actif"]

        # Remove existing permissions for this profile
        db.query(ProfilPermission).filter(ProfilPermission.profil_id == profil_id).delete()

        # Add all permissions to this profile
        for perm_id in permission_ids:
            profil_permission = ProfilPermission(
                profil_id=profil_id,
                permission_id=perm_id
            )
            db.add(profil_permission)

    profil.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profil)

    return profil


def delete_profil(db: Session, profil_id: str) -> bool:
    """
    Delete a profile (logical delete by changing status)
    """
    profil = db.query(Profil).filter(Profil.id == profil_id).first()
    if not profil:
        return False
    
    profil.statut = "Supprime"
    db.commit()
    return True


def get_user_profil(db: Session, user_id: str) -> Optional[Profil]:
    """
    Get the profile associated with a user
    """
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user or not user.profil_id:
        return None
    
    return db.query(Profil).filter(Profil.id == user.profil_id).first()