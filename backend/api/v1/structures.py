from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from database.database import get_db
from models.structures import Pays, Compagnie, Station
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService
from utils.security import get_current_user
from models.structures import Utilisateur

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "SuccessFuel Structures API"}


@router.get("/pays")
def get_pays(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    statut: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Récupère tous les pays
    """
    # Vérifier si l'utilisateur a la permission de gérer les pays
    if not RBACService.check_permission_by_user_obj(db, current_user, "lire_pays"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour accéder aux pays"
        )

    query = db.query(Pays)

    if statut:
        query = query.filter(Pays.statut == statut)
    if search:
        query = query.filter(Pays.nom_pays.ilike(f"%{search}%"))

    query = query.order_by(Pays.nom_pays)
    pays_list = query.offset(skip).limit(limit).all()

    # Compter le total pour la pagination
    total_query = db.query(Pays)
    if statut:
        total_query = total_query.filter(Pays.statut == statut)
    if search:
        total_query = total_query.filter(Pays.nom_pays.ilike(f"%{search}%"))
    total = total_query.count()

    pays_data = [
        {
            "id": str(pays.id),
            "code_pays": pays.code_pays,
            "nom_pays": pays.nom_pays,
            "devise_principale": pays.devise_principale,
            "taux_tva_par_defaut": float(pays.taux_tva_par_defaut) if pays.taux_tva_par_defaut else 0,
            "systeme_comptable": pays.systeme_comptable,
            "date_application_tva": pays.date_application_tva.isoformat() if pays.date_application_tva else None,
            "statut": pays.statut,
            "created_at": pays.created_at.isoformat() if pays.created_at else None,
            "updated_at": pays.updated_at.isoformat() if pays.updated_at else None
        }
        for pays in pays_list
    ]

    return {
        "success": True,
        "data": {
            "pays": pays_data,
            "pagination": {
                "page": (skip // limit) + 1 if limit != 0 else 1,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if limit != 0 else 0
            }
        },
        "message": "Pays récupérés avec succès"
    }


@router.post("/pays")
def create_pays(
    code_pays: str,
    nom_pays: str,
    devise_principale: str,
    taux_tva_par_defaut: Optional[float] = 0,
    systeme_comptable: Optional[str] = "OHADA",
    date_application_tva: Optional[str] = None,
    statut: Optional[str] = "Actif",
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Crée un nouveau pays
    """
    # Vérifier si l'utilisateur a la permission de créer des pays
    if not RBACService.check_permission_by_user_obj(db, current_user, "creer_pays"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour créer des pays"
        )

    # Vérifier si le code du pays existe déjà
    existing_pays = db.query(Pays).filter(Pays.code_pays == code_pays).first()
    if existing_pays:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un pays avec le code '{code_pays}' existe déjà"
        )

    # Convertir la date si fournie
    from datetime import datetime
    date_application = None
    if date_application_tva:
        try:
            date_application = datetime.strptime(date_application_tva, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

    # Créer le pays
    nouveau_pays = Pays(
        code_pays=code_pays,
        nom_pays=nom_pays,
        devise_principale=devise_principale,
        taux_tva_par_defaut=taux_tva_par_defaut,
        systeme_comptable=systeme_comptable,
        date_application_tva=date_application,
        statut=statut
    )

    db.add(nouveau_pays)
    db.commit()
    db.refresh(nouveau_pays)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="creation_pays",
        description=f"Pays '{nouveau_pays.nom_pays}' créé par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(nouveau_pays.id),
            "code_pays": nouveau_pays.code_pays,
            "nom_pays": nouveau_pays.nom_pays,
            "devise_principale": nouveau_pays.devise_principale,
            "taux_tva_par_defaut": float(nouveau_pays.taux_tva_par_defaut) if nouveau_pays.taux_tva_par_defaut else 0,
            "systeme_comptable": nouveau_pays.systeme_comptable,
            "date_application_tva": nouveau_pays.date_application_tva.isoformat() if nouveau_pays.date_application_tva else None,
            "statut": nouveau_pays.statut,
            "created_at": nouveau_pays.created_at.isoformat() if nouveau_pays.created_at else None,
            "updated_at": nouveau_pays.updated_at.isoformat() if nouveau_pays.updated_at else None
        },
        "message": "Pays créé avec succès"
    }


@router.put("/pays/{pays_id}")
def update_pays(
    pays_id: str,
    code_pays: Optional[str] = None,
    nom_pays: Optional[str] = None,
    devise_principale: Optional[str] = None,
    taux_tva_par_defaut: Optional[float] = None,
    systeme_comptable: Optional[str] = None,
    date_application_tva: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Met à jour un pays
    """
    # Vérifier si l'utilisateur a la permission de modifier des pays
    if not RBACService.check_permission_by_user_obj(db, current_user, "modifier_pays"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour modifier des pays"
        )

    # Récupérer le pays
    pays = db.query(Pays).filter(Pays.id == pays_id).first()
    if not pays:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pays non trouvé"
        )

    # Vérifier si le nouveau code existe déjà (sauf si c'est le même que l'actuel)
    if code_pays and code_pays != pays.code_pays:
        existing_pays = db.query(Pays).filter(Pays.code_pays == code_pays).first()
        if existing_pays:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un pays avec le code '{code_pays}' existe déjà"
            )

    # Mettre à jour les champs
    if code_pays is not None:
        pays.code_pays = code_pays
    if nom_pays is not None:
        pays.nom_pays = nom_pays
    if devise_principale is not None:
        pays.devise_principale = devise_principale
    if taux_tva_par_defaut is not None:
        pays.taux_tva_par_defaut = taux_tva_par_defaut
    if systeme_comptable is not None:
        pays.systeme_comptable = systeme_comptable
    if statut is not None:
        pays.statut = statut

    # Gérer la date d'application de la TVA
    if date_application_tva is not None:
        from datetime import datetime
        try:
            if date_application_tva == "":
                pays.date_application_tva = None
            else:
                date_application = datetime.strptime(date_application_tva, "%Y-%m-%d").date()
                pays.date_application_tva = date_application
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

    db.commit()
    db.refresh(pays)

    # Enregistrer l'événement de sécurité
    JournalisationService.log_security_event(
        db,
        type_evenement="modification_pays",
        description=f"Pays '{pays.nom_pays}' modifié par '{current_user.login}'",
        utilisateur_id=str(current_user.id)
    )

    return {
        "success": True,
        "data": {
            "id": str(pays.id),
            "code_pays": pays.code_pays,
            "nom_pays": pays.nom_pays,
            "devise_principale": pays.devise_principale,
            "taux_tva_par_defaut": float(pays.taux_tva_par_defaut) if pays.taux_tva_par_defaut else 0,
            "systeme_comptable": pays.systeme_comptable,
            "date_application_tva": pays.date_application_tva.isoformat() if pays.date_application_tva else None,
            "statut": pays.statut,
            "created_at": pays.created_at.isoformat() if pays.created_at else None,
            "updated_at": pays.updated_at.isoformat() if pays.updated_at else None
        },
        "message": "Pays mis à jour avec succès"
    }