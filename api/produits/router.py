from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_, func
from ..database import get_db
from ..models import Produit as ProduitModel, FamilleProduit as FamilleProduitModel, Lot as LotModel
from ..models.stock import StockProduit as StockModel
from ..models.compagnie import Station
from . import schemas
from ..utils.pagination import PaginatedResponse
from ..utils.filters import ProduitFilterParams, FamilleProduitFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user_security
from ..auth.journalisation import log_user_action
from ..auth.permission_check import check_company_access
from datetime import datetime, timezone

router = APIRouter()
security = HTTPBearer()

# Famille Produit endpoints
@router.get("/familles",
             response_model=PaginatedResponse[schemas.FamilleProduitResponse],
             summary="Récupérer les familles de produits",
             description="Récupère la liste paginée des familles de produits avec possibilité de filtrage et de tri. Les permissions varient selon le rôle de l'utilisateur. Uniquement accessible aux gérants de compagnie et utilisateurs avec permissions appropriées.",
             tags=["Produits"])
async def get_familles(
    filters: FamilleProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste paginée des familles de produits

    Args:
        filters: Paramètres de filtrage et de pagination
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Une réponse paginée contenant les familles de produits

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can view product families list
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view product families"
        )

    from sqlalchemy.orm import joinedload

    # Construction de la requête avec les filtres
    query = db.query(FamilleProduitModel)

    # Charger les familles parentes avec la requête pour éviter les requêtes N+1
    query = query.options(joinedload(FamilleProduitModel.famille_parente))

    # Application des filtres spécifiques
    query = apply_specific_filters(query, filters, FamilleProduitModel)

    # S'assurer que l'utilisateur ne voit que les familles de sa compagnie
    query = query.filter(FamilleProduitModel.compagnie_id == current_user.compagnie_id)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(FamilleProduitModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    familles = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=familles,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )

@router.post("/familles",
             response_model=schemas.FamilleProduitResponse,
             summary="Créer une nouvelle famille de produits",
             description="Permet de créer une nouvelle famille de produits. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. La famille créée permet d'organiser les produits par catégories.",
             tags=["Produits"])
async def create_famille(
    famille: schemas.FamilleProduitCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer une nouvelle famille de produits

    Args:
        famille: Données de la famille à créer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        La famille de produits nouvellement créée

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si une famille avec ce code existe déjà
    """
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can create families
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create product families"
        )

    # Check if famille with code already exists for the same company
    db_famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.code == famille.code,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if db_famille:
        raise HTTPException(status_code=400, detail="Famille with this code already exists for your company")

    # Create the famille with the current user's company_id
    famille_data = famille.dict()
    famille_data['compagnie_id'] = current_user.compagnie_id

    # Check if the parent family exists and belongs to the same company
    if famille_data.get('famille_parente_id'):
        parent_famille = db.query(FamilleProduitModel).filter(
            FamilleProduitModel.id == famille_data['famille_parente_id'],
            FamilleProduitModel.compagnie_id == current_user.compagnie_id
        ).first()
        if not parent_famille:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La famille parente n'existe pas ou n'appartient pas à votre compagnie"
            )

    db_famille = FamilleProduitModel(**famille_data)
    db.add(db_famille)
    db.commit()
    db.refresh(db_famille)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="famille_produit_management",
        donnees_apres={
            'id': str(db_famille.id),
            'nom': db_famille.nom,
            'description': db_famille.description,
            'code': db_famille.code,
            'compagnie_id': str(db_famille.compagnie_id),
            'famille_parente_id': str(db_famille.famille_parente_id) if db_famille.famille_parente_id else None
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_famille

@router.get("/familles/racines",
             response_model=PaginatedResponse[schemas.FamilleProduitResponse],
             summary="Récupérer les familles de produits racines",
             description="Récupère la liste paginée des familles de produits racines (sans parent) avec possibilité de filtrage et de tri. Les permissions varient selon le rôle de l'utilisateur. Uniquement accessible aux gérants de compagnie et utilisateurs avec permissions appropriées.",
             tags=["Produits"])
async def get_familles_racines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste paginée des familles de produits racines (sans parent)

    Args:
        skip: Nombre d'éléments à sauter pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Une réponse paginée contenant les familles de produits racines

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can view product families list
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view product families"
        )

    from sqlalchemy.orm import joinedload

    # Construction de la requête pour les familles racines (sans parent) avec compagnie_id NULL
    query = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.famille_parente_id == None,
        FamilleProduitModel.compagnie_id.is_(None)
    )

    # Charger les familles parentes avec la requête pour éviter les requêtes N+1
    query = query.options(joinedload(FamilleProduitModel.famille_parente))

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    familles_racines = query.offset(skip).limit(limit).all()

    # Pour contourner l'erreur de validation Pydantic avec compagnie_id NULL,
    # nous allons créer des objets FamilleProduitResponse avec un compagnie_id vide
    from . import schemas
    familles_racines_avec_compagnie_id = []
    for famille in familles_racines:
        famille_dict = {
            'id': str(famille.id),
            'nom': famille.nom,
            'description': famille.description,
            'code': famille.code,
            'compagnie_id': '',  # Utiliser une chaîne vide au lieu de None
            'famille_parente_id': str(famille.famille_parente_id) if famille.famille_parente_id else None,
            'famille_parente': famille.famille_parente
        }
        familles_racines_avec_compagnie_id.append(schemas.FamilleProduitResponse(**famille_dict))

    # Détermination s'il y a plus d'éléments
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=familles_racines_avec_compagnie_id,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/familles/{famille_id}",
             response_model=schemas.FamilleProduitResponse,
             summary="Récupérer une famille de produits par ID",
             description="Récupère les détails d'une famille de produits spécifique par son identifiant unique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
             tags=["Produits"])
async def get_famille_by_id(
    famille_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer une famille de produits par son identifiant

    Args:
        famille_id: Identifiant unique de la famille de produits
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Les détails de la famille de produits

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si la famille n'existe pas
    """
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access product families"
        )

    famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.id == famille_id,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille not found or does not belong to your company")
    return famille

