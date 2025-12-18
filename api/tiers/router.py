from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..models import User
from . import schemas, soldes_schemas, journal_schemas
from ..models.tiers import Tiers, SoldeTiers, JournalModificationTiers
from ..models.compagnie import Station
from ..rbac_decorators import require_permission

security = HTTPBearer()


# Dépendance pour obtenir l'utilisateur courant
async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)
    # Vérifier que l'utilisateur est authentifié
    if current_user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return current_user

router = APIRouter(tags=["Tiers"])


@router.post("/clients",
             response_model=schemas.TiersResponse,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Créer un nouveau client",
             description="Crée un nouveau client appartenant à la même compagnie que l'utilisateur connecté. Cet endpoint permet de créer un client avec ses informations de contact, son statut et les stations auxquelles il est associé.",
             tags=["Tiers"])
async def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Crée un nouveau client pour la compagnie de l'utilisateur connecté.

    Args:
        client (schemas.ClientCreate): Les données du client à créer, y compris nom, email, téléphone, adresse,
                                       statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et associer le client à la bonne compagnie.

    Returns:
        schemas.TiersResponse: Le client créé avec toutes ses informations.

    Raises:
        HTTPException: Si une station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station spécifiée appartient à la même compagnie
    if client.station_ids:
        for station_id in client.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Créer le client avec le compagnie_id de l'utilisateur connecté et le type 'client'
    db_client = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="client",
        nom=client.nom,
        email=client.email,
        telephone=client.telephone,
        adresse=client.adresse,
        statut=client.statut,
        donnees_personnelles=client.donnees_personnelles,
        station_ids=client.station_ids,
        metadonnees=client.metadonnees
    )

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


@router.post("/fournisseurs",
             response_model=schemas.TiersResponse,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Créer un nouveau fournisseur",
             description="Crée un nouveau fournisseur appartenant à la même compagnie que l'utilisateur connecté. Cet endpoint permet de créer un fournisseur avec ses informations de contact, son statut et les stations auxquelles il est associé.",
             tags=["Tiers"])
async def create_fournisseur(
    fournisseur: schemas.FournisseurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Crée un nouveau fournisseur pour la compagnie de l'utilisateur connecté.

    Args:
        fournisseur (schemas.FournisseurCreate): Les données du fournisseur à créer, y compris nom, email, téléphone, adresse,
                                       statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et associer le fournisseur à la bonne compagnie.

    Returns:
        schemas.TiersResponse: Le fournisseur créé avec toutes ses informations.

    Raises:
        HTTPException: Si une station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station spécifiée appartient à la même compagnie
    if fournisseur.station_ids:
        for station_id in fournisseur.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Créer le fournisseur avec le compagnie_id de l'utilisateur connecté et le type 'fournisseur'
    db_fournisseur = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="fournisseur",
        nom=fournisseur.nom,
        email=fournisseur.email,
        telephone=fournisseur.telephone,
        adresse=fournisseur.adresse,
        statut=fournisseur.statut,
        donnees_personnelles=fournisseur.donnees_personnelles,
        station_ids=fournisseur.station_ids,
        metadonnees=fournisseur.metadonnees
    )

    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)

    return db_fournisseur


@router.post("/employes",
             response_model=schemas.TiersResponse,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Créer un nouvel employé",
             description="Crée un nouvel employé appartenant à la même compagnie que l'utilisateur connecté. Cet endpoint permet de créer un employé avec ses informations de contact, son statut et les stations auxquelles il est associé.",
             tags=["Tiers"])
