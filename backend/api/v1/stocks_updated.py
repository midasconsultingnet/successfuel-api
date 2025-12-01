from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.database import get_db
from models.stocks import Stock as StockModel, StockMouvement as StockMouvementModel
from pydantic import BaseModel
from datetime import date
from utils.access_control import require_permission, prohibit_super_admin_access, create_permission_dependency
from utils.dependencies import get_current_user
from models.structures import Utilisateur

router = APIRouter(
    tags=["stocks_updated"],
    responses={404: {"description": "Endpoint non trouvé"}}
)

# Modèles Pydantic pour la table stocks
class StockBase(BaseModel):
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: str
    stock_theorique: float = 0.0
    stock_reel: Optional[float] = None
    compagnie_id: Optional[str] = None

class StockCreate(StockBase):
    est_initial: Optional[bool] = False

class StockUpdate(BaseModel):
    stock_theorique: Optional[float] = None
    stock_reel: Optional[float] = None

class StockResponse(StockBase):
    id: str
    est_initial: Optional[bool] = False
    ecart_stock: Optional[float] = None
    created_at: str
    updated_at: Optional[str] = None

    # Champs qui seront ajoutés via le script d'initialisation
    stock_minimal: Optional[float] = 0.0
    stock_maximal: Optional[float] = None
    prix_unitaire: Optional[float] = 0.0
    date_initialisation: Optional[date] = None
    utilisateur_initialisation: Optional[str] = None
    observation_initialisation: Optional[str] = None

    class Config:
        from_attributes = True

# Modèles Pydantic pour la table stocks_mouvements
class StockMouvementBase(BaseModel):
    stock_id: str
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: str
    type_mouvement: str
    quantite: float
    prix_unitaire: float = 0.0
    date_mouvement: str
    reference_operation: Optional[str] = None
    utilisateur_id: Optional[str] = None
    commentaire: Optional[str] = None
    compagnie_id: Optional[str] = None

class StockMouvementCreate(StockMouvementBase):
    est_initial: Optional[bool] = False
    operation_initialisation_id: Optional[str] = None

class StockMouvementUpdate(BaseModel):
    quantite: Optional[float] = None
    prix_unitaire: Optional[float] = None
    commentaire: Optional[str] = None

class StockMouvementResponse(StockMouvementBase):
    id: str
    est_initial: Optional[bool] = False
    operation_initialisation_id: Optional[str] = None
    cout_total: Optional[float] = None
    valeur_stock_avant: Optional[float] = None
    valeur_stock_apres: Optional[float] = None
    cout_unitaire_moyen_apres: Optional[float] = None
    created_at: str

    class Config:
        from_attributes = True

class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int

class StockListResponse(BaseModel):
    success: bool
    data: List[StockResponse]
    pagination: PaginationResponse

class StockMouvementListResponse(BaseModel):
    success: bool
    data: List[StockMouvementResponse]
    pagination: PaginationResponse