@router.put("/familles/{famille_id}",
             response_model=schemas.FamilleProduitResponse,
             summary="Mettre à jour une famille de produits",
             description="Met à jour les informations d'une famille de produits existante. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. La modification affecte les produits associés à cette famille.",
             tags=["Produits"])
async def update_famille(
    famille_id: str,  # UUID
    famille: schemas.FamilleProduitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour une famille de produits existante

    Args:
        famille_id: Identifiant unique de la famille à mettre à jour
        famille: Données de mise à jour de la famille
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        La famille de produits mise à jour

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si la famille n'existe pas,
                       ou si une famille avec ce code existe déjà
    """
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can update families
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update product families"
        )

    db_famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.id == famille_id,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille not found or does not belong to your company")

    # Check if famille with code already exists (excluding current famille)
    existing_famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.code == famille.code,
        FamilleProduitModel.id != famille_id,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if existing_famille:
        raise HTTPException(status_code=400, detail="Famille with this code already exists for your company")

    # Check if the parent family exists and belongs to the same company (if updating parent)
    update_data = famille.dict(exclude_unset=True)
    if 'famille_parente_id' in update_data and update_data['famille_parente_id']:
        parent_famille = db.query(FamilleProduitModel).filter(
            FamilleProduitModel.id == update_data['famille_parente_id'],
            FamilleProduitModel.compagnie_id == current_user.compagnie_id
        ).first()
        if not parent_famille:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La famille parente n'existe pas ou n'appartient pas à votre compagnie"
            )
    elif 'famille_parente_id' in update_data and update_data['famille_parente_id'] is None:
        # Allow setting parent to None (for root families)
        pass

    # Log the action before update
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="famille_produit_management",
        donnees_avant=db_famille.__dict__,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    for field, value in update_data.items():
        setattr(db_famille, field, value)

    db.commit()
    db.refresh(db_famille)
    return db_famille

@router.delete("/familles/{famille_id}",
               summary="Supprimer une famille de produits",
               description="Supprime une famille de produits existante. Seuls les utilisateurs avec les permissions appropriées peuvent supprimer une famille de produits. La suppression n'est possible que si la famille ne contient pas de sous-familles ni de produits associés.",
               tags=["Produits"])
async def delete_famille(
    famille_id: str,  # UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprimer une famille de produits existante

    Args:
        famille_id: Identifiant unique de la famille à supprimer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Un message de confirmation de suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si la famille n'existe pas,
                       ou si la famille contient des sous-familles ou des produits associés
    """
    current_user = get_current_user_security(credentials, db)
    # According to specifications, gerant_compagnie and utilisateur_compagnie with permissions can delete families
    if current_user.role not in ["admin", "gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete product families"
        )

    famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.id == famille_id,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille not found or does not belong to your company")

    # Check if the famille has sub-familles
    sous_familles = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.famille_parente_id == famille_id
    ).count()
    if sous_familles > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer une famille qui contient des sous-familles"
        )

    # Check if the famille has products associated
    from ..models.produit import Produit
    produits = db.query(Produit).filter(Produit.famille_id == famille_id).count()
    if produits > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer une famille qui contient des produits"
        )

    # Log the action before deletion
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="famille_produit_management",
        donnees_avant={
            'id': str(famille.id),
            'nom': famille.nom,
            'description': famille.description,
            'code': famille.code,
            'compagnie_id': str(famille.compagnie_id),
            'famille_parente_id': str(famille.famille_parente_id) if famille.famille_parente_id else None
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(famille)
    db.commit()
    return {"message": "Famille de produits deleted successfully"}

@router.get("/familles/{famille_id}/enfants",
             response_model=PaginatedResponse[schemas.FamilleProduitEnfant],
             summary="Récupérer les familles enfants d'une famille parente",
             description="Récupère la liste paginée des familles enfants associées à une famille parente spécifique. Permet de visualiser la structure hiérarchique des familles de produits.",
             tags=["Produits"])
async def get_famille_enfants(
    famille_id: str,  # UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer les familles enfants d'une famille parente

    Args:
        famille_id: Identifiant unique de la famille parente
        skip: Nombre d'éléments à sauter pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Une réponse paginée contenant les familles enfants de la famille spécifiée

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    # Vérifier que l'utilisateur a les permissions nécessaires
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view product family children"
        )

    # Construction de la requête pour les familles enfants
    query = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.famille_parente_id == famille_id,
        FamilleProduitModel.compagnie_id == current_user.compagnie_id
    )

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    familles_enfants = query.offset(skip).limit(limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=familles_enfants,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

# Produit endpoints
@router.get("/",
             response_model=PaginatedResponse[schemas.ProduitResponse],
             summary="Récupérer les produits",
             description="Récupère la liste paginée des produits avec possibilité de filtrage et de tri. Les permissions varient selon le rôle de l'utilisateur. Les gérants de compagnie ont accès à tous les produits de leur compagnie, tandis que les autres utilisateurs n'ont accès qu'aux produits des stations auxquelles ils sont affectés.",
             tags=["Produits"])
async def get_produits(
    filters: ProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste paginée des produits

    Args:
        filters: Paramètres de filtrage et de pagination
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Une réponse paginée contenant les produits

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view products"
        )

    # Construction de la requête de base
    query = db.query(ProduitModel)

    # Pour les utilisateurs autres que gerant_compagnie, vérifier les affectations de station
    if current_user.role != "gerant_compagnie":
        # Les utilisateur_compagnie ne peuvent voir que les produits des stations auxquelles ils sont affectés
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        stations_autorisees = db.query(AffectationUtilisateurStation.station_id).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id
        ).subquery()

        query = query.filter(ProduitModel.compagnie_id == current_user.compagnie_id)
    else:
        # Les gerant_compagnie peuvent voir tous les produits de leur compagnie
        query = query.filter(ProduitModel.compagnie_id == current_user.compagnie_id)

    # Application des filtres spécifiques (après avoir filtré les stations autorisées)
    # Mais avant, vérifions si un filtre de station_id est appliqué
    if filters.station_id:
        # Si un utilisateur_compagnie tente de filtrer par une station spécifique,
        # vérifier qu'il a accès à cette station
        if current_user.role != "gerant_compagnie":
            from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
            utilisateur_station = db.query(AffectationUtilisateurStation).filter(
                AffectationUtilisateurStation.utilisateur_id == current_user.id,
                AffectationUtilisateurStation.station_id == filters.station_id
            ).first()

            if not utilisateur_station:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access this station"
                )
        else:
            # Pour les gerant_compagnie, vérifier que la station appartient à leur compagnie
            station = db.query(Station).filter(
                Station.id == filters.station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()

            if not station:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access this station"
                )

        # Maintenant appliquer le filtre de station_id (converti en filtre par compagnie)
        # On vérifie que la station appartient à la même compagnie que le produit
        from ..models.station import Station
        station = db.query(Station).filter(
            Station.id == filters.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this station or station does not exist"
            )

        # Filtrer les produits de la compagnie de l'utilisateur
        query = query.filter(ProduitModel.compagnie_id == current_user.compagnie_id)
    else:
        # Si aucun station_id spécifique n'est fourni, appliquer les autres filtres
        # Exclure le station_id des filtres spécifiques pour ne pas le réappliquer
        temp_filters = filters.copy()
        temp_filters.station_id = None
        query = apply_specific_filters(query, temp_filters, ProduitModel)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(ProduitModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    produits = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=produits,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )


