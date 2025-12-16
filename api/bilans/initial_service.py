from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date
from uuid import UUID
from ..models import Station
from ..models.tresorerie import EtatInitialTresorerie
from ..models.compagnie import EtatInitialCuve
from ..models.tiers import SoldeTiers
from ..models.immobilisation import Immobilisation
from ..models.stock import StockProduit
from .initial_schemas import BilanInitialItem, BilanInitialResponse, BilanInitialCreate, BilanInitialUpdate, BilanInitialDBResponse
from fastapi import HTTPException


def create_bilan_initial_depart(
    db: Session,
    bilan_data: BilanInitialCreate,
    utilisateur_id: UUID,
    est_deja_valide: bool = False
) -> BilanInitialDBResponse:
    """
    Créer un bilan initial de départ dans la base de données
    """
    from ..models.bilan_initial_depart import BilanInitialDepart

    # Calcul des totaux
    total_actif = bilan_data.actif_immobilise + bilan_data.actif_circulant
    total_passif = bilan_data.capitaux_propres + bilan_data.dettes + bilan_data.provisions

    # Vérifier l'équilibre du bilan
    if abs(total_actif - total_passif) > 0.01:  # Tolérance pour les arrondis
        raise HTTPException(
            status_code=400,
            detail=f"Bilan déséquilibré: Actif ({total_actif}) ≠ Passif ({total_passif})"
        )

    # Créer l'instance de bilan initial
    bilan_initial = BilanInitialDepart(
        compagnie_id=bilan_data.compagnie_id,
        station_id=bilan_data.station_id,
        date_bilan=bilan_data.date_bilan,
        actif_immobilise=bilan_data.actif_immobilise,
        actif_circulant=bilan_data.actif_circulant,
        total_actif=total_actif,
        capitaux_propres=bilan_data.capitaux_propres,
        dettes=bilan_data.dettes,
        provisions=bilan_data.provisions,
        total_passif=total_passif,
        utilisateur_generation_id=utilisateur_id,
        date_generation=datetime.utcnow(),
        est_valide=est_deja_valide
    )

    db.add(bilan_initial)
    db.commit()
    db.refresh(bilan_initial)

    # Convertir en BilanInitialDBResponse
    return BilanInitialDBResponse(
        id=bilan_initial.id,
        compagnie_id=bilan_initial.compagnie_id,
        station_id=bilan_initial.station_id,
        date_bilan=bilan_initial.date_bilan,
        actif_immobilise=bilan_initial.actif_immobilise,
        actif_circulant=bilan_initial.actif_circulant,
        capitaux_propres=bilan_initial.capitaux_propres,
        dettes=bilan_initial.dettes,
        provisions=bilan_initial.provisions,
        total_actif=bilan_initial.total_actif,
        total_passif=bilan_initial.total_passif,
        utilisateur_generation_id=bilan_initial.utilisateur_generation_id,
        date_generation=bilan_initial.date_generation,
        est_valide=bilan_initial.est_valide
    )


def get_bilan_initial_depart_by_station(
    db: Session,
    station_id: UUID
) -> Optional[BilanInitialDBResponse]:
    """
    Récupérer le bilan initial de départ pour une station spécifique
    """
    from ..models.bilan_initial_depart import BilanInitialDepart

    bilan_initial = db.query(BilanInitialDepart).filter(
        BilanInitialDepart.station_id == station_id
    ).first()

    if bilan_initial is None:
        return None

    return BilanInitialDBResponse(
        id=bilan_initial.id,
        compagnie_id=bilan_initial.compagnie_id,
        station_id=bilan_initial.station_id,
        date_bilan=bilan_initial.date_bilan,
        actif_immobilise=bilan_initial.actif_immobilise,
        actif_circulant=bilan_initial.actif_circulant,
        capitaux_propres=bilan_initial.capitaux_propres,
        dettes=bilan_initial.dettes,
        provisions=bilan_initial.provisions,
        total_actif=bilan_initial.total_actif,
        total_passif=bilan_initial.total_passif,
        utilisateur_generation_id=bilan_initial.utilisateur_generation_id,
        date_generation=bilan_initial.date_generation,
        est_valide=bilan_initial.est_valide
    )