async def create_employe(
    employe: schemas.EmployeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Crée un nouvel employé pour la compagnie de l'utilisateur connecté.

    Args:
        employe (schemas.EmployeCreate): Les données de l'employé à créer, y compris nom, prénom, email, téléphone, adresse,
                                       statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et associer l'employé à la bonne compagnie.

    Returns:
        schemas.TiersResponse: L'employé créé avec toutes ses informations.

    Raises:
        HTTPException: Si une station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station spécifiée appartient à la même compagnie
    if employe.station_ids:
        for station_id in employe.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Créer l'employé avec le compagnie_id de l'utilisateur connecté et le type 'employé'
    db_employe = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="employé",
        nom=employe.nom,
        email=employe.email,
        telephone=employe.telephone,
        adresse=employe.adresse,
        statut=employe.statut,
        donnees_personnelles=employe.donnees_personnelles,
        station_ids=employe.station_ids,
        metadonnees=employe.metadonnees
    )

    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)

    return db_employe


@router.get("/stations/{station_id}/clients",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les clients associés à une station spécifique",
            description="Récupère tous les clients associés à une station spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les clients actifs sont retournés.",
            tags=["Tiers"])
async def get_clients_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les clients associés à une station spécifique.

    Args:
        station_id (uuid.UUID): L'identifiant de la station pour laquelle récupérer les clients.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que la station appartient à la même compagnie.

    Returns:
        List[schemas.TiersResponse]: Une liste de clients associés à la station spécifiée.

    Raises:
        HTTPException: Si la station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les clients associés à cette station
    clients = db.query(Tiers).filter(
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return clients


@router.get("/clients/{client_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer un client spécifique",
            description="Récupère un client spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les clients actifs sont retournés.",
            tags=["Tiers"])
async def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupère un client spécifique.

    Args:
        client_id (uuid.UUID): L'identifiant du client à récupérer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le client appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: Les informations du client demandé.

    Raises:
        HTTPException: Si le client spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé").
    """
    client = db.query(Tiers).filter(
        Tiers.id == client_id,
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.get("/fournisseurs/{fournisseur_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer un fournisseur spécifique",
            description="Récupère un fournisseur spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les fournisseurs actifs sont retournés.",
            tags=["Tiers"])
async def get_fournisseur(
    fournisseur_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupère un fournisseur spécifique.

    Args:
        fournisseur_id (uuid.UUID): L'identifiant du fournisseur à récupérer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le fournisseur appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: Les informations du fournisseur demandé.

    Raises:
        HTTPException: Si le fournisseur spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé").
    """
    fournisseur = db.query(Tiers).filter(
        Tiers.id == fournisseur_id,
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    return fournisseur


@router.get("/clients",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les clients de la compagnie",
            description="Récupère tous les clients appartenant à la même compagnie que l'utilisateur connecté. Seuls les clients actifs sont retournés.",
            tags=["Tiers"])
async def get_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les clients de la compagnie de l'utilisateur connecté.

    Args:
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que seuls les clients de la même compagnie sont retournés.

    Returns:
        List[schemas.TiersResponse]: Une liste de tous les clients de la compagnie.

    Raises:
        HTTPException: Aucune exception spécifique levée par cette fonction, mais des vérifications de permissions
                       sont effectuées via le décorateur require_permission.
    """
    clients = db.query(Tiers).filter(
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return clients


@router.get("/fournisseurs",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les fournisseurs de la compagnie",
            description="Récupère tous les fournisseurs appartenant à la même compagnie que l'utilisateur connecté. Seuls les fournisseurs actifs sont retournés.",
            tags=["Tiers"])
async def get_all_fournisseurs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les fournisseurs de la compagnie de l'utilisateur connecté.

    Args:
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que seuls les fournisseurs de la même compagnie sont retournés.

    Returns:
        List[schemas.TiersResponse]: Une liste de tous les fournisseurs de la compagnie.

    Raises:
        HTTPException: Aucune exception spécifique levée par cette fonction, mais des vérifications de permissions
                       sont effectuées via le décorateur require_permission.
    """
    fournisseurs = db.query(Tiers).filter(
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return fournisseurs


@router.get("/employes",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les employés de la compagnie",
            description="Récupère tous les employés appartenant à la même compagnie que l'utilisateur connecté. Seuls les employés actifs sont retournés.",
            tags=["Tiers"])
async def get_all_employes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les employés de la compagnie de l'utilisateur connecté.

    Args:
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que seuls les employés de la même compagnie sont retournés.

    Returns:
        List[schemas.TiersResponse]: Une liste de tous les employés de la compagnie.

    Raises:
        HTTPException: Aucune exception spécifique levée par cette fonction, mais des vérifications de permissions
                       sont effectuées via le décorateur require_permission.
    """
    employes = db.query(Tiers).filter(
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return employes


@router.get("/employes/{employe_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer un employé spécifique",
            description="Récupère un employé spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les employés actifs sont retournés.",
            tags=["Tiers"])
async def get_employe(
    employe_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupère un employé spécifique.

    Args:
        employe_id (uuid.UUID): L'identifiant de l'employé à récupérer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que l'employé appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: Les informations de l'employé demandé.

    Raises:
        HTTPException: Si l'employé spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé").
    """
    employe = db.query(Tiers).filter(
        Tiers.id == employe_id,
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not employe:
        raise HTTPException(status_code=404, detail="Employé not found")

    return employe


@router.get("/stations/{station_id}/fournisseurs",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les fournisseurs associés à une station spécifique",
            description="Récupère tous les fournisseurs associés à une station spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les fournisseurs actifs sont retournés.",
            tags=["Tiers"])
async def get_fournisseurs_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les fournisseurs associés à une station spécifique.

    Args:
        station_id (uuid.UUID): L'identifiant de la station pour laquelle récupérer les fournisseurs.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que la station appartient à la même compagnie.

    Returns:
        List[schemas.TiersResponse]: Une liste de fournisseurs associés à la station spécifiée.

    Raises:
        HTTPException: Si la station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les fournisseurs associés à cette station
    fournisseurs = db.query(Tiers).filter(
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return fournisseurs


@router.put("/clients/{client_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Mettre à jour un client spécifique",
            description="Met à jour un client existant appartenant à la même compagnie que l'utilisateur connecté. Seuls les champs spécifiés dans la requête sont mis à jour.",
            tags=["Tiers"])
async def update_client(
    client_id: uuid.UUID,
    client_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Met à jour un client spécifique.

    Args:
        client_id (uuid.UUID): L'identifiant du client à mettre à jour.
        client_update (schemas.TiersUpdate): Les données mises à jour du client, y compris nom, email, téléphone, adresse,
                                            statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le client appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: Le client mis à jour avec toutes ses informations.

    Raises:
        HTTPException: Si le client spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé"), ou si une station spécifiée n'est pas trouvée
                       ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Récupérer le client existant
    db_client = db.query(Tiers).filter(
        Tiers.id == client_id,
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Vérifier si des stations sont spécifiées dans la mise à jour
    if client_update.station_ids:
        for station_id in client_update.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Mettre à jour les champs modifiables
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)

    db.commit()
    db.refresh(db_client)

    return db_client


@router.put("/fournisseurs/{fournisseur_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Mettre à jour un fournisseur spécifique",
            description="Met à jour un fournisseur existant appartenant à la même compagnie que l'utilisateur connecté. Seuls les champs spécifiés dans la requête sont mis à jour.",
            tags=["Tiers"])
async def update_fournisseur(
    fournisseur_id: uuid.UUID,
    fournisseur_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Met à jour un fournisseur spécifique.

    Args:
        fournisseur_id (uuid.UUID): L'identifiant du fournisseur à mettre à jour.
        fournisseur_update (schemas.TiersUpdate): Les données mises à jour du fournisseur, y compris nom, email, téléphone, adresse,
                                                 statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le fournisseur appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: Le fournisseur mis à jour avec toutes ses informations.

    Raises:
        HTTPException: Si le fournisseur spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé"), ou si une station spécifiée n'est pas trouvée
                       ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Récupérer le fournisseur existant
    db_fournisseur = db.query(Tiers).filter(
        Tiers.id == fournisseur_id,
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    # Vérifier si des stations sont spécifiées dans la mise à jour
    if fournisseur_update.station_ids:
        for station_id in fournisseur_update.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Mettre à jour les champs modifiables
    update_data = fournisseur_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fournisseur, field, value)

    db.commit()
    db.refresh(db_fournisseur)

    return db_fournisseur


@router.put("/employes/{employe_id}",
            response_model=schemas.TiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Mettre à jour un employé spécifique",
            description="Met à jour un employé existant appartenant à la même compagnie que l'utilisateur connecté. Seuls les champs spécifiés dans la requête sont mis à jour.",
            tags=["Tiers"])
async def update_employe(
    employe_id: uuid.UUID,
    employe_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Met à jour un employé spécifique.

    Args:
        employe_id (uuid.UUID): L'identifiant de l'employé à mettre à jour.
        employe_update (schemas.TiersUpdate): Les données mises à jour de l'employé, y compris nom, email, téléphone, adresse,
                                            statut, données personnelles, stations associées et métadonnées.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que l'employé appartient à la même compagnie.

    Returns:
        schemas.TiersResponse: L'employé mis à jour avec toutes ses informations.

    Raises:
        HTTPException: Si l'employé spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a été supprimé (statut "supprimé"), ou si une station spécifiée n'est pas trouvée
                       ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Récupérer l'employé existant
    db_employe = db.query(Tiers).filter(
        Tiers.id == employe_id,
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_employe:
        raise HTTPException(status_code=404, detail="Employé not found")

    # Vérifier si des stations sont spécifiées dans la mise à jour
    if employe_update.station_ids:
        for station_id in employe_update.station_ids:
            station = db.query(Station).filter(
                Station.id == station_id,
                Station.compagnie_id == current_user.compagnie_id
            ).first()
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} non trouvée ou non autorisée")

    # Mettre à jour les champs modifiables
    update_data = employe_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employe, field, value)

    db.commit()
    db.refresh(db_employe)

    return db_employe


@router.delete("/clients/{client_id}",
               response_model=dict,
               dependencies=[Depends(require_permission("Module Tiers"))],
               summary="Supprimer un client spécifique (suppression logique)",
               description="Supprime un client spécifique appartenant à la même compagnie que l'utilisateur connecté. La suppression est logique : le statut du client est mis à jour à 'supprimé' au lieu d'être physiquement supprimé de la base de données.",
               tags=["Tiers"])
async def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprime un client spécifique (suppression logique).

    Args:
        client_id (uuid.UUID): L'identifiant du client à supprimer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le client appartient à la même compagnie.

    Returns:
        dict: Un message indiquant que le client a été supprimé avec succès.

    Raises:
        HTTPException: Si le client spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a déjà été supprimé (statut "supprimé").
    """
    # Récupérer le client existant
    db_client = db.query(Tiers).filter(
        Tiers.id == client_id,
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Ne pas permettre de supprimer un tiers déjà supprimé
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Mise à jour du statut à "supprimé" (suppression logique)
    db_client.statut = "supprimé"
    db.commit()

    return {"message": f"Client {client_id} supprimé avec succès"}


@router.delete("/fournisseurs/{fournisseur_id}",
               response_model=dict,
               dependencies=[Depends(require_permission("Module Tiers"))],
               summary="Supprimer un fournisseur spécifique (suppression logique)",
               description="Supprime un fournisseur spécifique appartenant à la même compagnie que l'utilisateur connecté. La suppression est logique : le statut du fournisseur est mis à jour à 'supprimé' au lieu d'être physiquement supprimé de la base de données.",
               tags=["Tiers"])
async def delete_fournisseur(
    fournisseur_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprime un fournisseur spécifique (suppression logique).

    Args:
        fournisseur_id (uuid.UUID): L'identifiant du fournisseur à supprimer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le fournisseur appartient à la même compagnie.

    Returns:
        dict: Un message indiquant que le fournisseur a été supprimé avec succès.

    Raises:
        HTTPException: Si le fournisseur spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a déjà été supprimé (statut "supprimé").
    """
    # Récupérer le fournisseur existant
    db_fournisseur = db.query(Tiers).filter(
        Tiers.id == fournisseur_id,
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Ne pas permettre de supprimer un tiers déjà supprimé
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    # Mise à jour du statut à "supprimé" (suppression logique)
    db_fournisseur.statut = "supprimé"
    db.commit()

    return {"message": f"Fournisseur {fournisseur_id} supprimé avec succès"}


@router.delete("/employes/{employe_id}",
               response_model=dict,
               dependencies=[Depends(require_permission("Module Tiers"))],
               summary="Supprimer un employé spécifique (suppression logique)",
               description="Supprime un employé spécifique appartenant à la même compagnie que l'utilisateur connecté. La suppression est logique : le statut de l'employé est mis à jour à 'supprimé' au lieu d'être physiquement supprimé de la base de données.",
               tags=["Tiers"])
async def delete_employe(
    employe_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprime un employé spécifique (suppression logique).

    Args:
        employe_id (uuid.UUID): L'identifiant de l'employé à supprimer.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que l'employé appartient à la même compagnie.

    Returns:
        dict: Un message indiquant que l'employé a été supprimé avec succès.

    Raises:
        HTTPException: Si l'employé spécifié n'est pas trouvé, n'appartient pas à la compagnie de l'utilisateur,
                       ou a déjà été supprimé (statut "supprimé").
    """
    # Récupérer l'employé existant
    db_employe = db.query(Tiers).filter(
        Tiers.id == employe_id,
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Ne pas permettre de supprimer un tiers déjà supprimé
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_employe:
        raise HTTPException(status_code=404, detail="Employé not found")

    # Mise à jour du statut à "supprimé" (suppression logique)
    db_employe.statut = "supprimé"
    db.commit()

    return {"message": f"Employé {employe_id} supprimé avec succès"}


@router.post("/tiers/{tiers_id}/associer-station/{station_id}",
             response_model=dict,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Associer un tiers à une station",
             description="Associe un tiers (client, fournisseur ou employé) à une station spécifique appartenant à la même compagnie que l'utilisateur connecté.",
             tags=["Tiers"])
async def associer_tiers_a_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Associe un tiers à une station spécifique.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers à associer à la station.
        station_id (uuid.UUID): L'identifiant de la station à laquelle associer le tiers.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers et la station appartiennent à la même compagnie.

    Returns:
        dict: Un message indiquant que le tiers a été associé à la station avec succès.

    Raises:
        HTTPException: Si la station ou le tiers spécifié n'est pas trouvé, n'appartient pas à la
                       compagnie de l'utilisateur, ou si le type de tiers est invalide.
    """
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found or not authorized")

    # Vérifier que le tiers existe et appartient à la même compagnie
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.statut != "supprimé"
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found or not authorized")

    # Vérifier que le type de tiers est correct
    if tiers.type not in ["client", "fournisseur", "employé"]:
        raise HTTPException(status_code=400, detail="Type de tiers invalide")

    # Utiliser la fonction utilitaire pour associer le tiers à la station
    from .utils import associer_tiers_a_station as associer_util
    success = associer_util(db, tiers_id, station_id)

    if not success:
        raise HTTPException(status_code=400, detail="Échec de l'association du tiers à la station")

    return {"message": f"Tiers {tiers_id} associé à la station {station_id} avec succès"}


@router.post("/tiers/{tiers_id}/dissocier-station/{station_id}",
             response_model=dict,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Dissocier un tiers d'une station",
             description="Dissocie un tiers (client, fournisseur ou employé) d'une station spécifique appartenant à la même compagnie que l'utilisateur connecté.",
             tags=["Tiers"])
async def dissocier_tiers_de_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Dissocie un tiers d'une station spécifique.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers à dissocier de la station.
        station_id (uuid.UUID): L'identifiant de la station de laquelle dissocier le tiers.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers et la station appartiennent à la même compagnie.

    Returns:
        dict: Un message indiquant que le tiers a été dissocié de la station avec succès.

    Raises:
        HTTPException: Si la station ou le tiers spécifié n'est pas trouvé, n'appartient pas à la
                       compagnie de l'utilisateur, ou si le type de tiers est invalide.
    """
    # Vérifier que la station appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found or not authorized")

    # Vérifier que le tiers existe et appartient à la même compagnie
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.statut != "supprimé"
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found or not authorized")

    # Vérifier que le type de tiers est correct
    if tiers.type not in ["client", "fournisseur", "employé"]:
        raise HTTPException(status_code=400, detail="Type de tiers invalide")

    # Utiliser la fonction utilitaire pour dissocier le tiers de la station
    from .utils import dissociate_tiers_de_station as dissocier_util
    success = dissocier_util(db, tiers_id, station_id)

    if not success:
        raise HTTPException(status_code=400, detail="Échec de la dissociation du tiers de la station")

    return {"message": f"Tiers {tiers_id} dissocié de la station {station_id} avec succès"}


@router.get("/stations/{station_id}/employes",
            response_model=List[schemas.TiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les employés associés à une station spécifique",
            description="Récupère tous les employés associés à une station spécifique appartenant à la même compagnie que l'utilisateur connecté. Seuls les employés actifs sont retournés.",
            tags=["Tiers"])
async def get_employes_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupère tous les employés associés à une station spécifique.

    Args:
        station_id (uuid.UUID): L'identifiant de la station pour laquelle récupérer les employés.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que la station appartient à la même compagnie.

    Returns:
        List[schemas.TiersResponse]: Une liste d'employés associés à la station spécifiée.

    Raises:
        HTTPException: Si la station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station appartient à la compagnie de l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer les employés associés à cette station
    employes = db.query(Tiers).filter(
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id,
        Tiers.station_ids.op('?')(str(station_id))  # Vérifie si station_id est dans station_ids
    ).all()

    return employes


@router.post("/tiers/{tiers_id}/soldes/{station_id}",
             response_model=soldes_schemas.SoldeTiersResponse,
             dependencies=[Depends(require_permission("Module Tiers"))],
             summary="Initialiser le solde d'un tiers pour une station spécifique",
             description="Initialise le solde d'un tiers (client, fournisseur ou employé) pour une station spécifique. Le solde initial est également utilisé comme solde actuel au moment de la création.",
             tags=["Tiers"])
async def create_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    solde_create: soldes_schemas.SoldeTiersCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Initialise le solde d'un tiers (client, fournisseur ou employé) pour une station spécifique.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers pour lequel initialiser le solde.
        station_id (uuid.UUID): L'identifiant de la station pour laquelle initialiser le solde.
        solde_create (soldes_schemas.SoldeTiersCreate): Les informations nécessaires pour créer le solde initial,
                                                       y compris le montant initial, le type de solde initial (dette ou créance) et la devise.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers et la station appartiennent à la même compagnie.

    Returns:
        soldes_schemas.SoldeTiersResponse: Le solde initial créé avec toutes ses informations.

    Raises:
        HTTPException: Si le tiers ou la station spécifié n'est pas trouvé, n'appartient pas à la
                       compagnie de l'utilisateur, ou si un solde existe déjà pour ce tiers et cette station.
    """
    # Vérifier que le tiers existe et appartient à la même compagnie que l'utilisateur
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")

    # Vérifier que la station existe et appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Vérifier s'il existe déjà un solde initial pour ce tiers et cette station
    existing_solde = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id,
        SoldeTiers.station_id == station_id
    ).first()

    if existing_solde:
        raise HTTPException(
            status_code=400,
            detail="Le solde initial pour ce tiers et cette station existe déjà. Utilisez PUT pour le mettre à jour."
        )

    from datetime import datetime

    # Créer le solde initial
    db_solde_initial = SoldeTiers(
        tiers_id=tiers_id,
        station_id=station_id,
        montant_initial=solde_create.montant_initial,
        montant_actuel=solde_create.montant_initial,  # Initialement, le solde actuel est identique au solde initial
        devise=solde_create.devise,
        date_derniere_mise_a_jour=datetime.utcnow()  # Ajouter la date de création
    )

    db.add(db_solde_initial)
    db.commit()
    db.refresh(db_solde_initial)

    return db_solde_initial


@router.get("/tiers/{tiers_id}/soldes/{station_id}",
            response_model=soldes_schemas.SoldeTiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer le solde initial d'un tiers pour une station spécifique",
            description="Récupère le solde initial d'un tiers (client, fournisseur ou employé) pour une station spécifique appartenant à la même compagnie que l'utilisateur connecté.",
            tags=["Tiers"])
async def get_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Récupère le solde initial d'un tiers pour une station spécifique.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers pour lequel récupérer le solde.
        station_id (uuid.UUID): L'identifiant de la station pour laquelle récupérer le solde.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers et la station appartiennent à la même compagnie.

    Returns:
        soldes_schemas.SoldeTiersResponse: Le solde initial du tiers pour la station spécifiée.

    Raises:
        HTTPException: Si le tiers ou la station spécifié n'est pas trouvé, n'appartient pas à la
                       compagnie de l'utilisateur, ou si aucun solde n'existe pour ce tiers et cette station.
    """
    # Vérifier que le tiers existe et appartient à la même compagnie que l'utilisateur
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")

    # Vérifier que la station existe et appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer le solde initial du tiers pour cette station
    solde_initial = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id,
        SoldeTiers.station_id == station_id
    ).first()

    if not solde_initial:
        raise HTTPException(status_code=404, detail="Le solde initial pour ce tiers et cette station n'existe pas")

    return solde_initial


@router.put("/tiers/{tiers_id}/soldes/{station_id}",
            response_model=soldes_schemas.SoldeTiersResponse,
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Mettre à jour le solde initial d'un tiers pour une station spécifique",
            description="Met à jour le solde initial d'un tiers (client, fournisseur ou employé) pour une station spécifique appartenant à la même compagnie que l'utilisateur connecté.",
            tags=["Tiers"])
async def update_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    solde_update: soldes_schemas.SoldeTiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Met à jour le solde initial d'un tiers pour une station spécifique.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers pour lequel mettre à jour le solde.
        station_id (uuid.UUID): L'identifiant de la station pour laquelle mettre à jour le solde.
        solde_update (soldes_schemas.SoldeTiersUpdate): Les informations de mise à jour du solde,
                                                       y compris le montant initial et le montant actuel.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers et la station appartiennent à la même compagnie.

    Returns:
        soldes_schemas.SoldeTiersResponse: Le solde mis à jour du tiers pour la station spécifiée.

    Raises:
        HTTPException: Si le tiers ou la station spécifié n'est pas trouvé, n'appartient pas à la
                       compagnie de l'utilisateur, ou si aucun solde n'existe pour ce tiers et cette station.
    """
    # Vérifier que le tiers existe et appartient à la même compagnie que l'utilisateur
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")

    # Vérifier que la station existe et appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer le solde initial du tiers pour cette station
    solde_initial = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id,
        SoldeTiers.station_id == station_id
    ).first()

    if not solde_initial:
        raise HTTPException(status_code=404, detail="Le solde initial pour ce tiers et cette station n'existe pas")

    from datetime import datetime

    # Mettre à jour les champs modifiables
    update_data = solde_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(solde_initial, field, value)

    # Mettre à jour la date de la dernière modification
    solde_initial.date_derniere_mise_a_jour = datetime.utcnow()

    db.commit()
    db.refresh(solde_initial)

    return solde_initial


@router.get("/tiers/{tiers_id}/soldes",
            response_model=List[soldes_schemas.SoldeTiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les soldes d'un tiers par station",
            description="Récupère tous les soldes d'un tiers (client, fournisseur ou employé) par station appartenant à la même compagnie que l'utilisateur connecté.",
            tags=["Tiers"])
async def get_soldes_tiers_par_station(
    tiers_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[soldes_schemas.SoldeTiersResponse]:
    """
    Récupère tous les soldes d'un tiers par station.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers pour lequel récupérer les soldes.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers appartient à la même compagnie.

    Returns:
        List[soldes_schemas.SoldeTiersResponse]: Une liste des soldes du tiers pour toutes les stations.

    Raises:
        HTTPException: Si le tiers spécifié n'est pas trouvé ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que le tiers existe et appartient à la même compagnie que l'utilisateur
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")

    # Récupérer tous les soldes du tiers
    soldes = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id
    ).all()

    return soldes


@router.get("/stations/{station_id}/soldes",
            response_model=List[soldes_schemas.SoldeTiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer tous les soldes pour une station spécifique",
            description="Récupère tous les soldes pour une station spécifique appartenant à la même compagnie que l'utilisateur connecté. Inclut les soldes de tous les tiers (clients, fournisseurs, employés) associés à cette station.",
            tags=["Tiers"])
async def get_soldes_par_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[soldes_schemas.SoldeTiersResponse]:
    """
    Récupère tous les soldes pour une station spécifique.

    Args:
        station_id (uuid.UUID): L'identifiant de la station pour laquelle récupérer les soldes.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que la station appartient à la même compagnie.

    Returns:
        List[soldes_schemas.SoldeTiersResponse]: Une liste des soldes pour tous les tiers associés à la station.

    Raises:
        HTTPException: Si la station spécifiée n'est pas trouvée ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que la station existe et appartient à la même compagnie que l'utilisateur
    station = db.query(Station).filter(
        Station.id == station_id,
        Station.compagnie_id == current_user.compagnie_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Récupérer tous les soldes pour cette station
    soldes = db.query(SoldeTiers).filter(
        SoldeTiers.station_id == station_id
    ).all()

    return soldes


@router.get("/tiers/{tiers_id}/historique-modifications",
            response_model=List[journal_schemas.JournalModificationTiersResponse],
            dependencies=[Depends(require_permission("Module Tiers"))],
            summary="Récupérer l'historique des modifications d'un tiers",
            description="Récupère l'historique des modifications d'un tiers (client, fournisseur ou employé) appartenant à la même compagnie que l'utilisateur connecté. Les modifications sont triées par date de création en ordre descendant.",
            tags=["Tiers"])
async def get_historique_modifications_tiers(
    tiers_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[journal_schemas.JournalModificationTiersResponse]:
    """
    Récupère l'historique des modifications d'un tiers.

    Args:
        tiers_id (uuid.UUID): L'identifiant du tiers pour lequel récupérer l'historique des modifications.
        db (Session): Session de base de données pour les opérations.
        current_user (User): Informations sur l'utilisateur connecté, utilisé pour vérifier les permissions
                             et s'assurer que le tiers appartient à la même compagnie.

    Returns:
        List[journal_schemas.JournalModificationTiersResponse]: Une liste des modifications du tiers triée par date décroissante.

    Raises:
        HTTPException: Si le tiers spécifié n'est pas trouvé ou n'appartient pas à la compagnie de l'utilisateur.
    """
    # Vérifier que le tiers existe et appartient à la même compagnie que l'utilisateur
    tiers = db.query(Tiers).filter(
        Tiers.id == tiers_id,
        Tiers.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found")

    # Récupérer l'historique des modifications du tiers
    historique = db.query(JournalModificationTiers).filter(
        JournalModificationTiers.tiers_id == tiers_id
    ).order_by(JournalModificationTiers.created_at.desc()).all()

    return historique