@router.get("/produits_avec_stock",
             response_model=PaginatedResponse[schemas.ProduitStockResponse],
             summary="Récupérer les produits avec leur stock",
             description="Récupère la liste paginée des produits avec leurs quantités en stock. Permet de visualiser l'inventaire en temps réel selon les stations auxquelles l'utilisateur a accès. Les gérants de compagnie ont accès à tous les stocks de leur compagnie, tandis que les autres utilisateurs n'ont accès qu'aux stocks des stations auxquelles ils sont affectés.",
             tags=["Produits"])
async def get_produits_avec_stock(
    filters: ProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste paginée des produits avec leur stock

    Args:
        filters: Paramètres de filtrage et de pagination
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Une réponse paginée contenant les produits avec leur quantité en stock

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view products with stock"
        )

    from ..models.stock import StockProduit as StockModel

    # Construction d'une sous-requête pour les produits autorisés
    produits_autorises = db.query(ProduitModel.id, ProduitModel.compagnie_id)

    # Pour les utilisateurs autres que gerant_compagnie, vérifier les affectations de station
    if current_user.role != "gerant_compagnie":
        # Les utilisateur_compagnie ne peuvent voir que les produits de leur compagnie
        produits_autorises = produits_autorises.filter(ProduitModel.compagnie_id == current_user.compagnie_id)
    else:
        # Les gerant_compagnie peuvent voir tous les produits de leur compagnie
        produits_autorises = produits_autorises.filter(ProduitModel.compagnie_id == current_user.compagnie_id)

    # Application des filtres de produit
    if filters.station_id:
        # Si un utilisateur_compagnie tente de filtrer par une station spécifique,
        # vérifier qu'il a accès à cette station
        if current_user.role != "gerant_compagnie":
            from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
            utilisateur_station = db.query(AffectationUtilisateurStation).filter(
                AffectationUtilisateurStation.utilisateur_id == current_user.id,
                AffectationUtilisateurStation.station_id == filters.station_id
            ).first()

            if not utilisateur_station:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access this station"
                )
        else:
            # Pour les gerant_compagnie, vérifier que la station appartient à leur compagnie
            station = db.query(Station).filter(
                Station.id == filters.station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()

            if not station:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access this station"
                )

        # Maintenant appliquer le filtre de station_id (converti en filtre par compagnie)
        # On vérifie que la station appartient à la même compagnie que le produit
        from ..models.station import Station
        station = db.query(Station).filter(
            Station.id == filters.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this station or station does not exist"
            )

        # Filtrer les produits de la compagnie de l'utilisateur
        produits_autorises = produits_autorises.filter(ProduitModel.compagnie_id == current_user.compagnie_id)
    else:
        # Si aucun station_id spécifique n'est fourni, appliquer les autres filtres
        # Exclure le station_id des filtres spécifiques pour ne pas le réappliquer
        temp_filters = filters.copy()
        temp_filters.station_id = None
        for field, value in temp_filters.dict(exclude={'skip', 'limit', 'sort_by', 'sort_order', 'q'}).items():
            if value is not None and field != 'station_id':
                model_attr = getattr(ProduitModel, field, None)
                if model_attr is not None:
                    produits_autorises = produits_autorises.filter(model_attr == value)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(ProduitModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                produits_autorises = produits_autorises.order_by(sort_field.desc())
            else:
                produits_autorises = produits_autorises.order_by(sort_field.asc())

    # Maintenant, faire la requête finale en combinant les produits autorisés avec la jointure
    # Utiliser une sous-requête pour les produits autorisés
    produits_subquery = produits_autorises.subquery()

    # Créer une requête qui combine les stocks avec les produits
    # On utilise la table stock_produit comme table principale et on joint avec la table produit
    query = db.query(
        StockModel,
        ProduitModel
    ).join(
        ProduitModel,
        StockModel.produit_id == ProduitModel.id
    ).join(
        produits_subquery,
        produits_subquery.c.id == ProduitModel.id
    )

    # Filtrer par station si spécifié
    if filters.station_id:
        query = query.filter(StockModel.station_id == filters.station_id)

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    resultats = query.offset(filters.skip).limit(filters.limit).all()

    # Transformer les résultats en objets ProduitStockResponse
    produits_avec_stock = []
    for stock, produit in resultats:
        produit_dict = {c.name: getattr(produit, c.name) for c in produit.__table__.columns}
        produit_dict['quantite_stock'] = float(stock.quantite_theorique or 0)
        produit_dict['prix_vente'] = float(stock.prix_vente or 0)
        produit_dict['seuil_stock_min'] = float(stock.seuil_stock_min or 0)
        produit_dict['prix_achat'] = float(stock.cout_moyen_pondere or 0)
        produits_avec_stock.append(schemas.ProduitStockResponse(**produit_dict))

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=produits_avec_stock,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )

