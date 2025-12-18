from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.methode_paiement import MethodePaiement, TresorerieMethodePaiement
from ..models.tresorerie import Tresorerie, TresorerieStation
from ..models.compagnie import Station  # Le modèle Station est dans compagnie.py
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user_security
import uuid
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# Endpoints pour les méthodes de paiement
@router.get("/",
            response_model=List[schemas.MethodePaiementResponse],
            summary="Récupérer les méthodes de paiement",
            description="Récupère la liste des méthodes de paiement avec pagination. Cet endpoint permet de consulter toutes les méthodes de paiement disponibles, y compris celles spécifiques à certaines trésoreries et celles globales à la compagnie. Nécessite une authentification valide.",
            tags=["Methodes paiement"])
async def get_methodes_paiement(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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

@router.post("/",
             response_model=schemas.MethodePaiementResponse,
             summary="Créer une nouvelle méthode de paiement",
             description="Crée une nouvelle méthode de paiement dans le système. La méthode peut être globale (non associée à une trésorerie spécifique) ou spécifique à une trésorerie. Nécessite une authentification valide et des droits d'accès appropriés à la trésorerie concernée.",
             tags=["Methodes paiement"])
async def create_methode_paiement(
    methode_paiement: schemas.MethodePaiementCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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

@router.get("/{methode_paiement_id}",
            response_model=schemas.MethodePaiementResponse,
            summary="Récupérer une méthode de paiement par ID",
            description="Récupère les détails d'une méthode de paiement spécifique par son identifiant. Permet d'obtenir toutes les informations relatives à une méthode de paiement, y compris son association éventuelle à une trésorerie. Nécessite une authentification valide et des droits d'accès appropriés.",
            tags=["Methodes paiement"])
async def get_methode_paiement_by_id(
    methode_paiement_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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

@router.put("/{methode_paiement_id}",
            response_model=schemas.MethodePaiementResponse,
            summary="Mettre à jour une méthode de paiement",
            description="Met à jour les informations d'une méthode de paiement existante. Permet de modifier les détails de la méthode de paiement, comme son nom, son type ou son état d'activation. Nécessite une authentification valide et des droits d'accès appropriés.",
            tags=["Methodes paiement"])
async def update_methode_paiement(
    methode_paiement_id: uuid.UUID,
    methode_paiement: schemas.MethodePaiementUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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

@router.delete("/{methode_paiement_id}",
                summary="Désactiver une méthode de paiement",
                description="Désactive une méthode de paiement du système. Cet endpoint effectue une suppression logique en mettant à jour le statut d'activation de la méthode. La méthode ne sera plus disponible pour les transactions mais les données historiques sont conservées. Nécessite une authentification valide et des droits d'accès appropriés.",
                tags=["Methodes paiement"])
async def delete_methode_paiement(
    methode_paiement_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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
@router.post("/associer/",
             response_model=schemas.TresorerieMethodePaiementResponse,
             summary="Associer une méthode de paiement à une trésorerie",
             description="Crée une association entre une méthode de paiement et une trésorerie spécifique. Cela permet de limiter l'utilisation de la méthode de paiement à une trésorerie précise. Nécessite une authentification valide et des droits d'accès appropriés à la trésorerie concernée.",
             tags=["Methodes paiement"])
async def associer_methode_paiement_a_tresorerie(
    association: schemas.TresorerieMethodePaiementCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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

@router.get("/tresorerie/{tresorerie_id}",
            response_model=List[schemas.MethodePaiementResponse],
            summary="Récupérer les méthodes de paiement d'une trésorerie",
            description="Récupère la liste des méthodes de paiement associées à une trésorerie spécifique. Cet endpoint permet de consulter toutes les méthodes de paiement disponibles pour une trésorerie donnée, y compris les méthodes globales. Nécessite une authentification valide et des droits d'accès appropriés à la trésorerie concernée.",
            tags=["Methodes paiement"])
async def get_methodes_paiement_par_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

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