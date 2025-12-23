from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Livraison as LivraisonModel
from . import schemas
from ..services.livraisons.livraison_service import (
    get_livraisons as service_get_livraisons,
    get_livraison_by_id as service_get_livraison_by_id,
    create_livraison as service_create_livraison,
    update_livraison as service_update_livraison,
    delete_livraison as service_delete_livraison,
    get_livraisons_by_cuve as service_get_livraisons_by_cuve
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid
from ..rbac_decorators import require_permission

router = APIRouter(
    prefix="/livraisons",
    responses={404: {"description": "Livraison non trouvée"}}
)
security = HTTPBearer()

@router.get("/",
            response_model=List[schemas.LivraisonResponse],
            summary="Récupérer les livraisons",
            description="Récupérer la liste des livraisons de carburant avec pagination. Ces endpoints gèrent les livraisons physiques de carburant liées aux achats de carburant. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
            dependencies=[Depends(require_permission("livraisons", "read"))])
async def get_livraisons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer la liste des livraisons de carburant avec pagination

    Cette fonction récupère les livraisons de carburant enregistrées dans le système.
    Les livraisons sont liées aux achats de carburant et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        skip (int): Nombre de livraisons à ignorer pour la pagination
        limit (int): Nombre maximum de livraisons à retourner
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        List[schemas.LivraisonResponse]: Liste des livraisons de carburant

    Raises:
        HTTPException: Si l'utilisateur n'est pas autorisé
    """
    try:
        livraisons = service_get_livraisons(db, skip, limit)
        return livraisons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/",
             response_model=schemas.LivraisonResponse,
             summary="Créer une livraison",
             description="Créer une nouvelle livraison de carburant dans le système. Cette endpoint gère les livraisons physiques de carburant liées aux achats de carburant. La livraison représente l'approvisionnement effectif des cuves et est utilisée pour les calculs de stock théorique. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
             dependencies=[Depends(require_permission("livraisons", "create"))])
async def create_livraison(
    livraison: schemas.LivraisonCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Créer une nouvelle livraison de carburant

    Cette fonction crée une nouvelle livraison de carburant qui représente
    une livraison physique effectuée aux cuves, liée à un achat de carburant.

    Args:
        livraison (schemas.LivraisonCreate): Données de la nouvelle livraison
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonResponse: La livraison nouvellement créée

    Raises:
        HTTPException: Si une erreur survient lors de la création
    """
    try:
        # Validate UUID fields
        uuid.UUID(livraison.station_id)
        uuid.UUID(livraison.cuve_id)
        uuid.UUID(livraison.carburant_id)
        uuid.UUID(livraison.utilisateur_id)
        uuid.UUID(livraison.compagnie_id)

        if livraison.achat_carburant_id:
            uuid.UUID(livraison.achat_carburant_id)

        return service_create_livraison(db, livraison)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{livraison_id}",
            response_model=schemas.LivraisonResponse,
            summary="Récupérer une livraison par ID",
            description="Récupérer les détails d'une livraison de carburant spécifique par son identifiant. Cette endpoint gère les livraisons physiques de carburant liées aux achats de carburant. Permet d'obtenir toutes les informations relatives à une livraison spécifique, y compris les mesures de jauge et les différences éventuelles. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
            dependencies=[Depends(require_permission("livraisons", "read"))])