@router.post("/",
             response_model=schemas.ProduitResponse,
             summary="Créer un nouveau produit",
             description="Permet de créer un nouveau produit dans le système de gestion. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. Le produit est affecté à la station de l'utilisateur ou à la première station de la compagnie.",
             tags=["Produits"])
async def create_produit(
    produit: schemas.ProduitCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer un nouveau produit

    Args:
        produit: Données du produit à créer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Le produit nouvellement créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si un produit avec ce code existe déjà
    """
    current_user = get_current_user_security(credentials, db)
    # According to specifications, gerant_compagnie and utilisateur_compagnie with permissions can create products
    if current_user.role not in ["admin", "gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create products"
        )

    # Check if produit with same name already exists (case-insensitive) for the same company
    db_produit_name = db.query(ProduitModel).filter(
        func.lower(ProduitModel.nom) == func.lower(produit.nom),
        ProduitModel.compagnie_id == current_user.compagnie_id
    ).first()

    if db_produit_name:
        # If a product with the same name already exists for this company, return it instead of creating a new one
        return db_produit_name

    # Check if produit with code already exists for the same company
    db_produit = db.query(ProduitModel).filter(
        ProduitModel.code == produit.code,
        ProduitModel.compagnie_id == current_user.compagnie_id
    ).first()
    if db_produit:
        raise HTTPException(status_code=400, detail="Produit with this code already exists for your company")

    # Check if produit with code_barre already exists (code_barre is required)
    # Only check if code_barre is not empty or None
    if produit.code_barre and produit.code_barre.strip() != "":
        db_produit_barcode = db.query(ProduitModel).filter(ProduitModel.code_barre == produit.code_barre).first()
        if db_produit_barcode:
            raise HTTPException(status_code=400, detail="Produit with this code_barre already exists")

    # Déterminer la station à laquelle affecter le produit
    if current_user.role == "gerant_compagnie":
        # Les gérants de compagnie peuvent affecter le produit à n'importe quelle station de leur compagnie
        # Pour l'instant, on affecte à la station de l'utilisateur s'il en a une, ou on attend un paramètre
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id
        ).first()

        if utilisateur_station:
            # Si l'utilisateur est affecté à une station, on peut utiliser cette station
            station_id = utilisateur_station.station_id
        else:
            # Sinon, le gérant devrait spécifier la station dans une future version
            # Pour l'instant, on ne peut pas créer de produit sans déterminer la station
            from ..models.compagnie import Station
            stations = db.query(Station).filter(Station.compagnie_id == current_user.compagnie_id).all()
            if not stations:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Aucune station disponible pour cette compagnie"
                )
            # Pour l'instant, utiliser la première station (à améliorer dans une future version)
            station_id = stations[0].id
    else:
        # Les autres utilisateurs doivent être affectés à une station
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id
        ).first()

        if not utilisateur_station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'est affecté à aucune station"
            )

        station_id = utilisateur_station.station_id

    # Ajouter le compagnie_id au dictionnaire du produit
    produit_dict = produit.dict()
    produit_dict['compagnie_id'] = current_user.compagnie_id

    # Convertir les valeurs vides de code_barre en None pour éviter la contrainte d'unicité
    if 'code_barre' in produit_dict and produit_dict['code_barre'] is not None and produit_dict['code_barre'].strip() == "":
        produit_dict['code_barre'] = None

    db_produit = ProduitModel(**produit_dict)
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="produit_management",
        donnees_apres={c.name: getattr(db_produit, c.name) for c in db_produit.__table__.columns},
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_produit

@router.get("/{produit_id}",
             response_model=schemas.ProduitResponse,
             summary="Récupérer un produit par ID",
             description="Récupère les détails d'un produit spécifique par son identifiant unique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur. L'utilisateur doit avoir accès à la station à laquelle le produit est affecté.",
             tags=["Produits"])
async def get_produit_by_id(
    produit_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer un produit par son identifiant

    Args:
        produit_id: Identifiant unique du produit
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Les détails du produit

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le produit n'existe pas
    """
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access products"
        )

    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Vérifier si l'utilisateur a le droit d'accéder au produit
    # Les gerants de compagnie ont accès à tous les produits de leur compagnie
    if current_user.role == "gerant_compagnie":
        # Vérifier que le produit appartient à la compagnie de l'utilisateur
        if produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this product"
            )
    else:
        # Les autres utilisateurs doivent appartenir à la même compagnie que le produit
        if produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'a pas accès à ce produit"
            )

    return produit

