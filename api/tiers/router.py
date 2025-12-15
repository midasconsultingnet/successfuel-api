from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..models import User
from . import schemas, soldes_schemas
from ..models.tiers import Tiers, SoldeTiers
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

router = APIRouter(tags=["tiers"])


@router.post("/clients", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Créer un nouveau client
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


@router.post("/fournisseurs", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_fournisseur(
    fournisseur: schemas.FournisseurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Créer un nouveau fournisseur
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


@router.post("/employes", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_employe(
    employe: schemas.EmployeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Créer un nouvel employé
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


@router.get("/stations/{station_id}/clients", response_model=List[schemas.TiersResponse], dependencies=[Depends(require_permission("Module Tiers"))])
async def get_clients_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les clients associés à une station spécifique
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


@router.get("/clients/{client_id}", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupérer un client spécifique
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


@router.get("/fournisseurs/{fournisseur_id}", response_model=schemas.TiersResponse)
async def get_fournisseur(
    fournisseur_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupérer un fournisseur spécifique
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


@router.get("/clients", response_model=List[schemas.TiersResponse])
async def get_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les clients de la compagnie
    """
    clients = db.query(Tiers).filter(
        Tiers.type == "client",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return clients


@router.get("/fournisseurs", response_model=List[schemas.TiersResponse])
async def get_all_fournisseurs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les fournisseurs de la compagnie
    """
    fournisseurs = db.query(Tiers).filter(
        Tiers.type == "fournisseur",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return fournisseurs


@router.get("/employes", response_model=List[schemas.TiersResponse])
async def get_all_employes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les employés de la compagnie
    """
    employes = db.query(Tiers).filter(
        Tiers.type == "employé",
        Tiers.statut != "supprimé",  # Exclure les tiers supprimés
        Tiers.compagnie_id == current_user.compagnie_id
    ).all()

    return employes


@router.get("/employes/{employe_id}", response_model=schemas.TiersResponse)
async def get_employe(
    employe_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Récupérer un employé spécifique
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


@router.get("/stations/{station_id}/fournisseurs", response_model=List[schemas.TiersResponse])
async def get_fournisseurs_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les fournisseurs associés à une station spécifique
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


@router.put("/clients/{client_id}", response_model=schemas.TiersResponse)
async def update_client(
    client_id: uuid.UUID,
    client_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Mettre à jour un client spécifique
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


@router.put("/fournisseurs/{fournisseur_id}", response_model=schemas.TiersResponse)
async def update_fournisseur(
    fournisseur_id: uuid.UUID,
    fournisseur_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Mettre à jour un fournisseur spécifique
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


@router.put("/employes/{employe_id}", response_model=schemas.TiersResponse)
async def update_employe(
    employe_id: uuid.UUID,
    employe_update: schemas.TiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> schemas.TiersResponse:
    """
    Mettre à jour un employé spécifique
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


@router.delete("/clients/{client_id}", response_model=dict)
async def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprimer un client spécifique (suppression logique)
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


@router.delete("/fournisseurs/{fournisseur_id}", response_model=dict)
async def delete_fournisseur(
    fournisseur_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprimer un fournisseur spécifique (suppression logique)
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


@router.delete("/employes/{employe_id}", response_model=dict)
async def delete_employe(
    employe_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Supprimer un employé spécifique (suppression logique)
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


@router.post("/tiers/{tiers_id}/associer-station/{station_id}", response_model=dict)
async def associer_tiers_a_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Associer un tiers à une station
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


@router.post("/tiers/{tiers_id}/dissocier-station/{station_id}", response_model=dict)
async def dissocier_tiers_de_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Dissocier un tiers d'une station
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


@router.get("/stations/{station_id}/employes", response_model=List[schemas.TiersResponse])
async def get_employes_by_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[schemas.TiersResponse]:
    """
    Récupérer tous les employés associés à une station spécifique
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


@router.post("/tiers/{tiers_id}/soldes/{station_id}", response_model=soldes_schemas.SoldeTiersResponse)
async def create_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    solde_create: soldes_schemas.SoldeTiersCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Initialiser le solde d'un tiers (client, fournisseur ou employé) pour une station spécifique
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

    # Créer le solde initial
    db_solde_initial = SoldeTiers(
        tiers_id=tiers_id,
        station_id=station_id,
        montant_initial=solde_create.montant_initial,
        montant_actuel=solde_create.montant_initial,  # Initialement, le solde actuel est identique au solde initial
        devise=solde_create.devise
    )

    db.add(db_solde_initial)
    db.commit()
    db.refresh(db_solde_initial)

    return db_solde_initial


@router.get("/tiers/{tiers_id}/soldes/{station_id}", response_model=soldes_schemas.SoldeTiersResponse)
async def get_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Récupérer le solde initial d'un tiers pour une station spécifique
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


@router.put("/tiers/{tiers_id}/soldes/{station_id}", response_model=soldes_schemas.SoldeTiersResponse)
async def update_solde_initial_tiers_par_station(
    tiers_id: uuid.UUID,
    station_id: uuid.UUID,
    solde_update: soldes_schemas.SoldeTiersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> soldes_schemas.SoldeTiersResponse:
    """
    Mettre à jour le solde initial d'un tiers pour une station spécifique
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

    # Mettre à jour les champs modifiables
    update_data = solde_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(solde_initial, field, value)

    db.commit()
    db.refresh(solde_initial)

    return solde_initial


@router.get("/tiers/{tiers_id}/soldes", response_model=List[soldes_schemas.SoldeTiersResponse])
async def get_soldes_tiers_par_station(
    tiers_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[soldes_schemas.SoldeTiersResponse]:
    """
    Récupérer tous les soldes d'un tiers par station
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


@router.get("/stations/{station_id}/soldes", response_model=List[soldes_schemas.SoldeTiersResponse])
async def get_soldes_par_station(
    station_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[soldes_schemas.SoldeTiersResponse]:
    """
    Récupérer tous les soldes pour une station spécifique
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