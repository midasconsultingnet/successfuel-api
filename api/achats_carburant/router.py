import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import AchatCarburant as AchatCarburantModel, LigneAchatCarburant as LigneAchatCarburantModel, CompensationFinanciere as CompensationFinanciereModel, AvoirCompensation as AvoirCompensationModel, PrixCarburant, OperationJournal as OperationJournalModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..rbac_decorators import require_permission
from ..services.achats_carburant.stock_calculation_service import StockCalculationService

router = APIRouter()
security = HTTPBearer()

# Endpoints pour les achats de carburant
@router.get("/", response_model=List[schemas.AchatCarburantCreate], dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def get_achats_carburant(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    achats_carburant = db.query(AchatCarburantModel).offset(skip).limit(limit).all()
    return achats_carburant

@router.post("/", response_model=schemas.AchatCarburantCreate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def create_achat_carburant(
    achat_carburant: schemas.AchatCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Créer l'enregistrement d'achat de carburant
    db_achat_carburant = AchatCarburantModel(
        fournisseur_id=achat_carburant.fournisseur_id,
        date_achat=achat_carburant.date_achat,
        numero_bl=achat_carburant.numero_bl,
        numero_facture=achat_carburant.numero_facture,
        montant_total=achat_carburant.montant_total,
        station_id=achat_carburant.station_id,
        utilisateur_id=achat_carburant.utilisateur_id
    )

    db.add(db_achat_carburant)
    db.commit()
    db.refresh(db_achat_carburant)

    # Si l'achat est créé directement avec le statut "validé" ou "facturé", créer les écritures comptables
    if hasattr(achat_carburant, 'statut') and achat_carburant.statut in ["validé", "facturé"]:
        # Récupérer les détails de l'achat pour créer les écritures comptables
        # Pour l'instant, on n'a pas de lignes d'achat car elles sont créées séparément,
        # donc on crée une écriture pour le montant total
        # Créer une écriture de stock (débit) - augmentation du stock
        stock_debit = OperationJournalModel(
            journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
            date_operation=db_achat_carburant.date_achat,
            libelle_operation=f"Entrée de stock pour l'achat carburant {db_achat_carburant.numero_bl or db_achat_carburant.id}",
            compte_debit="375",  # Compte de stock de carburant
            compte_credit="607",  # Compte d'achat de carburant
            montant=float(db_achat_carburant.montant_total),
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
            libelle_operation=f"Dette fournisseur pour l'achat carburant {db_achat_carburant.numero_bl or db_achat_carburant.id}",
            compte_debit="607",  # Compte d'achat de carburant
            compte_credit="401",  # Compte fournisseur
            montant=float(db_achat_carburant.montant_total),
            devise="XOF",
            reference_operation=f"AC{db_achat_carburant.id}",
            module_origine="achats_carburant",
            utilisateur_enregistrement_id=db_achat_carburant.utilisateur_id
        )
        db.add(fournisseur_credit)

        db.commit()

    return db_achat_carburant

@router.get("/{achat_carburant_id}", response_model=schemas.AchatCarburantCreate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def get_achat_carburant_by_id(
    achat_carburant_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    achat_carburant = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat_carburant:
        raise HTTPException(status_code=404, detail="Achat carburant not found")
    return achat_carburant

@router.put("/{achat_carburant_id}", response_model=schemas.AchatCarburantUpdate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def update_achat_carburant(
    achat_carburant_id: int,
    achat_carburant: schemas.AchatCarburantUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
            LigneAchatCarburantModel.achat_carburant_id == str(achat_carburant_id)
        ).all()

        # Créer les écritures comptables pour chaque ligne d'achat
        for ligne in lignes_achat:
            # Créer une écriture de stock (débit) - augmentation du stock
            stock_debit = OperationJournalModel(
                journal_operations_id=uuid.uuid4(),  # Remplacez par l'ID réel du journal des opérations
                date_operation=db_achat_carburant.date_achat,
                libelle_operation=f"Entrée de stock pour l'achat carburant {db_achat_carburant.numero_bl or db_achat_carburant.id}",
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
                libelle_operation=f"Dette fournisseur pour l'achat carburant {db_achat_carburant.numero_bl or db_achat_carburant.id}",
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

@router.delete("/{achat_carburant_id}", dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def delete_achat_carburant(
    achat_carburant_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    achat_carburant = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == achat_carburant_id).first()
    if not achat_carburant:
        raise HTTPException(status_code=404, detail="Achat carburant not found")

    db.delete(achat_carburant)
    db.commit()
    return {"message": "Achat carburant deleted successfully"}

# Endpoints pour les lignes d'achat de carburant
@router.get("/{achat_carburant_id}/lignes", response_model=List[schemas.LigneAchatCarburantCreate], dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def get_lignes_achat_carburant(
    achat_carburant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    lignes = db.query(LigneAchatCarburantModel).filter(LigneAchatCarburantModel.achat_carburant_id == achat_carburant_id).offset(skip).limit(limit).all()
    return lignes

@router.post("/{achat_carburant_id}/lignes", response_model=schemas.LigneAchatCarburantCreate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def create_ligne_achat_carburant(
    achat_carburant_id: int,
    ligne: schemas.LigneAchatCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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
        cuve_id=ligne.cuve_id
    )

    db.add(db_ligne)

    # Mettre à jour le prix d'achat dans la table prix_carburant selon le CUMP
    # Récupérer les informations de la cuve pour déterminer la station et le niveau actuel
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT c.station_id, c.niveau_actuel
        FROM cuve c
        WHERE c.id = :cuve_id
    """), {"cuve_id": ligne.cuve_id})
    cuve_data = result.fetchone()

    if cuve_data:
        # Vérifier si un prix existe déjà pour ce couple carburant/station
        prix_existing = db.query(PrixCarburant).filter(
            PrixCarburant.carburant_id == ligne.carburant_id,
            PrixCarburant.station_id == cuve_data.station_id
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
                station_id=cuve_data.station_id,
                prix_achat=ligne.prix_unitaire
            )
            db.add(prix_carburant)

    db.commit()
    db.refresh(db_ligne)

    return db_ligne

# Endpoints pour les compensations financières
@router.post("/compensations", response_model=schemas.CompensationFinanciereCreate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def create_compensation_financiere(
    compensation: schemas.CompensationFinanciereCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Vérifier que l'achat existe
    achat = db.query(AchatCarburantModel).filter(AchatCarburantModel.id == int(compensation.achat_carburant_id)).first()
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
                libelle_operation=f"Avoir reçu du fournisseur pour l'achat carburant {achat.numero_bl or achat.id}",
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
                libelle_operation=f"Avoir dû au fournisseur pour l'achat carburant {achat.numero_bl or achat.id}",
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
@router.post("/avoirs_compensation", response_model=schemas.AvoirCompensationCreate, dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def create_avoir_compensation(
    avoir: schemas.AvoirCompensationCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Récupérer la compensation pour vérifier les détails
    compensation = db.query(CompensationFinanciereModel).filter(CompensationFinanciereModel.id == int(avoir.compensation_financiere_id)).first()
    if not compensation:
        raise HTTPException(status_code=404, detail="Compensation financière not found")

    # Créer l'avoir de compensation
    db_avoir = AvoirCompensationModel(
        compensation_financiere_id=avoir.compensation_financiere_id,
        tiers_id=avoir.tiers_id,
        montant=avoir.montant,
        date_emission=db.query(AchatCarburantModel).filter(AchatCarburantModel.id == compensation.achat_carburant_id).first().date_achat,
        utilisateur_emission_id=avoir.utilisateur_emission_id
    )

    db.add(db_avoir)
    db.commit()
    db.refresh(db_avoir)

    return db_avoir

# Endpoint pour le calcul du stock théorique après livraison
@router.post("/{achat_carburant_id}/calcul_stock_theorique", dependencies=[Depends(require_permission("Module Achats Carburant"))])
async def calculer_stock_theorique_apres_achat(
    achat_carburant_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Calcule automatiquement le stock théorique pour toutes les cuves concernées par cet achat
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