@router.put("/{produit_id}",
             response_model=schemas.ProduitResponse,
             summary="Mettre à jour un produit",
             description="Met à jour les informations d'un produit existant. Nécessite des droits de gérant de compagnie ou utilisateur avec permissions appropriées. La modification affecte les ventes futures et les calculs de stock.",
             tags=["Produits"])
async def update_produit(
    produit_id: str,  # UUID
    produit: schemas.ProduitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour un produit existant

    Args:
        produit_id: Identifiant unique du produit à mettre à jour
        produit: Données de mise à jour du produit
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Le produit mis à jour

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le produit n'existe pas
    """
    current_user = get_current_user_security(credentials, db)
    # According to specifications, gerant_compagnie and utilisateur_compagnie with permissions can update products
    if current_user.role not in ["admin", "gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update products"
        )

    db_produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not db_produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Check if the user has access to this station (the station of the product)
    from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
    # Vérifier si l'utilisateur a le droit d'accéder au produit
    # Les gerants de compagnie ont accès à tous les produits de leur compagnie
    if current_user.role == "gerant_compagnie":
        # Vérifier que le produit appartient à la compagnie de l'utilisateur
        if db_produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this product"
            )
    else:
        # Les autres utilisateurs doivent appartenir à la même compagnie que le produit
        if db_produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'a pas accès à ce produit"
            )

    # Log the action before update
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="produit_management",
        donnees_avant={c.name: getattr(db_produit, c.name) for c in db_produit.__table__.columns},
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = produit.dict(exclude_unset=True)
    # Remove compagnie_id from update data to prevent changing it
    update_data.pop('compagnie_id', None)

    # Check if code is being updated and if it already exists for the same company
    if 'code' in update_data:
        existing_produit = db.query(ProduitModel).filter(
            ProduitModel.code == update_data['code'],
            ProduitModel.compagnie_id == current_user.compagnie_id,
            ProduitModel.id != produit_id  # Exclude current product
        ).first()
        if existing_produit:
            raise HTTPException(status_code=400, detail="Produit with this code already exists for your company")

    # Check if code_barre is being updated and if it already exists for another product
    if 'code_barre' in update_data:
        existing_produit = db.query(ProduitModel).filter(
            ProduitModel.code_barre == update_data['code_barre'],
            ProduitModel.id != produit_id  # Exclude current product
        ).first()
        if existing_produit:
            raise HTTPException(status_code=400, detail="Produit with this code_barre already exists")

    for field, value in update_data.items():
        setattr(db_produit, field, value)

    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/{produit_id}",
               summary="Supprimer un produit",
               description="Supprime un produit existant. Seuls les utilisateurs avec les permissions appropriées peuvent supprimer un produit.",
               tags=["Produits"])
async def delete_produit(
    produit_id: str,  # UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprimer un produit existant

    Args:
        produit_id: Identifiant unique du produit à supprimer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Un message de confirmation de suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le produit n'existe pas
    """
    current_user = get_current_user_security(credentials, db)
    # According to specifications, gerant_compagnie and utilisateur_compagnie with permissions can delete products
    if current_user.role not in ["admin", "gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete products"
        )

    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Vérifier si l'utilisateur a le droit d'accéder au produit
    # Les gerants de compagnie ont accès à tous les produits de leur compagnie
    if current_user.role == "gerant_compagnie":
        # Vérifier que le produit appartient à la compagnie de l'utilisateur
        if produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this product"
            )
    else:
        # Les autres utilisateurs doivent appartenir à la même compagnie que le produit
        if produit.compagnie_id != current_user.compagnie_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'a pas accès à ce produit"
            )

    # Log the action before deletion
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="produit_management",
        donnees_avant={c.name: getattr(produit, c.name) for c in produit.__table__.columns},
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    db.delete(produit)
    db.commit()
    return {"message": "Produit deleted successfully"}


