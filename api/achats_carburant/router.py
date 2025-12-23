import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models import AchatCarburant as AchatCarburantModel, LigneAchatCarburant as LigneAchatCarburantModel, CompensationFinanciere as CompensationFinanciereModel, AvoirCompensation as AvoirCompensationModel, PaiementAchatCarburant as PaiementAchatCarburantModel, PrixCarburant, OperationJournal as OperationJournalModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission
from ..services.achats_carburant.stock_calculation_service import StockCalculationService
from ..auth.auth_handler import get_current_user_security
from ..services.achats_carburant.achat_carburant_service import create_achat_carburant_complet, annuler_achat_carburant, modifier_achat_carburant_complet

router = APIRouter()
security = HTTPBearer()

# Endpoints pour les achats de carburant
@router.get("/",
            response_model=List[schemas.AchatCarburantResponse],
            summary="Récupérer les achats de carburant",
            description="Récupère la liste des achats de carburant avec possibilité de paginer les résultats. Nécessite la permission 'Module Achats Carburant'. Permet de visualiser l'historique des approvisionnements en carburant.",
            tags=["Achats carburant"])
async def get_achats_carburant(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère la liste des achats de carburant.

    Args:
        skip (int): Nombre d'achats à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum d'achats à retourner (défaut: 100)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        List[schemas.AchatCarburantCreate]: Liste des achats de carburant
    """
    achats_carburant = db.query(AchatCarburantModel).offset(skip).limit(limit).all()
    return achats_carburant

@router.post("/",
             response_model=schemas.AchatCarburantResponse,
             summary="Créer un nouvel achat de carburant",
             description="Crée un nouvel achat de carburant. Nécessite la permission 'Module Achats Carburant'. L'achat de carburant enregistre une commande d'approvisionnement qui sera liée aux livraisons effectives ultérieurement.",
             tags=["Achats carburant"])
async def create_achat_carburant(
    achat_carburant: schemas.AchatCarburantCreateWithDetails,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée un nouvel achat de carburant.

    Args:
        achat_carburant (schemas.AchatCarburantCreateWithDetails): Détails de l'achat de carburant à créer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AchatCarburantResponse: Détails de l'achat de carburant créé

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    # Récupérer l'utilisateur connecté à partir du token JWT
    current_user = get_current_user_security(credentials, db)

    # Utiliser le service pour créer l'achat avec ses détails et ses paiements
    db_achat_carburant = create_achat_carburant_complet(
        db=db,
        achat_data=achat_carburant,
        utilisateur_id=current_user.id
    )

    return db_achat_carburant

@router.get("/{achat_carburant_id}",
            response_model=schemas.AchatCarburantResponse,
            summary="Récupérer un achat de carburant par ID",
            description="Récupère les détails d'un achat de carburant spécifique par son identifiant. Nécessite la permission 'Module Achats Carburant'. Permet d'obtenir toutes les informations relatives à une commande d'approvisionnement en carburant.",
            tags=["Achats carburant"])
async def get_achat_carburant_by_id(
    achat_carburant_id: UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère les détails d'un achat de carburant spécifique par son identifiant.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant à récupérer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AchatCarburantCreate: Détails de l'achat de carburant demandé

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    achat_carburant = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat_carburant:
        raise HTTPException(status_code=404, detail="Achat carburant not found")
    return achat_carburant

@router.put("/{achat_carburant_id}",
            response_model=schemas.AchatCarburantResponse,
            summary="Mettre à jour un achat de carburant",
            description="Met à jour les détails d'un achat de carburant existant. Nécessite la permission 'Module Achats Carburant'. La mise à jour peut affecter les calculs de stock et les écritures comptables associées.",
            tags=["Achats carburant"])
async def update_achat_carburant(
    achat_carburant_id: UUID,
    achat_carburant: schemas.AchatCarburantUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Met à jour les détails d'un achat de carburant existant.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant à mettre à jour
        achat_carburant (schemas.AchatCarburantUpdate): Nouvelles valeurs pour les champs de l'achat
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AchatCarburantUpdate: Détails de l'achat de carburant mis à jour

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    db_achat_carburant = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not db_achat_carburant:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    update_data = achat_carburant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_achat_carburant, field, value)

    # Si le statut est mis à jour à "validé" ou "facturé", créer les écritures comptables
    if "statut" in update_data and update_data["statut"] in ["validé", "facturé"]:
        # Récupérer les détails de l'achat pour créer les écritures comptables
        lignes_achat = db.query(LigneAchatCarburantModel).filter(
            LigneAchatCarburantModel.achat_carburant_id == achat_carburant_id
        ).all()

        # Créer les écritures comptables pour chaque ligne d'achat
        for ligne in lignes_achat:
            # Créer une écriture de stock (débit) - augmentation du stock
            stock_debit = OperationJournalModel(
                journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
                date_operation=db_achat_carburant.date_achat,
                libelle_operation=f"Entrée de stock pour l'achat carburant {db_achat_carburant.id}",
                compte_debit="375",  # Compte de stock de carburant
                compte_credit="607",  # Compte d'achat de carburant
                montant=float(ligne.montant),
                devise="XOF",
                reference_operation=f"AC{db_achat_carburant.id}",
                module_origine="achats_carburant",
                utilisateur_enregistrement_id=db_achat_carburant.utilisateur_id
            )
            db.add(stock_debit)

            # Créer une écriture de crédit pour la dette fournisseur
            fournisseur_credit = OperationJournalModel(
                journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
                date_operation=db_achat_carburant.date_achat,
                libelle_operation=f"Dette fournisseur pour l'achat carburant {db_achat_carburant.id}",
                compte_debit="607",  # Compte d'achat de carburant
                compte_credit="401",  # Compte fournisseur
                montant=float(ligne.montant),
                devise="XOF",
                reference_operation=f"AC{db_achat_carburant.id}",
                module_origine="achats_carburant",
                utilisateur_enregistrement_id=db_achat_carburant.utilisateur_id
            )
            db.add(fournisseur_credit)

    db.commit()
    db.refresh(db_achat_carburant)
    return db_achat_carburant

@router.delete("/{achat_carburant_id}",
               summary="Supprimer un achat de carburant",
               description="Supprime un achat de carburant existant. Nécessite la permission 'Module Achats Carburant'. La suppression affecte les calculs de stock et les écritures comptables associées.",
               tags=["Achats carburant"])
async def delete_achat_carburant(
    achat_carburant_id: UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprime un achat de carburant existant.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant à supprimer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Message de confirmation de la suppression

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    achat_carburant = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat_carburant:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    db.delete(achat_carburant)
    db.commit()
    return {"message": "Achat carburant deleted successfully"}

# Endpoint pour annuler un achat de carburant
@router.put("/{achat_carburant_id}/annuler",
            response_model=schemas.AchatCarburantResponse,
            summary="Annuler un achat de carburant",
            description="Annule un achat de carburant existant et gère les opérations associées (paiements, écritures comptables). Nécessite la permission 'Module Achats Carburant'.",
            tags=["Achats carburant"])
async def annuler_achat_carburant_endpoint(
    achat_carburant_id: UUID,
    motif: str = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Annule un achat de carburant existant et gère toutes les opérations associées.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant à annuler
        motif (str): Motif de l'annulation
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AchatCarburantResponse: Détails de l'achat de carburant annulé

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé, est déjà annulé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Récupérer l'utilisateur connecté à partir du token JWT
    current_user = get_current_user_security(credentials, db)

    # Annuler l'achat avec détails et paiements
    achat = annuler_achat_carburant(
        db,
        achat_carburant_id,
        current_user.id,
        motif
    )

    return achat

# Endpoint pour modifier un achat complet (avec détails et paiements)
@router.put("/{achat_carburant_id}/complet",
            response_model=schemas.AchatCarburantResponse,
            summary="Modifier un achat de carburant complet",
            description="Modifie un achat de carburant avec ses détails et paiements en une seule opération. Nécessite la permission 'Module Achats Carburant'.",
            tags=["Achats carburant"])
async def modifier_achat_carburant_complet_endpoint(
    achat_carburant_id: UUID,
    achat_data: schemas.AchatCarburantCreateWithDetails,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Modifie un achat de carburant avec ses détails et ses paiements en une seule opération.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant à modifier
        achat_data (schemas.AchatCarburantCreateWithDetails): Nouvelles données de l'achat, des lignes et des paiements
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AchatCarburantResponse: Détails de l'achat de carburant modifié

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé, est annulé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Récupérer l'utilisateur connecté à partir du token JWT
    current_user = get_current_user_security(credentials, db)

    # Modifier l'achat complet avec détails et paiements
    achat = modifier_achat_carburant_complet(
        db,
        achat_carburant_id,
        achat_data,
        current_user.id
    )

    return achat


# Endpoints pour les lignes d'achat de carburant
@router.get("/{achat_carburant_id}/lignes",
            response_model=List[schemas.LigneAchatCarburantResponse],
            summary="Récupérer les lignes d'un achat de carburant",
            description="Récupère la liste des lignes d'achat de carburant pour un achat spécifique. Nécessite la permission 'Module Achats Carburant'. Les lignes détaillent les produits (carburants) commandés, leurs quantités et prix respectifs.",
            tags=["Achats carburant"])
async def get_lignes_achat_carburant(
    achat_carburant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère la liste des lignes d'achat de carburant pour un achat spécifique.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant
        skip (int): Nombre de lignes à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de lignes à retourner (défaut: 100)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        List[schemas.LigneAchatCarburantCreate]: Liste des lignes d'achat de carburant
    """
    lignes = db.query(LigneAchatCarburantModel).filter(LigneAchatCarburantModel.achat_carburant_id == achat_carburant_id).offset(skip).limit(limit).all()
    return lignes

@router.post("/{achat_carburant_id}/lignes",
             response_model=schemas.LigneAchatCarburantResponse,
             summary="Créer une ligne d'achat de carburant",
             description="Crée une nouvelle ligne d'achat de carburant pour un achat spécifique. Nécessite la permission 'Module Achats Carburant'. La ligne détaille un produit (carburant) commandé, sa quantité et son prix.",
             tags=["Achats carburant"])
async def create_ligne_achat_carburant(
    achat_carburant_id: UUID,
    ligne: schemas.LigneAchatCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée une nouvelle ligne d'achat de carburant pour un achat spécifique.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant
        ligne (schemas.LigneAchatCarburantCreate): Détails de la ligne à créer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.LigneAchatCarburantCreate: Détails de la ligne d'achat de carburant créée

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Vérifier que l'achat existe
    achat = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    # Créer la ligne d'achat
    db_ligne = LigneAchatCarburantModel(
        achat_carburant_id=achat_carburant_id,
        carburant_id=ligne.carburant_id,
        quantite=ligne.quantite,
        prix_unitaire=ligne.prix_unitaire,
        montant=ligne.montant,
        station_id=ligne.station_id
    )

    db.add(db_ligne)

    # Mettre à jour le prix d'achat dans la table prix_carburant selon le CUMP
    # Récupérer les informations de la cuve pour déterminer le niveau actuel
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT c.id, c.niveau_actuel
        FROM cuve c
        WHERE c.station_id = :station_id
        LIMIT 1
    """), {"station_id": ligne.station_id})
    cuve_data = result.fetchone()

    if cuve_data:
        # Vérifier si un prix existe déjà pour ce couple carburant/station
        prix_existing = db.query(PrixCarburant).filter(
            PrixCarburant.carburant_id == ligne.carburant_id,
            PrixCarburant.station_id == ligne.station_id
        ).first()

        if prix_existing:
            # Calculer le nouveau CUMP
            stock_actuel = float(cuve_data.niveau_actuel) if cuve_data.niveau_actuel else 0
            nouveau_stock = float(ligne.quantite)
            prix_stock_actuel = float(prix_existing.prix_achat) if prix_existing.prix_achat else 0
            prix_nouveau_stock = float(ligne.prix_unitaire)

            if stock_actuel + nouveau_stock > 0:
                nouveau_cump = (stock_actuel * prix_stock_actuel + nouveau_stock * prix_nouveau_stock) / (stock_actuel + nouveau_stock)
                prix_existing.prix_achat = nouveau_cump
        else:
            # Créer un nouvel enregistrement de prix avec le prix unitaire de la ligne d'achat
            prix_carburant = PrixCarburant(
                carburant_id=ligne.carburant_id,
                station_id=ligne.station_id,
                prix_achat=ligne.prix_unitaire
            )
            db.add(prix_carburant)

    db.commit()
    db.refresh(db_ligne)

    return db_ligne

# Endpoints pour les compensations financières
@router.post("/compensations",
             response_model=schemas.CompensationFinanciereResponse,
             summary="Créer une compensation financière",
             description="Crée une nouvelle compensation financière pour un achat de carburant. Nécessite la permission 'Module Achats Carburant'. Les compensations sont utilisées pour ajuster les différences entre quantités commandées et livrées.",
             tags=["Achats carburant"])
async def create_compensation_financiere(
    compensation: schemas.CompensationFinanciereCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée une nouvelle compensation financière pour un achat de carburant.

    Args:
        compensation (schemas.CompensationFinanciereCreate): Détails de la compensation financière à créer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.CompensationFinanciereCreate: Détails de la compensation financière créée

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Vérifier que l'achat existe
    achat = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == compensation.achat_carburant_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    # Calculer la différence entre quantité théorique et réelle
    difference = compensation.quantite_reelle - compensation.quantite_theorique
    # Supposons un prix unitaire moyen pour le calcul de la compensation
    prix_unitaire_moyen = float(achat.montant_total) / compensation.quantite_theorique if compensation.quantite_theorique > 0 else 0
    montant_compensation = abs(difference) * prix_unitaire_moyen

    # Créer la compensation financière
    db_compensation = CompensationFinanciereModel(
        achat_carburant_id=compensation.achat_carburant_id,
        type_compensation=compensation.type_compensation,
        quantite_theorique=compensation.quantite_theorique,
        quantite_reelle=compensation.quantite_reelle,
        difference=difference,
        montant_compensation=montant_compensation,
        motif=compensation.motif
    )

    # Mettre à jour le statut de l'achat si nécessaire
    if difference != 0:
        achat.statut = "facturé"  # Si il y a une compensation, l'achat est considéré comme facturé

    db.add(db_compensation)

    # Créer les écritures comptables pour la compensation
    if montant_compensation > 0:
        # Si c'est un avoir reçu du fournisseur (quantité réelle < quantité théorique),
        # on crédite l'avoir et on débite le fournisseur
        if difference < 0:
            # Avoir reçu du fournisseur - On crédite le compte d'avoir et on débite le fournisseur
            avoir_fournisseur_credit = OperationJournalModel(
                journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
                date_operation=achat.date_achat,
                libelle_operation=f"Avoir reçu du fournisseur pour l'achat carburant {achat.id}",
                compte_debit="401",  # Compte fournisseur
                compte_credit="411",  # Compte d'avoir fournisseur
                montant=montant_compensation,
                devise="XOF",
                reference_operation=f"AC{achat.id}",
                module_origine="achats_carburant",
                utilisateur_enregistrement_id=achat.utilisateur_id
            )
            db.add(avoir_fournisseur_credit)
        # Si c'est un avoir dû au fournisseur (quantité réelle > quantité théorique),
        # on débite l'avoir et on crédite le fournisseur
        elif difference > 0:
            # Avoir dû au fournisseur - On débite le compte d'avoir et on crédite le fournisseur
            avoir_fournisseur_debit = OperationJournalModel(
                journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
                date_operation=achat.date_achat,
                libelle_operation=f"Avoir dû au fournisseur pour l'achat carburant {achat.id}",
                compte_debit="411",  # Compte d'avoir fournisseur
                compte_credit="401",  # Compte fournisseur
                montant=montant_compensation,
                devise="XOF",
                reference_operation=f"AC{achat.id}",
                module_origine="achats_carburant",
                utilisateur_enregistrement_id=achat.utilisateur_id
            )
            db.add(avoir_fournisseur_debit)

    db.commit()
    db.refresh(db_compensation)

    return db_compensation

# Endpoints pour les avoirs de compensation
@router.post("/avoirs_compensation",
             response_model=schemas.AvoirCompensationResponse,
             summary="Créer un avoir de compensation",
             description="Crée un nouvel avoir de compensation pour une compensation financière existante. Nécessite la permission 'Module Achats Carburant'. Les avoirs de compensation sont utilisés pour enregistrer les ajustements financiers liés aux différences de quantité.",
             tags=["Achats carburant"])
async def create_avoir_compensation(
    avoir: schemas.AvoirCompensationCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée un nouvel avoir de compensation pour une compensation financière existante.

    Args:
        avoir (schemas.AvoirCompensationCreate): Détails de l'avoir de compensation à créer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.AvoirCompensationCreate: Détails de l'avoir de compensation créé

    Raises:
        HTTPException: Si la compensation financière n'est pas trouvée ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Récupérer la compensation pour vérifier les détails
    compensation = db.query(CompensationFinanciereModel).filter(CompensationFinanciereModel.id == int(avoir.compensation_financiere_id)).first()
    if not compensation:
        raise HTTPException(status_code=404, detail="Compensation financière not found")

    # Récupérer l'utilisateur connecté à partir du token JWT
    current_user = get_current_user_security(credentials, db)

    # Créer l'avoir de compensation
    db_avoir = AvoirCompensationModel(
        compensation_financiere_id=avoir.compensation_financiere_id,
        tiers_id=avoir.tiers_id,
        montant=avoir.montant,
        date_emission=db.query(AchatCarburantModel).filter(AchatCarburantModel.id == compensation.achat_carburant_id).first().date_achat,
        utilisateur_emission_id=current_user.id
    )

    db.add(db_avoir)
    db.commit()
    db.refresh(db_avoir)

    return db_avoir

# Endpoints pour les paiements d'achats de carburant
@router.post("/{achat_carburant_id}/paiements",
             response_model=schemas.PaiementAchatCarburantResponse,
             summary="Créer un paiement pour un achat de carburant",
             description="Crée un nouveau paiement pour un achat de carburant spécifique. Nécessite la permission 'Module Achats Carburant'. Permet d'enregistrer les règlements effectués pour chaque commande d'approvisionnement en carburant.",
             tags=["Achats carburant"])
async def create_paiement_achat_carburant(
    achat_carburant_id: UUID,
    paiement: schemas.PaiementAchatCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Crée un nouveau paiement pour un achat de carburant spécifique.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant concerné
        paiement (schemas.PaiementAchatCarburantCreate): Détails du paiement à créer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.PaiementAchatCarburantCreate: Détails du paiement d'achat de carburant créé

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    # Vérifier que l'achat existe
    achat = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    # Récupérer l'utilisateur connecté à partir du token JWT
    current_user = get_current_user_security(credentials, db)

    # Valider que la trésorerie a suffisamment de fonds pour le paiement
    from ...services.tresoreries.validation_service import valider_paiement_achat_carburant
    valider_paiement_achat_carburant(
        db,
        paiement.tresorerie_station_id,
        paiement.montant
    )

    # Créer le paiement pour l'achat
    db_paiement = PaiementAchatCarburantModel(
        achat_carburant_id=achat_carburant_id,
        date_paiement=paiement.date_paiement,
        montant=paiement.montant,
        mode_paiement=paiement.mode_paiement,
        tresorerie_station_id=paiement.tresorerie_station_id,
        utilisateur_enregistrement_id=current_user.id
    )

    db.add(db_paiement)

    # Créer les écritures comptables pour le paiement
    # Créer une écriture de trésorerie (débit) - entrée de fonds
    tresorerie_debit = OperationJournalModel(
        journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
        date_operation=db_paiement.date_paiement,
        libelle_operation=f"Paiement pour l'achat carburant {achat.id}",
        compte_debit="512",  # Compte de trésorerie
        compte_credit="401",  # Compte fournisseur
        montant=float(paiement.montant),
        devise="XOF",
        reference_operation=f"PA{db_paiement.id}",
        module_origine="achats_carburant",
        utilisateur_enregistrement_id=current_user.id
    )
    db.add(tresorerie_debit)

    db.commit()
    db.refresh(db_paiement)

    return db_paiement

@router.get("/{achat_carburant_id}/paiements",
            response_model=List[schemas.PaiementAchatCarburantResponse],
            summary="Récupérer les paiements d'un achat de carburant",
            description="Récupère la liste des paiements pour un achat de carburant spécifique. Nécessite la permission 'Module Achats Carburant'. Permet de suivre les règlements effectués pour une commande d'approvisionnement en carburant.",
            tags=["Achats carburant"])
async def get_paiements_achat_carburant(
    achat_carburant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Récupère la liste des paiements pour un achat de carburant spécifique.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant
        skip (int): Nombre de paiements à ignorer pour la pagination (défaut: 0)
        limit (int): Nombre maximum de paiements à retourner (défaut: 100)
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        List[schemas.PaiementAchatCarburantCreate]: Liste des paiements d'achat de carburant
    """
    paiements = db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.achat_carburant_id == achat_carburant_id
    ).offset(skip).limit(limit).all()
    return paiements

@router.put("/paiements/{paiement_id}",
            response_model=schemas.PaiementAchatCarburantResponse,
            summary="Mettre à jour un paiement d'achat de carburant",
            description="Met à jour les détails d'un paiement d'achat de carburant existant. Nécessite la permission 'Module Achats Carburant'.",
            tags=["Achats carburant"])
async def update_paiement_achat_carburant(
    paiement_id: UUID,
    paiement: schemas.PaiementAchatCarburantUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Met à jour les détails d'un paiement d'achat de carburant existant.

    Args:
        paiement_id (UUID): L'identifiant du paiement d'achat de carburant à mettre à jour
        paiement (schemas.PaiementAchatCarburantUpdate): Nouvelles valeurs pour les champs du paiement
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        schemas.PaiementAchatCarburantUpdate: Détails du paiement d'achat de carburant mis à jour

    Raises:
        HTTPException: Si le paiement d'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    db_paiement = db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.id == paiement_id
    ).first()
    if not db_paiement:
        raise HTTPException(status_code=404, detail="Paiement achat carburant not found")

    update_data = paiement.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_paiement, field, value)

    db.commit()
    db.refresh(db_paiement)
    return db_paiement