def update_bilan_initial_depart(
    db: Session,
    station_id: UUID,
    bilan_data: BilanInitialUpdate,
    current_user
) -> BilanInitialDBResponse:
    """
    Mettre à jour le bilan initial de départ pour une station
    """
    from ..models.bilan_initial_depart import BilanInitialDepart

    bilan_initial = db.query(BilanInitialDepart).filter(
        BilanInitialDepart.station_id == station_id
    ).first()

    if not bilan_initial:
        raise HTTPException(status_code=404, detail="Bilan initial non trouvé pour cette station")

    # Vérifier si le bilan est déjà validé
    if bilan_initial.est_valide:
        raise HTTPException(status_code=400, detail="Impossible de modifier un bilan validé")

    # Vérifier les droits d'accès
    if current_user.compagnie_id != bilan_initial.compagnie_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce bilan")

    # Mettre à jour les champs
    for field, value in bilan_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(bilan_initial, field, value)

    # Recalculer les totaux
    bilan_initial.total_actif = (
        bilan_initial.actif_immobilise +
        bilan_initial.actif_circulant
    )
    bilan_initial.total_passif = (
        bilan_initial.capitaux_propres +
        bilan_initial.dettes +
        bilan_initial.provisions
    )

    # Vérifier l'équilibre
    if abs(bilan_initial.total_actif - bilan_initial.total_passif) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Bilan déséquilibré après mise à jour: Actif ({bilan_initial.total_actif}) ≠ Passif ({bilan_initial.total_passif})"
        )

    bilan_initial.date_generation = datetime.utcnow()

    db.commit()
    db.refresh(bilan_initial)

    return BilanInitialDBResponse(
        id=bilan_initial.id,
        compagnie_id=bilan_initial.compagnie_id,
        station_id=bilan_initial.station_id,
        date_bilan=bilan_initial.date_bilan,
        actif_immobilise=bilan_initial.actif_immobilise,
        actif_circulant=bilan_initial.actif_circulant,
        capitaux_propres=bilan_initial.capitaux_propres,
        dettes=bilan_initial.dettes,
        provisions=bilan_initial.provisions,
        total_actif=bilan_initial.total_actif,
        total_passif=bilan_initial.total_passif,
        utilisateur_generation_id=bilan_initial.utilisateur_generation_id,
        date_generation=bilan_initial.date_generation,
        est_valide=bilan_initial.est_valide
    )


def validate_bilan_initial_depart(
    db: Session,
    station_id: UUID
) -> BilanInitialDBResponse:
    """
    Valider le bilan initial de départ pour une station
    """
    from ..models.bilan_initial_depart import BilanInitialDepart

    bilan_initial = db.query(BilanInitialDepart).filter(
        BilanInitialDepart.station_id == station_id
    ).first()

    if not bilan_initial:
        raise HTTPException(status_code=404, detail="Bilan initial non trouvé pour cette station")

    bilan_initial.est_valide = True
    bilan_initial.date_generation = datetime.utcnow()

    db.commit()
    db.refresh(bilan_initial)

    return BilanInitialDBResponse(
        id=bilan_initial.id,
        compagnie_id=bilan_initial.compagnie_id,
        station_id=bilan_initial.station_id,
        date_bilan=bilan_initial.date_bilan,
        actif_immobilise=bilan_initial.actif_immobilise,
        actif_circulant=bilan_initial.actif_circulant,
        capitaux_propres=bilan_initial.capitaux_propres,
        dettes=bilan_initial.dettes,
        provisions=bilan_initial.provisions,
        total_actif=bilan_initial.total_actif,
        total_passif=bilan_initial.total_passif,
        utilisateur_generation_id=bilan_initial.utilisateur_generation_id,
        date_generation=bilan_initial.date_generation,
        est_valide=bilan_initial.est_valide
    )


def get_actif_immobilise_for_station(db: Session, station_id: UUID) -> float:
    """
    Calculer l'actif immobilisé pour une station
    """
    immobilisations = db.query(Immobilisation).filter(
        Immobilisation.station_id == station_id
    ).all()

    total = 0.0
    for immobilisation in immobilisations:
        valeur = float(immobilisation.valeur_origine or 0)
        total += valeur

    return total


def get_actif_circulant_for_station(db: Session, station_id: UUID) -> tuple[float, int, int]:
    """
    Calculer l'actif circulant pour une station
    Retourne le montant total, le nombre de trésoreries et le nombre de stocks de boutique
    """
    from ..models.tresorerie import TresorerieStation
    from ..models.produit import Produit

    actif_circulant = 0.0
    nombre_trésoreries = 0
    nombre_stocks_boutique = 0

    # Trésoreries
    trésoreries_station = db.query(TresorerieStation).filter(
        TresorerieStation.station_id == station_id
    ).all()

    for trésorerie_station in trésoreries_station:
        # Récupérer l'état initial de trésorerie
        etat_initial = db.query(EtatInitialTresorerie).filter(
            EtatInitialTresorerie.tresorerie_station_id == trésorerie_station.id
        ).first()

        if etat_initial:
            actif_circulant += float(etat_initial.montant)

    nombre_trésoreries = len(trésoreries_station)

    # Stocks de carburant
    from ..models.compagnie import Cuve
    cuves = db.query(Cuve).filter(Cuve.station_id == station_id).all()

    for cuve in cuves:
        etat_initial = db.query(EtatInitialCuve).filter(
            EtatInitialCuve.cuve_id == cuve.id
        ).first()

        if etat_initial:
            # Le volume est valorisé sans prix unitaire pour le moment
            actif_circulant += float(etat_initial.volume_initial_calcule or 0)

    # Stocks de boutique
    stocks_boutique = db.query(StockProduit).filter(
        StockProduit.station_id == station_id
    ).all()

    for stock in stocks_boutique:
        produit = db.query(Produit).filter(Produit.id == stock.produit_id).first()

        if produit and produit.type != "service":  # Ne pas inclure les services
            valeur_stock = float(stock.quantite_theorique or 0) * float(produit.prix_unitaire or 0)
            actif_circulant += valeur_stock

    nombre_stocks_boutique = len([s for s in stocks_boutique if db.query(Produit).filter(Produit.id == s.produit_id).first() and db.query(Produit).filter(Produit.id == s.produit_id).first().type != "service"])

    return actif_circulant, nombre_trésoreries, nombre_stocks_boutique


