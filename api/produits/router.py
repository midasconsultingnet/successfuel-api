from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Produit as ProduitModel, FamilleProduit as FamilleProduitModel, Lot as LotModel
from ..models.compagnie import Station
from . import schemas
from ..utils.pagination import PaginatedResponse
from ..utils.filters import ProduitFilterParams, FamilleProduitFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user_security
from ..auth.journalisation import log_user_action
from ..auth.permission_check import check_company_access
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# Famille Produit endpoints
@router.get("/familles", response_model=PaginatedResponse[schemas.FamilleProduitResponse])
async def get_familles(
    filters: FamilleProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
    # (Supposant que FamilleProduitModel a un champ compagnie_id)
    # query = query.filter(FamilleProduitModel.compagnie_id == current_user.compagnie_id)

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

@router.post("/familles", response_model=schemas.FamilleProduitResponse)
async def create_famille(
    famille: schemas.FamilleProduitCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can create families
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create product families"
        )

    # Check if famille with code already exists
    db_famille = db.query(FamilleProduitModel).filter(FamilleProduitModel.code == famille.code).first()
    if db_famille:
        raise HTTPException(status_code=400, detail="Famille with this code already exists")

    db_famille = FamilleProduitModel(**famille.dict())
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
            'famille_parente_id': str(db_famille.famille_parente_id) if db_famille.famille_parente_id else None
        },
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return db_famille

@router.get("/familles/{famille_id}", response_model=schemas.FamilleProduitResponse)
async def get_famille_by_id(
    famille_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access product families"
        )

    famille = db.query(FamilleProduitModel).filter(FamilleProduitModel.id == famille_id).first()
    if not famille:
        raise HTTPException(status_code=404, detail="Famille not found")
    return famille

@router.put("/familles/{famille_id}", response_model=schemas.FamilleProduitResponse)
async def update_famille(
    famille_id: str,  # UUID
    famille: schemas.FamilleProduitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # gerant_compagnie and utilisateur_compagnie with permissions can update families
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update product families"
        )

    db_famille = db.query(FamilleProduitModel).filter(FamilleProduitModel.id == famille_id).first()
    if not db_famille:
        raise HTTPException(status_code=404, detail="Famille not found")

    # Check if famille with code already exists (excluding current famille)
    existing_famille = db.query(FamilleProduitModel).filter(
        FamilleProduitModel.code == famille.code,
        FamilleProduitModel.id != famille_id
    ).first()
    if existing_famille:
        raise HTTPException(status_code=400, detail="Famille with this code already exists")

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

    update_data = famille.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_famille, field, value)

    db.commit()
    db.refresh(db_famille)
    return db_famille

