from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import StockProduit as StockModel, MouvementStock as MouvementStockModel
from . import schemas
from ..utils.pagination import PaginatedResponse, BaseFilterParams
from ..utils.filters import StockFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from ..services.stock_service import mettre_a_jour_stock_produit
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/{station_id}", response_model=PaginatedResponse[schemas.StockResponse])
async def get_stocks(
    station_id: str,
    filters: StockFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que l'utilisateur a accès à cette station
    from ..auth.permission_check import check_company_access
    check_company_access(db, current_user, station_id)

    # Construction de la requête avec les filtres
    query = db.query(StockModel).filter(StockModel.station_id == station_id)

    # Application des filtres spécifiques
    query = apply_specific_filters(query, filters, StockModel)

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(StockModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    stocks = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=stocks,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )

@router.get("/{station_id}/{produit_id}", response_model=schemas.StockResponse)
async def get_stock_by_product(
    station_id: str,
    produit_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    stock = db.query(StockModel).filter(
        StockModel.station_id == station_id,
        StockModel.produit_id == produit_id
    ).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.put("/{station_id}/{produit_id}", response_model=schemas.StockUpdate)
async def update_stock(
    station_id: str,
    produit_id: str,
    stock: schemas.StockUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_stock = db.query(StockModel).filter(
        StockModel.station_id == station_id,
        StockModel.produit_id == produit_id
    ).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    update_data = stock.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stock, field, value)

    db.commit()
    db.refresh(db_stock)
    return db_stock

# Endpoints pour les mouvements de stock
@router.get("/{produit_id}/mouvements", response_model=PaginatedResponse[schemas.MouvementStockResponse])
async def get_mouvements_stock(
    produit_id: str,
    filters: BaseFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Construction de la requête avec les filtres
    query = db.query(MouvementStockModel).filter(MouvementStockModel.produit_id == produit_id)

    # Application des filtres génériques
    if filters.q:
        query = query.filter(
            MouvementStockModel.description.ilike(f"%{filters.q}%") |
            MouvementStockModel.type_mouvement.ilike(f"%{filters.q}%")
        )

    # Application du tri
    if filters.sort_by:
        sort_field = getattr(MouvementStockModel, filters.sort_by, None)
        if sort_field:
            if filters.sort_order == 'desc':
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    mouvements = query.offset(filters.skip).limit(filters.limit).all()

    # Détermination s'il y a plus d'éléments
    has_more = (filters.skip + filters.limit) < total

    return PaginatedResponse(
        items=mouvements,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
        has_more=has_more
    )

@router.post("/{station_id}/{produit_id}/mouvements")
async def create_mouvement_stock(
    station_id: str,
    produit_id: str,
    type_mouvement: str,  # "entree", "sortie", "ajustement"
    quantite: float,
    description: str = None,
    module_origine: str = None,
    reference_origine: str = None,
    utilisateur_id: str = None,
    cout_unitaire: float = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Créer un mouvement de stock
    from ..models import MouvementStock
    import uuid
    from datetime import datetime

    nouveau_mouvement = MouvementStock(
        id=uuid.uuid4(),
        produit_id=produit_id,
        station_id=station_id,  # Ajout du station_id au mouvement
        type_mouvement=type_mouvement,
        quantite=quantite,
        date_mouvement=datetime.utcnow(),  # Utilisation de la date courante
        description=description,
        module_origine=module_origine or 'stocks',
        reference_origine=reference_origine,
        utilisateur_id=utilisateur_id,
        cout_unitaire=cout_unitaire
    )

    db.add(nouveau_mouvement)
    db.commit()
    db.refresh(nouveau_mouvement)

    # Mettre à jour la quantité dans la table stock
    stock_mis_a_jour = mettre_a_jour_stock_produit(db, produit_id, station_id, quantite, type_mouvement)

    return {"message": f"Mouvement de stock {type_mouvement} de {quantite} unités enregistré", "stock_mis_a_jour": stock_mis_a_jour}
