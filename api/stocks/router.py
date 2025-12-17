from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.produit import Produit as ProduitModel
from ..models.stock import StockProduit as StockModel
from ..models.lot import Lot
from ..models.mouvement_stock import MouvementStock
from ..models.user import User
from . import schemas, lot_schemas
from ..services.mouvement_stock_service import enregistrer_mouvement_stock
from ..utils.pagination import PaginatedResponse
from ..utils.filters import StockFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user_security
from ..auth.journalisation import log_user_action
from datetime import datetime
import uuid

router = APIRouter()
security = HTTPBearer()

# Endpoint pour la gestion des stocks initiaux
@router.post("/stocks_initiaux", response_model=schemas.StockInitialResponse)
async def creer_stock_initial(
    stock_initial: schemas.StockInitialCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Seuls les rôles gerant_compagnie et utilisateur_compagnie avec les bonnes permissions peuvent créer des stocks initiaux
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create initial stocks"
        )

    # Vérifier que le produit existe
    produit = db.query(ProduitModel).filter(ProduitModel.id == stock_initial.produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Vérifier que le produit a un stock (n'est pas un service)
    if not produit.has_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer un stock initial pour un produit de type service"
        )

    # Vérifier que la station appartient à la compagnie de l'utilisateur
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == stock_initial.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    # Vérifier que le stock n'existe pas déjà pour ce produit et cette station
    stock_existant = db.query(StockModel).filter(
        StockModel.produit_id == stock_initial.produit_id,
        StockModel.station_id == stock_initial.station_id
    ).first()
    
    if stock_existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le stock initial existe déjà pour ce produit et cette station"
        )

    # Créer l'enregistrement de stock
    nouveau_stock = StockModel(
        produit_id=stock_initial.produit_id,
        station_id=stock_initial.station_id,
        quantite_theorique=stock_initial.quantite_initiale
    )

    # Créer l'écriture d'historique pour le mouvement initial via le service
    enregistrer_mouvement_stock(
        db,
        produit_id=stock_initial.produit_id,
        station_id=stock_initial.station_id,
        type_mouvement="stock_initial",
        quantite=stock_initial.quantite_initiale,
        cout_unitaire=stock_initial.cout_unitaire,
        utilisateur_id=current_user.id,
        module_origine="stock_initial",
        reference_origine="Stock Initial"
    )

    # Commit après l'enregistrement du mouvement
    db.commit()
    db.refresh(nouveau_stock)

    # Calculer et mettre à jour le coût moyen du produit
    from ..services.cout_moyen_service import mettre_a_jour_cout_moyen_produit
    mettre_a_jour_cout_moyen_produit(db, stock_initial.produit_id, stock_initial.station_id)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="stock_initial_management",
        donnees_apres={
            'produit_id': str(nouveau_stock.produit_id),
            'station_id': str(nouveau_stock.station_id),
            'quantite': float(nouveau_stock.quantite_theorique or 0)
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Retourner le stock initial créé
    return schemas.StockInitialResponse(
        id=nouveau_stock.id,
        produit_id=nouveau_stock.produit_id,
        station_id=nouveau_stock.station_id,
        quantite=float(nouveau_stock.quantite_theorique or 0),
        date_creation=nouveau_stock.created_at
    )


# Endpoint pour la gestion des lots
@router.post("/lots", response_model=lot_schemas.LotResponse)
async def creer_lot(
    lot: lot_schemas.LotCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Seuls les rôles gerant_compagnie et utilisateur_compagnie avec les bonnes permissions peuvent créer des lots
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create lots"
        )

    # Vérifier que le produit existe
    produit = db.query(ProduitModel).filter(ProduitModel.id == lot.produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Vérifier que le produit a un stock (n'est pas un service)
    if not produit.has_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer un lot pour un produit de type service"
        )

    # Vérifier que la station appartient à la compagnie de l'utilisateur
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == lot.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    # Vérifier que le numéro de lot n'existe pas déjà pour ce produit et cette station
    lot_existant = db.query(Lot).filter(
        Lot.numero_lot == lot.numero_lot,
        Lot.produit_id == lot.produit_id,
        Lot.station_id == lot.station_id
    ).first()

    if lot_existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le numéro de lot existe déjà pour ce produit et cette station"
        )

    # Créer l'enregistrement de lot
    nouveau_lot = Lot(
        produit_id=lot.produit_id,
        station_id=lot.station_id,
        numero_lot=lot.numero_lot,
        date_fabrication=lot.date_fabrication,
        date_limite_consommation=lot.date_limite_consommation,
        quantite=lot.quantite,
        statut=lot.statut
    )

    db.add(nouveau_lot)
    db.commit()
    db.refresh(nouveau_lot)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="lot_management",
        donnees_apres={
            'produit_id': str(nouveau_lot.produit_id),
            'station_id': str(nouveau_lot.station_id),
            'numero_lot': nouveau_lot.numero_lot,
            'quantite': float(nouveau_lot.quantite or 0)
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return nouveau_lot


@router.get("/lots/{lot_id}", response_model=lot_schemas.LotResponse)
async def get_lot_par_id(
    lot_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Vérifier que l'utilisateur a accès à cette compagnie
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access lots"
        )

    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")

    # Vérifier que l'utilisateur a accès à la station du lot
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == lot.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    return lot


@router.get("/produits/{produit_id}/lots", response_model=List[lot_schemas.LotResponse])
async def get_lots_par_produit(
    produit_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Vérifier que l'utilisateur a accès à cette compagnie
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access lots"
        )

    # Vérifier que le produit appartient à la compagnie de l'utilisateur
    produit = db.query(ProduitModel).filter(
        ProduitModel.id == produit_id,
        ProduitModel.station_id.in_(
            db.query(Station.id).filter(Station.compagnie_id == current_user.compagnie_id).subquery()
        )
    ).first()

    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé ou non autorisé")

    lots = db.query(Lot).filter(Lot.produit_id == produit_id).offset(skip).limit(limit).all()
    return lots


@router.put("/lots/{lot_id}", response_model=lot_schemas.LotResponse)
async def update_lot(
    lot_id: uuid.UUID,
    lot_update: lot_schemas.LotUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Seuls les rôles gerant_compagnie et utilisateur_compagnie avec les bonnes permissions peuvent mettre à jour des lots
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update lots"
        )

    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")

    # Vérifier que l'utilisateur a accès à la station du lot
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == lot.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    # Log the action before update
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="lot_management",
        donnees_avant={
            'id': str(lot.id),
            'produit_id': str(lot.produit_id),
            'station_id': str(lot.station_id),
            'numero_lot': lot.numero_lot,
            'quantite': float(lot.quantite or 0),
            'statut': lot.statut
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = lot_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lot, field, value)

    db.commit()
    db.refresh(lot)
    return lot


@router.delete("/lots/{lot_id}")
async def delete_lot(
    lot_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Seuls les rôles gerant_compagnie et utilisateur_compagnie avec les bonnes permissions peuvent supprimer des lots
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete lots"
        )

    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot non trouvé")

    # Vérifier que l'utilisateur a accès à la station du lot
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == lot.station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="lot_management",
        donnees_avant={
            'id': str(lot.id),
            'produit_id': str(lot.produit_id),
            'station_id': str(lot.station_id),
            'numero_lot': lot.numero_lot,
            'quantite': float(lot.quantite or 0),
            'statut': lot.statut
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(lot)
    db.commit()
    return {"message": f"Lot {lot_id} supprimé avec succès"}