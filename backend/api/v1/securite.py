from datetime import timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from models.structures import Utilisateur, Profil, ProfilPermission, Permission, Module
from models.securite import EvenementSecurite, ModificationSensible
from services.auth_service import AuthentificationService
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService
from utils.security import get_current_user

router = APIRouter()

class ProfileCreate(BaseModel):
    code: str
    libelle: str
    description: Optional[str] = None
    permission_ids: List[str] = []

class ProfileUpdate(BaseModel):
    libelle: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    permission_ids: List[str] = []

class ModuleCreate(BaseModel):
    libelle: str
    statut: Optional[str] = "Actif"

class PermissionCreate(BaseModel):
    libelle: str
    module_id: str
    description: Optional[str] = None
    statut: Optional[str] = "Actif"

@router.post("/login")
def login(
    request: Request,
    login: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et génère un jeton JWT
    """
    ip_connexion = request.client.host

    result = AuthentificationService.login_user(
        db,
        login,
        password,
        ip_connexion=ip_connexion
    )

    if not result:
        JournalisationService.log_security_event(
            db,
            type_evenement="tentative_connexion_echouee",
            description=f"Tentative de connexion échouée pour l'utilisateur '{login}'",
            ip_utilisateur=ip_connexion
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )

    return {
        "success": True,
        "data": result,
        "message": "Connexion réussie"
    }


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Déconnecte l'utilisateur en invalidant le jeton
    """
    # Note: Cette implémentation suppose que le token est passé dans la requête
    # En pratique, vous devez extraire le token des en-têtes pour l'invalider
    # Pour l'instant, nous retournons simplement un message de succès
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }


@router.get("/profiles")
def get_profiles(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    """
    Récupère tous les profils avec leurs permissions
    """
    # Vérifier si l'utilisateur a la permission de gérer les profils
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_profils"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux profils"
        )

    query = db.query(Profil)

    if search:
        query = query.filter(Profil.libelle.ilike(f"%{search}%"))

    query = query.order_by(Profil.created_at.desc())
    profiles = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total = db.query(Profil).count()

    # Récupérer les permissions pour chaque profil
    profile_data = []
    for profile in profiles:
        permissions = (
            db.query(Permission)
            .join(ProfilPermission, Permission.id == ProfilPermission.permission_id)
            .filter(ProfilPermission.profil_id == profile.id)
            .all()
        )

        profile_data.append({
            "id": str(profile.id),
            "code": profile.code,
            "libelle": profile.libelle,
            "description": profile.description,
            "statut": profile.statut,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "permissions": [
                {
                    "id": str(perm.id),
                    "libelle": perm.libelle,
                    "description": perm.description,
                }
                for perm in permissions
            ]
        })

    return {
        "success": True,
        "data": {
            "profiles": profile_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Profils récupérés avec succès"
    }


@router.post("/profiles")
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée un nouveau profil avec ses permissions
    """
    # Vérifier si l'utilisateur a la permission de créer des profils
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_profils"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des profils"
        )

    # Créer le profil avec ses permissions
    try:
        nouveau_profil = RBACService.create_profile(
            db,
            code=profile_data.code,
            libelle=profile_data.libelle,
            description=profile_data.description,
            permission_ids=profile_data.permission_ids
        )

        # Enregistrer l'événement de sécurité
        JournalisationService.log_security_event(
            db,
            type_evenement="creation_profil",
            description=f"Profil '{nouveau_profil.libelle}' créé par '{current_user.login}'",
            utilisateur_id=str(current_user.id)
        )

        return {
            "success": True,
            "data": {
                "id": str(nouveau_profil.id),
                "code": nouveau_profil.code,
                "libelle": nouveau_profil.libelle,
                "description": nouveau_profil.description,
                "statut": nouveau_profil.statut,
                "created_at": nouveau_profil.created_at,
                "updated_at": nouveau_profil.updated_at,
            },
            "message": "Profil créé avec succès"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du profil: {str(e)}"
        )


@router.put("/profiles/{profile_id}")
def update_profile(
    profile_id: str,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Met à jour un profil avec ses permissions
    """
    # Vérifier si l'utilisateur a la permission de modifier des profils
    if not RBACService.check_permission_by_user_obj(db, current_user, "modifier_profils"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour modifier des profils"
        )

    # Récupérer le profil
    profil = db.query(Profil).filter(Profil.id == profile_id).first()
    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil non trouvé"
        )

    # Mettre à jour les champs
    if profile_data.libelle is not None:
        profil.libelle = profile_data.libelle
    if profile_data.description is not None:
        profil.description = profile_data.description
    if profile_data.statut is not None:
        profil.statut = profile_data.statut

    # Mettre à jour les permissions si elles sont spécifiées
    if profile_data.permission_ids is not None:
        RBACService.update_profile_permissions(db, profile_id, profile_data.permission_ids)

    db.commit()
    db.refresh(profil)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="modification_profil",
        description=f"Profil '{profil.libelle}' modifié par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(profil.id),
            "code": profil.code,
            "libelle": profil.libelle,
            "description": profil.description,
            "statut": profil.statut,
            "created_at": profil.created_at,
            "updated_at": profil.updated_at,
        },
        "message": "Profil mis à jour avec succès"
    }


