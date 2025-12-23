from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
import logging
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission

# Création d'un logger spécifique pour ce module
logger = logging.getLogger(__name__)
from ..services.tresoreries import (
    get_tresoreries_station as service_get_tresoreries_station,
    get_tresoreries_station_by_station as service_get_tresoreries_station_by_station,
    get_tresoreries as service_get_tresoreries,
    create_tresorerie as service_create_tresorerie,
    get_tresorerie_by_id as service_get_tresorerie_by_id,
    update_tresorerie as service_update_tresorerie,
    delete_tresorerie as service_delete_tresorerie,
    create_tresorerie_station as service_create_tresorerie_station,
    get_tresorerie_station_by_id as service_get_tresorerie_station_by_id,
    update_tresorerie_station as service_update_tresorerie_station,
    delete_tresorerie_station as service_delete_tresorerie_station,
    create_etat_initial_tresorerie as service_create_etat_initial_tresorerie,
    create_mouvement_tresorerie as service_create_mouvement_tresorerie,
    get_mouvements_tresorerie as service_get_mouvements_tresorerie,
    get_mouvements_tresorerie_by_id as service_get_mouvements_tresorerie_by_id,
    get_mouvement_tresorerie_by_id as service_get_mouvement_tresorerie_by_id,
    update_mouvement_tresorerie as service_update_mouvement_tresorerie,
    delete_mouvement_tresorerie as service_delete_mouvement_tresorerie,
    annuler_mouvement_tresorerie as service_annuler_mouvement_tresorerie,
    create_transfert_tresorerie as service_create_transfert_tresorerie,
    get_transferts_tresorerie as service_get_transferts_tresorerie,
    get_transfert_tresorerie_by_id as service_get_transfert_tresorerie_by_id,
    update_transfert_tresorerie as service_update_transfert_tresorerie,
    delete_transfert_tresorerie as service_delete_transfert_tresorerie,
    mettre_a_jour_solde_tresorerie as service_mettre_a_jour_solde_tresorerie,
    get_solde_tresorerie as service_get_solde_tresorerie,
    get_solde_tresorerie_station as service_get_solde_tresorerie_station,
    refresh_vue_solde_tresorerie as service_refresh_vue_solde_tresorerie,
    cloture_soldes_mensuels as service_cloture_soldes_mensuels,
    get_tresoreries_sans_methode_paiement as service_get_tresoreries_sans_methode_paiement
)

router = APIRouter(tags=["Tresorerie"])

# Tresorerie station endpoints
@router.get("/stations",
            response_model=List[schemas.StationTresorerieResponse],
            summary="Récupérer les tresoreries par station",
            description="Récupère la liste des tresoreries associées aux stations avec pagination. Permet de consulter toutes les tresoreries définies par station, y compris leurs soldes et configurations. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les stations concernées.",
            tags=["Tresorerie"])
