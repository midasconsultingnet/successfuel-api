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
            description="Récupère la liste des méthodes de paiement avec pagination. Cet endpoint permet de consulter toutes les méthodes de paiement disponibles dans la compagnie de l'utilisateur. Nécessite une authentification valide.",
            tags=["Methodes paiement"])
async def get_methodes_paiement(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Récupérer les méthodes de paiement appartenant à la compagnie de l'utilisateur
    methodes_paiement = db.query(MethodePaiement).filter(
        MethodePaiement.actif == True
    ).offset(skip).limit(limit).all()

    return methodes_paiement

@router.post("/",
             response_model=schemas.MethodePaiementResponse,
             summary="Créer une nouvelle méthode de paiement",
             description="Crée une nouvelle méthode de paiement dans le système. La méthode est créée sans association à une trésorerie spécifique. Pour associer la méthode à une trésorerie, utilisez l'endpoint d'association. Nécessite une authentification valide.",
             tags=["Methodes paiement"])
async def create_methode_paiement(
    methode_paiement: schemas.MethodePaiementCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que le nom est unique au sein de la compagnie de l'utilisateur
    existing_methode = db.query(MethodePaiement).join(
        Tresorerie,
        MethodePaiement.tresorerie_id == Tresorerie.id,
        isouter=True  # LEFT JOIN pour inclure les méthodes globales
    ).join(
        TresorerieStation,
        Tresorerie.id == TresorerieStation.tresorerie_id,
        isouter=True
    ).join(
        Station,
        TresorerieStation.station_id == Station.id,
        isouter=True
    ).filter(
        MethodePaiement.nom == methode_paiement.nom,
        (Station.compagnie_id == current_user.compagnie_id) | (MethodePaiement.tresorerie_id.is_(None))
    ).first()

    if existing_methode:
        raise HTTPException(status_code=400, detail="Méthode de paiement with this name already exists in your company")

    # Créer la méthode de paiement
    db_methode = MethodePaiement(**methode_paiement.dict())
    db.add(db_methode)
    db.commit()
    db.refresh(db_methode)

    return db_methode

@router.get("/{methode_paiement_id}",
            response_model=schemas.MethodePaiementResponse,
            summary="Récupérer une méthode de paiement par ID",
            description="Récupère les détails d'une méthode de paiement spécifique par son identifiant. Permet d'obtenir toutes les informations relatives à une méthode de paiement. Nécessite une authentification valide et des droits d'accès appropriés.",
            tags=["Methodes paiement"])
async def get_methode_paiement_by_id(
    methode_paiement_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == methode_paiement_id,
        MethodePaiement.actif == True
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

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
        MethodePaiement.id == methode_paiement_id,
        MethodePaiement.actif == True
    ).first()

    if not db_methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

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
        MethodePaiement.id == methode_paiement_id,
        MethodePaiement.actif == True
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

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
    tresorerie_station = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        TresorerieStation.tresorerie_id == association.tresorerie_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Vérifier que la méthode de paiement existe
    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == association.methode_paiement_id
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier si une association existe déjà (active ou inactive)
    existing_assoc = db.query(TresorerieMethodePaiement).filter(
        TresorerieMethodePaiement.tresorerie_id == association.tresorerie_id,
        TresorerieMethodePaiement.methode_paiement_id == association.methode_paiement_id
    ).first()

    if existing_assoc:
        # Si l'association existe déjà, la réactiver si elle est inactive
        if not existing_assoc.est_actif:
            existing_assoc.est_actif = True
            db.commit()
            db.refresh(existing_assoc)
            return existing_assoc
        else:
            raise HTTPException(status_code=400, detail="Association already exists and is active")

    # Créer l'association
    db_assoc = TresorerieMethodePaiement(**association.dict())
    db.add(db_assoc)
    db.commit()
    db.refresh(db_assoc)

    return db_assoc

@router.get("/tresorerie/{tresorerie_id}",
            response_model=List[schemas.MethodePaiementTresorerieResponse],
            summary="Récupérer les méthodes de paiement d'une trésorerie",
            description="Récupère la liste des méthodes de paiement associées à une trésorerie spécifique via la table d'association. Cet endpoint permet de consulter toutes les méthodes de paiement disponibles pour une trésorerie donnée. Nécessite une authentification valide et des droits d'accès appropriés à la trésorerie concernée.",
            tags=["Methodes paiement"])
async def get_methodes_paiement_par_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la trésorerie existe et appartient à la compagnie de l'utilisateur
    # D'abord, vérifier si c'est une trésorerie globale
    tresorerie_globale = db.query(Tresorerie).filter(
        Tresorerie.id == tresorerie_id,
        Tresorerie.compagnie_id == current_user.compagnie_id
    ).first()

    # Si ce n'est pas une trésorerie globale, vérifier si c'est une trésorerie station
    tresorerie_station = None
    if not tresorerie_globale:
        tresorerie_station = db.query(TresorerieStation).join(
            Station,
            TresorerieStation.station_id == Station.id
        ).filter(
            TresorerieStation.tresorerie_id == tresorerie_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not tresorerie_station:
            raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Vérifier si la trésorerie a été trouvée soit comme globale, soit comme liée à une station
    if not tresorerie_globale and not tresorerie_station:
        raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Récupérer les associations entre méthodes de paiement et la trésorerie spécifique avec les informations de la trésorerie
    associations = db.query(TresorerieMethodePaiement, MethodePaiement, Tresorerie).join(
        MethodePaiement,
        TresorerieMethodePaiement.methode_paiement_id == MethodePaiement.id
    ).join(
        Tresorerie,
        TresorerieMethodePaiement.tresorerie_id == Tresorerie.id
    ).filter(
        TresorerieMethodePaiement.tresorerie_id == tresorerie_id,
        TresorerieMethodePaiement.est_actif == True,
        MethodePaiement.actif == True
    ).all()

    # Créer la liste des méthodes de paiement avec les informations de la trésorerie
    methodes = []
    for association, methode, tresorerie in associations:
        # Créer un objet avec les propriétés de la méthode de paiement et la trésorerie
        methode.tresorerie_id = association.tresorerie_id
        methode.tresorerie_info = tresorerie
        methodes.append(methode)

    return methodes

@router.post("/dissocier/",
             response_model=dict,
             summary="Dissocier une méthode de paiement d'une trésorerie",
             description="Supprime l'association entre une méthode de paiement et une trésorerie spécifique. Cette opération n'est possible que si l'association n'a pas de mouvements liés. Nécessite une authentification valide et des droits d'accès appropriés à la trésorerie concernée.",
             tags=["Methodes paiement"])
async def dissocier_methode_paiement_de_tresorerie(
    dissociation: schemas.TresorerieMethodePaiementDissocier,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)

    # Vérifier que la trésorerie appartient à la compagnie de l'utilisateur
    tresorerie_station = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        TresorerieStation.tresorerie_id == dissociation.tresorerie_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not tresorerie_station:
        # Vérifier si c'est une trésorerie globale
        tresorerie_globale = db.query(Tresorerie).filter(
            Tresorerie.id == dissociation.tresorerie_id,
            Tresorerie.compagnie_id == current_user.compagnie_id
        ).first()

        if not tresorerie_globale:
            raise HTTPException(status_code=404, detail="Trésorerie not found in your company")

    # Vérifier que la méthode de paiement existe
    methode = db.query(MethodePaiement).filter(
        MethodePaiement.id == dissociation.methode_paiement_id
    ).first()

    if not methode:
        raise HTTPException(status_code=404, detail="Méthode de paiement not found")

    # Vérifier que l'association existe
    association = db.query(TresorerieMethodePaiement).filter(
        TresorerieMethodePaiement.tresorerie_id == dissociation.tresorerie_id,
        TresorerieMethodePaiement.methode_paiement_id == dissociation.methode_paiement_id,
        TresorerieMethodePaiement.est_actif == True
    ).first()

    if not association:
        raise HTTPException(status_code=404, detail="Association not found")

    # Vérifier s'il y a des mouvements liés à cette association (trésorerie + méthode de paiement)
    from ..models.tresorerie import MouvementTresorerie
    mouvements_count = db.query(MouvementTresorerie).filter(
        MouvementTresorerie.methode_paiement_id == dissociation.methode_paiement_id
    ).join(
        TresorerieStation,
        MouvementTresorerie.tresorerie_station_id == TresorerieStation.id,
        isouter=True
    ).join(
        Tresorerie,
        (MouvementTresorerie.tresorerie_globale_id == Tresorerie.id) |
        (TresorerieStation.tresorerie_id == Tresorerie.id),
        isouter=True
    ).filter(
        Tresorerie.id == dissociation.tresorerie_id
    ).count()

    if mouvements_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de dissocier la méthode de paiement de la trésorerie car {mouvements_count} mouvement(s) sont liés à cette association."
        )

    # Désactiver l'association (soft delete)
    association.est_actif = False
    db.commit()

    return {"message": "Dissociation réussie", "association_id": str(association.id)}