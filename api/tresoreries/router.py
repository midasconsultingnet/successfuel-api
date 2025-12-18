from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from . import schemas
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from ..services.tresoreries import (
    get_tresoreries_station as service_get_tresoreries_station,
    get_tresoreries_station_by_station as service_get_tresoreries_station_by_station,
    get_tresoreries as service_get_tresoreries,
    create_tresorerie as service_create_tresorerie,
    get_tresorerie_by_id as service_get_tresorerie_by_id,
    update_tresorerie as service_update_tresorerie,
    delete_tresorerie as service_delete_tresorerie,
    create_tresorerie_station as service_create_tresorerie_station,
    create_etat_initial_tresorerie as service_create_etat_initial_tresorerie,
    create_mouvement_tresorerie as service_create_mouvement_tresorerie,
    get_mouvements_tresorerie as service_get_mouvements_tresorerie,
    create_transfert_tresorerie as service_create_transfert_tresorerie,
    get_transferts_tresorerie as service_get_transferts_tresorerie,
    mettre_a_jour_solde_tresorerie as service_mettre_a_jour_solde_tresorerie
)

router = APIRouter(tags=["Tresorerie"])

# Tresorerie station endpoints
@router.get("/stations",
            response_model=List[schemas.StationTresorerieResponse],
            summary="Récupérer les trésoreries par station",
            description="Récupère la liste des trésoreries associées aux stations avec pagination. Permet de consulter toutes les trésoreries définies par station, y compris leurs soldes et configurations. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les stations concernées.",
            tags=["Tresorerie"])
async def get_tresoreries_station(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries_station(db, current_user, skip, limit)


@router.get("/stations/{station_id}/tresoreries",
            response_model=List[schemas.StationTresorerieResponse],
            summary="Récupérer les trésoreries d'une station spécifique",
            description="Récupère la liste des trésoreries associées à une station spécifique par son identifiant. Permet de consulter toutes les trésoreries définies pour une station particulière, y compris leurs soldes et configurations. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la station concernée.",
            tags=["Tresorerie"])
async def get_tresoreries_station_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_tresoreries_station_by_station(db, current_user, station_id)

# Tresorerie endpoints (globales) - Using root path to avoid double nesting
@router.get("/",
            response_model=List[schemas.TresorerieResponse],
            summary="Récupérer les trésoreries globales",
            description="Récupère la liste des trésoreries globales avec pagination. Ces trésoreries sont des comptes généraux qui ne sont pas spécifiquement liés à une station. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que les trésoreries concernées.",
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
             description="Crée une nouvelle trésorerie globale dans le système. Une trésorerie globale est un compte général qui ne dépend pas d'une station spécifique. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit appartenir à la même compagnie que la trésorerie à créer.",
             tags=["Tresorerie"])
async def create_tresorerie(
    tresorerie: schemas.TresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_tresorerie(db, current_user, tresorerie)

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

# Etat initial trésorerie endpoints
@router.post("/etats-initiaux",
             response_model=schemas.EtatInitialTresorerieResponse,
             summary="Créer un état initial pour une trésorerie",
             description="Crée un état initial pour une trésorerie, définissant son solde de départ. Cet état sert de base pour tous les calculs de trésorerie ultérieurs. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la trésorerie concernée via sa compagnie ou sa station.",
             tags=["Tresorerie"])
async def create_etat_initial_tresorerie(
    etat_initial: schemas.EtatInitialTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_etat_initial_tresorerie(db, current_user, etat_initial)

# Mouvements trésorerie endpoints
@router.post("/mouvements",
             response_model=schemas.MouvementTresorerieResponse,
             summary="Créer un nouveau mouvement de trésorerie",
             description="Enregistre un nouveau mouvement financier dans une trésorerie, comme un encaissement, un décaissement ou un transfert. Ce mouvement modifie le solde de la trésorerie concernée. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès à la trésorerie concernée via sa compagnie ou sa station.",
             tags=["Tresorerie"])
async def create_mouvement_tresorerie(
    mouvement: schemas.MouvementTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_mouvement_tresorerie(db, current_user, mouvement)

@router.get("/mouvements",
            response_model=List[schemas.MouvementTresorerieResponse],
            summary="Récupérer les mouvements de trésorerie",
            description="Récupère la liste des mouvements financiers effectués sur les trésoreries avec pagination. Permet de consulter l'historique des encaissements, décaissements et transferts. Nécessite la permission 'Module Trésorerie'. L'utilisateur ne peut voir que les mouvements liés à sa compagnie ou aux stations auxquelles il a accès.",
            tags=["Tresorerie"])
async def get_mouvements_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_mouvements_tresorerie(db, current_user, skip, limit)

# Transferts trésorerie endpoints
@router.post("/transferts",
             response_model=schemas.TransfertTresorerieResponse,
             summary="Créer un transfert entre trésoreries",
             description="Enregistre un transfert financier entre deux trésoreries. Ce transfert modifie les soldes des trésoreries concernées. Nécessite la permission 'Module Trésorerie'. L'utilisateur doit avoir accès aux trésoreries concernées via sa compagnie ou ses stations.",
             tags=["Tresorerie"])
async def create_transfert_tresorerie(
    transfert: schemas.TransfertTresorerieCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_create_transfert_tresorerie(db, current_user, transfert)

@router.get("/transferts",
            response_model=List[schemas.TransfertTresorerieResponse],
            summary="Récupérer les transferts entre trésoreries",
            description="Récupère la liste des transferts financiers effectués entre trésoreries avec pagination. Permet de consulter l'historique des transferts entre différentes trésoreries. Nécessite la permission 'Module Trésorerie'. L'utilisateur ne peut voir que les transferts liés à sa compagnie ou aux stations auxquelles il a accès.",
            tags=["Tresorerie"])
async def get_transferts_tresorerie(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("Module Trésorerie"))
):
    return service_get_transferts_tresorerie(db, current_user, skip, limit)
