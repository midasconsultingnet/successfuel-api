from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.ventes import (
    get_ventes as service_get_ventes,
    create_vente as service_create_vente,
    get_vente_by_id as service_get_vente_by_id,
    update_vente as service_update_vente,
    delete_vente as service_delete_vente,
    get_vente_details as service_get_vente_details,
    get_ventes_carburant as service_get_ventes_carburant,
    create_vente_carburant as service_create_vente_carburant,
    get_vente_carburant_by_id as service_get_vente_carburant_by_id,
    update_vente_carburant as service_update_vente_carburant,
    delete_vente_carburant as service_delete_vente_carburant,
    get_creances_employes as service_get_creances_employes,
    get_creance_employe_by_id as service_get_creance_employe_by_id
)

router = APIRouter(
    prefix="/ventes",
    responses={404: {"description": "Vente non trouvée"}}
)
security = HTTPBearer()

@router.get("/",
            response_model=List[schemas.VenteCreate],
            summary="Récupérer les ventes de produits",
            description="Récupérer la liste des ventes de produits avec pagination. Cet endpoint permet de consulter toutes les ventes effectuées dans le module de boutique, avec filtrage possible par utilisateur, station et compagnie. Nécessite la permission 'Module Ventes Boutique'.",
            tags=["Ventes"])
async def get_ventes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Récupère la liste des ventes de produits avec pagination.

    Cet endpoint permet de récupérer toutes les ventes effectuées dans le module de boutique.
    Les ventes sont filtrées par la compagnie de l'utilisateur connecté.

    Args:
        skip (int): Nombre de ventes à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de ventes à retourner (défaut: 100)
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        List[schemas.VenteCreate]: Liste des ventes de produits

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module
    """
    return service_get_ventes(db, current_user, skip, limit)

@router.post("/",
             response_model=schemas.VenteCreate,
             summary="Créer une nouvelle vente de produits",
             description="Crée une nouvelle vente de produits dans le système. Cet endpoint permet d'enregistrer une vente avec ses détails, y compris les produits vendus, les quantités, les prix et les éventuelles remises. Nécessite la permission 'Module Ventes Boutique'.",
             tags=["Ventes"])
async def create_vente(
    vente: schemas.VenteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Crée une nouvelle vente de produits.

    Cet endpoint permet d'enregistrer une nouvelle vente dans le module de boutique.
    La vente est liée à la compagnie de l'utilisateur connecté.

    Args:
        vente (schemas.VenteCreate): Données de la vente à créer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteCreate: La vente nouvellement créée

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module
    """
    return service_create_vente(db, current_user, vente)

@router.get("/{vente_id}",
            response_model=schemas.VenteCreate,
            summary="Récupérer une vente de produit par ID",
            description="Récupère les détails d'une vente de produit spécifique par son identifiant. Cet endpoint permet d'obtenir toutes les informations relatives à une vente spécifique, y compris ses détails de produits vendus. Nécessite la permission 'Module Ventes Boutique'.",
            tags=["Ventes"])
