from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Tiers as TiersModel, SoldeTiers as SoldeTiersModel
from . import schemas
from .soldes_schemas import SoldeTiersCreate, SoldeTiersUpdate, SoldeTiersResponse, MouvementTiersCreate, MouvementTiersUpdate, MouvementTiersResponse, TypeSoldeInitial
from ..models.tiers import SoldeTiers, MouvementTiers
from ..utils.pagination import PaginatedResponse
from ..utils.filters import TiersFilterParams
from ..services.pagination_service import apply_filters_and_pagination, apply_specific_filters
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
from datetime import datetime
from .utils import calculer_solde_actuel

router = APIRouter()
security = HTTPBearer()

# Nouveaux endpoints spécifiques

@router.post("/clients", response_model=schemas.ClientResponse)
async def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Check if client already exists based on name
    db_client = db.query(TiersModel).filter(
        TiersModel.nom == client.nom,
        TiersModel.type == "client",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()
    if db_client:
        raise HTTPException(status_code=400, detail="Client with this name already exists in your company")

    # Create the client with the company ID from the authenticated user
    db_client = TiersModel(
        nom=client.nom,
        type="client",
        adresse=client.adresse,
        telephone=client.telephone,
        email=client.email,
        identifiant_fiscal=client.identifiant_fiscal,
        seuil_credit=client.seuil_credit,
        conditions_paiement=client.conditions_paiement,
        categorie_client=client.categorie_client,
        compagnie_id=current_user.compagnie_id,
        statut="inactif"  # Nouveau client est inactif jusqu'à l'ajout d'un solde initial
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    # Ajouter le solde actuel à la réponse
    db_client.solde_actuel = calculer_solde_actuel(db, db_client.id)
    return db_client

@router.get("/clients", response_model=PaginatedResponse[schemas.ClientResponse])
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Fetch only clients for the user's company that are not marked as supprimé
    query = db.query(TiersModel).filter(
        TiersModel.type == "client",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Exclure les tiers supprimés
    )

    # Application du tri
    query = query.order_by(TiersModel.nom.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    clients = query.offset(skip).limit(limit).all()

    # Ajouter le solde actuel à chaque client
    for client in clients:
        client.solde_actuel = calculer_solde_actuel(db, client.id)

    # Détermination s'il y a plus d'éléments
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=clients,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/clients/{client_id}", response_model=schemas.ClientResponse)
async def get_client_by_id(
    client_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    client = db.query(TiersModel).filter(
        TiersModel.id == client_id,
        TiersModel.type == "client",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Vérifier que le client n'est pas supprimé
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Ajouter le solde actuel à la réponse
    client.solde_actuel = calculer_solde_actuel(db, client.id)
    return client

@router.put("/clients/{client_id}", response_model=schemas.ClientResponse)
async def update_client(
    client_id: uuid.UUID,  # Changement du type pour utiliser UUID
    client: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    db_client = db.query(TiersModel).filter(
        TiersModel.id == client_id,
        TiersModel.type == "client",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)

    db.commit()
    db.refresh(db_client)

    # Ajouter le solde actuel à la réponse
    db_client.solde_actuel = calculer_solde_actuel(db, db_client.id)
    return db_client

@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    client = db.query(TiersModel).filter(
        TiersModel.id == client_id,
        TiersModel.type == "client",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Marquer le tiers comme supprimé au lieu de le supprimer physiquement
    client.statut = "supprimé"
    db.commit()
    db.refresh(client)
    return {"message": "Client marked as deleted successfully"}


# Endpoints pour les fournisseurs

@router.post("/fournisseurs", response_model=schemas.FournisseurResponse)
async def create_fournisseur(
    fournisseur: schemas.FournisseurCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Check if fournisseur already exists based on name
    db_fournisseur = db.query(TiersModel).filter(
        TiersModel.nom == fournisseur.nom,
        TiersModel.type == "fournisseur",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()
    if db_fournisseur:
        raise HTTPException(status_code=400, detail="Fournisseur with this name already exists in your company")

    # Create the fournisseur with the company ID from the authenticated user
    db_fournisseur = TiersModel(
        nom=fournisseur.nom,
        type="fournisseur",
        adresse=fournisseur.adresse,
        telephone=fournisseur.telephone,
        email=fournisseur.email,
        identifiant_fiscal=fournisseur.identifiant_fiscal,
        conditions_livraison=fournisseur.conditions_livraison,
        delai_paiement=fournisseur.delai_paiement,
        compagnie_id=current_user.compagnie_id,
        statut="inactif"  # Nouveau fournisseur est inactif jusqu'à l'ajout d'un solde initial
    )
    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)

    # Ajouter le solde actuel à la réponse
    db_fournisseur.solde_actuel = calculer_solde_actuel(db, db_fournisseur.id)
    return db_fournisseur

@router.get("/fournisseurs", response_model=PaginatedResponse[schemas.FournisseurResponse])
async def get_fournisseurs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Fetch only fournisseurs for the user's company that are not marked as supprimé
    query = db.query(TiersModel).filter(
        TiersModel.type == "fournisseur",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Exclure les tiers supprimés
    )

    # Application du tri
    query = query.order_by(TiersModel.nom.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    fournisseurs = query.offset(skip).limit(limit).all()

    # Ajouter le solde actuel à chaque fournisseur
    for fournisseur in fournisseurs:
        fournisseur.solde_actuel = calculer_solde_actuel(db, fournisseur.id)

    # Détermination s'il y a plus d'éléments
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=fournisseurs,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/fournisseurs/{fournisseur_id}", response_model=schemas.FournisseurResponse)
async def get_fournisseur_by_id(
    fournisseur_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    fournisseur = db.query(TiersModel).filter(
        TiersModel.id == fournisseur_id,
        TiersModel.type == "fournisseur",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Vérifier que le fournisseur n'est pas supprimé
    ).first()

    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    # Ajouter le solde actuel à la réponse
    fournisseur.solde_actuel = calculer_solde_actuel(db, fournisseur.id)
    return fournisseur

@router.put("/fournisseurs/{fournisseur_id}", response_model=schemas.FournisseurResponse)
async def update_fournisseur(
    fournisseur_id: uuid.UUID,  # Changement du type pour utiliser UUID
    fournisseur: schemas.FournisseurUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    db_fournisseur = db.query(TiersModel).filter(
        TiersModel.id == fournisseur_id,
        TiersModel.type == "fournisseur",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    update_data = fournisseur.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fournisseur, field, value)

    db.commit()
    db.refresh(db_fournisseur)

    # Ajouter le solde actuel à la réponse
    db_fournisseur.solde_actuel = calculer_solde_actuel(db, db_fournisseur.id)
    return db_fournisseur

@router.delete("/fournisseurs/{fournisseur_id}")
async def delete_fournisseur(
    fournisseur_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    fournisseur = db.query(TiersModel).filter(
        TiersModel.id == fournisseur_id,
        TiersModel.type == "fournisseur",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")

    # Marquer le tiers comme supprimé au lieu de le supprimer physiquement
    fournisseur.statut = "supprimé"
    db.commit()
    db.refresh(fournisseur)
    return {"message": "Fournisseur marked as deleted successfully"}


# Endpoints pour les employés

@router.post("/employes", response_model=schemas.EmployeResponse)
async def create_employe(
    employe: schemas.EmployeCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Check if employe already exists based on name
    db_employe = db.query(TiersModel).filter(
        TiersModel.nom == employe.nom,
        TiersModel.type == "employé",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()
    if db_employe:
        raise HTTPException(status_code=400, detail="Employe with this name already exists in your company")

    # Convertir la date_embauche de string à datetime si elle est fournie
    date_embauche = None
    if employe.date_embauche:
        from datetime import datetime
        try:
            date_embauche = datetime.fromisoformat(employe.date_embauche.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_embauche incorrect. Utilisez le format ISO 8601.")

    # Create the employe with the company ID from the authenticated user
    db_employe = TiersModel(
        nom=employe.nom,
        type="employé",
        adresse=employe.adresse,
        telephone=employe.telephone,
        email=employe.email,
        poste=employe.poste,
        date_embauche=date_embauche,
        compagnie_id=current_user.compagnie_id,
        statut="inactif"  # Nouvel employé est inactif jusqu'à l'ajout d'un solde initial
    )
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)

    # Ajouter le solde actuel à la réponse
    db_employe.solde_actuel = calculer_solde_actuel(db, db_employe.id)
    return db_employe

@router.get("/employes", response_model=PaginatedResponse[schemas.EmployeResponse])
async def get_employes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Fetch only employes for the user's company that are not marked as supprimé
    query = db.query(TiersModel).filter(
        TiersModel.type == "employé",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Exclure les tiers supprimés
    )

    # Application du tri
    query = query.order_by(TiersModel.nom.asc())

    # Calcul du total avant pagination
    total = query.count()

    # Application de la pagination
    employes = query.offset(skip).limit(limit).all()

    # Ajouter le solde actuel à chaque employé
    for employe in employes:
        employe.solde_actuel = calculer_solde_actuel(db, employe.id)

    # Détermination s'il y a plus d'éléments
    has_more = (skip + limit) < total

    return PaginatedResponse(
        items=employes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/employes/{employe_id}", response_model=schemas.EmployeResponse)
async def get_employe_by_id(
    employe_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    employe = db.query(TiersModel).filter(
        TiersModel.id == employe_id,
        TiersModel.type == "employé",
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut != "supprimé"  # Vérifier que l'employé n'est pas supprimé
    ).first()

    if not employe:
        raise HTTPException(status_code=404, detail="Employe not found")

    # Ajouter le solde actuel à la réponse
    employe.solde_actuel = calculer_solde_actuel(db, employe.id)
    return employe

@router.put("/employes/{employe_id}", response_model=schemas.EmployeResponse)
async def update_employe(
    employe_id: uuid.UUID,  # Changement du type pour utiliser UUID
    employe: schemas.EmployeUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    db_employe = db.query(TiersModel).filter(
        TiersModel.id == employe_id,
        TiersModel.type == "employé",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not db_employe:
        raise HTTPException(status_code=404, detail="Employe not found")

    update_data = employe.dict(exclude_unset=True)

    # Convertir la date_embauche de string à datetime si elle est fournie
    if 'date_embauche' in update_data and update_data['date_embauche']:
        from datetime import datetime
        try:
            date_embauche = datetime.fromisoformat(update_data['date_embauche'].replace('Z', '+00:00'))
            update_data['date_embauche'] = date_embauche
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date_embauche incorrect. Utilisez le format ISO 8601.")

    for field, value in update_data.items():
        setattr(db_employe, field, value)

    db.commit()
    db.refresh(db_employe)

    # Ajouter le solde actuel à la réponse
    db_employe.solde_actuel = calculer_solde_actuel(db, db_employe.id)
    return db_employe

@router.delete("/employes/{employe_id}")
async def delete_employe(
    employe_id: uuid.UUID,  # Changement du type pour utiliser UUID
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    employe = db.query(TiersModel).filter(
        TiersModel.id == employe_id,
        TiersModel.type == "employé",
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not employe:
        raise HTTPException(status_code=404, detail="Employe not found")

    # Marquer le tiers comme supprimé au lieu de le supprimer physiquement
    employe.statut = "supprimé"
    db.commit()
    db.refresh(employe)
    return {"message": "Employe marked as deleted successfully"}


# Endpoint pour supprimer définitivement les tiers sans historique
@router.delete("/tiers-nettoyage")
async def supprimer_tiers_sans_historique(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    from sqlalchemy import func

    # Trouver les tiers sans historique (pas de solde initial ni de mouvements) pour la compagnie de l'utilisateur
    tiers_a_supprimer = db.query(TiersModel).filter(
        TiersModel.compagnie_id == current_user.compagnie_id,
        TiersModel.statut == "inactif"  # Ceux qui n'ont pas de solde initial
    ).filter(
        ~TiersModel.id.in_(db.query(SoldeTiers.tiers_id))  # Sans solde initial
    ).filter(
        ~TiersModel.id.in_(db.query(MouvementTiers.tiers_id))  # Sans mouvements
    ).all()

    nb_supprimes = 0
    for tiers in tiers_a_supprimer:
        db.delete(tiers)
        nb_supprimes += 1

    db.commit()

    return {
        "message": f"{nb_supprimes} tiers sans historique supprimés définitivement",
        "details": [str(tiers.id) for tiers in tiers_a_supprimer]
    }


# Nouveaux endpoints pour la gestion des soldes et des mouvements

@router.post("/soldes", response_model=SoldeTiersResponse)
async def create_solde_initial(
    solde_data: SoldeTiersCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que le tiers appartient à la compagnie de l'utilisateur
    tiers = db.query(TiersModel).filter(
        TiersModel.id == solde_data.tiers_id,
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found in your company")

    # Vérifier s'il existe déjà un solde initial pour ce tiers
    solde_existant = db.query(SoldeTiers).filter(SoldeTiers.tiers_id == solde_data.tiers_id).first()
    if solde_existant:
        raise HTTPException(status_code=400, detail="Solde initial already exists for this tiers")

    # Gestion selon le type de solde initial
    montant_initial = solde_data.montant_initial
    mouvement_initial = None

    if solde_data.type_solde_initial == "creance":
        # Une créance est un crédit pour l'entreprise, donc un mouvement de crédit pour le tiers
        # Le solde initial dans la base de données sera 0
        montant_initial = 0
        # Créer un mouvement de crédit pour enregistrer la créance
        from ..models.tiers import MouvementTiers
        mouvement_initial = MouvementTiers(
            tiers_id=solde_data.tiers_id,
            type_mouvement="crédit",
            montant=solde_data.montant_initial,
            date_mouvement=datetime.utcnow(),
            description="Créance initiale enregistrée via solde initial",
            module_origine="soldes_initiaux",
            reference_origine="SI-001",  # Devrait être généré dynamiquement dans une implémentation complète
            utilisateur_id=current_user.id
        )
    elif solde_data.type_solde_initial == "dette":
        # Une dette est un débit pour l'entreprise, donc un mouvement de débit pour le tiers
        # Le solde initial dans la base de données sera 0
        montant_initial = 0
        # Créer un mouvement de débit pour enregistrer la dette
        from ..models.tiers import MouvementTiers
        mouvement_initial = MouvementTiers(
            tiers_id=solde_data.tiers_id,
            type_mouvement="débit",
            montant=solde_data.montant_initial,
            date_mouvement=datetime.utcnow(),
            description="Dette initiale enregistrée via solde initial",
            module_origine="soldes_initiaux",
            reference_origine="SI-001",  # Devrait être généré dynamiquement dans une implémentation complète
            utilisateur_id=current_user.id
        )

    # Créer le solde initial
    solde_initial = SoldeTiers(
        tiers_id=solde_data.tiers_id,
        montant_initial=montant_initial,
        devise=solde_data.devise
    )
    db.add(solde_initial)

    # Ajouter le mouvement initial si nécessaire
    if mouvement_initial:
        db.add(mouvement_initial)

    db.commit()
    db.refresh(solde_initial)

    # Mettre à jour le montant_actuel
    from .utils import mettre_a_jour_solde_actuel, mettre_a_jour_statut_tiers
    mettre_a_jour_solde_actuel(db, solde_initial.tiers_id)

    # Mettre à jour le statut du tiers (devrait devenir "actif")
    mettre_a_jour_statut_tiers(db, solde_initial.tiers_id)

    return solde_initial


class SoldeTiersUpdateWithDetails(schemas.BaseModel):
    montant_initial: Optional[float] = None
    montant_actuel: Optional[float] = None
    type_solde_initial: Optional[str] = None  # Utilisation de str au lieu de TypeSoldeInitial pour éviter les problèmes d'import
    devise: Optional[str] = None

    class Config:
        from_attributes = True

@router.put("/soldes/{tiers_id}", response_model=SoldeTiersResponse)
async def update_solde_initial(
    tiers_id: uuid.UUID,
    solde_data: SoldeTiersUpdateWithDetails,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que le tiers appartient à la compagnie de l'utilisateur
    tiers = db.query(TiersModel).filter(
        TiersModel.id == tiers_id,
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found in your company")

    # Récupérer le solde initial existant
    solde_initial = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id
    ).first()

    if not solde_initial:
        raise HTTPException(status_code=404, detail="Solde initial not found")

    # Gestion selon les paramètres fournis
    if solde_data.montant_initial is not None:
        # Si un type est spécifié, on gère comme un nouveau mouvement
        if solde_data.type_solde_initial:
            if solde_data.type_solde_initial == "creance":
                # Créer un mouvement de crédit pour enregistrer la créance
                from ..models.tiers import MouvementTiers
                mouvement_initial = MouvementTiers(
                    tiers_id=tiers_id,
                    type_mouvement="crédit",
                    montant=solde_data.montant_initial,
                    date_mouvement=datetime.utcnow(),
                    description="Mise à jour de créance initiale via solde initial",
                    module_origine="soldes_initiaux",
                    reference_origine="SI-002",
                    utilisateur_id=current_user.id
                )
                db.add(mouvement_initial)
            elif solde_data.type_solde_initial == "dette":
                # Créer un mouvement de débit pour enregistrer la dette
                from ..models.tiers import MouvementTiers
                mouvement_initial = MouvementTiers(
                    tiers_id=tiers_id,
                    type_mouvement="débit",
                    montant=solde_data.montant_initial,
                    date_mouvement=datetime.utcnow(),
                    description="Mise à jour de dette initiale via solde initial",
                    module_origine="soldes_initiaux",
                    reference_origine="SI-002",
                    utilisateur_id=current_user.id
                )
                db.add(mouvement_initial)
        else:
            # Montant initial sans type spécifié, mise à jour normale
            solde_initial.montant_initial = solde_data.montant_initial

    if solde_data.montant_actuel is not None:
        solde_initial.montant_actuel = solde_data.montant_actuel

    if solde_data.devise is not None:
        solde_initial.devise = solde_data.devise

    db.commit()
    db.refresh(solde_initial)

    # Mettre à jour le montant_actuel
    from .utils import mettre_a_jour_solde_actuel, mettre_a_jour_statut_tiers
    mettre_a_jour_solde_actuel(db, solde_initial.tiers_id)

    # Mettre à jour le statut du tiers
    mettre_a_jour_statut_tiers(db, solde_initial.tiers_id)

    return solde_initial


@router.get("/soldes/{tiers_id}", response_model=SoldeTiersResponse)
async def get_solde_initial(
    tiers_id: uuid.UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que le tiers appartient à la compagnie de l'utilisateur
    tiers = db.query(TiersModel).filter(
        TiersModel.id == tiers_id,
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found in your company")

    solde_initial = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id
    ).first()

    if not solde_initial:
        raise HTTPException(status_code=404, detail="Solde initial not found")

    return solde_initial


@router.post("/mouvements", response_model=MouvementTiersResponse)
async def create_mouvement_tiers(
    mouvement_data: MouvementTiersCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user
    current_user = get_current_user(db, credentials.credentials)

    # Vérifier que le tiers appartient à la compagnie de l'utilisateur
    tiers = db.query(TiersModel).filter(
        TiersModel.id == mouvement_data.tiers_id,
        TiersModel.compagnie_id == current_user.compagnie_id
    ).first()

    if not tiers:
        raise HTTPException(status_code=404, detail="Tiers not found in your company")

    # Vérifier que le type de mouvement est valide
    if mouvement_data.type_mouvement not in ['débit', 'crédit']:
        raise HTTPException(status_code=400, detail="Le type de mouvement doit être 'débit' ou 'crédit'")

    # Créer le mouvement
    mouvement = MouvementTiers(**mouvement_data.dict())
    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)

    # Mettre à jour le solde actuel
    from .utils import mettre_a_jour_solde_actuel, mettre_a_jour_statut_tiers
    mettre_a_jour_solde_actuel(db, mouvement.tiers_id)

    # Mettre à jour le statut du tiers
    mettre_a_jour_statut_tiers(db, mouvement.tiers_id)

    return mouvement
