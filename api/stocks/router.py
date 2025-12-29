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
@router.post("/stocks_initiaux",
             response_model=schemas.StockInitialResponse,
             summary="Créer un stock initial",
             description="Crée un stock initial pour un produit spécifique dans une station. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. Le stock initial est essentiel pour commencer la gestion des stocks dans le système.",
             tags=["Stock initial"])
async def creer_stock_initial(
    stock_initial: schemas.StockInitialCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée un stock initial pour un produit spécifique dans une station.

    Args:
        stock_initial (schemas.StockInitialCreate): Les détails du stock initial à créer
        request (Request): La requête HTTP
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.StockInitialResponse: Détails du stock initial créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires,
                       si le produit n'existe pas, si le produit n'a pas de stock,
                       si la station n'appartient pas à la compagnie de l'utilisateur,
                       ou si un stock initial existe déjà pour ce produit et cette station
    """
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

    # Vérifier si un stock existe déjà pour ce produit et cette station
    stock_existant = db.query(StockModel).filter(
        StockModel.produit_id == stock_initial.produit_id,
        StockModel.station_id == stock_initial.station_id
    ).first()

    # Si un stock existe déjà, on met à jour les informations existantes
    # Cela permet de modifier les informations du stock initial si nécessaire
    if stock_existant:
        # Mettre à jour les informations du stock existant
        if stock_initial.quantite_initiale is not None:
            stock_existant.quantite_theorique = stock_initial.quantite_initiale
        if stock_initial.prix_vente is not None:
            from decimal import Decimal
            stock_existant.prix_vente = Decimal(str(stock_initial.prix_vente))

        # Mettre à jour la date de dernier calcul
        from datetime import datetime, timezone
        stock_existant.date_dernier_calcul = datetime.now(timezone.utc)

        # Enregistrer les modifications
        db.commit()
        db.refresh(stock_existant)

        # Mettre à jour le coût moyen pondéré du produit
        from ..services.cout_moyen_service import mettre_a_jour_cout_moyen_produit_initial
        if stock_initial.cout_unitaire is not None:
            mettre_a_jour_cout_moyen_produit_initial(db, stock_initial.produit_id, stock_initial.station_id, stock_initial.cout_unitaire)

        # Retourner le stock mis à jour
        return schemas.StockInitialResponse(
            id=stock_existant.id,
            produit_id=stock_existant.produit_id,
            station_id=stock_existant.station_id,
            quantite=float(stock_existant.quantite_theorique or 0),
            date_creation=stock_existant.created_at
        )

    # S'assurer que les IDs sont valides avant de les utiliser
    import uuid
    try:
        produit_uuid = uuid.UUID(str(stock_initial.produit_id)) if isinstance(stock_initial.produit_id, (str, uuid.UUID)) else stock_initial.produit_id
        station_uuid = uuid.UUID(str(stock_initial.station_id)) if isinstance(stock_initial.station_id, (str, uuid.UUID)) else stock_initial.station_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format d'identifiant invalide: {str(e)}"
        )

    # Créer l'écriture d'historique pour le mouvement initial via le service
    # Cela créera automatiquement l'enregistrement dans stock_produit via le trigger
    enregistrer_mouvement_stock(
        db,
        produit_id=produit_uuid,
        station_id=station_uuid,
        type_mouvement="stock_initial",
        quantite=stock_initial.quantite_initiale,
        cout_unitaire=stock_initial.cout_unitaire,
        utilisateur_id=current_user.id,
        module_origine="stock_initial",
        reference_origine="Stock Initial",
        prix_vente=stock_initial.prix_vente,  # Ajouter le prix de vente
        seuil_stock_min=stock_initial.seuil_stock_min  # Ajouter le seuil de stock minimum
    )

    # Mettre à jour le coût moyen pondéré du produit pour ce stock initial
    from ..services.cout_moyen_service import mettre_a_jour_cout_moyen_produit_initial
    if stock_initial.cout_unitaire is not None:
        mettre_a_jour_cout_moyen_produit_initial(db, produit_uuid, station_uuid, stock_initial.cout_unitaire)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="stock_initial_management",
        donnees_apres={
            'produit_id': str(stock_initial.produit_id),
            'station_id': str(stock_initial.station_id),
            'quantite': float(stock_initial.quantite_initiale or 0)
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Récupérer le stock nouvellement créé/mis à jour
    stock_final = db.query(StockModel).filter(
        StockModel.produit_id == stock_initial.produit_id,
        StockModel.station_id == stock_initial.station_id
    ).first()

    # Vérifier que l'objet a été récupéré
    if stock_final is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du stock après création"
        )

    # Récupérer explicitement les valeurs dont on a besoin pour la réponse
    # pour éviter l'erreur "Instance is not persistent within this Session"
    stock_id = stock_final.id
    produit_id = stock_final.produit_id
    station_id = stock_final.station_id
    quantite = float(stock_final.quantite_theorique or 0)
    date_creation = stock_final.created_at

    # Retourner le stock initial créé en utilisant les valeurs stockées localement
    return schemas.StockInitialResponse(
        id=stock_id,
        produit_id=produit_id,
        station_id=station_id,
        quantite=quantite,
        date_creation=date_creation
    )


# Endpoint pour la gestion des lots
@router.post("/lots",
             response_model=lot_schemas.LotResponse,
             summary="Créer un nouveau lot",
             description="Crée un nouveau lot pour un produit spécifique dans une station. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. Utilisé pour des produits avec gestion de lots et péremption.",
             tags=["lots"])
async def creer_lot(
    lot: lot_schemas.LotCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée un nouveau lot pour un produit spécifique dans une station.

    Args:
        lot (lot_schemas.LotCreate): Les détails du lot à créer
        request (Request): La requête HTTP
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        lot_schemas.LotResponse: Détails du lot créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires,
                       si le produit n'existe pas, si le produit n'a pas de stock,
                       si la station n'appartient pas à la compagnie de l'utilisateur,
                       ou si le numéro de lot existe déjà pour ce produit et cette station
    """
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


@router.get("/lots/{lot_id}",
            response_model=lot_schemas.LotResponse,
            summary="Récupérer un lot par ID",
            description="Récupère les détails d'un lot spécifique par son identifiant unique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur. L'utilisateur doit avoir accès à la station à laquelle le lot est affecté.",
            tags=["lots"])
async def get_lot_par_id(
    lot_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère les détails d'un lot spécifique par son identifiant unique.

    Args:
        lot_id (uuid.UUID): L'identifiant du lot à récupérer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        lot_schemas.LotResponse: Détails du lot demandé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le lot n'existe pas
    """
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


@router.get("/produits/{produit_id}/lots",
            response_model=List[lot_schemas.LotResponse],
            summary="Récupérer les lots d'un produit",
            description="Récupère la liste des lots associés à un produit spécifique. Permet de paginer les résultats. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur et l'accès aux stations du produit.",
            tags=["lots"])
async def get_lots_par_produit(
    produit_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère la liste des lots associés à un produit spécifique.

    Args:
        produit_id (uuid.UUID): L'identifiant du produit
        skip (int): Nombre de lots à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de lots à retourner (défaut: 100)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        List[lot_schemas.LotResponse]: Liste des lots associés au produit

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le produit n'existe pas
    """
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


@router.put("/lots/{lot_id}",
            response_model=lot_schemas.LotResponse,
            summary="Mettre à jour un lot",
            description="Met à jour les détails d'un lot existant. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. La modification affecte la gestion des stocks et les alertes de péremption.",
            tags=["lots"])
async def update_lot(
    lot_id: uuid.UUID,
    lot_update: lot_schemas.LotUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Met à jour les détails d'un lot existant.

    Args:
        lot_id (uuid.UUID): L'identifiant du lot à mettre à jour
        lot_update (lot_schemas.LotUpdate): Nouvelles valeurs pour les champs du lot
        request (Request): La requête HTTP
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        lot_schemas.LotResponse: Détails du lot mis à jour

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le lot n'existe pas
    """
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


@router.delete("/lots/{lot_id}",
               summary="Supprimer un lot",
               description="Supprime un lot existant. Nécessite des droits de gérant de compagnie ou administrateur. La suppression affecte les calculs de stock et les alertes de péremption.",
               tags=["lots"])
async def delete_lot(
    lot_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprime un lot existant.

    Args:
        lot_id (uuid.UUID): L'identifiant du lot à supprimer
        request (Request): La requête HTTP
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Message de confirmation de la suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le lot n'existe pas
    """
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