def get_dettes_for_station(db: Session, station_id: UUID) -> tuple[float, float, int, int]:
    """
    Calculer les dettes et les créances pour une station
    Retourne dettes, capitaux_propres_potentiels, nombre_creances, nombre_dettes
    """
    soldes_tiers = db.query(SoldeTiers).filter(
        SoldeTiers.station_id == station_id
    ).all()

    dettes = 0.0
    capitaux_propres_potentiels = 0.0  # Créances (montants positifs)
    nombre_creances = 0
    nombre_dettes = 0

    for solde_tiers in soldes_tiers:
        montant_initial = float(solde_tiers.montant_initial)
        if montant_initial >= 0:
            # C'est une créance (partie de l'actif circulant) - déjà ajoutée ailleurs
            capitaux_propres_potentiels += montant_initial
            nombre_creances += 1
        else:
            # C'est une dette (partie du passif)
            dettes += abs(montant_initial)  # Utiliser la valeur absolue pour la dette
            nombre_dettes += 1

    return dettes, capitaux_propres_potentiels, nombre_creances, nombre_dettes


def get_nombre_stocks_carburant(db: Session, station_id: UUID) -> int:
    """
    Calculer le nombre de stocks de carburant pour une station
    """
    from ..models.compagnie import Cuve, EtatInitialCuve

    cuves = db.query(Cuve).filter(Cuve.station_id == station_id).all()
    return len([c for c in cuves if db.query(EtatInitialCuve).filter(EtatInitialCuve.cuve_id == c.id).first()])


def get_bilan_initial(db: Session, station_id: str) -> BilanInitialResponse:
    """
    Générer le bilan initial de départ pour une station
    """
    try:
        station_uuid = UUID(station_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de station invalide")

    # Vérifier si la station existe
    station = db.query(Station).filter(Station.id == station_uuid).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station non trouvée")

    # Calculer les différentes parties du bilan
    actif_immobilise = get_actif_immobilise_for_station(db, station_uuid)

    actif_circulant, nombre_trésoreries, nombre_stocks_boutique = get_actif_circulant_for_station(db, station_uuid)

    dettes, capitaux_propres_potentiels, nombre_creances, nombre_dettes = get_dettes_for_station(db, station_uuid)

    # Calculer les totaux
    total_actif = actif_immobilise + actif_circulant
    nombre_stocks_carburant = get_nombre_stocks_carburant(db, station_uuid)

    # Calculer le capital propre et autres éléments du passif
    # Dans un bilan initial, on suppose que le capital propre est connu ou déduit
    # Pour simplifier, nous allons supposer que les capitaux propres sont égaux à la différence
    # entre l'actif et les dettes/provisions, mais dans la pratique comptable,
    # le capital propre est généralement une information connue à l'avance
    provisions = 0.0  # Pour le moment fixées à 0, mais pourraient être récupérées d'une table spécifique
    capitaux_propres = total_actif - (dettes + provisions)

    # Calculer le total passif
    total_passif = capitaux_propres + dettes + provisions

    # Vérifier l'équilibre du bilan
    if abs(total_actif - total_passif) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Bilan initial déséquilibré: Actif ({total_actif}) ≠ Passif ({total_passif})"
        )

    response = BilanInitialResponse(
        date_bilan=datetime.utcnow(),
        station_id=station_uuid,
        actif_immobilise=actif_immobilise,
        actif_circulant=actif_circulant,
        total_actif=total_actif,
        capitaux_propres=capitaux_propres,
        dettes=dettes,
        provisions=provisions,
        total_passif=total_passif,
        details={
            "nombre_trésoreries": nombre_trésoreries,
            "nombre_immobilisations": len(db.query(Immobilisation).filter(Immobilisation.station_id == station_uuid).all()),
            "nombre_stocks_carburant": nombre_stocks_carburant,
            "nombre_stocks_boutique": nombre_stocks_boutique,
            "nombre_dettes_creances": nombre_creances,  # Créances
            "nombre_dettes": nombre_dettes  # Dettes
        }
    )

    return response