from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.methode_paiement import MethodePaiement, TresorerieMethodePaiement
from ..models.tresorerie import Tresorerie, TresorerieStation
from ..models.compagnie import Station  # Le modèle Station est dans compagnie.py
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user
import uuid
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# Endpoints pour les méthodes de paiement
@router.get("/", response_model=List[schemas.MethodePaiementResponse])
async def get_methodes_paiement(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Récupérer les méthodes de paiement appartenant à la compagnie de l'utilisateur
    # Pour cela, on joint trésorerie -> trésorerie_station -> station
    methodes_paiement = db.query(MethodePaiement).join(
        Tresorerie,
        MethodePaiement.trésorerie_id == Tresorerie.id,
        isouter=True  # LEFT JOIN pour inclure les méthodes globales
    ).join(
        TresorerieStation,
        Tresorerie.id == TresorerieStation.trésorerie_id,
        isouter=True
    ).join(
        Station,
        TresorerieStation.station_id == Station.id,
        isouter=True
    ).filter(
        (Station.compagnie_id == current_user.compagnie_id) | (MethodePaiement.trésorerie_id.is_(None))
    ).offset(skip).limit(limit).all()

    return methodes_paiement

@router.post("/", response_model=schemas.MethodePaiementResponse)
async def create_methode_paiement(
    methode_paiement: schemas.MethodePaiementCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Si la méthode est associée à une trésorerie spécifique, vérifier que la trésorerie appartient à la compagnie
    if methode_paiement.trésorerie_id:
        # Vérifier que la trésorerie appartient à une station de la compagnie de l'utilisateur
        trésorerie_station = db.query(TresorerieStation).join(
            Station,
            TresorerieStation.station_id == Station.id
        ).filter(
            TresorerieStation.trésorerie_id == methode_paiement.trésorerie_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Vérifier que le nom est unique pour cette trésorerie (ou globalement si trésorerie_id est None)
    existing_methode = db.query(MethodePaiement).filter(
        MethodePaiement.nom == methode_paiement.nom,
        MethodePaiement.trésorerie_id == methode_paiement.trésorerie_id
    ).first()

    if existing_methode:
        raise HTTPException(status_code=400, detail="Méthode de paiement with this name already exists for this trésorerie")

    # Créer la méthode de paiement
    db_methode = MethodePaiement(**methode_paiement.dict())
    db.add(db_methode)
    db.commit()
    db.refresh(db_methode)

    return db_methode

@router.get("/{methode_paiement_id}", response_model=schemas.MethodePaiementResponse)
async def get_methode_paiement_by_id(
    methode_paiement_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == methode_paiement_id
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier que la méthode appartient à une trésorerie de la compagnie de l'utilisateur (ou est globale)
    if methode.trésorerie_id:
        trésorerie_station = db.query(TresorerieStation).join(
            Station,
            TresorerieStation.station_id == Station.id
        ).filter(
            TresorerieStation.trésorerie_id == methode.trésorerie_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=403, detail="Accès non autorisé à cette méthode de paiement")

    return methode

@router.put("/{methode_paiement_id}", response_model=schemas.MethodePaiementResponse)
async def update_methode_paiement(
    methode_paiement_id: uuid.UUID,
    methode_paiement: schemas.MethodePaiementUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    db_methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == methode_paiement_id
    ).first()

    if not db_methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier que la méthode appartient à une trésorerie de la compagnie de l'utilisateur (ou est globale)
    if db_methode.trésorerie_id:
        trésorerie_station = db.query(TresorerieStation).join(
            Station,
            TresorerieStation.station_id == Station.id
        ).filter(
            TresorerieStation.trésorerie_id == db_methode.trésorerie_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=403, detail="Accès non autorisé à cette méthode de paiement")

    update_data = methode_paiement.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_methode, field, value)

    db.commit()
    db.refresh(db_methode)
    return db_methode

@router.delete("/{methode_paiement_id}")
async def delete_methode_paiement(
    methode_paiement_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == methode_paiement_id
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier que la méthode appartient à une trésorerie de la compagnie de l'utilisateur (ou est globale)
    if methode.trésorerie_id:
        trésorerie_station = db.query(TresorerieStation).join(
            Station,
            TresorerieStation.station_id == Station.id
        ).filter(
            TresorerieStation.trésorerie_id == methode.trésorerie_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not trésorerie_station:
            raise HTTPException(status_code=403, detail="Accès non autorisé à cette méthode de paiement")

    # Ne pas supprimer, mais désactiver
    methode.actif = False
    db.commit()
    return {"message": "Méthode de paiement désactivée avec succès"}

# Endpoints pour la liaison trésorerie-méthode de paiement
@router.post("/associer/", response_model=schemas.TresorerieMethodePaiementResponse)
async def associer_methode_paiement_a_tresorerie(
    association: schemas.TresorerieMethodePaiementCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que la trésorerie appartient à la compagnie de l'utilisateur
    trésorerie_station = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        TresorerieStation.trésorerie_id == association.trésorerie_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Vérifier que la méthode de paiement existe
    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == association.methode_paiement_id
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier l'unicité de l'association
    existing_assoc = db.query(TresorerieMethodePaiement).filter(
        TresorerieMethodePaiement.trésorerie_id == association.trésorerie_id,
        TresorerieMethodePaiement.methode_paiement_id == association.methode_paiement_id
    ).first()

    if existing_assoc:
        raise HTTPException(status_code=400, detail="Association already exists")

    # Créer l'association
    db_assoc = TresorerieMethodePaiement(**association.dict())
    db.add(db_assoc)
    db.commit()
    db.refresh(db_assoc)

    return db_assoc

@router.get("/tresorerie/{tresorerie_id}", response_model=List[schemas.MethodePaiementResponse])
async def get_methodes_paiement_par_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que la trésorerie appartient à la compagnie de l'utilisateur
    trésorerie_station = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        TresorerieStation.trésorerie_id == tresorerie_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not trésorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Récupérer les méthodes de paiement associées à cette trésorerie
    # Soit directement via la colonne trésorerie_id dans la méthode de paiement
    # Soit via la table d'association TresorerieMethodePaiement
    methodes = db.query(MethodePaiement).filter(
        (MethodePaiement.trésorerie_id == tresorerie_id) |
        (
            MethodePaiement.id.in_(
                db.query(TresorerieMethodePaiement.methode_paiement_id).filter(
                    TresorerieMethodePaiement.trésorerie_id == tresorerie_id,
                    TresorerieMethodePaiement.actif == True
                )
            )
        ),
        MethodePaiement.actif == True
    ).all()

    return methodes