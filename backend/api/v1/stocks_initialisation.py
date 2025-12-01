from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid
from pydantic import BaseModel

from database.database import get_db
from models.stocks import QualiteCarburantInitial, CoutLogistiqueStockInitial, BilanInitialStocks, BilanInitialStocksLigne
from models.structures import Utilisateur  # Pour la vérification des permissions
from schemas.stocks_initialisation import (
    QualiteCarburantInitialCreate, QualiteCarburantInitialUpdate, QualiteCarburantInitialResponse,
    CoutLogistiqueStockInitialCreate, CoutLogistiqueStockInitialUpdate, CoutLogistiqueStockInitialResponse,
    BilanInitialCreate, BilanInitialUpdate, BilanInitialResponse, BilanInitialSummary,
    BilanInitialLigneCreate, BilanInitialLigneUpdate, BilanInitialLigneResponse
)
from utils.dependencies import get_current_user
from utils.access_control import has_permission, check_company_access, prohibit_super_admin_access
from utils.pagination import PaginationResponse

# Création du routeur pour les endpoints d'initialisation des stocks
# Le tag "Stocks Initialisations" est utilisé pour l'affichage dans l'interface Swagger
router = APIRouter(prefix="/stocks-initialisation", tags=["Stocks Initialisation"])


def check_permission(current_user: Utilisateur, db: Session, resource: str, action: str, company_id: str):
    """
    Fonction d'aide pour vérifier les permissions
    """
    # Vérifier si l'utilisateur a accès à la compagnie
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: Vous n'avez pas accès à cette compagnie"
        )

    # Construire la permission spécifique
    permission = f"{resource}_{action}"

    # Vérifier si l'utilisateur a la permission
    user_has_perm = has_permission(db, str(current_user.id), permission)

    if not user_has_perm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' requise"
        )

class QualiteCarburantInitialListResponse(BaseModel):
    items: List[QualiteCarburantInitialResponse]
    pagination: PaginationResponse


# CRUD pour la qualité du carburant initial
@router.get("/qualites-carburant", response_model=QualiteCarburantInitialListResponse)
async def lister_qualites_carburant_initial(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Vérifier les permissions
    check_permission(current_user, db, "qualite_carburant_initial", "read", user_company_id)

    # Filtrer par compagnie_id de l'utilisateur
    query = db.query(QualiteCarburantInitial).filter(QualiteCarburantInitial.compagnie_id == user_company_id)
    
    total = query.count()
    qualites = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            QualiteCarburantInitialResponse(
                id=str(q.id),
                cuve_id=str(q.cuve_id) if q.cuve_id else None,
                carburant_id=str(q.carburant_id) if q.carburant_id else None,
                date_analyse=q.date_analyse.isoformat(),
                utilisateur_id=str(q.utilisateur_id) if q.utilisateur_id else None,
                densite=float(q.densite) if q.densite else None,
                indice_octane=q.indice_octane,
                soufre_ppm=float(q.soufre_ppm) if q.soufre_ppm else None,
                type_additif=q.type_additif,
                commentaire_qualite=q.commentaire_qualite,
                resultat_qualite=q.resultat_qualite,
                compagnie_id=str(q.compagnie_id),
                created_at=q.created_at.isoformat()
            )
            for q in qualites
        ],
        "pagination": PaginationResponse(
            skip=skip,
            limit=limit,
            total=total
        )
    }