# Routes pour la gestion des stocks
@router.get("/stocks", response_model=StockListResponse)
@prohibit_super_admin_access
async def get_stocks_list(
    station_id: Optional[str] = Query(None, description="Filtrer par station"),
    article_id: Optional[str] = Query(None, description="Filtrer par article"),
    cuve_id: Optional[str] = Query(None, description="Filtrer par cuve"),
    limit: int = Query(50, ge=1, le=100, description="Nombre d'éléments à retourner"),
    offset: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    current_user: Utilisateur = Depends(create_permission_dependency("stocks.lire")),
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des stocks avec filtres optionnels
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Construction de la requête
    query = db.query(StockModel)
    
    # Filtrer par compagnie pour les utilisateurs non-admins
    if not is_admin_or_super_admin(user_type) and user_company_id:
        query = query.filter(StockModel.compagnie_id == user_company_id)
    
    # Appliquer les filtres
    if station_id:
        query = query.filter(StockModel.station_id == station_id)
    if article_id:
        query = query.filter(StockModel.article_id == article_id)
    if cuve_id:
        query = query.filter(StockModel.cuve_id == cuve_id)

    total = query.count()
    stocks = query.offset(offset).limit(limit).all()

    return StockListResponse(
        success=True,
        data=[
            StockResponse(
                id=str(stock.id),
                article_id=str(stock.article_id) if stock.article_id else None,
                cuve_id=str(stock.cuve_id) if stock.cuve_id else None,
                station_id=str(stock.station_id),
                stock_theorique=float(stock.stock_theorique) if stock.stock_theorique else 0.0,
                stock_reel=float(stock.stock_reel) if stock.stock_reel else 0.0,
                est_initial=stock.est_initial,
                ecart_stock=float(stock.ecart_stock) if stock.ecart_stock else None,
                compagnie_id=str(stock.compagnie_id),
                created_at=stock.created_at.isoformat(),
                updated_at=stock.updated_at.isoformat() if stock.updated_at else None,
                # Champs qui seront ajoutés via le script d'initialisation (valeurs par défaut pour l'instant)
                stock_minimal=0.0,
                stock_maximal=None,
                prix_unitaire=0.0,
                date_initialisation=None,
                utilisateur_initialisation=None,
                observation_initialisation=None
            )
            for stock in stocks
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )

@router.post("/stocks", response_model=StockResponse)
@prohibit_super_admin_access
async def create_stock(
    stock_data: StockCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("stocks.creer")),
    db: Session = Depends(get_db)
):
    """
    Créer un nouvel enregistrement de stock
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Si le modèle n'inclut pas le compagnie_id ou s'il est vide, on le déduit de l'utilisateur connecté
    stock_company_id = stock_data.compagnie_id if stock_data.compagnie_id else user_company_id

    # Vérifier que l'utilisateur appartient à la même compagnie
    if not is_admin_or_super_admin(user_type) and stock_company_id != user_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez créer des stocks que pour votre propre compagnie"
        )

    # Vérifier que les IDs référencés existent
    if stock_data.article_id:
        from models.structures import Article
        article_exists = db.query(Article).filter(Article.id == stock_data.article_id).first()
        if not article_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article avec ID {stock_data.article_id} non trouvé"
            )

    if stock_data.cuve_id:
        from models.structures import Cuve
        cuve_exists = db.query(Cuve).filter(Cuve.id == stock_data.cuve_id).first()
        if not cuve_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuve avec ID {stock_data.cuve_id} non trouvée"
            )

    from models.structures import Station
    station_exists = db.query(Station).filter(Station.id == stock_data.station_id).first()
    if not station_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station avec ID {stock_data.station_id} non trouvée"
        )

    # Création du stock
    db_stock = StockModel(
        article_id=stock_data.article_id,
        cuve_id=stock_data.cuve_id,
        station_id=stock_data.station_id,
        stock_theorique=stock_data.stock_theorique,
        stock_reel=stock_data.stock_reel,
        est_initial=stock_data.est_initial,
        compagnie_id=stock_company_id
    )

    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)

    return StockResponse(
        id=str(db_stock.id),
        article_id=str(db_stock.article_id) if db_stock.article_id else None,
        cuve_id=str(db_stock.cuve_id) if db_stock.cuve_id else None,
        station_id=str(db_stock.station_id),
        stock_theorique=float(db_stock.stock_theorique) if db_stock.stock_theorique else 0.0,
        stock_reel=float(db_stock.stock_reel) if db_stock.stock_reel else 0.0,
        est_initial=db_stock.est_initial,
        ecart_stock=float(db_stock.ecart_stock) if db_stock.ecart_stock else None,
        compagnie_id=str(db_stock.compagnie_id),
        created_at=db_stock.created_at.isoformat(),
        updated_at=db_stock.updated_at.isoformat() if db_stock.updated_at else None,
        # Champs qui seront ajoutés via le script d'initialisation (valeurs par défaut pour l'instant)
        stock_minimal=0.0,
        stock_maximal=None,
        prix_unitaire=0.0,
        date_initialisation=None,
        utilisateur_initialisation=None,
        observation_initialisation=None
    )

# Routes pour la gestion des mouvements de stock
@router.get("/stocks-mouvements", response_model=StockMouvementListResponse)
@prohibit_super_admin_access
async def get_stocks_mouvements_list(
    stock_id: Optional[str] = Query(None, description="Filtrer par stock"),
    type_mouvement: Optional[str] = Query(None, description="Filtrer par type de mouvement"),
    date_debut: Optional[str] = Query(None, description="Filtrer par date de début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Filtrer par date de fin (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Nombre d'éléments à retourner"),
    offset: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    current_user: Utilisateur = Depends(create_permission_dependency("stocks_mouvements.lire")),
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des mouvements de stock avec filtres optionnels
    """
    from utils.access_control import is_admin_or_super_admin
    from datetime import datetime
    user_type = current_user.type_utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Construction de la requête
    query = db.query(StockMouvementModel)
    
    # Filtrer par compagnie pour les utilisateurs non-admins
    if not is_admin_or_super_admin(user_type) and user_company_id:
        query = query.filter(StockMouvementModel.compagnie_id == user_company_id)
    
    # Appliquer les filtres
    if stock_id:
        query = query.filter(StockMouvementModel.stock_id == stock_id)
    if type_mouvement:
        query = query.filter(StockMouvementModel.type_mouvement == type_mouvement)
    if date_debut:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d").date()
        query = query.filter(StockMouvementModel.date_mouvement >= date_debut_obj)
    if date_fin:
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d").date()
        query = query.filter(StockMouvementModel.date_mouvement <= date_fin_obj)

    total = query.count()
    mouvements = query.offset(offset).limit(limit).all()

    return StockMouvementListResponse(
        success=True,
        data=[
            StockMouvementResponse(
                id=str(mvt.id),
                stock_id=str(mvt.stock_id),
                article_id=str(mvt.article_id) if mvt.article_id else None,
                cuve_id=str(mvt.cuve_id) if mvt.cuve_id else None,
                station_id=str(mvt.station_id),
                type_mouvement=mvt.type_mouvement,
                quantite=float(mvt.quantite),
                prix_unitaire=float(mvt.prix_unitaire) if mvt.prix_unitaire else 0.0,
                date_mouvement=mvt.date_mouvement.isoformat() if hasattr(mvt.date_mouvement, 'isoformat') else str(mvt.date_mouvement),
                reference_operation=mvt.reference_operation,
                utilisateur_id=str(mvt.utilisateur_id) if mvt.utilisateur_id else None,
                commentaire=mvt.commentaire,
                compagnie_id=str(mvt.compagnie_id),
                est_initial=mvt.est_initial,
                operation_initialisation_id=str(mvt.operation_initialisation_id) if mvt.operation_initialisation_id else None,
                cout_total=float(mvt.cout_total) if mvt.cout_total else None,
                valeur_stock_avant=float(mvt.valeur_stock_avant) if mvt.valeur_stock_avant else None,
                valeur_stock_apres=float(mvt.valeur_stock_apres) if mvt.valeur_stock_apres else None,
                cout_unitaire_moyen_apres=float(mvt.cout_unitaire_moyen_apres) if mvt.cout_unitaire_moyen_apres else None,
                created_at=mvt.created_at.isoformat()
            )
            for mvt in mouvements
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset
        )
    )

@router.post("/stocks-mouvements", response_model=StockMouvementResponse)
@prohibit_super_admin_access
async def create_stock_mouvement(
    mouvement_data: StockMouvementCreate,
    current_user: Utilisateur = Depends(create_permission_dependency("stocks_mouvements.creer")),
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau mouvement de stock
    """
    from utils.access_control import is_admin_or_super_admin
    user_type = current_user.type_utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    # Si le modèle n'inclut pas le compagnie_id ou s'il est vide, on le déduit de l'utilisateur connecté
    mouvement_company_id = mouvement_data.compagnie_id if mouvement_data.compagnie_id else user_company_id

    # Vérifier que l'utilisateur appartient à la même compagnie
    if not is_admin_or_super_admin(user_type) and mouvement_company_id != user_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez créer des mouvements de stock que pour votre propre compagnie"
        )

    # Vérifier que les IDs référencés existent
    from models.structures import Stock, Article, Cuve, Station, Utilisateur as UserModel
    stock_exists = db.query(Stock).filter(Stock.id == mouvement_data.stock_id).first()
    if not stock_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock avec ID {mouvement_data.stock_id} non trouvé"
        )

    if mouvement_data.article_id:
        article_exists = db.query(Article).filter(Article.id == mouvement_data.article_id).first()
        if not article_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article avec ID {mouvement_data.article_id} non trouvé"
            )

    if mouvement_data.cuve_id:
        cuve_exists = db.query(Cuve).filter(Cuve.id == mouvement_data.cuve_id).first()
        if not cuve_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuve avec ID {mouvement_data.cuve_id} non trouvée"
            )

    station_exists = db.query(Station).filter(Station.id == mouvement_data.station_id).first()
    if not station_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station avec ID {mouvement_data.station_id} non trouvée"
        )

    if mouvement_data.utilisateur_id:
        utilisateur_exists = db.query(UserModel).filter(UserModel.id == mouvement_data.utilisateur_id).first()
        if not utilisateur_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utilisateur avec ID {mouvement_data.utilisateur_id} non trouvé"
            )

    # Conversion de la date
    from datetime import datetime
    try:
        date_mouvement = datetime.strptime(mouvement_data.date_mouvement, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )

    # Création du mouvement
    db_mouvement = StockMouvementModel(
        stock_id=mouvement_data.stock_id,
        article_id=mouvement_data.article_id,
        cuve_id=mouvement_data.cuve_id,
        station_id=mouvement_data.station_id,
        type_mouvement=mouvement_data.type_mouvement,
        quantite=mouvement_data.quantite,
        prix_unitaire=mouvement_data.prix_unitaire,
        date_mouvement=date_mouvement,
        reference_operation=mouvement_data.reference_operation,
        utilisateur_id=mouvement_data.utilisateur_id,
        commentaire=mouvement_data.commentaire,
        compagnie_id=mouvement_company_id,
        est_initial=mouvement_data.est_initial,
        operation_initialisation_id=mouvement_data.operation_initialisation_id
    )

    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)

    return StockMouvementResponse(
        id=str(db_mouvement.id),
        stock_id=str(db_mouvement.stock_id),
        article_id=str(db_mouvement.article_id) if db_mouvement.article_id else None,
        cuve_id=str(db_mouvement.cuve_id) if db_mouvement.cuve_id else None,
        station_id=str(db_mouvement.station_id),
        type_mouvement=db_mouvement.type_mouvement,
        quantite=float(db_mouvement.quantite),
        prix_unitaire=float(db_mouvement.prix_unitaire) if db_mouvement.prix_unitaire else 0.0,
        date_mouvement=db_mouvement.date_mouvement.isoformat() if hasattr(db_mouvement.date_mouvement, 'isoformat') else str(db_mouvement.date_mouvement),
        reference_operation=db_mouvement.reference_operation,
        utilisateur_id=str(db_mouvement.utilisateur_id) if db_mouvement.utilisateur_id else None,
        commentaire=db_mouvement.commentaire,
        compagnie_id=str(db_mouvement.compagnie_id),
        est_initial=db_mouvement.est_initial,
        operation_initialisation_id=str(db_mouvement.operation_initialisation_id) if db_mouvement.operation_initialisation_id else None,
        cout_total=float(db_mouvement.cout_total) if db_mouvement.cout_total else None,
        valeur_stock_avant=float(db_mouvement.valeur_stock_avant) if db_mouvement.valeur_stock_avant else None,
        valeur_stock_apres=float(db_mouvement.valeur_stock_apres) if db_mouvement.valeur_stock_apres else None,
        cout_unitaire_moyen_apres=float(db_mouvement.cout_unitaire_moyen_apres) if db_mouvement.cout_unitaire_moyen_apres else None,
        created_at=db_mouvement.created_at.isoformat()
    )