# Produit endpoints
@router.get("/", response_model=PaginatedResponse[schemas.ProduitResponse])
async def get_produits(
    filters: ProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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

        query = query.join(Station, ProduitModel.station_id == Station.id).filter(
            Station.id.in_(stations_autorisees)
        )
    else:
        # Les gerant_compagnie peuvent voir tous les produits de leur compagnie
        query = query.join(Station, ProduitModel.station_id == Station.id).filter(
            Station.compagnie_id == current_user.compagnie_id
        )

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

        # Maintenant appliquer le filtre de station_id
        query = query.filter(ProduitModel.station_id == filters.station_id)
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


@router.get("/produits_avec_stock", response_model=PaginatedResponse[schemas.ProduitStockResponse])
async def get_produits_avec_stock(
    filters: ProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view products with stock"
        )

    from ..models.stock import StockProduit as StockModel

    # Construction de la requête de base avec jointure entre Produit et Stock
    query = db.query(ProduitModel, StockModel.quantite_theorique).join(
        StockModel,
        (ProduitModel.id == StockModel.produit_id) & (ProduitModel.station_id == StockModel.station_id),
        isouter=True  # LEFT JOIN pour inclure les produits sans stock
    )

    # Pour les utilisateurs autres que gerant_compagnie, vérifier les affectations de station
    if current_user.role != "gerant_compagnie":
        # Les utilisateur_compagnie ne peuvent voir que les produits des stations auxquelles ils sont affectés
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        stations_autorisees = db.query(AffectationUtilisateurStation.station_id).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id
        ).subquery()

        query = query.join(Station, ProduitModel.station_id == Station.id).filter(
            Station.id.in_(stations_autorisees)
        )
    else:
        # Les gerant_compagnie peuvent voir tous les produits de leur compagnie
        query = query.join(Station, ProduitModel.station_id == Station.id).filter(
            Station.compagnie_id == current_user.compagnie_id
        )

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

        # Maintenant appliquer le filtre de station_id
        query = query.filter(ProduitModel.station_id == filters.station_id)
    else:
        # Si aucun station_id spécifique n'est fourni, appliquer les autres filtres
        # Exclure le station_id des filtres spécifiques pour ne pas le réappliquer
        temp_filters = filters.copy()
        temp_filters.station_id = None
        for field, value in temp_filters.dict(exclude={'skip', 'limit', 'sort_by', 'sort_order', 'q'}).items():
            if value is not None and field != 'station_id':
                model_attr = getattr(ProduitModel, field, None)
                if model_attr is not None:
                    query = query.filter(model_attr == value)

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
    resultats = query.offset(filters.skip).limit(filters.limit).all()

    # Transformer les résultats en objets ProduitStockResponse
    produits_avec_stock = []
    for produit, quantite_theorique in resultats:
        produit_dict = {c.name: getattr(produit, c.name) for c in produit.__table__.columns}
        produit_dict['quantite_stock'] = float(quantite_theorique or 0)  # Pour les produits sans stock, mettre 0
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

@router.post("/", response_model=schemas.ProduitResponse)
async def create_produit(
    produit: schemas.ProduitCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    # According to specifications, gerant_compagnie and utilisateur_compagnie with permissions can create products
    if current_user.role not in ["admin", "gerant_compagnie", "utilisateur_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create products"
        )

    # Check if produit with code already exists
    db_produit = db.query(ProduitModel).filter(ProduitModel.code == produit.code).first()
    if db_produit:
        raise HTTPException(status_code=400, detail="Produit with this code already exists")

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

    # Ajouter le station_id au dictionnaire du produit
    produit_dict = produit.dict()
    produit_dict['station_id'] = station_id

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

@router.get("/{produit_id}", response_model=schemas.ProduitResponse)
async def get_produit_by_id(
    produit_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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

    # Vérifier si l'utilisateur a le droit d'accéder à la station du produit
    # Les gerants de compagnie ont accès à toutes les stations de leur compagnie
    from ..models.compagnie import Station
    if current_user.role == "gerant_compagnie":
        # Vérifier que la station du produit appartient à la compagnie de l'utilisateur
        station = db.query(Station).filter(
            Station.id == produit.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this station"
            )
    else:
        # Les autres utilisateurs doivent être affectés à la station du produit
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id,
            AffectationUtilisateurStation.station_id == produit.station_id
        ).first()

        if not utilisateur_station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'est pas affecté à cette station"
            )

    return produit

@router.put("/{produit_id}", response_model=schemas.ProduitUpdate)
async def update_produit(
    produit_id: str,  # UUID
    produit: schemas.ProduitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
    # Vérifier si l'utilisateur a le droit d'accéder à la station du produit
    # Les gerants de compagnie ont accès à toutes les stations de leur compagnie
    from ..models.compagnie import Station
    if current_user.role == "gerant_compagnie":
        # Vérifier que la station du produit appartient à la compagnie de l'utilisateur
        station = db.query(Station).filter(
            Station.id == db_produit.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this station"
            )
    else:
        # Les autres utilisateurs doivent être affectés à la station du produit
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id,
            AffectationUtilisateurStation.station_id == db_produit.station_id
        ).first()

        if not utilisateur_station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'est pas affecté à cette station"
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
    # Remove station_id from update data to prevent changing it
    update_data.pop('station_id', None)
    for field, value in update_data.items():
        setattr(db_produit, field, value)

    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/{produit_id}")