@router.get("/{produit_id}/lots",
             response_model=List[schemas.LotResponse],
             summary="Récupérer les lots d'un produit",
             description="Récupère la liste des lots associés à un produit spécifique. Nécessite des droits de gérant de compagnie ou administrateur. Uniquement disponible pour les produits avec gestion de stock.",
             tags=["Produits"])
async def get_lots(
    produit_id: str,  # UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer les lots d'un produit spécifique

    Args:
        produit_id: Identifiant du produit dont on veut récupérer les lots
        skip: Nombre d'éléments à ignorer (pour la pagination)
        limit: Nombre maximum d'éléments à retourner (pour la pagination)
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Liste des lots associés au produit

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view lots"
        )

    lots = db.query(LotModel).filter(LotModel.produit_id == produit_id).offset(skip).limit(limit).all()
    return lots

@router.post("/{produit_id}/lots",
             response_model=schemas.LotResponse,
             summary="[DÉPRÉCIÉ] Créer un nouveau lot pour un produit",
             description="[DÉPRÉCIÉ] Crée un nouveau lot associé à un produit spécifique. Utiliser create_lot avec le schéma LotCreate. Nécessite des droits de gérant de compagnie ou administrateur.",
             tags=["Produits"])
async def create_lot_old(
    produit_id: str,  # UUID
    numero_lot: str,
    quantite: int,
    date_production: str = None,
    date_peremption: str = None,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer un nouveau lot pour un produit spécifique (ancienne version)
    NOTE: Cette fonction est dépréciée, utiliser create_lot avec le schéma LotCreate

    Args:
        produit_id: Identifiant du produit auquel associer le lot
        numero_lot: Numéro du lot
        quantite: Quantité du lot
        date_production: Date de production du lot (optionnelle)
        date_peremption: Date de péremption du lot (optionnelle)
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Le lot nouvellement créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si le produit n'existe pas,
                       ou si un lot avec ce numéro existe déjà
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create lots"
        )

    # Convertir les dates si elles sont fournies
    from datetime import datetime, timezone
    date_prod = datetime.fromisoformat(date_production) if date_production else None
    date_per = datetime.fromisoformat(date_peremption) if date_peremption else None

    # Vérifier que le produit existe
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Vérifier que le lot n'existe pas déjà
    existing_lot = db.query(LotModel).filter(
        LotModel.numero_lot == numero_lot,
        LotModel.produit_id == produit_id
    ).first()
    if existing_lot:
        raise HTTPException(status_code=400, detail="Lot with this number already exists for this product")

    # Créer le lot
    from sqlalchemy.dialects.postgresql import UUID
    import uuid
    nouveau_lot = LotModel(
        id=uuid.uuid4(),
        produit_id=produit_id,
        numero_lot=numero_lot,
        quantite=quantite,
        date_production=date_prod,
        date_peremption=date_per,
        date_creation=datetime.now(timezone.utc)
    )

    db.add(nouveau_lot)
    db.commit()
    db.refresh(nouveau_lot)

    # Log the action
    if request:
        log_user_action(
            db,
            utilisateur_id=str(current_user.id),
            type_action="create",
            module_concerne="lot_management",
            donnees_apres=nouveau_lot.__dict__,
            ip_utilisateur=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    return nouveau_lot


@router.post("/{produit_id}/lots",
             response_model=schemas.LotResponse,
             summary="Créer un nouveau lot pour un produit",
             description="Crée un nouveau lot associé à un produit spécifique. Nécessite des droits de gérant de compagnie ou administrateur. Uniquement disponible pour les produits avec gestion de stock.",
             tags=["Produits"])
async def create_lot(
    produit_id: str,  # UUID
    lot_data: schemas.LotCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer un nouveau lot pour un produit spécifique

    Args:
        produit_id: Identifiant du produit auquel associer le lot
        lot_data: Données du lot à créer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Le lot nouvellement créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si le produit n'existe pas,
                       si le produit n'a pas de stock, ou si un lot avec ce numéro existe déjà
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create lots"
        )

    # Vérifier que le produit existe
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Vérifier que le produit a un stock (n'est pas un service)
    if not produit.has_stock:
        raise HTTPException(
            status_code=status.HTTP_400,
            detail="Impossible de créer un lot pour un produit de type service (n'a pas de stock)"
        )

    # Vérifier que le lot n'existe pas déjà
    existing_lot = db.query(LotModel).filter(
        LotModel.numero_lot == lot_data.numero_lot,
        LotModel.produit_id == produit_id
    ).first()
    if existing_lot:
        raise HTTPException(status_code=400, detail="Lot with this number already exists for this product")

    # Convertir les dates si elles sont fournies
    from datetime import datetime, timezone
    date_prod = datetime.fromisoformat(lot_data.date_production) if lot_data.date_production else None
    date_per = datetime.fromisoformat(lot_data.date_peremption) if lot_data.date_peremption else None

    # Créer le lot
    from sqlalchemy.dialects.postgresql import UUID
    import uuid
    nouveau_lot = LotModel(
        id=uuid.uuid4(),
        produit_id=produit_id,
        numero_lot=lot_data.numero_lot,
        quantite=lot_data.quantite,
        date_production=date_prod,
        date_peremption=date_per,
        date_creation=datetime.now(timezone.utc)
    )

    db.add(nouveau_lot)
    db.commit()
    db.refresh(nouveau_lot)

    # Log the action
    if request:
        log_user_action(
            db,
            utilisateur_id=str(current_user.id),
            type_action="create",
            module_concerne="lot_management",
            donnees_apres=nouveau_lot.__dict__,
            ip_utilisateur=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    # Retourner les données dans le format attendu
    return {
        'produit_id': str(nouveau_lot.produit_id),
        'numero_lot': nouveau_lot.numero_lot,
        'quantite': nouveau_lot.quantite,
        'date_production': nouveau_lot.date_production.isoformat() if nouveau_lot.date_production else None,
        'date_peremption': nouveau_lot.date_peremption.isoformat() if nouveau_lot.date_peremption else None
    }

@router.get("/{produit_id}/lots/{lot_id}",
             response_model=schemas.LotResponse,
             summary="Récupérer un lot par ID",
             description="Récupère les détails d'un lot spécifique par son identifiant unique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur. L'utilisateur doit avoir accès à la station du produit associé.",
             tags=["Produits"])
async def get_lot_by_id(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer un lot spécifique par son identifiant

    Args:
        produit_id: Identifiant du produit auquel le lot est associé
        lot_id: Identifiant unique du lot
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Les détails du lot

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou si le lot n'existe pas
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access lots"
        )

    lot = db.query(LotModel).filter(
        LotModel.produit_id == produit_id,
        LotModel.id == lot_id
    ).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    # Retourner les données dans le format attendu
    return {
        'produit_id': str(lot.produit_id),
        'numero_lot': lot.numero_lot,
        'quantite': lot.quantite,
        'date_production': lot.date_production.isoformat() if lot.date_production else None,
        'date_peremption': lot.date_peremption.isoformat() if lot.date_peremption else None
    }

@router.put("/{produit_id}/lots/{lot_id}",
             response_model=schemas.LotResponse,
             summary="Mettre à jour un lot",
             description="Met à jour les informations d'un lot existant. Nécessite des droits de gérant de compagnie ou administrateur. La modification affecte la gestion des stocks et les alertes de péremption.",
             tags=["Produits"])
async def update_lot(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    lot_data: schemas.LotUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour un lot existant

    Args:
        produit_id: Identifiant du produit auquel le lot est associé
        lot_id: Identifiant unique du lot à mettre à jour
        lot_data: Données de mise à jour du lot
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Les données mises à jour du lot

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si le lot n'existe pas,
                       ou si le produit associé est un service (sans stock)
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update lots"
        )

    lot = db.query(LotModel).filter(
        LotModel.produit_id == produit_id,
        LotModel.id == lot_id
    ).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    # Vérifier que le produit associé existe et a un stock
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit or not produit.has_stock:
        raise HTTPException(
            status_code=status.HTTP_400,
            detail="Impossible de modifier un lot pour un produit de type service (n'a pas de stock)"
        )

    # Mettre à jour les champs seulement si fournis
    if lot_data.quantite is not None:
        lot.quantite = lot_data.quantite
    if lot_data.date_peremption:
        from datetime import datetime, timezone
        lot.date_peremption = datetime.fromisoformat(lot_data.date_peremption)

    # Log the action before update
    if request:
        log_user_action(
            db,
            utilisateur_id=str(current_user.id),
            type_action="update",
            module_concerne="lot_management",
            donnees_avant=lot.__dict__,
            ip_utilisateur=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    db.commit()
    db.refresh(lot)

    # Retourner les données dans le format attendu
    return {
        'quantite': lot.quantite,
        'date_peremption': lot.date_peremption.isoformat() if lot.date_peremption else None
    }

@router.delete("/{produit_id}/lots/{lot_id}",
               summary="Supprimer un lot",
               description="Supprime un lot existant. Nécessite des droits de gérant de compagnie ou administrateur. La suppression affecte les calculs de stock et les alertes de péremption.",
               tags=["Produits"])
async def delete_lot(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprimer un lot existant

    Args:
        produit_id: Identifiant du produit auquel le lot est associé
        lot_id: Identifiant unique du lot à supprimer
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Un message de confirmation de suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires, si le lot n'existe pas,
                       ou si le produit associé est un service (sans stock)
    """
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete lots"
        )

    lot = db.query(LotModel).filter(
        LotModel.produit_id == produit_id,
        LotModel.id == lot_id
    ).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    # Vérifier que le produit associé existe et a un stock
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit or not produit.has_stock:
        raise HTTPException(
            status_code=status.HTTP_400,
            detail="Impossible de supprimer un lot pour un produit de type service (n'a pas de stock)"
        )

    # Log the action before deletion
    if request:
        log_user_action(
            db,
            utilisateur_id=str(current_user.id),
            type_action="delete",
            module_concerne="lot_management",
            donnees_avant=lot.__dict__,
            ip_utilisateur=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    db.delete(lot)
    db.commit()
    return {"message": "Lot deleted successfully"}


@router.get("/par_station/{station_id}",
             response_model=List[schemas.ProduitStockResponse],
             summary="Récupérer les produits avec stock par station",
             description="Récupère tous les produits avec leur stock pour une station spécifique. Permet de visualiser l'inventaire d'une station précise. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur : les gérants de compagnie ont accès à toutes les stations de leur compagnie, les autres utilisateurs n'ont accès qu'aux stations auxquelles ils sont affectés.",
             tags=["Produits"])
async def get_produits_par_station(
    station_id: str,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer tous les produits avec leur stock pour une station spécifique

    Args:
        station_id: Identifiant de la station pour laquelle récupérer les produits
        request: Requête HTTP entrante
        db: Session de base de données
        credentials: Informations d'authentification de l'utilisateur

    Returns:
        Liste des produits avec leur quantité en stock pour la station spécifiée

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires ou n'a pas accès à la station
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier les permissions
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view products with stock by station"
        )

    # Vérifier que la station existe et appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette station"
        )

    # Vérifier si l'utilisateur est autorisé à accéder à cette station
    # Pour les utilisateur_compagnie, vérifier s'il est affecté à cette station
    if current_user.role == "utilisateur_compagnie":
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id,
            AffectationUtilisateurStation.station_id == station_id
        ).first()

        if not utilisateur_station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'êtes pas affecté à cette station"
            )

    # Récupérer les produits avec leur stock pour la station spécifiée
    # On utilise la table stock_produit comme table principale et on joint avec la table produit
    query = db.query(StockModel, ProduitModel).join(
        ProduitModel,
        StockModel.produit_id == ProduitModel.id
    ).filter(
        StockModel.station_id == station_id  # Filtrer par la station spécifiée
    ).filter(
        ProduitModel.compagnie_id == current_user.compagnie_id
    ).filter(
        ProduitModel.has_stock == True  # On ne retourne que les produits qui ont du stock
    )

    resultats = query.all()

    produits_avec_stock = []
    for stock, produit in resultats:
        produit_dict = {c.name: getattr(produit, c.name) for c in produit.__table__.columns}
        # Ajouter les informations de stock
        produit_dict['quantite_stock'] = float(stock.quantite_theorique or 0)
        produit_dict['prix_vente'] = float(stock.prix_vente or 0)
        produit_dict['seuil_stock_min'] = float(stock.seuil_stock_min or 0)
        # Ajouter le prix d'achat (cout moyen pondéré)
        produit_dict['prix_achat'] = float(stock.cout_moyen_pondere or 0)

        produits_avec_stock.append(schemas.ProduitStockResponse(**produit_dict))

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="read",
        module_concerne="produit_management",
        donnees_apres={'compagnie_id': current_user.compagnie_id, 'nombre_produits': len(produits_avec_stock)},
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return produits_avec_stock