async def get_vente_by_id(
    vente_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Récupère les détails d'une vente de produit spécifique par son identifiant.

    Cet endpoint permet d'obtenir toutes les informations relatives à une vente spécifique,
    y compris ses détails de produits vendus.

    Args:
        vente_id (uuid.UUID): L'identifiant de la vente à récupérer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteCreate: Détails de la vente demandée

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_get_vente_by_id(db, current_user, vente_id)

@router.put("/{vente_id}",
            response_model=schemas.VenteUpdate,
            summary="Mettre à jour une vente de produit",
            description="Met à jour les informations d'une vente de produit existante. Cet endpoint permet de modifier les détails d'une vente, comme le client, la date, le statut ou le numéro de pièce comptable. Nécessite la permission 'Module Ventes Boutique'.",
            tags=["Ventes"])
async def update_vente(
    vente_id: uuid.UUID,
    vente: schemas.VenteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Met à jour les informations d'une vente de produit existante.

    Cet endpoint permet de modifier les détails d'une vente, comme le client,
    la date, le statut ou le numéro de pièce comptable.

    Args:
        vente_id (uuid.UUID): L'identifiant de la vente à mettre à jour
        vente (schemas.VenteUpdate): Nouvelles données de la vente
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteUpdate: La vente mise à jour

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_update_vente(db, current_user, vente_id, vente)

@router.delete("/{vente_id}",
               summary="Supprimer une vente de produit",
               description="Supprime une vente de produit du système. Cet endpoint effectue une suppression logique de la vente en mettant à jour son statut. Nécessite la permission 'Module Ventes Boutique'.",
               tags=["Ventes"])
async def delete_vente(
    vente_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Supprime une vente de produit du système.

    Cet endpoint effectue une suppression logique de la vente en mettant à jour son statut.

    Args:
        vente_id (uuid.UUID): L'identifiant de la vente à supprimer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        dict: Message de confirmation de suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_delete_vente(db, current_user, vente_id)

@router.get("/{vente_id}/details",
            response_model=List[schemas.VenteDetailCreate],
            summary="Récupérer les détails d'une vente",
            description="Récupère les détails d'une vente spécifique, y compris les produits vendus, les quantités, les prix unitaires et les montants. Nécessite la permission 'Module Ventes Boutique'.",
            tags=["Ventes"])
async def get_vente_details(
    vente_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Boutique"))
):
    """
    Récupère les détails d'une vente spécifique.

    Cet endpoint permet d'obtenir les détails d'une vente spécifique, y compris
    les produits vendus, les quantités, les prix unitaires et les montants.

    Args:
        vente_id (uuid.UUID): L'identifiant de la vente
        skip (int): Nombre de détails à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de détails à retourner (défaut: 100)
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        List[schemas.VenteDetailCreate]: Liste des détails de la vente

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_get_vente_details(db, current_user, vente_id, skip, limit)

# Endpoints pour les ventes de carburant
@router.get("/carburant",
            response_model=List[schemas.VenteCarburantCreate],
            summary="Récupérer les ventes de carburant",
            description="Récupérer la liste des ventes de carburant avec pagination. Cet endpoint permet de consulter toutes les ventes de carburant effectuées, y compris les détails de quantité vendue, prix, indices de pistolet et éventuels écarts de mesure. Nécessite la permission 'Module Ventes Carburant'.",
            tags=["Ventes"])
async def get_ventes_carburant(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Récupère la liste des ventes de carburant avec pagination.

    Cet endpoint permet de récupérer toutes les ventes de carburant effectuées.
    Les ventes sont filtrées par la compagnie de l'utilisateur connecté.

    Args:
        skip (int): Nombre de ventes à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de ventes à retourner (défaut: 100)
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        List[schemas.VenteCarburantCreate]: Liste des ventes de carburant

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module
    """
    return service_get_ventes_carburant(db, current_user, skip, limit)

@router.post("/carburant",
             response_model=schemas.VenteCarburantCreate,
             summary="Créer une nouvelle vente de carburant",
             description="Crée une nouvelle vente de carburant dans le système. Cet endpoint permet d'enregistrer une vente de carburant avec les détails de quantité vendue, indices de pistolet, prix de vente et informations sur le pompiste. Nécessite la permission 'Module Ventes Carburant'.",
             tags=["Ventes"])
async def create_vente_carburant(
    vente_carburant: schemas.VenteCarburantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Crée une nouvelle vente de carburant.

    Cet endpoint permet d'enregistrer une nouvelle vente de carburant dans le module
    de distribution de carburant. La vente est liée à la compagnie de l'utilisateur connecté.

    Args:
        vente_carburant (schemas.VenteCarburantCreate): Données de la vente de carburant à créer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteCarburantCreate: La vente de carburant nouvellement créée

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module
    """
    # Appel au service pour créer la vente carburant
    return service_create_vente_carburant(db, current_user, vente_carburant)

@router.get("/carburant/{vente_carburant_id}",
            response_model=schemas.VenteCarburantCreate,
            summary="Récupérer une vente de carburant par ID",
            description="Récupère les détails d'une vente de carburant spécifique par son identifiant. Cet endpoint permet d'obtenir toutes les informations relatives à une vente de carburant spécifique, y compris les indices de pistolet, les mesures et les éventuels écarts. Nécessite la permission 'Module Ventes Carburant'.",
            tags=["Ventes"])
async def get_vente_carburant_by_id(
    vente_carburant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Récupère les détails d'une vente de carburant spécifique par son identifiant.

    Cet endpoint permet d'obtenir toutes les informations relatives à une vente
    de carburant spécifique, y compris les indices de pistolet, les mesures et
    les éventuels écarts.

    Args:
        vente_carburant_id (uuid.UUID): L'identifiant de la vente de carburant à récupérer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteCarburantCreate: Détails de la vente de carburant demandée

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_get_vente_carburant_by_id(db, current_user, vente_carburant_id)

@router.put("/carburant/{vente_carburant_id}",
            response_model=schemas.VenteCarburantUpdate,
            summary="Mettre à jour une vente de carburant",
            description="Met à jour les informations d'une vente de carburant existante. Cet endpoint permet de modifier les détails d'une vente de carburant, comme le mode de paiement, le montant payé, ou le statut. Nécessite la permission 'Module Ventes Carburant'.",
            tags=["Ventes"])
async def update_vente_carburant(
    vente_carburant_id: uuid.UUID,
    vente_carburant: schemas.VenteCarburantUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Met à jour les informations d'une vente de carburant existante.

    Cet endpoint permet de modifier les détails d'une vente de carburant,
    comme le mode de paiement, le montant payé, ou le statut.

    Args:
        vente_carburant_id (uuid.UUID): L'identifiant de la vente de carburant à mettre à jour
        vente_carburant (schemas.VenteCarburantUpdate): Nouvelles données de la vente de carburant
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.VenteCarburantUpdate: La vente de carburant mise à jour

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_update_vente_carburant(db, current_user, vente_carburant_id, vente_carburant)

@router.delete("/carburant/{vente_carburant_id}",
               summary="Supprimer une vente de carburant",
               description="Supprime une vente de carburant du système. Cet endpoint effectue une suppression logique de la vente en mettant à jour son statut. Nécessite la permission 'Module Ventes Carburant'.",
               tags=["Ventes"])
async def delete_vente_carburant(
    vente_carburant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Supprime une vente de carburant du système.

    Cet endpoint effectue une suppression logique de la vente en mettant à jour son statut.

    Args:
        vente_carburant_id (uuid.UUID): L'identifiant de la vente de carburant à supprimer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        dict: Message de confirmation de suppression

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la vente n'existe pas
    """
    return service_delete_vente_carburant(db, current_user, vente_carburant_id)

# Endpoints pour les créances employés
@router.get("/creances_employes",
            response_model=List[schemas.CreanceEmployeCreate],
            summary="Récupérer les créances des employés",
            description="Récupérer la liste des créances des employés avec pagination. Cet endpoint permet de consulter toutes les créances liées aux employés (notamment les pompistes) pour les ventes de carburant, y compris les montants dus, les montants payés et les dates d'échéance. Nécessite la permission 'Module Ventes Carburant'.",
            tags=["Ventes"])
async def get_creances_employes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Récupère la liste des créances des employés avec pagination.

    Cet endpoint permet de récupérer toutes les créances liées aux employés
    (notamment les pompistes) pour les ventes de carburant.

    Args:
        skip (int): Nombre de créances à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de créances à retourner (défaut: 100)
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        List[schemas.CreanceEmployeCreate]: Liste des créances des employés

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module
    """
    return service_get_creances_employes(db, current_user, skip, limit)

@router.get("/creances_employes/{creance_id}",
            response_model=schemas.CreanceEmployeCreate,
            summary="Récupérer une créance employé par ID",
            description="Récupère les détails d'une créance d'employé spécifique par son identifiant. Cet endpoint permet d'obtenir toutes les informations relatives à une créance d'employé spécifique, y compris le montant dû, le montant payé et la date d'échéance. Nécessite la permission 'Module Ventes Carburant'.",
            tags=["Ventes"])
async def get_creance_employe_by_id(
    creance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Ventes Carburant"))
):
    """
    Récupère les détails d'une créance d'employé spécifique par son identifiant.

    Cet endpoint permet d'obtenir toutes les informations relatives à une
    créance d'employé spécifique, y compris le montant dû, le montant payé
    et la date d'échéance.

    Args:
        creance_id (uuid.UUID): L'identifiant de la créance d'employé à récupérer
        db (Session): Session de base de données
        current_user: Informations sur l'utilisateur connecté (fourni par le décorateur de permission)

    Returns:
        schemas.CreanceEmployeCreate: Détails de la créance d'employé demandée

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission d'accéder à ce module ou si la créance n'existe pas
    """
    return service_get_creance_employe_by_id(db, current_user, creance_id)