async def delete_produit(
    produit_id: str,  # UUID
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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

    # Vérifier si l'utilisateur a le droit d'accéder à la station du produit
    # Les gerants de compagnie ont accès à toutes les stations de leur compagnie
    from ..models.compagnie import Station
    if current_user.role == "gerant_compagnie":
        # Vérifier que la station du produit appartient à la compagnie de l'utilisateur
        station = db.query(Station).filter(
            Station.id == produit.station_id,
            Station.compagnie_id == current_user.compagnie_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this station"
            )
    else:
        # Les autres utilisateurs doivent être affectés à la station du produit
        from ..models.affectation_utilisateur_station import AffectationUtilisateurStation
        utilisateur_station = db.query(AffectationUtilisateurStation).filter(
            AffectationUtilisateurStation.utilisateur_id == current_user.id,
            AffectationUtilisateurStation.station_id == produit.station_id
        ).first()

        if not utilisateur_station:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utilisateur n'est pas affecté à cette station"
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


@router.get("/{produit_id}/lots", response_model=List[schemas.LotResponse])
async def get_lots(
    produit_id: str,  # UUID
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view lots"
        )

    lots = db.query(LotModel).filter(LotModel.produit_id == produit_id).offset(skip).limit(limit).all()
    return lots

@router.post("/{produit_id}/lots", response_model=schemas.LotResponse)
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
    current_user = get_current_user_security(credentials, db)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create lots"
        )

    # Convertir les dates si elles sont fournies
    from datetime import datetime
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
        date_creation=datetime.utcnow()
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


@router.post("/{produit_id}/lots", response_model=schemas.LotResponse)
async def create_lot(
    produit_id: str,  # UUID
    lot_data: schemas.LotCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
    from datetime import datetime
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
        date_creation=datetime.utcnow()
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

@router.get("/{produit_id}/lots/{lot_id}", response_model=schemas.LotResponse)
async def get_lot_by_id(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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

@router.put("/{produit_id}/lots/{lot_id}", response_model=schemas.LotUpdate)
async def update_lot(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    lot_data: schemas.LotUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
        from datetime import datetime
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

@router.delete("/{produit_id}/lots/{lot_id}")
async def delete_lot(
    produit_id: str,  # UUID
    lot_id: str,  # UUID
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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


@router.get("/par_station", response_model=List[schemas.ProduitStockResponse])
async def get_produits_par_station(
    station_id: str,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer tous les produits avec leur stock pour une station spécifique
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

    # Récupérer les produits avec leur stock pour cette station
    query = db.query(ProduitModel, StockModel).outerjoin(
        StockModel,
        and_(
            ProduitModel.id == StockModel.produit_id,
            ProduitModel.station_id == StockModel.station_id
        )
    ).filter(
        ProduitModel.station_id == station_id
    ).filter(
        ProduitModel.has_stock == True  # On ne retourne que les produits qui ont du stock
    )

    resultats = query.all()

    produits_avec_stock = []
    for produit, stock in resultats:
        produit_dict = {c.name: getattr(produit, c.name) for c in produit.__table__.columns}
        # Ajouter la quantité de stock
        if stock:
            produit_dict['quantite_stock'] = float(stock.quantite_theorique or 0)
        else:
            produit_dict['quantite_stock'] = 0.0

        produits_avec_stock.append(schemas.ProduitStockResponse(**produit_dict))

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="read",
        module_concerne="produit_management",
        donnees_apres={'station_id': station_id, 'nombre_produits': len(produits_avec_stock)},
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return produits_avec_stock