@router.get("/modules")
def get_modules(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    """
    Récupère tous les modules
    """
    # Vérifier si l'utilisateur a la permission de gérer les modules
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_modules"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux modules"
        )

    query = db.query(Module)

    if search:
        query = query.filter(Module.libelle.ilike(f"%{search}%"))

    query = query.order_by(Module.libelle)
    modules = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total = db.query(Module).count()

    module_data = [
        {
            "id": str(module.id),
            "libelle": module.libelle,
            "statut": module.statut,
        }
        for module in modules
    ]

    return {
        "success": True,
        "data": {
            "modules": module_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Modules récupérés avec succès"
    }


@router.post("/modules")
def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée un nouveau module
    """
    # Vérifier si l'utilisateur a la permission de créer des modules
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_modules"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des modules"
        )

    # Vérifier si le module existe déjà
    existing_module = db.query(Module).filter(Module.libelle == module_data.libelle).first()
    if existing_module:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un module avec le libellé '{module_data.libelle}' existe déjà"
        )

    # Créer le module
    nouveau_module = Module(
        libelle=module_data.libelle,
        statut=module_data.statut
    )

    db.add(nouveau_module)
    db.commit()
    db.refresh(nouveau_module)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="creation_module",
        description=f"Module '{nouveau_module.libelle}' créé par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(nouveau_module.id),
            "libelle": nouveau_module.libelle,
            "statut": nouveau_module.statut,
        },
        "message": "Module créé avec succès"
    }


@router.get("/permissions")
def get_permissions(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    module_id: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Récupère toutes les permissions avec filtre optionnel par module
    """
    # Vérifier si l'utilisateur a la permission de gérer les permissions
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux permissions"
        )

    query = db.query(Permission).join(Module, Permission.module_id == Module.id)

    if module_id:
        query = query.filter(Permission.module_id == module_id)
    if search:
        query = query.filter(Permission.libelle.ilike(f"%{search}%"))

    query = query.order_by(Module.libelle, Permission.libelle)
    permissions = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total_query = db.query(Permission).join(Module, Permission.module_id == Module.id)
    if module_id:
        total_query = total_query.filter(Permission.module_id == module_id)
    if search:
        total_query = total_query.filter(Permission.libelle.ilike(f"%{search}%"))
    total = total_query.count()

    permission_data = [
        {
            "id": str(permission.id),
            "libelle": permission.libelle,
            "description": permission.description,
            "statut": permission.statut,
            "module": {
                "id": str(permission.module.id),
                "libelle": permission.module.libelle,
            },
            "created_at": permission.created_at,
        }
        for permission in permissions
    ]

    return {
        "success": True,
        "data": {
            "permissions": permission_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Permissions récupérées avec succès"
    }


@router.post("/permissions")
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée une nouvelle permission
    """
    # Vérifier si l'utilisateur a la permission de créer des permissions
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des permissions"
        )

    # Vérifier si le module existe
    module = db.query(Module).filter(Module.id == permission_data.module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module non trouvé"
        )

    # Vérifier si la permission existe déjà
    existing_permission = db.query(Permission).filter(Permission.libelle == permission_data.libelle).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une permission avec le libellé '{permission_data.libelle}' existe déjà"
        )

    # Créer la permission
    nouvelle_permission = Permission(
        libelle=permission_data.libelle,
        module_id=permission_data.module_id,
        description=permission_data.description,
        statut=permission_data.statut
    )

    db.add(nouvelle_permission)
    db.commit()
    db.refresh(nouvelle_permission)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="creation_permission",
        description=f"Permission '{nouvelle_permission.libelle}' créé par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(nouvelle_permission.id),
            "libelle": nouvelle_permission.libelle,
            "description": nouvelle_permission.description,
            "module_id": nouvelle_permission.module_id,
            "statut": nouvelle_permission.statut,
            "created_at": nouvelle_permission.created_at,
        },
        "message": "Permission créée avec succès"
    }


@router.get("/companies")
def get_companies(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    statut: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Récupère toutes les compagnies
    """
    # Vérifier si l'utilisateur a la permission de gérer les compagnies
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_compagnies"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux compagnies"
        )

    query = db.query(Compagnie)

    if statut:
        query = query.filter(Compagnie.statut == statut)
    if search:
        query = query.filter(Compagnie.nom.ilike(f"%{search}%"))

    query = query.order_by(Compagnie.created_at.desc())
    companies = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total_query = db.query(Compagnie)
    if statut:
        total_query = total_query.filter(Compagnie.statut == statut)
    if search:
        total_query = total_query.filter(Compagnie.nom.ilike(f"%{search}%"))
    total = total_query.count()

    company_data = [
        {
            "id": str(company.id),
            "code": company.code,
            "nom": company.nom,
            "adresse": company.adresse,
            "telephone": company.telephone,
            "email": company.email,
            "nif": company.nif,
            "statut": company.statut,
            "pays_id": str(company.pays_id) if company.pays_id else None,
            "devise_principale": company.devise_principale,
            "created_at": company.created_at,
            "updated_at": company.updated_at
        }
        for company in companies
    ]

    return {
        "success": True,
        "data": {
            "companies": company_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Compagnies récupérées avec succès"
    }


@router.post("/companies")
def create_company(
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    nif: Optional[str] = None,
    pays_id: Optional[str] = None,
    devise_principale: Optional[str] = "MGA",
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée une nouvelle compagnie
    """
    # Vérifier si l'utilisateur a la permission de créer des compagnies
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_compagnies"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des compagnies"
        )

    # Vérifier si le code existe déjà
    existing_company = db.query(Compagnie).filter(Compagnie.code == code).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une compagnie avec le code '{code}' existe déjà"
        )

    # Créer la compagnie
    nouvelle_compagnie = Compagnie(
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        email=email,
        nif=nif,
        pays_id=pays_id,
        devise_principale=devise_principale
    )

    db.add(nouvelle_compagnie)
    db.commit()
    db.refresh(nouvelle_compagnie)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="creation_compagnie",
        description=f"Compagnie '{nouvelle_compagnie.nom}' créée par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(nouvelle_compagnie.id),
            "code": nouvelle_compagnie.code,
            "nom": nouvelle_compagnie.nom,
            "adresse": nouvelle_compagnie.adresse,
            "telephone": nouvelle_compagnie.telephone,
            "email": nouvelle_compagnie.email,
            "nif": nouvelle_compagnie.nif,
            "statut": nouvelle_compagnie.statut,
            "pays_id": str(nouvelle_compagnie.pays_id) if nouvelle_compagnie.pays_id else None,
            "devise_principale": nouvelle_compagnie.devise_principale,
            "created_at": nouvelle_compagnie.created_at,
            "updated_at": nouvelle_compagnie.updated_at
        },
        "message": "Compagnie créée avec succès"
    }


@router.get("/stations")
def get_stations(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Récupère toutes les stations
    """
    # Vérifier si l'utilisateur a la permission de gérer les stations
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux stations"
        )

    query = db.query(Station).join(Compagnie, Station.compagnie_id == Compagnie.id)

    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Station.statut == statut)
    if search:
        query = query.filter(Station.nom.ilike(f"%{search}%"))

    query = query.order_by(Station.created_at.desc())
    stations = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total_query = db.query(Station).join(Compagnie, Station.compagnie_id == Compagnie.id)
    if compagnie_id:
        total_query = total_query.filter(Station.compagnie_id == compagnie_id)
    if statut:
        total_query = total_query.filter(Station.statut == statut)
    if search:
        total_query = total_query.filter(Station.nom.ilike(f"%{search}%"))
    total = total_query.count()

    station_data = [
        {
            "id": str(station.id),
            "compagnie_id": str(station.compagnie_id),
            "compagnie_nom": station.compagnie.nom,
            "code": station.code,
            "nom": station.nom,
            "adresse": station.adresse,
            "telephone": station.telephone,
            "email": station.email,
            "pays_id": str(station.pays_id) if station.pays_id else None,
            "statut": station.statut,
            "created_at": station.created_at,
        }
        for station in stations
    ]

    return {
        "success": True,
        "data": {
            "stations": station_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Stations récupérées avec succès"
    }


@router.post("/stations")
def create_station(
    compagnie_id: str,
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    pays_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée une nouvelle station
    """
    # Vérifier si l'utilisateur a la permission de créer des stations
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_stations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des stations"
        )

    # Vérifier que la compagnie existe
    compagnie = db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
    if not compagnie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compagnie non trouvée"
        )

    # Vérifier si le code existe déjà
    existing_station = db.query(Station).filter(Station.code == code).first()
    if existing_station:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une station avec le code '{code}' existe déjà"
        )

    # Créer la station
    nouvelle_station = Station(
        compagnie_id=compagnie_id,
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        email=email,
        pays_id=pays_id
    )

    db.add(nouvelle_station)
    db.commit()
    db.refresh(nouvelle_station)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="creation_station",
        description=f"Station '{nouvelle_station.nom}' créée par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(nouvelle_station.id),
            "compagnie_id": str(nouvelle_station.compagnie_id),
            "code": nouvelle_station.code,
            "nom": nouvelle_station.nom,
            "adresse": nouvelle_station.adresse,
            "telephone": nouvelle_station.telephone,
            "email": nouvelle_station.email,
            "pays_id": str(nouvelle_station.pays_id) if nouvelle_station.pays_id else None,
            "statut": nouvelle_station.statut,
            "created_at": nouvelle_station.created_at,
        },
        "message": "Station créée avec succès"
    }


@router.get("/logs")
def get_security_logs(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    type_evenement: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,    # format: YYYY-MM-DD
    end_date: Optional[str] = None,     # format: YYYY-MM-DD
    skip: int = 0,
    limit: int = 10
):
    """
    Récupère les logs de sécurité avec options de filtrage
    """
    # Vérifier si l'utilisateur a la permission de consulter les logs
    if not RBACService.check_permission_by_user_obj(db, current_user, "consulter_logs"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour consulter les logs"
        )

    # Convertir les dates en objets datetime si elles sont fournies
    from datetime import datetime
    start_datetime = None
    end_datetime = None

    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date start_date invalide. Utilisez YYYY-MM-DD"
            )

    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date end_date invalide. Utilisez YYYY-MM-DD"
            )

    logs = JournalisationService.get_security_logs(
        db,
        type_evenement=type_evenement,
        utilisateur_id=user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        skip=skip,
        limit=limit
    )

    # Compter le total pour la pagination
    # Pour une implémentation complète, nous utiliserions une requête COUNT
    total = len(logs) if logs else 0

    return {
        "success": True,
        "data": {
            "logs": [
                {
                    "id": str(log.id),
                    "type_evenement": log.type_evenement,
                    "description": log.description,
                    "utilisateur_id": str(log.utilisateur_id) if log.utilisateur_id else None,
                    "utilisateur_nom": "N/A",  # TODO: Récupérer le nom de l'utilisateur
                    "ip_utilisateur": log.ip_utilisateur,
                    "date": log.created_at.isoformat() if log.created_at else None,
                    "statut": log.statut
                }
                for log in logs
            ],
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Logs de sécurité récupérés avec succès"
    }