async def get_livraison_by_id(
    livraison_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer les détails d'une livraison spécifique par son ID

    Cette fonction récupère les détails d'une livraison spécifique de carburant.
    Les livraisons sont liées aux achats de carburant et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (str): Identifiant de la livraison (UUID)
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonResponse: Détails de la livraison demandée

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    try:
        uuid.UUID(livraison_id)
        return service_get_livraison_by_id(db, livraison_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{livraison_id}",
            response_model=schemas.LivraisonResponse,
            summary="Mettre à jour une livraison",
            description="Mettre à jour les informations d'une livraison de carburant existante. Cette endpoint gère les livraisons physiques de carburant liées aux achats de carburant. La mise à jour peut affecter les calculs de stock et les vérifications d'écarts. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
            dependencies=[Depends(require_permission("livraisons", "update"))])
async def update_livraison(
    livraison_id: str,
    livraison: schemas.LivraisonUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Mettre à jour une livraison existante

    Cette fonction met à jour une livraison de carburant existante.
    Les livraisons sont liées aux achats de carburant et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (str): Identifiant de la livraison à mettre à jour (UUID)
        livraison (schemas.LivraisonUpdate): Nouvelles données de la livraison
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        schemas.LivraisonResponse: La livraison mise à jour

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    try:
        uuid.UUID(livraison_id)
        return service_update_livraison(db, livraison_id, livraison)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{livraison_id}",
               summary="Supprimer une livraison",
               description="Supprimer une livraison de carburant du système. Cette endpoint gère les livraisons physiques de carburant liées aux achats de carburant. La suppression affecte les calculs de stock théorique et les vérifications d'écarts. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
               dependencies=[Depends(require_permission("livraisons", "delete"))])
async def delete_livraison(
    livraison_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprimer une livraison existante

    Cette fonction supprime une livraison de carburant du système.
    Les livraisons sont liées aux achats de carburant et représentent les livraisons
    physiques effectuées aux cuves.

    Args:
        livraison_id (str): Identifiant de la livraison à supprimer (UUID)
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        dict: Message de confirmation de suppression

    Raises:
        HTTPException: Si la livraison n'est pas trouvée
    """
    try:
        uuid.UUID(livraison_id)
        success = service_delete_livraison(db, livraison_id)
        if success:
            return {"message": "Livraison deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Livraison not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cuve/{cuve_id}/historique",
            response_model=List[schemas.LivraisonResponse],
            summary="Historique des livraisons pour une cuve",
            description="Récupérer l'historique des livraisons pour une cuve spécifique. Cette endpoint gère les livraisons physiques de carburant liées aux achats de carburant. Permet de visualiser toutes les livraisons effectuées à une cuve précise pour des analyses de stock ou de performance. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
            dependencies=[Depends(require_permission("livraisons", "read"))])
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
    à une cuve spécifique. Les livraisons sont liées aux achats de carburant
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
    try:
        uuid.UUID(cuve_id)
        livraisons = service_get_livraisons_by_cuve(db, cuve_id, skip, limit)
        return livraisons
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/achat/{achat_carburant_id}/livraisons",
            response_model=List[schemas.LivraisonResponse],
            summary="Historique des livraisons pour un achat de carburant",
            description="Récupérer l'historique des livraisons liées à un achat de carburant spécifique. Cette endpoint permet de suivre les livraisons effectuées pour un achat donné, utile pour comparer les quantités commandées vs livrées. Nécessite des droits d'accès appropriés selon le rôle de l'utilisateur.",
            dependencies=[Depends(require_permission("livraisons", "read"))])
async def get_livraisons_by_achat(
    achat_carburant_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupérer l'historique des livraisons liées à un achat de carburant spécifique

    Cette fonction récupère l'historique de toutes les livraisons effectuées
    pour un achat de carburant spécifique. Cela permet de suivre les livraisons
    par rapport aux commandes et de comparer les quantités.

    Args:
        achat_carburant_id (str): Identifiant de l'achat de carburant (UUID)
        skip (int): Nombre de livraisons à ignorer pour la pagination
        limit (int): Nombre maximum de livraisons à retourner
        db (Session): Session de base de données SQLAlchemy
        credentials: Informations d'authentification

    Returns:
        List[schemas.LivraisonResponse]: Historique des livraisons pour l'achat spécifié

    Raises:
        HTTPException: Si l'utilisateur n'est pas autorisé
    """
    try:
        uuid.UUID(achat_carburant_id)
        livraisons = db.query(LivraisonModel).filter(LivraisonModel.achat_carburant_id == achat_carburant_id).offset(skip).limit(limit).all()
        return livraisons
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