@router.get("/qualites-carburant/{qualite_id}", response_model=QualiteCarburantInitialResponse)
async def obtenir_qualite_carburant_initial(
    qualite_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        qualite_uuid = uuid.UUID(qualite_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de qualité invalide")
    
    qualite = db.query(QualiteCarburantInitial).filter(QualiteCarburantInitial.id == qualite_uuid).first()
    
    if not qualite:
        raise HTTPException(status_code=404, detail="Qualité du carburant initial non trouvée")
    
    # Vérifier les permissions
    check_permission(current_user, db, "qualite_carburant_initial", "read", str(qualite.compagnie_id))
    
    return QualiteCarburantInitialResponse(
        id=str(qualite.id),
        cuve_id=str(qualite.cuve_id) if qualite.cuve_id else None,
        carburant_id=str(qualite.carburant_id) if qualite.carburant_id else None,
        date_analyse=qualite.date_analyse.isoformat(),
        utilisateur_id=str(qualite.utilisateur_id) if qualite.utilisateur_id else None,
        densite=float(qualite.densite) if qualite.densite else None,
        indice_octane=qualite.indice_octane,
        soufre_ppm=float(qualite.soufre_ppm) if qualite.soufre_ppm else None,
        type_additif=qualite.type_additif,
        commentaire_qualite=qualite.commentaire_qualite,
        resultat_qualite=qualite.resultat_qualite,
        compagnie_id=str(qualite.compagnie_id),
        created_at=qualite.created_at.isoformat()
    )


@router.post("/qualites-carburant", response_model=QualiteCarburantInitialResponse)
@prohibit_super_admin_access
async def creer_qualite_carburant_initial(
    qualite_data: QualiteCarburantInitialCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Si le modèle n'inclut pas le compagnie_id ou s'il est vide, on le déduit de l'utilisateur connecté
    qualite_company_id = qualite_data.compagnie_id if qualite_data.compagnie_id else user_company_id

    # Vérifier les permissions
    check_permission(current_user, db, "qualite_carburant_initial", "create", qualite_company_id)

    try:
        compagnie_uuid = uuid.UUID(qualite_company_id)
        cuve_uuid = uuid.UUID(qualite_data.cuve_id) if qualite_data.cuve_id else None
        carburant_uuid = uuid.UUID(qualite_data.carburant_id) if qualite_data.carburant_id else None
        utilisateur_uuid = uuid.UUID(qualite_data.utilisateur_id) if qualite_data.utilisateur_id else None
    except ValueError:
        raise HTTPException(status_code=400, detail="ID invalide")

    # Création de la qualité du carburant initial
    db_qualite = QualiteCarburantInitial(
        cuve_id=cuve_uuid,
        carburant_id=carburant_uuid,
        date_analyse=qualite_data.date_analyse,
        utilisateur_id=utilisateur_uuid,
        densite=qualite_data.densite,
        indice_octane=qualite_data.indice_octane,
        soufre_ppm=qualite_data.soufre_ppm,
        type_additif=qualite_data.type_additif,
        commentaire_qualite=qualite_data.commentaire_qualite,
        resultat_qualite=qualite_data.resultat_qualite,
        compagnie_id=compagnie_uuid
    )
    
    db.add(db_qualite)
    db.commit()
    db.refresh(db_qualite)
    
    return QualiteCarburantInitialResponse(
        id=str(db_qualite.id),
        cuve_id=str(db_qualite.cuve_id) if db_qualite.cuve_id else None,
        carburant_id=str(db_qualite.carburant_id) if db_qualite.carburant_id else None,
        date_analyse=db_qualite.date_analyse.isoformat(),
        utilisateur_id=str(db_qualite.utilisateur_id) if db_qualite.utilisateur_id else None,
        densite=float(db_qualite.densite) if db_qualite.densite else None,
        indice_octane=db_qualite.indice_octane,
        soufre_ppm=float(db_qualite.soufre_ppm) if db_qualite.soufre_ppm else None,
        type_additif=db_qualite.type_additif,
        commentaire_qualite=db_qualite.commentaire_qualite,
        resultat_qualite=db_qualite.resultat_qualite,
        compagnie_id=str(db_qualite.compagnie_id),
        created_at=db_qualite.created_at.isoformat()
    )


@router.put("/qualites-carburant/{qualite_id}", response_model=QualiteCarburantInitialResponse)
@prohibit_super_admin_access
async def mettre_a_jour_qualite_carburant_initial(
    qualite_id: str,
    qualite_data: QualiteCarburantInitialUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        qualite_uuid = uuid.UUID(qualite_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de qualité invalide")
    
    qualite = db.query(QualiteCarburantInitial).filter(QualiteCarburantInitial.id == qualite_uuid).first()
    
    if not qualite:
        raise HTTPException(status_code=404, detail="Qualité du carburant initial non trouvée")
    
    # Vérifier les permissions
    check_permission(current_user, db, "qualite_carburant_initial", "update", str(qualite.compagnie_id))
    
    # Mise à jour des champs
    if qualite_data.densite is not None:
        qualite.densite = qualite_data.densite
    if qualite_data.indice_octane is not None:
        qualite.indice_octane = qualite_data.indice_octane
    if qualite_data.soufre_ppm is not None:
        qualite.soufre_ppm = qualite_data.soufre_ppm
    if qualite_data.type_additif is not None:
        qualite.type_additif = qualite_data.type_additif
    if qualite_data.commentaire_qualite is not None:
        qualite.commentaire_qualite = qualite_data.commentaire_qualite
    if qualite_data.resultat_qualite is not None:
        qualite.resultat_qualite = qualite_data.resultat_qualite
    
    db.commit()
    db.refresh(qualite)
    
    return QualiteCarburantInitialResponse(
        id=str(qualite.id),
        cuve_id=str(qualite.cuve_id) if qualite.cuve_id else None,
        carburant_id=str(qualite.carburant_id) if qualite.carburant_id else None,
        date_analyse=qualite.date_analyse.isoformat(),
        utilisateur_id=str(qualite.utilisateur_id) if qualite.utilisateur_id else None,
        densite=float(qualite.densite) if qualite.densite else None,
        indice_octane=qualite.indice_octane,
        soufre_ppm=float(qualite.soufre_ppm) if qualite.soufre_ppm else None,
        type_additif=qualite.type_additif,
        commentaire_qualite=qualite.commentaire_qualite,
        resultat_qualite=qualite.resultat_qualite,
        compagnie_id=str(qualite.compagnie_id),
        created_at=qualite.created_at.isoformat()
    )


@router.delete("/qualites-carburant/{qualite_id}", status_code=status.HTTP_204_NO_CONTENT)
@prohibit_super_admin_access
async def supprimer_qualite_carburant_initial(
    qualite_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        qualite_uuid = uuid.UUID(qualite_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de qualité invalide")
    
    qualite = db.query(QualiteCarburantInitial).filter(QualiteCarburantInitial.id == qualite_uuid).first()
    
    if not qualite:
        raise HTTPException(status_code=404, detail="Qualité du carburant initial non trouvée")
    
    # Vérifier les permissions
    check_permission(current_user, db, "qualite_carburant_initial", "delete", str(qualite.compagnie_id))
    
    db.delete(qualite)
    db.commit()
    
    return {"message": "Qualité du carburant initial supprimée avec succès"}


# Modèles pour les coûts logistiques initiaux
class CoutLogistiqueStockInitialBase(BaseModel):
    type_cout: str  # 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description: Optional[str] = None
    montant: float
    date_cout: date
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    utilisateur_saisie_id: Optional[str] = None
    compagnie_id: str


class CoutLogistiqueStockInitialCreate(CoutLogistiqueStockInitialBase):
    pass


class CoutLogistiqueStockInitialUpdate(BaseModel):
    type_cout: Optional[str] = None
    description: Optional[str] = None
    montant: Optional[float] = None
    date_cout: Optional[date] = None
    article_id: Optional[str] = None
    cuve_id: Optional[str] = None
    station_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    utilisateur_saisie_id: Optional[str] = None


class CoutLogistiqueStockInitialResponse(CoutLogistiqueStockInitialBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True


class CoutLogistiqueStockInitialListResponse(BaseModel):
    items: List[CoutLogistiqueStockInitialResponse]
    pagination: PaginationResponse


class BilanInitialListResponse(BaseModel):
    items: List[BilanInitialSummary]
    pagination: PaginationResponse


class BilanInitialLigneListResponse(BaseModel):
    items: List[BilanInitialLigneResponse]
    pagination: PaginationResponse


# CRUD pour les coûts logistiques initiaux
@router.get("/couts-logistiques", response_model=CoutLogistiqueStockInitialListResponse)
async def lister_couts_logistiques_initial(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Vérifier les permissions
    check_permission(current_user, db, "cout_logistique_initial", "read", user_company_id)

    # Filtrer par compagnie_id de l'utilisateur
    query = db.query(CoutLogistiqueStockInitial).filter(CoutLogistiqueStockInitial.compagnie_id == user_company_id)
    
    total = query.count()
    couts = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            CoutLogistiqueStockInitialResponse(
                id=str(c.id),
                type_cout=c.type_cout,
                description=c.description,
                montant=float(c.montant) if c.montant else 0.0,
                date_cout=c.date_cout.isoformat(),
                article_id=str(c.article_id) if c.article_id else None,
                cuve_id=str(c.cuve_id) if c.cuve_id else None,
                station_id=str(c.station_id) if c.station_id else None,
                fournisseur_id=str(c.fournisseur_id) if c.fournisseur_id else None,
                utilisateur_saisie_id=str(c.utilisateur_saisie_id) if c.utilisateur_saisie_id else None,
                compagnie_id=str(c.compagnie_id),
                created_at=c.created_at.isoformat()
            )
            for c in couts
        ],
        "pagination": PaginationResponse(
            skip=skip,
            limit=limit,
            total=total
        )
    }


@router.get("/couts-logistiques/{cout_id}", response_model=CoutLogistiqueStockInitialResponse)
async def obtenir_cout_logistique_initial(
    cout_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        cout_uuid = uuid.UUID(cout_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de coût invalide")
    
    cout = db.query(CoutLogistiqueStockInitial).filter(CoutLogistiqueStockInitial.id == cout_uuid).first()
    
    if not cout:
        raise HTTPException(status_code=404, detail="Coût logistique initial non trouvé")
    
    # Vérifier les permissions
    check_permission(current_user, db, "cout_logistique_initial", "read", str(cout.compagnie_id))
    
    return CoutLogistiqueStockInitialResponse(
        id=str(cout.id),
        type_cout=cout.type_cout,
        description=cout.description,
        montant=float(cout.montant) if cout.montant else 0.0,
        date_cout=cout.date_cout.isoformat(),
        article_id=str(cout.article_id) if cout.article_id else None,
        cuve_id=str(cout.cuve_id) if cout.cuve_id else None,
        station_id=str(cout.station_id) if cout.station_id else None,
        fournisseur_id=str(cout.fournisseur_id) if cout.fournisseur_id else None,
        utilisateur_saisie_id=str(cout.utilisateur_saisie_id) if cout.utilisateur_saisie_id else None,
        compagnie_id=str(cout.compagnie_id),
        created_at=cout.created_at.isoformat()
    )


@router.post("/couts-logistiques", response_model=CoutLogistiqueStockInitialResponse)
@prohibit_super_admin_access
async def creer_cout_logistique_initial(
    cout_data: CoutLogistiqueStockInitialCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Si le modèle n'inclut pas le compagnie_id ou s'il est vide, on le déduit de l'utilisateur connecté
    cout_company_id = cout_data.compagnie_id if cout_data.compagnie_id else user_company_id

    # Vérifier les permissions
    check_permission(current_user, db, "cout_logistique_initial", "create", cout_company_id)

    try:
        compagnie_uuid = uuid.UUID(cout_company_id)
        article_uuid = uuid.UUID(cout_data.article_id) if cout_data.article_id else None
        cuve_uuid = uuid.UUID(cout_data.cuve_id) if cout_data.cuve_id else None
        station_uuid = uuid.UUID(cout_data.station_id) if cout_data.station_id else None
        fournisseur_uuid = uuid.UUID(cout_data.fournisseur_id) if cout_data.fournisseur_id else None
        utilisateur_uuid = uuid.UUID(cout_data.utilisateur_saisie_id) if cout_data.utilisateur_saisie_id else None
    except ValueError:
        raise HTTPException(status_code=400, detail="ID invalide")

    # Création du coût logistique initial
    db_cout = CoutLogistiqueStockInitial(
        type_cout=cout_data.type_cout,
        description=cout_data.description,
        montant=cout_data.montant,
        date_cout=cout_data.date_cout,
        article_id=article_uuid,
        cuve_id=cuve_uuid,
        station_id=station_uuid,
        fournisseur_id=fournisseur_uuid,
        utilisateur_saisie_id=utilisateur_uuid,
        compagnie_id=compagnie_uuid
    )
    
    db.add(db_cout)
    db.commit()
    db.refresh(db_cout)
    
    return CoutLogistiqueStockInitialResponse(
        id=str(db_cout.id),
        type_cout=db_cout.type_cout,
        description=db_cout.description,
        montant=float(db_cout.montant) if db_cout.montant else 0.0,
        date_cout=db_cout.date_cout.isoformat(),
        article_id=str(db_cout.article_id) if db_cout.article_id else None,
        cuve_id=str(db_cout.cuve_id) if db_cout.cuve_id else None,
        station_id=str(db_cout.station_id) if db_cout.station_id else None,
        fournisseur_id=str(db_cout.fournisseur_id) if db_cout.fournisseur_id else None,
        utilisateur_saisie_id=str(db_cout.utilisateur_saisie_id) if db_cout.utilisateur_saisie_id else None,
        compagnie_id=str(db_cout.compagnie_id),
        created_at=db_cout.created_at.isoformat()
    )


# Modèles pour le bilan initial
class BilanInitialBase(BaseModel):
    compagnie_id: str
    date_bilan: date
    commentaire: Optional[str] = None
    valeur_totale_stocks: Optional[float] = 0.0
    nombre_elements: Optional[int] = 0
    statut: Optional[str] = "Brouillon"  # 'Brouillon', 'En cours', 'Termine', 'Validé'


class BilanInitialCreate(BilanInitialBase):
    pass


class BilanInitialUpdate(BaseModel):
    commentaire: Optional[str] = None
    statut: Optional[str] = None  # 'Brouillon', 'En cours', 'Termine', 'Validé'
    utilisateur_validation_id: Optional[str] = None
    date_validation: Optional[date] = None


class BilanInitialSummary(BaseModel):
    id: str
    compagnie_id: str
    date_bilan: date
    valeur_totale_stocks: float
    nombre_elements: int
    statut: str
    est_valide: bool
    created_at: str

    class Config:
        from_attributes = True


class BilanInitialResponse(BilanInitialBase):
    id: str
    utilisateur_validation_id: Optional[str] = None
    date_validation: Optional[date] = None
    est_valide: bool
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class BilanInitialListResponse(BaseModel):
    items: List[BilanInitialSummary]
    pagination: PaginationResponse


# CRUD pour le bilan initial
@router.get("/bilans-initial", response_model=BilanInitialListResponse)
async def lister_bilans_initial(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Vérifier les permissions
    check_permission(current_user, db, "bilan_initial", "read", user_company_id)

    # Filtrer par compagnie_id de l'utilisateur
    query = db.query(BilanInitialStocks).filter(BilanInitialStocks.compagnie_id == user_company_id)
    
    total = query.count()
    bilans = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            BilanInitialSummary(
                id=str(b.id),
                compagnie_id=str(b.compagnie_id),
                date_bilan=b.date_bilan.isoformat(),
                valeur_totale_stocks=float(b.valeur_totale_stocks) if b.valeur_totale_stocks else 0.0,
                nombre_elements=b.nombre_elements,
                statut=b.statut,
                est_valide=b.est_valide,
                created_at=b.created_at.isoformat()
            )
            for b in bilans
        ],
        "pagination": PaginationResponse(
            skip=skip,
            limit=limit,
            total=total
        )
    }


@router.get("/bilans-initial/{bilan_id}", response_model=BilanInitialResponse)
async def obtenir_bilan_initial(
    bilan_id: str,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        bilan_uuid = uuid.UUID(bilan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de bilan invalide")

    bilan = db.query(BilanInitialStocks).filter(BilanInitialStocks.id == bilan_uuid).first()
    
    if not bilan:
        raise HTTPException(status_code=404, detail="Bilan initial non trouvé")
    
    # Vérifier les permissions
    check_permission(current_user, db, "bilan_initial", "read", str(bilan.compagnie_id))
    
    return BilanInitialResponse(
        id=str(bilan.id),
        compagnie_id=str(bilan.compagnie_id),
        date_bilan=bilan.date_bilan.isoformat(),
        commentaire=bilan.commentaire,
        valeur_totale_stocks=float(bilan.valeur_totale_stocks) if bilan.valeur_totale_stocks else 0.0,
        nombre_elements=bilan.nombre_elements,
        statut=bilan.statut,
        utilisateur_validation_id=str(bilan.utilisateur_validation_id) if bilan.utilisateur_validation_id else None,
        date_validation=bilan.date_validation.isoformat() if bilan.date_validation else None,
        est_valide=bilan.est_valide,
        created_at=bilan.created_at.isoformat(),
        updated_at=bilan.updated_at.isoformat() if bilan.updated_at else None
    )


@router.post("/bilans-initial", response_model=BilanInitialResponse)
@prohibit_super_admin_access
async def creer_bilan_initial(
    bilan_data: BilanInitialCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Récupérer la compagnie de l'utilisateur
    user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None

    if not user_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur n'est associé à aucune compagnie"
        )

    # Si le modèle n'inclut pas le compagnie_id ou s'il est vide, on le déduit de l'utilisateur connecté
    bilan_company_id = bilan_data.compagnie_id if bilan_data.compagnie_id else user_company_id

    # Vérifier les permissions
    check_permission(current_user, db, "bilan_initial", "create", bilan_company_id)

    try:
        compagnie_uuid = uuid.UUID(bilan_company_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de compagnie invalide")

    # Création du bilan initial
    db_bilan = BilanInitialStocks(
        compagnie_id=compagnie_uuid,
        date_bilan=bilan_data.date_bilan,
        commentaire=bilan_data.commentaire,
        valeur_totale_stocks=bilan_data.valeur_totale_stocks,
        nombre_elements=bilan_data.nombre_elements,
        statut=bilan_data.statut
    )
    
    db.add(db_bilan)
    db.commit()
    db.refresh(db_bilan)
    
    return BilanInitialResponse(
        id=str(db_bilan.id),
        compagnie_id=str(db_bilan.compagnie_id),
        date_bilan=db_bilan.date_bilan.isoformat(),
        commentaire=db_bilan.commentaire,
        valeur_totale_stocks=float(db_bilan.valeur_totale_stocks) if db_bilan.valeur_totale_stocks else 0.0,
        nombre_elements=db_bilan.nombre_elements,
        statut=db_bilan.statut,
        utilisateur_validation_id=str(db_bilan.utilisateur_validation_id) if db_bilan.utilisateur_validation_id else None,
        date_validation=db_bilan.date_validation.isoformat() if db_bilan.date_validation else None,
        est_valide=db_bilan.est_valide,
        created_at=db_bilan.created_at.isoformat(),
        updated_at=db_bilan.updated_at.isoformat() if db_bilan.updated_at else None
    )


# Modèles pour les lignes du bilan initial
class BilanInitialLigneBase(BaseModel):
    bilan_initial_stocks_id: str
    type_element: str  # 'carburant', 'article_boutique', 'autre'
    element_id: str  # ID de la cuve ou de l'article
    description_element: Optional[str] = None
    quantite: float
    unite_mesure: Optional[str] = None
    prix_unitaire: float
    valeur_totale: Optional[float] = None  # Générée à partir de quantité * prix_unitaire
    taux_tva: Optional[float] = 0.0
    montant_tva: Optional[float] = None
    montant_ht: Optional[float] = None


class BilanInitialLigneCreate(BilanInitialLigneBase):
    pass


class BilanInitialLigneUpdate(BaseModel):
    description_element: Optional[str] = None
    quantite: Optional[float] = None
    unite_mesure: Optional[str] = None
    prix_unitaire: Optional[float] = None
    taux_tva: Optional[float] = None


class BilanInitialLigneResponse(BilanInitialLigneBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True


class BilanInitialLigneListResponse(BaseModel):
    items: List[BilanInitialLigneResponse]
    pagination: PaginationResponse


# CRUD pour les lignes du bilan initial
@router.get("/bilans-initial-lignes", response_model=BilanInitialLigneListResponse)
async def lister_bilans_initial_lignes(
    bilan_id: str = Query(..., description="ID du bilan initial"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        bilan_uuid = uuid.UUID(bilan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de bilan invalide")

    # Récupérer le bilan pour vérifier les permissions
    bilan = db.query(BilanInitialStocks).filter(BilanInitialStocks.id == bilan_uuid).first()
    if not bilan:
        raise HTTPException(status_code=404, detail="Bilan initial non trouvé")

    # Vérifier les permissions
    check_permission(current_user, db, "bilan_initial_ligne", "read", str(bilan.compagnie_id))

    # Filtrer par bilan_initial_stocks_id
    query = db.query(BilanInitialStocksLigne).filter(BilanInitialStocksLigne.bilan_initial_stocks_id == bilan_uuid)
    
    total = query.count()
    lignes = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            BilanInitialLigneResponse(
                id=str(l.id),
                bilan_initial_stocks_id=str(l.bilan_initial_stocks_id),
                type_element=l.type_element,
                element_id=str(l.element_id),
                description_element=l.description_element,
                quantite=float(l.quantite) if l.quantite else 0.0,
                unite_mesure=l.unite_mesure,
                prix_unitaire=float(l.prix_unitaire) if l.prix_unitaire else 0.0,
                valeur_totale=float(l.valeur_totale) if l.valeur_totale else 0.0,
                taux_tva=float(l.taux_tva) if l.taux_tva else 0.0,
                montant_tva=float(l.montant_tva) if l.montant_tva else 0.0,
                montant_ht=float(l.montant_ht) if l.montant_ht else 0.0,
                created_at=l.created_at.isoformat()
            )
            for l in lignes
        ],
        "pagination": PaginationResponse(
            skip=skip,
            limit=limit,
            total=total
        )
    }