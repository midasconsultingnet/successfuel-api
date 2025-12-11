from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Produit as ProduitModel, FamilleProduit as FamilleProduitModel, Lot as LotModel
from . import schemas
from ..utils.pagination import PaginatedResponse
from ..utils.filters import ProduitFilterParams, FamilleProduitFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_handler import get_current_user
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
    current_user = get_current_user(db, credentials.credentials)
    # Check if the user has access to this company
    # Note: For central carburant management, admin might manage carburants
    if current_user.role not in ["gerant_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view product families"
        )

    # Construction de la requête avec les filtres
    query = db.query(FamilleProduitModel)

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
    current_user = get_current_user(db, credentials.credentials)
    # Only admin users can create families according to specs
    if current_user.role not in ["admin", "super_admin"]:
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
        donnees_apres=db_famille.__dict__,
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
    current_user = get_current_user(db, credentials.credentials)
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

# Produit endpoints
@router.get("/", response_model=PaginatedResponse[schemas.ProduitResponse])
async def get_produits(
    filters: ProduitFilterParams = Depends(),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view products"
        )

    # Construction de la requête avec les filtres
    query = db.query(ProduitModel)

    # Application des filtres spécifiques
    query = apply_specific_filters(query, filters, ProduitModel)

    # S'assurer que l'utilisateur ne voit que les produits de sa compagnie
    query = query.filter(ProduitModel.compagnie_id == current_user.compagnie_id)

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

@router.post("/", response_model=schemas.ProduitResponse)
async def create_produit(
    produit: schemas.ProduitCreate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
    # According to specs, "utilisateurs de compagnie ne peuvent pas gérer (créer/modifier/supprimer) les types de carburant"
    # So only admin and gerant_compagnie can create products
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create products"
        )

    # Check if produit with code already exists
    db_produit = db.query(ProduitModel).filter(ProduitModel.code == produit.code).first()
    if db_produit:
        raise HTTPException(status_code=400, detail="Produit with this code already exists")

    db_produit = ProduitModel(**produit.dict())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)

    # Log the action
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="create",
        module_concerne="produit_management",
        donnees_apres=db_produit.__dict__,
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
    current_user = get_current_user(db, credentials.credentials)
    # Check if the user has access to this company
    if current_user.role not in ["gerant_compagnie", "utilisateur_compagnie", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access products"
        )

    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")
    return produit

@router.put("/{produit_id}", response_model=schemas.ProduitUpdate)
async def update_produit(
    produit_id: int,
    produit: schemas.ProduitUpdate,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
    # According to specs, "utilisateurs de compagnie ne peuvent pas gérer (créer/modifier/supprimer) les types de carburant"
    # So only admin and gerant_compagnie can update products
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update products"
        )

    db_produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not db_produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Log the action before update
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="update",
        module_concerne="produit_management",
        donnees_avant=db_produit.__dict__,
        ip_utilisateur=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    update_data = produit.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_produit, field, value)

    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.delete("/{produit_id}")
async def delete_produit(
    produit_id: int,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
    # According to specs, "utilisateurs de compagnie ne peuvent pas gérer (créer/modifier/supprimer) les types de carburant"
    # So only admin and gerant_compagnie can delete products
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete products"
        )

    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

    # Log the action before deletion
    log_user_action(
        db,
        utilisateur_id=str(current_user.id),
        type_action="delete",
        module_concerne="produit_management",
        donnees_avant=produit.__dict__,
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
    current_user = get_current_user(db, credentials.credentials)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view lots"
        )

    lots = db.query(LotModel).filter(LotModel.produit_id == produit_id).offset(skip).limit(limit).all()
    return lots

@router.post("/{produit_id}/lots", response_model=schemas.LotResponse)
async def create_lot(
    produit_id: str,  # UUID
    numero_lot: str,
    quantite: int,
    date_production: str = None,
    date_peremption: str = None,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
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
    current_user = get_current_user(db, credentials.credentials)
    if current_user.role not in ["admin", "gerant_compagnie"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create lots"
        )

    # Vérifier que le produit existe
    produit = db.query(ProduitModel).filter(ProduitModel.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit not found")

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
    current_user = get_current_user(db, credentials.credentials)
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
    produit_id: int,
    lot_id: int,
    lot_data: schemas.LotUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
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
    produit_id: int,
    lot_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = get_current_user(db, credentials.credentials)
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