async def get_tresoreries_station(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries_station(db, current_user, skip, limit)


# Tresorerie endpoints (globales) - Using root path to avoid double nesting
@router.get("/",
            response_model=List[schemas.TresorerieResponse],
            summary="Récupérer les tresoreries globales",
            description="Récupère la liste des tresoreries globales avec pagination. Ces tresoreries sont des comptes généraux qui ne sont pas spécifiquement liés à une station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les tresoreries concernées.",
            tags=["Tresorerie"])
async def get_tresoreries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries(db, current_user, skip, limit)

@router.post("/",
             response_model=schemas.TresorerieResponse,
             summary="Créer une nouvelle trésorerie globale",
             description="Crée une nouvelle trésorerie globale dans le système. Une trésorerie globale est un compte général qui ne dépend pas d'une station spécifique. Le solde initial est défini lors de l'affectation à une station via l'endpoint POST /api/v1/tresoreries/stations. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la trésorerie à créer.",
             tags=["Tresorerie"])
async def create_tresorerie(
    tresorerie: schemas.TresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    logger.info(f"Début de la création d'une nouvelle trésorerie: {tresorerie.nom}")
    logger.debug(f"Payload reçu pour la création de la trésorerie: {tresorerie}")
    logger.debug(f"Utilisateur courant: {current_user.id}")

    result = service_create_tresorerie(db, current_user, tresorerie)

    logger.info(f"Trésorerie créée avec succès. ID: {result.id}, Nom: {result.nom}")
    logger.debug(f"Détails de la trésorerie créée: ID={result.id}, Nom={result.nom}, Solde initial={result.solde_initial}, Solde trésorerie={result.solde_tresorerie}, Devise={result.devise}, Type={result.type}, Statut={result.statut}")

    return result


# Endpoints spécifiques (doivent être définis avant les routes avec paramètres pour éviter les conflits)
@router.get("/sans_methode_paiement",
            response_model=List[schemas.TresorerieResponse],
            summary="Récupérer les tresoreries sans méthode de paiement",
            description="Récupère la liste des tresoreries qui n'ont aucune méthode de paiement associée. Permet d'identifier les tresoreries qui n'ont pas encore été configurées avec des méthodes de paiement. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les tresoreries concernées.",
            tags=["Tresorerie"])
async def get_tresoreries_sans_methode_paiement(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries_sans_methode_paiement(db, current_user)


@router.post("/stations",
             response_model=schemas.TresorerieStationResponse,
             summary="Créer une nouvelle trésorerie associée à une station",
             description="Crée une nouvelle trésorerie liée à une station spécifique. Cette trésorerie est utilisée pour gérer les flux financiers spécifiques à une station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
             tags=["Tresorerie"])
async def create_tresorerie_station(
    tresorerie_station: schemas.TresorerieStationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_tresorerie_station(db, current_user, tresorerie_station)




@router.get("/stations/{station_id}/tresoreries",
            response_model=List[schemas.StationTresorerieResponse],
            summary="Récupérer les tresoreries d'une station spécifique",
            description="Récupère la liste des tresoreries associées à une station spécifique par son identifiant. Permet de consulter toutes les tresoreries définies pour une station particulière, y compris leurs soldes et configurations. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la station concernée.",
            tags=["Tresorerie"])
async def get_tresoreries_station_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries_station_by_station(db, current_user, station_id)

# CRUD pour TresorerieStation


# CRUD pour MouvementTresorerie
@router.post("/mouvements",
             response_model=schemas.MouvementTresorerieResponse,
             summary="Créer un nouveau mouvement de trésorerie",
             description="Crée un nouveau mouvement (entrée/sortie) dans une trésorerie station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
             tags=["Tresorerie"])
async def create_mouvement_tresorerie(
    mouvement: schemas.MouvementTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_mouvement_tresorerie(db, current_user, mouvement)


@router.get("/mouvements",
            response_model=List[schemas.MouvementTresorerieResponse],
            summary="Récupérer tous les mouvements de trésorerie",
            description="Récupère la liste de tous les mouvements de trésorerie avec pagination. Nécessite la permission 'Module Trésorerie'. L'utilisateur ne peut voir que les mouvements liés à sa compagnie.",
            tags=["Tresorerie"])
async def get_all_mouvements_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_mouvements_tresorerie(db, current_user, skip, limit)


@router.get("/mouvements/{mouvement_id}",
            response_model=schemas.MouvementTresorerieResponse,
            summary="Récupérer un mouvement de trésorerie",
            description="Récupère les détails d'un mouvement de trésorerie spécifique par son identifiant. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
            tags=["Tresorerie"])
async def get_mouvement_tresorerie_by_id(
    mouvement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_mouvement_tresorerie_by_id(db, current_user, mouvement_id)


@router.put("/mouvements/{mouvement_id}",
            response_model=schemas.MouvementTresorerieResponse,
            summary="Mettre à jour un mouvement de trésorerie",
            description="Met à jour les informations d'un mouvement de trésorerie existant. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
            tags=["Tresorerie"])
async def update_mouvement_tresorerie(
    mouvement_id: uuid.UUID,
    mouvement: schemas.MouvementTresorerieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_update_mouvement_tresorerie(db, current_user, mouvement_id, mouvement)


@router.post("/mouvements/{mouvement_id}/annuler",
             summary="Annuler un mouvement de trésorerie",
             description="Annule un mouvement de trésorerie existant en créant un mouvement inverse. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
             tags=["Tresorerie"])
async def annuler_mouvement_tresorerie(
    mouvement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_annuler_mouvement_tresorerie(db, current_user, mouvement_id)


@router.delete("/mouvements/{mouvement_id}",
                summary="Supprimer un mouvement de trésorerie",
                description="Supprime un mouvement de trésorerie du système. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
                tags=["Tresorerie"])
async def delete_mouvement_tresorerie(
    mouvement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_delete_mouvement_tresorerie(db, current_user, mouvement_id)




# CRUD pour TransfertTresorerie
@router.post("/transferts",
             response_model=schemas.TransfertTresorerieResponse,
             summary="Créer un nouveau transfert de trésorerie",
             description="Crée un nouveau transfert entre deux trésoreries. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
             tags=["Tresorerie"])
async def create_transfert_tresorerie(
    transfert: schemas.TransfertTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_transfert_tresorerie(db, current_user, transfert)


@router.get("/transferts",
            response_model=List[schemas.TransfertTresorerieResponse],
            summary="Récupérer tous les transferts de trésorerie",
            description="Récupère la liste de tous les transferts de trésorerie avec pagination. Nécessite la permission 'Module Trésorerie'. L'utilisateur ne peut voir que les transferts liés à sa compagnie.",
            tags=["Tresorerie"])
async def get_all_transferts_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_transferts_tresorerie(db, current_user, skip, limit)


@router.get("/transferts/{transfert_id}",
            response_model=schemas.TransfertTresorerieResponse,
            summary="Récupérer un transfert de trésorerie",
            description="Récupère les détails d'un transfert de trésorerie spécifique par son identifiant. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
            tags=["Tresorerie"])
async def get_transfert_tresorerie_by_id(
    transfert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_transfert_tresorerie_by_id(db, current_user, transfert_id)


@router.put("/transferts/{transfert_id}",
            response_model=schemas.TransfertTresorerieResponse,
            summary="Mettre à jour un transfert de trésorerie",
            description="Met à jour les informations d'un transfert de trésorerie existant. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
            tags=["Tresorerie"])
async def update_transfert_tresorerie(
    transfert_id: uuid.UUID,
    transfert: schemas.TransfertTresorerieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_update_transfert_tresorerie(db, current_user, transfert_id, transfert)


@router.delete("/transferts/{transfert_id}",
                summary="Supprimer un transfert de trésorerie",
                description="Supprime un transfert de trésorerie du système. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
                tags=["Tresorerie"])
async def delete_transfert_tresorerie(
    transfert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_delete_transfert_tresorerie(db, current_user, transfert_id)


# Endpoints spécifiques pour la nouvelle architecture
@router.post("/refresh-solde",
             summary="Rafraîchir les vues matérialisées de solde",
             description="Force le rafraîchissement des vues matérialisées de solde de trésorerie. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
             tags=["Tresorerie"])
async def refresh_solde_tresorerie(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_refresh_vue_solde_tresorerie(db)


@router.post("/cloture-mensuelle",
             summary="Clôture des soldes mensuels",
             description="Effectue la clôture mensuelle des soldes de trésorerie. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
             tags=["Tresorerie"])
async def cloture_soldes_mensuels(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    # Pour l'instant, on effectue la clôture pour le mois en cours
    from datetime import datetime
    return service_cloture_soldes_mensuels(db, datetime.utcnow().date())


# Routes par ID (doivent être à la fin pour éviter les conflits avec les routes nommées)
@router.get("/{tresorerie_id}",
            response_model=schemas.TresorerieResponse,
            summary="Récupérer une trésorerie par ID",
            description="Récupère les détails d'une trésorerie spécifique par son identifiant. Permet d'obtenir toutes les informations relatives à une trésorerie, y compris son solde, sa station associée et ses paramètres de configuration. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la trésorerie concernée via sa compagnie ou sa station.",
            tags=["Tresorerie"])
async def get_tresorerie_by_id(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresorerie_by_id(db, current_user, tresorerie_id)

@router.put("/{tresorerie_id}",
            response_model=schemas.TresorerieResponse,
            summary="Mettre à jour une trésorerie",
            description="Met à jour les informations d'une trésorerie existante. Permet de modifier les détails d'une trésorerie, comme son nom, sa devise ou ses paramètres de configuration. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la trésorerie concernée via sa compagnie ou sa station.",
            tags=["Tresorerie"])
async def update_tresorerie(
    tresorerie_id: uuid.UUID,
    tresorerie: schemas.TresorerieUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_update_tresorerie(db, current_user, tresorerie_id, tresorerie)

@router.delete("/{tresorerie_id}",
                summary="Supprimer une trésorerie",
                description="Supprime une trésorerie du système. Cette opération effectue une suppression logique de la trésorerie. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la trésorerie concernée via sa compagnie ou sa station. Ne doit être effectuée que si la trésorerie n'a pas d'opérations en cours ou liées.",
                tags=["Tresorerie"])
async def delete_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_delete_tresorerie(db, current_user, tresorerie_id)

@router.post("/stations",
             response_model=schemas.TresorerieStationResponse,
             summary="Créer une nouvelle trésorerie associée à une station",
             description="Crée une nouvelle trésorerie liée à une station spécifique. Cette trésorerie est utilisée pour gérer les flux financiers spécifiques à une station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
             tags=["Tresorerie"])
async def create_tresorerie_station(
    tresorerie_station: schemas.TresorerieStationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_tresorerie_station(db, current_user, tresorerie_station)


@router.get("/solde_tresorerie/{tresorerie_id}",
            response_model=schemas.TresorerieSoldeResponse,
            summary="Récupérer le solde d'une trésorerie",
            description="Récupère les informations et le solde actuel d'une trésorerie spécifique par son identifiant. Le solde actuel est calculé à partir de l'ensemble des tresoreries station associées à cette trésorerie. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la trésorerie concernée.",
            tags=["Tresorerie"])
async def get_solde_tresorerie(
    tresorerie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_solde_tresorerie(db, current_user, tresorerie_id)


# CRUD pour TresorerieStation
@router.get("/tresorerie-station/{tresorerie_station_id}",
            response_model=schemas.TresorerieStationResponse,
            summary="Récupérer une association trésorerie-station",
            description="Récupère les détails d'une association trésorerie-station spécifique par son identifiant. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
            tags=["Tresorerie"])
async def get_tresorerie_station_by_id(
    tresorerie_station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresorerie_station_by_id(db, current_user, tresorerie_station_id)


@router.put("/tresorerie-station/{tresorerie_station_id}",
            response_model=schemas.TresorerieStationResponse,
            summary="Mettre à jour une association trésorerie-station",
            description="Met à jour les informations d'une association trésorerie-station existante. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
            tags=["Tresorerie"])
async def update_tresorerie_station(
    tresorerie_station_id: uuid.UUID,
    tresorerie_station: schemas.TresorerieStationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_update_tresorerie_station(db, current_user, tresorerie_station_id, tresorerie_station)


@router.delete("/tresorerie-station/{tresorerie_station_id}",
                summary="Supprimer une association trésorerie-station",
                description="Supprime une association trésorerie-station du système. Cette opération dissocie la trésorerie de la station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
                tags=["Tresorerie"])
async def delete_tresorerie_station(
    tresorerie_station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_delete_tresorerie_station(db, current_user, tresorerie_station_id)


@router.get("/{tresorerie_id}/mouvements",
            response_model=List[schemas.MouvementTresorerieResponse],
            summary="Récupérer tous les mouvements d'une trésorerie spécifique",
            description="Récupère la liste de tous les mouvements d'une trésorerie spécifique par son identifiant, avec pagination. Nécessite la permission 'Module Trésorerie'. L'utilisateur ne peut voir que les mouvements liés à sa compagnie.",
            tags=["Tresorerie"])
async def get_mouvements_by_tresorerie(
    tresorerie_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    # Cette fonction récupère TOUS les mouvements d'une trésorerie spécifique (par tresorerie_id)
    # contrairement à get_mouvement_tresorerie_by_id qui récupère UN seul mouvement par son ID
    return service_get_mouvements_tresorerie_by_id(db, current_user, tresorerie_id, skip, limit)


@router.get("/solde-station/{tresorerie_station_id}",
            response_model=float,
            summary="Récupérer le solde d'une trésorerie par station",
            description="Récupère le solde actuel d'une trésorerie pour une station spécifique. Le solde est calculé à partir des mouvements enregistrés. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la station concernée.",
            tags=["Tresorerie"])
async def get_solde_tresorerie_station(
    tresorerie_station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_solde_tresorerie_station(db, current_user, tresorerie_station_id)

