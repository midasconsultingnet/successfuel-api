from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Livraison as LivraisonModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/livraisons",
    responses={404: {"description": "Livraison non trouvée"}}
)
security = HTTPBearer()

@router.get("/",
            response_model=List[schemas.LivraisonResponse],
            summary="Récupérer les livraisons",
            description="Récupérer la liste des livraisons de carburant avec pagination. Ces endpoints gèrent les livraisons physiques de carburant enregistrées indépendamment des commandes d'achat, à ne pas confondre avec les fonctionnalités liées aux achats de carburant dans le module correspondant. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def get_livraisons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste des livraisons de carburant avec pagination

    Cette fonction récupère les livraisons de carburant enregistrées dans le système.
    Les livraisons sont distinctes des commandes d'achat et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        skip (int): Nombre de livraisons à ignorer pour la pagination
        limit (int): Nombre maximum de livraisons à retourner
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        List[schemas.LivraisonCreate]: Liste des livraisons de carburant

    Raises:
        HTTPException: Si l'utilisateur n'est pas autorisé
    """
    livraisons = db.query(LivraisonModel).offset(skip).limit(limit).all()
    return livraisons

@router.post("/",
             response_model=schemas.LivraisonResponse,
             summary="Créer une livraison",
             description="Créer une nouvelle livraison de carburant dans le système. Cette endpoint gère les livraisons physiques de carburant indépendamment des commandes d'achat. La livraison représente l'approvisionnement effectif des cuves et est utilisée pour les calculs de stock théorique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def create_livraison(
    livraison: schemas.LivraisonCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer une nouvelle livraison de carburant

    Cette fonction crée une nouvelle livraison de carburant qui représente
    une livraison physique effectuée aux cuves, distincte des commandes d'achat.

    Args:
        livraison (schemas.LivraisonCreate): Données de la nouvelle livraison
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonCreate: La livraison nouvellement créée

    Raises:
        HTTPException: Si une erreur survient lors de la création
    """
    # Calculate montant_total if prix_unitaire is provided
    montant_total = None
    if livraison.prix_unitaire:
        montant_total = livraison.prix_unitaire * livraison.quantite_livree

    # Create the livraison record
    db_livraison = LivraisonModel(
        station_id=livraison.station_id,
        cuve_id=livraison.cuve_id,
        carburant_id=livraison.carburant_id,
        quantite_livree=livraison.quantite_livree,
        date=livraison.date,
        fournisseur_id=livraison.fournisseur_id,
        numero_bl=livraison.numero_bl,
        numero_facture=livraison.numero_facture,
        prix_unitaire=livraison.prix_unitaire,
        montant_total=montant_total,
        jauge_avant=livraison.jauge_avant,
        jauge_apres=livraison.jauge_apres,
        utilisateur_id=livraison.utilisateur_id,
        commentaires=livraison.commentaires,
        compagnie_id=livraison.compagnie_id
    )

    db.add(db_livraison)
    db.commit()
    db.refresh(db_livraison)

    return db_livraison

@router.get("/{livraison_id}",
            response_model=schemas.LivraisonResponse,
            summary="Récupérer une livraison par ID",
            description="Récupérer les détails d'une livraison de carburant spécifique par son identifiant. Cette endpoint gère les livraisons physiques de carburant enregistrées indépendamment des commandes d'achat. Permet d'obtenir toutes les informations relatives à une livraison spécifique, y compris les mesures de jauge et les différences éventuelles. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def get_livraison_by_id(
    livraison_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer les détails d'une livraison spécifique par son ID

    Cette fonction récupère les détails d'une livraison spécifique de carburant.
    Les livraisons sont distinctes des commandes d'achat et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (int): Identifiant de la livraison
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonCreate: Détails de la livraison demandée

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")
    return livraison

@router.put("/{livraison_id}",
            response_model=schemas.LivraisonResponse,
            summary="Mettre à jour une livraison",
            description="Mettre à jour les informations d'une livraison de carburant existante. Cette endpoint gère les livraisons physiques de carburant enregistrées indépendamment des commandes d'achat. La mise à jour peut affecter les calculs de stock et les vérifications d'écarts. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def update_livraison(
    livraison_id: int,
    livraison: schemas.LivraisonUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour une livraison existante

    Cette fonction met à jour une livraison de carburant existante.
    Les livraisons sont distinctes des commandes d'achat et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (int): Identifiant de la livraison à mettre à jour
        livraison (schemas.LivraisonUpdate): Nouvelles données de la livraison
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonUpdate: La livraison mise à jour

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    db_livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not db_livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")

    update_data = livraison.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_livraison, field, value)

    # Recalculate montant_total if prix_unitaire is updated
    if livraison.prix_unitaire and db_livraison.quantite_livree:
        db_livraison.montant_total = livraison.prix_unitaire * db_livraison.quantite_livree

    db.commit()
    db.refresh(db_livraison)
    return db_livraison

@router.delete("/{livraison_id}",
               summary="Supprimer une livraison",
               description="Supprimer une livraison de carburant du système. Cette endpoint gère les livraisons physiques de carburant enregistrées indépendamment des commandes d'achat. La suppression affecte les calculs de stock théorique et les vérifications d'écarts. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def delete_livraison(
    livraison_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprimer une livraison existante

    Cette fonction supprime une livraison de carburant du système.
    Les livraisons sont distinctes des commandes d'achat et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (int): Identifiant de la livraison à supprimer
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        dict: Message de confirmation de suppression

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    livraison = db.query(LivraisonModel).filter(LivraisonModel.id == livraison_id).first()
    if not livraison:
        raise HTTPException(status_code=404, detail="Livraison not found")

    db.delete(livraison)
    db.commit()
    return {"message": "Livraison deleted successfully"}

@router.get("/{cuve_id}/historique",
            response_model=List[schemas.LivraisonResponse],
            summary="Historique des livraisons pour une cuve",
            description="Récupérer l'historique des livraisons pour une cuve spécifique. Cette endpoint gère les livraisons physiques de carburant enregistrées indépendamment des commandes d'achat. Permet de visualiser toutes les livraisons effectuées à une cuve précise pour des analyses de stock ou de performance. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.")
async def get_livraisons_by_cuve(
    cuve_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer l'historique des livraisons pour une cuve spécifique

    Cette fonction récupère l'historique de toutes les livraisons effectuées
    à une cuve spécifique. Les livraisons sont distinctes des commandes d'achat
    et représentent les livraisons physiques effectuées aux cuves.

    Args:
        cuve_id (str): Identifiant de la cuve (UUID)
        skip (int): Nombre de livraisons à ignorer pour la pagination
        limit (int): Nombre maximum de livraisons à retourner
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        List[schemas.LivraisonResponse]: Historique des livraisons pour la cuve spécifiée

    Raises:
        HTTPException: Si l'utilisateur n'est pas autorisé
    """
    livraisons = db.query(LivraisonModel).filter(LivraisonModel.cuve_id == cuve_id).offset(skip).limit(limit).all()
    return livraisons
