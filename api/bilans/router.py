from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from . import schemas
from .initial_service import get_bilan_initial
from .initial_schemas import BilanInitialResponse, BilanInitialCreate, BilanInitialUpdate, BilanInitialDBResponse
from .journal_operations_service import get_journal_operations
from .journal_operations_schemas import JournalOperationsResponse
from .journal_comptable_service import get_journal_comptable
from .journal_comptable_schemas import JournalComptableResponse
from .consolidation_service import get_bilan_global
from ..auth.auth_handler import get_current_user_security
from ..models.compagnie import Station
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from datetime import datetime
from ..rbac_decorators import require_permission

router = APIRouter()
security = HTTPBearer()

@router.get("/operationnels", dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_operationnel(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would aggregate data from multiple modules:
    # - Ventes: total sales between the dates
    # - Achats: total purchases between the dates
    # - Calculate the net result
    
    # For now, return a placeholder response
    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "total_ventes": 1500000,
        "total_achats": 900000,
        "resultat": 600000,
        "message": "This endpoint would aggregate operational data from ventes, achats, and other modules"
    }

@router.get("/tresorerie", dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_tresorerie(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    station_id: str = None,
    type_tresorerie: str = None,
    tri: str = "date",  # "date", "nom", "solde"
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    # Import du service amélioré
    from .tresorerie_service import get_bilan_tresorerie_etendu

    # Appeler le service amélioré
    result = get_bilan_tresorerie_etendu(
        db,
        current_user,
        date_debut,
        date_fin,
        station_id,
        type_tresorerie,
        tri
    )

    return result

@router.get("/stocks", dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_stocks(
    date: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would aggregate stock data from produits/stocks modules
    
    # For now, return a placeholder response
    return {
        "date": date,
        "details": {
            "carburant": {"essence": 10000, "diesel": 8000},
            "boutique": {"total_value": 500000},
            "gaz": {"total_value": 200000}
        },
        "message": "This endpoint would aggregate stock data from produits and stocks modules"
    }

@router.get("/tiers", dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_tiers(
    date: str,  # Format: YYYY-MM-DD
    type_tiers: str = None,  # client, fournisseur, employe
    tri: str = "nom",  # "nom", "solde", "date"
    station_id: str = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    # Import du service amélioré
    from .tiers_service import get_bilan_tiers_etendu

    # Appeler le service amélioré
    result = get_bilan_tiers_etendu(
        db,
        current_user,
        date,
        type_tiers,
        tri,
        station_id
    )

    return result

@router.get("/export", dependencies=[Depends(require_permission("bilans"))])
async def export_bilans(
    format: str = "csv",  # csv, json
    type_bilan: str = None,  # tresorerie, tiers, operations, etc.
    date_debut: str = None,  # Format: YYYY-MM-DD
    date_fin: str = None,    # Format: YYYY-MM-DD
    station_id: str = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None  # Pour accéder à l'IP et user agent
):
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    # Import des services d'export et d'audit
    from .export_service import export_bilan_tresorerie, export_bilan_tiers, export_bilan_operations
    from .audit_service import log_export_action

    # Récupérer les informations sur le client pour l'audit
    ip_utilisateur = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    # Récupérer le type de bilan à exporter
    if type_bilan == "tresorerie":
        # Récupérer les données de bilan de trésorerie
        from .tresorerie_service import get_bilan_tresorerie_etendu
        data = get_bilan_tresorerie_etendu(
            db,
            current_user,
            date_debut or datetime.now().strftime("%Y-%m-%d"),
            date_fin or datetime.now().strftime("%Y-%m-%d"),
            station_id,
            None,
            "date"
        )

        # Enregistrer l'action d'export dans l'audit
        log_export_action(
            db,
            str(current_user.id),
            "tresorerie",
            format,
            fichier_genere=f"export_tresorerie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
            ip_utilisateur=ip_utilisateur,
            user_agent=user_agent,
            details=f"Export du bilan de trésorerie pour la période {date_debut or 'date non spécifiée'} à {date_fin or 'date non spécifiée'}"
        )

        return export_bilan_tresorerie(data, format)

    elif type_bilan == "tiers":
        # Récupérer les données de bilan des tiers
        from .tiers_service import get_bilan_tiers_etendu
        data = get_bilan_tiers_etendu(
            db,
            current_user,
            date_debut or datetime.now().strftime("%Y-%m-%d"),
            None,
            "nom",
            station_id
        )

        # Enregistrer l'action d'export dans l'audit
        log_export_action(
            db,
            str(current_user.id),
            "tiers",
            format,
            fichier_genere=f"export_tiers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
            ip_utilisateur=ip_utilisateur,
            user_agent=user_agent,
            details=f"Export du bilan des tiers pour la date {date_debut or 'date non spécifiée'}"
        )

        return export_bilan_tiers(data, format)

    elif type_bilan == "operations":
        # Récupérer les données de bilan des opérations
        from .journal_operations_service import get_journal_operations
        data = get_journal_operations(
            db,
            date_debut or datetime.now().strftime("%Y-%m-%d"),
            date_fin or datetime.now().strftime("%Y-%m-%d"),
            station_id,
            None
        )

        # Enregistrer l'action d'export dans l'audit
        log_export_action(
            db,
            str(current_user.id),
            "operations",
            format,
            fichier_genere=f"export_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
            ip_utilisateur=ip_utilisateur,
            user_agent=user_agent,
            details=f"Export du journal des opérations pour la période {date_debut or 'date non spécifiée'} à {date_fin or 'date non spécifiée'}"
        )

        return export_bilan_operations(data, format)

    else:
        # Pour les autres types de bilans, on retourne une erreur
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Type de bilan non supporté pour l'export: {type_bilan}")


def check_station_access(db: Session, current_user, station_id: str) -> Station:
    """
    Vérifie que l'utilisateur a accès à la station spécifiée
    """
    try:
        station_uuid = UUID(station_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de station invalide")

    station = db.query(Station).filter(
        Station.id == station_uuid,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou non autorisée")

    return station


@router.get("/initial/{station_id}", response_model=BilanInitialResponse, dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_initial_depart(
    station_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour générer le bilan initial de départ d'une station
    """
    current_user = get_current_user_security(credentials, db)

    # Vérifier que l'utilisateur a accès à cette station
    station = check_station_access(db, current_user, station_id)

    # Générer le bilan initial
    bilan_initial = get_bilan_initial(db, station_id)
    return bilan_initial


@router.get("/journal_operations", response_model=JournalOperationsResponse, dependencies=[Depends(require_permission("bilans"))])
async def get_journal_operations_endpoint(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    station_id: str = None,
    type_operation: str = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour générer le journal des opérations entre deux dates
    """
    current_user = get_current_user_security(credentials, db)

    # Si une station est spécifiée, vérifier que l'utilisateur y a accès
    if station_id:
        station = check_station_access(db, current_user, station_id)

    # Générer le journal des opérations
    journal_operations = get_journal_operations(db, date_debut, date_fin, station_id, type_operation)
    return journal_operations


@router.get("/journal_comptable", response_model=JournalComptableResponse, dependencies=[Depends(require_permission("bilans"))])
async def get_journal_comptable_endpoint(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour générer le journal comptable entre deux dates
    """
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    # Générer le journal comptable
    journal_comptable = get_journal_comptable(db, date_debut, date_fin)
    return journal_comptable


@router.get("/consolide", dependencies=[Depends(require_permission("bilans"))])
async def get_bilan_consolidé(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    station_id: str = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint pour générer le bilan consolidé global
    """
    current_user = get_current_user_security(credentials, db)

    # Si une station est spécifiée, vérifier que l'utilisateur y a accès
    if station_id:
        station = check_station_access(db, current_user, station_id)

    # Générer le bilan consolidé
    bilan_consolidé = get_bilan_global(db, current_user, date_debut, date_fin, station_id)
    return bilan_consolidé




@router.get("/initial_enregistre/{station_id}", response_model=BilanInitialDBResponse, dependencies=[Depends(require_permission("bilans"))])
async def lire_bilan_initial_depart(
    station_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Lire le bilan initial de départ enregistré dans la base de données pour une station
    """
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    try:
        station_uuid = UUID(station_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de station invalide")

    # Vérifier que l'utilisateur a accès à cette station
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == station_uuid,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou non autorisée")

    # Appeler le service pour lire le bilan initial
    from .initial_service import get_bilan_initial_depart_by_station
    bilan_initial = get_bilan_initial_depart_by_station(db, station_uuid)

    if not bilan_initial:
        raise HTTPException(status_code=404, detail="Bilan initial non trouvé pour cette station")

    return bilan_initial


@router.put("/initial/{station_id}", response_model=BilanInitialDBResponse, dependencies=[Depends(require_permission("bilans"))])
async def mettre_a_jour_bilan_initial_depart(
    station_id: str,
    bilan_data: BilanInitialUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour le bilan initial de départ pour une station
    """
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    try:
        station_uuid = UUID(station_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de station invalide")

    # Appeler le service pour mettre à jour le bilan initial
    from .initial_service import update_bilan_initial_depart
    bilan_initial = update_bilan_initial_depart(
        db,
        station_uuid,
        bilan_data,
        current_user
    )

    return bilan_initial


@router.post("/initial/{station_id}/validation", response_model=BilanInitialDBResponse, dependencies=[Depends(require_permission("bilans"))])
async def valider_bilan_initial_depart(
    station_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Enregistrer et valider le bilan initial de départ pour une station selon les calculs automatiques
    """
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    try:
        station_uuid = UUID(station_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de station invalide")

    # Vérifier que l'utilisateur a accès à cette station
    from ..models.compagnie import Station
    station = db.query(Station).filter(
        Station.id == station_uuid,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée ou non autorisée")

    # Générer les données du bilan initial à partir des calculs automatiques
    from .initial_service import get_bilan_initial
    bilan_initial_data = get_bilan_initial(db, station_id)

    # Créer un objet BilanInitialCreate à partir des données calculées
    from .initial_schemas import BilanInitialCreate
    bilan_data = BilanInitialCreate(
        compagnie_id=station.compagnie_id,
        station_id=station_uuid,
        date_bilan=bilan_initial_data.date_bilan.date() if isinstance(bilan_initial_data.date_bilan, datetime) else bilan_initial_data.date_bilan,
        actif_immobilise=bilan_initial_data.actif_immobilise,
        actif_circulant=bilan_initial_data.actif_circulant,
        capitaux_propres=bilan_initial_data.capitaux_propres,
        dettes=bilan_initial_data.dettes,
        provisions=bilan_initial_data.provisions
    )

    # Enregistrer directement le bilan initial avec est_valide = True
    from .initial_service import create_bilan_initial_depart
    bilan_initial = create_bilan_initial_depart(
        db,
        bilan_data,
        current_user.id,
        est_deja_valide=True
    )

    return bilan_initial