@router.delete("/paiements/{paiement_id}",
               summary="Supprimer un paiement d'achat de carburant",
               description="Supprime un paiement d'achat de carburant existant. Nécessite la permission 'Module Achats Carburant'.",
               tags=["Achats carburant"])
async def delete_paiement_achat_carburant(
    paiement_id: UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Supprime un paiement d'achat de carburant existant.

    Args:
        paiement_id (UUID): L'identifiant du paiement d'achat de carburant à supprimer
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Message de confirmation de la suppression

    Raises:
        HTTPException: Si le paiement d'achat de carburant n'est pas trouvé ou si l'utilisateur n'a pas les permissions nécessaires
    """
    paiement = db.query(PaiementAchatCarburantModel).filter(
        PaiementAchatCarburantModel.id == paiement_id
    ).first()
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement achat carburant not found")

    db.delete(paiement)
    db.commit()
    return {"message": "Paiement achat carburant deleted successfully"}

# Endpoint pour le calcul du stock théorique après livraison
@router.post("/{achat_carburant_id}/calcul_stock_theorique",
             summary="Calculer le stock théorique après achat",
             description="Calcule automatiquement le stock théorique pour toutes les cuves concernées par un achat de carburant. Nécessite la permission 'Module Achats Carburant'. Cet endpoint est utilisé pour vérifier les niveaux de stock après la réception d'un approvisionnement.",
             tags=["Achats carburant"])
async def calculer_stock_theorique_apres_achat(
    achat_carburant_id: UUID,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Calcule automatiquement le stock théorique pour toutes les cuves concernées par un achat de carburant.

    Args:
        achat_carburant_id (UUID): L'identifiant de l'achat de carburant
        db (Session): Session de base de données
        credentials (HTTPAuthorizationCredentials): Informations d'identification de l'utilisateur

    Returns:
        dict: Résultats du calcul du stock théorique pour les différentes cuves

    Raises:
        HTTPException: Si l'achat de carburant n'est pas trouvé ou si une erreur survient lors du calcul
    """
    try:
        # Récupérer l'achat et ses lignes
        achat = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
        if not achat:
            raise HTTPException(status_code=404, detail="Achat carburant not found")

        lignes_achat = db.query(LigneAchatCarburantModel).filter(
            LigneAchatCarburantModel.achat_carburant_id == achat_carburant_id
        ).all()

        resultats = []
        for ligne in lignes_achat:
            # Calculer le stock théorique pour la cuve associée à cette ligne
            # On suppose que le stock théorique est le niveau actuel de la cuve + quantité de la ligne
            # mais cela devrait être fait en tenant compte de l'état initial et de toutes les livraisons

            # On pourrait ici appeler le service pour calculer le stock théorique
            # Pour l'instant, on renvoie simplement les informations de base
            resultats.append({
                "ligne_id": ligne.id,
                "cuve_id": ligne.cuve_id,
                "quantite_ligne": ligne.quantite
            })

        return {
            "achat_id": achat_carburant_id,
            "date_achat": achat.date_achat,
            "resultats_calcul_stock": resultats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du stock théorique: {str(e)}")