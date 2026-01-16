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
from ..services.comptabilite import ComptabiliteManager, TypeOperationComptable
from ..models.plan_comptable import PlanComptableModel

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


@router.post("/clients", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_client(
    client: schemas.ClientCreateRequest,
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

    # Gérer la logique de catégorie pour le compte associé
    metadonnees = client.metadonnees or {}

    if "categorie" in metadonnees:
        categorie_value = metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Premier cas : la catégorie est un UUID de plan comptable existant
            plan_comptable = db.query(PlanComptableModel).filter(
                PlanComptableModel.id == categorie_uuid,
                PlanComptableModel.compagnie_id == current_user.compagnie_id
            ).first()

            if plan_comptable:
                # Remplacer la valeur de categorie par le libellé du compte
                metadonnees["categorie"] = plan_comptable.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du plan trouvé
                compte_associe = plan_comptable.id
            else:
                # Si le plan comptable n'existe pas, lever une exception
                raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Deuxième cas : la catégorie est un string libre comme "nouvelle client"

            # Vérifier si une catégorie avec ce libellé existe déjà dans les métadonnées des clients de la compagnie
            categorie_existe = db.query(Tiers).filter(
                Tiers.type == "client",
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.metadonnees.op('->>')('categorie') == categorie_value
            ).first()

            if categorie_existe:
                raise HTTPException(status_code=400, detail="Catégorie déjà existante")

            try:
                # Créer un nouveau compte dans le plan comptable
                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="411",
                    libelle_compte=categorie_value,
                    categorie="client",  # Catégorie appropriée pour un compte client
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Actif"  # Type approprié pour les clients
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    # Créer le client avec le compagnie_id de l'utilisateur connecté et le type 'client'
    db_client = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="client",
        nom=client.nom,
        email=client.email,
        telephone=client.telephone,
        adresse=client.adresse,
        statut=client.statut,
        compte_associe=compte_associe if 'compte_associe' in locals() else None,
        donnees_personnelles=client.donnees_personnelles,
        station_ids=client.station_ids,
        metadonnees=metadonnees
    )

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


@router.post("/fournisseurs", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_fournisseur(
    fournisseur: schemas.FournisseurCreateRequest,
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

    # Gérer la logique de catégorie pour le compte associé
    metadonnees = fournisseur.metadonnees or {}

    if "categorie" in metadonnees:
        categorie_value = metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Premier cas : la catégorie est un UUID de plan comptable existant
            plan_comptable = db.query(PlanComptableModel).filter(
                PlanComptableModel.id == categorie_uuid,
                PlanComptableModel.compagnie_id == current_user.compagnie_id
            ).first()

            if plan_comptable:
                # Remplacer la valeur de categorie par le libellé du compte
                metadonnees["categorie"] = plan_comptable.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du plan trouvé
                compte_associe = plan_comptable.id
            else:
                # Si le plan comptable n'existe pas, lever une exception
                raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Deuxième cas : la catégorie est un string libre comme "nouveau fournisseur"
            try:
                # Créer un nouveau compte dans le plan comptable
                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="401",  # Compte parent pour les fournisseurs
                    libelle_compte=categorie_value,
                    categorie="fournisseur",  # Catégorie appropriée pour un compte fournisseur
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Actif"  # Type approprié pour les fournisseurs
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    # Créer le fournisseur avec le compagnie_id de l'utilisateur connecté et le type 'fournisseur'
    db_fournisseur = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="fournisseur",
        nom=fournisseur.nom,
        email=fournisseur.email,
        telephone=fournisseur.telephone,
        adresse=fournisseur.adresse,
        statut=fournisseur.statut,
        compte_associe=compte_associe if 'compte_associe' in locals() else None,
        donnees_personnelles=fournisseur.donnees_personnelles,
        station_ids=fournisseur.station_ids,
        metadonnees=metadonnees,
        type_paiement=fournisseur.type_paiement,
        delai_paiement=fournisseur.delai_paiement,
        acompte_requis=fournisseur.acompte_requis,
        seuil_credit=fournisseur.seuil_credit
    )

    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)

    return db_fournisseur


@router.post("/employes", response_model=schemas.TiersResponse, dependencies=[Depends(require_permission("Module Tiers"))])
async def create_employe(
    employe: schemas.EmployeCreateRequest,
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

    # Gérer la logique de catégorie pour le compte associé
    metadonnees = employe.metadonnees or {}

    if "categorie" in metadonnees:
        categorie_value = metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Premier cas : la catégorie est un UUID de plan comptable existant
            plan_comptable = db.query(PlanComptableModel).filter(
                PlanComptableModel.id == categorie_uuid,
                PlanComptableModel.compagnie_id == current_user.compagnie_id
            ).first()

            if plan_comptable:
                # Remplacer la valeur de categorie par le libellé du compte
                metadonnees["categorie"] = plan_comptable.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du plan trouvé
                compte_associe = plan_comptable.id
            else:
                # Si le plan comptable n'existe pas, lever une exception
                raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Deuxième cas : la catégorie est un string libre comme "nouvel employé"
            try:
                # Créer un nouveau compte dans le plan comptable
                # Pour les employés, on pourrait utiliser un compte parent spécifique
                # ou créer un compte parent pour les employés s'il n'existe pas
                from sqlalchemy import func

                # Chercher un compte parent pour les employés (ex: 421 - Personnel)
                compte_parent = PlanComptableHelper.get_compte_parent(db, "421", current_user.compagnie_id)

                # Si le compte parent n'existe pas, on le crée
                if not compte_parent:
                    plan_service = PlanComptableService(db)

                    # Créer le compte parent pour les employés
                    compte_parent_data = PlanComptableCreate(
                        numero_compte="421",
                        libelle_compte="Personnel - Rémunérations dues",
                        categorie="personnel",
                        type_compte="Passif",
                        parent_id=None,  # Compte racine
                        compagnie_id=current_user.compagnie_id
                    )

                    compte_parent = plan_service.create_plan_comptable(compte_parent_data)

                    # Convertir en objet modèle pour le retour
                    compte_parent = db.query(PlanComptableModel).filter(
                        PlanComptableModel.id == compte_parent.id
                    ).first()

                # Créer le compte enfant pour l'employé
                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="421",  # Compte parent pour les employés
                    libelle_compte=categorie_value,
                    categorie="employé",  # Catégorie appropriée pour un compte employé
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Passif"  # Type approprié pour les employés
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    # Créer l'employé avec le compagnie_id de l'utilisateur connecté et le type 'employé'
    db_employe = Tiers(
        compagnie_id=current_user.compagnie_id,
        type="employé",
        nom=employe.nom,
        email=employe.email,
        telephone=employe.telephone,
        adresse=employe.adresse,
        statut=employe.statut,
        compte_associe=compte_associe if 'compte_associe' in locals() else None,
        donnees_personnelles=employe.donnees_personnelles,
        station_ids=employe.station_ids,
        metadonnees=metadonnees
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

    # Gérer la logique de catégorie pour le compte associé si présente dans la mise à jour
    if client_update.metadonnees and "categorie" in client_update.metadonnees:
        categorie_value = client_update.metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Vérifier si ce plan comptable est déjà associé à un autre client
            # On recherche tous les tiers (clients) qui ont ce plan comptable dans leurs metadonnees
            autres_clients = db.query(Tiers).filter(
                Tiers.type == "client",
                Tiers.id != client_id,  # Exclure le client en cours de mise à jour
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.statut != "supprimé",
                Tiers.metadonnees.op('->>')('categorie') == str(categorie_uuid)
            ).all()

            if autres_clients:
                # Si le plan comptable est déjà associé à un autre client,
                # on crée un nouveau compte dans le plan comptable
                try:
                    print(f"[DEBUG] Appel de PlanComptableHelper.creer_compte_enfant pour client (mise à jour)")
                    nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                        db=db,
                        numero_compte_parent="411",
                        libelle_compte=categorie_value,
                        categorie="client",  # Catégorie appropriée pour un compte client
                        compagnie_id=current_user.compagnie_id,
                        type_compte="Actif"  # Type approprié pour les clients
                    )

                    # Mettre à jour la valeur de categorie dans les metadonnees avec l'UUID du nouveau plan
                    client_update.metadonnees["categorie"] = str(nouveau_plan.id)
                except ValueError as e:
                    raise HTTPException(status_code=404, detail=str(e))
            else:
                # Si le plan comptable n'est associé à aucun autre client,
                # on peut le mettre à jour avec la nouvelle catégorie
                plan_comptable = db.query(PlanComptableModel).filter(
                    PlanComptableModel.id == categorie_uuid,
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()

                if plan_comptable:
                    # Mettre à jour le libellé du compte avec la nouvelle catégorie
                    plan_comptable.libelle_compte = categorie_value
                    db.commit()
                else:
                    # Si le plan comptable n'existe pas, lever une exception
                    raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Si la valeur n'est pas un UUID, on la traite comme une chaîne libre
            # et on crée un nouveau compte dans le plan comptable

            # Vérifier si une catégorie avec ce libellé existe déjà dans les métadonnées des clients de la compagnie
            categorie_existe = db.query(Tiers).filter(
                Tiers.type == "client",
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.metadonnees.op('->>')('categorie') == categorie_value
            ).first()

            if categorie_existe and str(categorie_existe.id) != str(client_id):
                raise HTTPException(status_code=400, detail="Catégorie déjà existante")

            try:
                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="411",
                    libelle_compte=categorie_value,
                    categorie="client",  # Catégorie appropriée pour un compte client
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Actif"  # Type approprié pour les clients
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                client_update.metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                client_update.compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

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

    # Gérer la logique de catégorie pour le compte associé si présente dans la mise à jour
    if fournisseur_update.metadonnees and "categorie" in fournisseur_update.metadonnees:
        categorie_value = fournisseur_update.metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Vérifier si ce plan comptable est déjà associé à un autre fournisseur
            # On recherche tous les tiers (fournisseurs) qui ont ce plan comptable dans leurs metadonnees
            autres_fournisseurs = db.query(Tiers).filter(
                Tiers.type == "fournisseur",
                Tiers.id != fournisseur_id,  # Exclure le fournisseur en cours de mise à jour
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.statut != "supprimé",
                Tiers.metadonnees.op('->>')('categorie') == str(categorie_uuid)
            ).all()

            if autres_fournisseurs:
                # Si le plan comptable est déjà associé à un autre fournisseur,
                # on crée un nouveau compte dans le plan comptable
                try:
                    nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                        db=db,
                        numero_compte_parent="401",  # Compte parent pour les fournisseurs
                        libelle_compte=categorie_value,
                        categorie="fournisseur",  # Catégorie appropriée pour un compte fournisseur
                        compagnie_id=current_user.compagnie_id,
                        type_compte="Actif"  # Type approprié pour les fournisseurs
                    )

                    # Mettre à jour la valeur de categorie dans les metadonnees avec l'UUID du nouveau plan
                    fournisseur_update.metadonnees["categorie"] = str(nouveau_plan.id)
                except ValueError as e:
                    raise HTTPException(status_code=404, detail=str(e))
            else:
                # Si le plan comptable n'est associé à aucun autre fournisseur,
                # on peut le mettre à jour avec la nouvelle catégorie
                plan_comptable = db.query(PlanComptableModel).filter(
                    PlanComptableModel.id == categorie_uuid,
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()

                if plan_comptable:
                    # Mettre à jour le libellé du compte avec la nouvelle catégorie
                    plan_comptable.libelle_compte = categorie_value
                    db.commit()
                else:
                    # Si le plan comptable n'existe pas, lever une exception
                    raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Si la valeur n'est pas un UUID, on la traite comme une chaîne libre
            # et on crée un nouveau compte dans le plan comptable

            # Vérifier si une catégorie avec ce libellé existe déjà dans les métadonnées des fournisseurs de la compagnie
            categorie_existe = db.query(Tiers).filter(
                Tiers.type == "fournisseur",
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.metadonnees.op('->>')('categorie') == categorie_value
            ).first()

            if categorie_existe and str(categorie_existe.id) != str(fournisseur_id):
                raise HTTPException(status_code=400, detail="Catégorie déjà existante")

            try:
                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="401",  # Compte parent pour les fournisseurs
                    libelle_compte=categorie_value,
                    categorie="fournisseur",  # Catégorie appropriée pour un compte fournisseur
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Actif"  # Type approprié pour les fournisseurs
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                fournisseur_update.metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                fournisseur_update.compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

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

    # Gérer la logique de catégorie pour le compte associé si présente dans la mise à jour
    if employe_update.metadonnees and "categorie" in employe_update.metadonnees:
        categorie_value = employe_update.metadonnees["categorie"]

        # Importer le modèle PlanComptableModel
        from ..models.plan_comptable import PlanComptableModel
        from .plan_comptable_helper import PlanComptableHelper

        # Essayer de parser la valeur comme un UUID
        try:
            categorie_uuid = uuid.UUID(categorie_value)

            # Vérifier si ce plan comptable est déjà associé à un autre employé
            # On recherche tous les tiers (employés) qui ont ce plan comptable dans leurs metadonnees
            autres_employes = db.query(Tiers).filter(
                Tiers.type == "employé",
                Tiers.id != employe_id,  # Exclure l'employé en cours de mise à jour
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.statut != "supprimé",
                Tiers.metadonnees.op('->>')('categorie') == str(categorie_uuid)
            ).all()

            if autres_employes:
                # Si le plan comptable est déjà associé à un autre employé,
                # on crée un nouveau compte dans le plan comptable
                try:
                    # Chercher un compte parent pour les employés (ex: 421 - Personnel)
                    compte_parent = PlanComptableHelper.get_compte_parent(db, "421", current_user.compagnie_id)

                    # Si le compte parent n'existe pas, on le crée
                    if not compte_parent:
                        plan_service = PlanComptableService(db)

                        # Créer le compte parent pour les employés
                        compte_parent_data = PlanComptableCreate(
                            numero_compte="421",
                            libelle_compte="Personnel - Rémunérations dues",
                            categorie="personnel",
                            type_compte="Bilan",
                            parent_id=None,  # Compte racine
                            compagnie_id=current_user.compagnie_id
                        )

                        compte_parent = plan_service.create_plan_comptable(compte_parent_data)

                        # Convertir en objet modèle pour le retour
                        compte_parent = db.query(PlanComptableModel).filter(
                            PlanComptableModel.id == compte_parent.id
                        ).first()

                    nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                        db=db,
                        numero_compte_parent="421",  # Compte parent pour les employés
                        libelle_compte=categorie_value,
                        categorie="employé",  # Catégorie appropriée pour un compte employé
                        compagnie_id=current_user.compagnie_id,
                        type_compte="Passif"  # Type approprié pour les employés
                    )

                    # Mettre à jour la valeur de categorie dans les metadonnees avec l'UUID du nouveau plan
                    employe_update.metadonnees["categorie"] = str(nouveau_plan.id)
                except ValueError as e:
                    raise HTTPException(status_code=404, detail=str(e))
            else:
                # Si le plan comptable n'est associé à aucun autre employé,
                # on peut le mettre à jour avec la nouvelle catégorie
                plan_comptable = db.query(PlanComptableModel).filter(
                    PlanComptableModel.id == categorie_uuid,
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()

                if plan_comptable:
                    # Mettre à jour le libellé du compte avec la nouvelle catégorie
                    plan_comptable.libelle_compte = categorie_value
                    db.commit()
                else:
                    # Si le plan comptable n'existe pas, lever une exception
                    raise HTTPException(status_code=404, detail=f"Plan comptable {categorie_value} non trouvé")

        except ValueError:
            # Si la valeur n'est pas un UUID, on la traite comme une chaîne libre
            # et on crée un nouveau compte dans le plan comptable

            # Vérifier si une catégorie avec ce libellé existe déjà dans les métadonnées des employés de la compagnie
            categorie_existe = db.query(Tiers).filter(
                Tiers.type == "employé",
                Tiers.compagnie_id == current_user.compagnie_id,
                Tiers.metadonnees.op('->>')('categorie') == categorie_value
            ).first()

            if categorie_existe and str(categorie_existe.id) != str(employe_id):
                raise HTTPException(status_code=400, detail="Catégorie déjà existante")

            try:
                # Chercher un compte parent pour les employés (ex: 421 - Personnel)
                compte_parent = PlanComptableHelper.get_compte_parent(db, "421", current_user.compagnie_id)

                # Si le compte parent n'existe pas, on le crée
                if not compte_parent:
                    plan_service = PlanComptableService(db)

                    # Créer le compte parent pour les employés
                    compte_parent_data = PlanComptableCreate(
                        numero_compte="421",
                        libelle_compte="Personnel - Rémunérations dues",
                        categorie="personnel",
                        type_compte="Passif",
                        parent_id=None,  # Compte racine
                        compagnie_id=current_user.compagnie_id
                    )

                    compte_parent = plan_service.create_plan_comptable(compte_parent_data)

                    # Convertir en objet modèle pour le retour
                    compte_parent = db.query(PlanComptableModel).filter(
                        PlanComptableModel.id == compte_parent.id
                    ).first()

                nouveau_plan = PlanComptableHelper.creer_compte_enfant(
                    db=db,
                    numero_compte_parent="421",  # Compte parent pour les employés
                    libelle_compte=categorie_value,
                    categorie="employé",  # Catégorie appropriée pour un compte employé
                    compagnie_id=current_user.compagnie_id,
                    type_compte="Passif"  # Type approprié pour les employés
                )

                # Mettre à jour la valeur de categorie dans les metadonnees avec le libellé du nouveau plan
                employe_update.metadonnees["categorie"] = nouveau_plan.libelle_compte
                # Mettre à jour le champ compte_associe avec l'UUID du nouveau plan
                employe_update.compte_associe = nouveau_plan.id
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

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
        montant_actuel=0,  # On initialise à 0, le trigger s'occupera de le mettre à jour
        devise=solde_create.devise,
        type_solde_initial=solde_create.type_solde_initial.value  # Ajouter le type de solde initial
    )

    db.add(db_solde_initial)
    db.commit()
    db.refresh(db_solde_initial)

    # Enregistrer le mouvement de solde initial
    try:
        # Importer la fonction pour enregistrer le mouvement de tiers
        from ..services.tiers.tiers_solde_service import enregistrer_mouvement_tiers

        # Déterminer le type de mouvement selon le type de solde initial
        # Selon le trigger trig_update_solde_tiers:
        # - Un débit diminue le solde (ex: paiement fait à un fournisseur)
        # - Un crédit augmente le solde (ex: paiement reçu d'un client)
        if solde_create.type_solde_initial.value == "creance":
            # Si c'est une créance, le tiers est débiteur (doit de l'argent à l'entreprise)
            # Donc on enregistre un crédit pour augmenter son solde positif
            type_mouvement = "crédit"
        else:  # dette
            # Si c'est une dette, le tiers est créditeur (l'entreprise lui doit de l'argent)
            # Donc on enregistre un débit pour diminuer son solde (rendre négatif)
            type_mouvement = "débit"

        # Enregistrer le mouvement de solde initial
        enregistrer_mouvement_tiers(
            db=db,
            tiers_id=tiers_id,
            station_id=station_id,
            type_mouvement=type_mouvement,
            montant=solde_create.montant_initial,
            utilisateur_id=current_user.id,
            description=f"Initialisation du solde {solde_create.type_solde_initial.value}",
            module_origine="Module Tiers",
            reference_origine=f"INIT_SLD_{db_solde_initial.id}",
            transaction_source_id=db_solde_initial.id,
            type_transaction_source="solde_initial"
        )
    except Exception as e:
        # En cas d'erreur lors de l'enregistrement du mouvement, on loggue l'erreur
        # mais on ne bloque pas l'opération principale
        print(f"Erreur lors de l'enregistrement du mouvement de solde: {str(e)}")

    # Enregistrer l'écriture comptable pour l'initialisation du solde
    try:
        # Déterminer les comptes à utiliser selon le type de tiers et le type de solde
        compte_tiers = None
        if tiers.compte_associe:
            # Utiliser le compte associé au tiers s'il existe
            compte_tiers = db.query(PlanComptableModel).filter(
                PlanComptableModel.id == tiers.compte_associe
            ).first()

        # Si pas de compte associé, déterminer le compte selon le type de tiers
        if not compte_tiers:
            # Trouver le compte approprié selon le type de tiers
            if tiers.type == "client":
                # Recherche du compte client (commençant par 411)
                compte_tiers = db.query(PlanComptableModel).filter(
                    PlanComptableModel.numero_compte.like('411%'),
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()
            elif tiers.type == "fournisseur":
                # Recherche du compte fournisseur (commençant par 401)
                compte_tiers = db.query(PlanComptableModel).filter(
                    PlanComptableModel.numero_compte.like('401%'),
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()
            elif tiers.type == "employé":
                # Recherche du compte employé (commençant par 421)
                compte_tiers = db.query(PlanComptableModel).filter(
                    PlanComptableModel.numero_compte.like('421%'),
                    PlanComptableModel.compagnie_id == current_user.compagnie_id
                ).first()

        # Recherche du compte d'ouverture (890 ou 110)
        # Les comptes racines (sans parent_id) sont disponibles pour toutes les compagnies
        compte_ouverture = db.query(PlanComptableModel).filter(
            PlanComptableModel.numero_compte.in_(['890', '110']),
            PlanComptableModel.parent_id.is_(None)  # Compte racine
        ).first()

        if compte_tiers and compte_ouverture:
            # Déterminer le type d'écriture selon le type de solde initial
            if solde_create.type_solde_initial.value == "creance":
                # Si c'est une créance, le tiers est débiteur (ex: client qui doit de l'argent)
                # Donc on débite le compte tiers et on crédite le compte d'ouverture
                compte_debit_id = compte_tiers.id
                compte_credit_id = compte_ouverture.id
                print(f"Écriture comptable - Créance: Débit {compte_debit_id}, Crédit {compte_credit_id}")
            else:  # dette
                # Si c'est une dette, le tiers est créditeur (ex: entreprise qui doit de l'argent au client)
                # Donc on crédite le compte tiers et on débite le compte d'ouverture
                compte_debit_id = compte_ouverture.id
                compte_credit_id = compte_tiers.id
                print(f"Écriture comptable - Dette: Débit {compte_debit_id}, Crédit {compte_credit_id}")

            # Enregistrer l'écriture comptable
            print(f"Appel à enregistrer_ecriture_double avec montant: {solde_create.montant_initial}")
            ComptabiliteManager.enregistrer_ecriture_double(
                db=db,
                type_operation=TypeOperationComptable.TIERS_SOLDE_INITIAL,
                reference_origine=f"INIT_SLD_{db_solde_initial.id}",
                montant=solde_create.montant_initial,
                compte_debit=compte_debit_id,
                compte_credit=compte_credit_id,
                libelle=f"Initialisation solde {tiers.type} - {tiers.nom}",
                utilisateur_id=current_user.id,
                compagnie_id=current_user.compagnie_id
            )
            print("Écriture comptable enregistrée avec succès")
    except Exception as e:
        # En cas d'erreur lors de l'enregistrement comptable, on loggue l'erreur
        # mais on ne bloque pas l'opération principale
        print(f"Erreur lors de l'enregistrement comptable: {str(e)}")

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

    # Sauvegarder l'ancien montant pour comparer les changements
    ancien_montant = solde_initial.montant_initial

    # Mettre à jour les champs modifiables
    update_data = solde_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(solde_initial, field, value)

    # Si le montant initial a changé, enregistrer une écriture comptable
    if hasattr(solde_update, 'montant_initial') and solde_update.montant_initial != ancien_montant:
        # Importer la classe EcritureComptableHelper
        from .ecriture_comptable_helper import EcritureComptableHelper
        from ..models.plan_comptable import PlanComptableModel

        # Récupérer un compte de caisse par défaut pour la contrepartie
        # On peut chercher un compte de caisse dans le plan comptable
        compte_caisse = db.query(PlanComptableModel).filter(
            PlanComptableModel.numero_compte.like('53%'),  # Compte de caisse commence par 53
            PlanComptableModel.compagnie_id == current_user.compagnie_id
        ).first()

        if not compte_caisse:
            # Si aucun compte de caisse n'est trouvé, on peut chercher un compte bancaire
            compte_caisse = db.query(PlanComptableModel).filter(
                PlanComptableModel.numero_compte.like('512%'),  # Compte bancaire commence par 512
                PlanComptableModel.compagnie_id == current_user.compagnie_id
            ).first()

        if not compte_caisse:
            raise HTTPException(status_code=400, detail="Aucun compte de caisse ou banque trouvé pour la contrepartie")

        # Créer une écriture comptable pour le changement de solde
        EcritureComptableHelper.creer_ecriture_solde_initiale_tiers(
            db=db,
            tiers_id=tiers_id,
            compte_associe_id=tiers.compte_associe,  # Utiliser le compte associé au tiers
            montant=solde_update.montant_initial,
            devise=solde_initial.devise,
            utilisateur_id=current_user.id,
            compte_contrepartie_id=compte_caisse.id
        )

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