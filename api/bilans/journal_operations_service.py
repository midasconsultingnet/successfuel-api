from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .journal_operations_schemas import JournalOperationItem, JournalOperationsResponse
from fastapi import HTTPException


def get_journal_operations(
    db: Session,
    date_debut: str,
    date_fin: str,
    station_id: str = None,
    type_operation: str = None
) -> JournalOperationsResponse:
    """
    Générer le journal des opérations entre deux dates
    """
    from uuid import UUID
    try:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")

        station_uuid = UUID(station_id) if station_id else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date ou d'ID invalide")

    items: List[JournalOperationItem] = []
    total_montant = 0.0

    # 1. Récupérer les ventes
    from ..models.vente import Vente
    ventes_query = db.query(Vente).filter(
        Vente.date >= date_debut_obj,
        Vente.date <= date_fin_obj
    )

    if station_uuid:
        ventes_query = ventes_query.filter(Vente.station_id == station_uuid)

    ventes = ventes_query.all()

    for vente in ventes:
        montant = float(vente.montant_total or 0)
        item = JournalOperationItem(
            id=vente.id,
            type_operation="vente",
            date_operation=vente.date,
            montant=montant,
            devise="XOF",  # Valeur par défaut car le champ n'existe pas dans le modèle
            description=f"Vente #{vente.numero_piece_comptable or vente.id}",
            station_id=vente.station_id,
            reference=str(vente.id),
            module_origine="ventes",
            details={
                "numero_piece_comptable": vente.numero_piece_comptable,
                "client": vente.client.nom if vente.client else "N/A"
            }
        )
        items.append(item)
        total_montant += montant

    # 2. Récupérer les achats
    from ..models.achat import Achat
    achats_query = db.query(Achat).filter(
        Achat.date >= date_debut_obj,
        Achat.date <= date_fin_obj
    )

    if station_uuid:
        achats_query = achats_query.filter(Achat.station_id == station_uuid)

    achats = achats_query.all()

    for achat in achats:
        montant = float(achat.montant_total or 0)
        item = JournalOperationItem(
            id=achat.id,
            type_operation="achat",
            date_operation=achat.date,
            montant=montant,
            devise="XOF",  # Valeur par défaut car le champ n'existe pas dans le modèle
            description=f"Achat #{achat.numero_piece_comptable or achat.id}",
            station_id=achat.station_id,
            reference=str(achat.id),
            module_origine="achats",
            details={
                "numero_piece_comptable": achat.numero_piece_comptable,
                "fournisseur": achat.fournisseur.nom if achat.fournisseur else "N/A"
            }
        )
        items.append(item)
        total_montant += montant

    # 3. Récupérer les charges
    from ..models.charge import Charge
    charges_query = db.query(Charge).filter(
        Charge.date >= date_debut_obj,
        Charge.date <= date_fin_obj
    )

    if station_uuid:
        charges_query = charges_query.filter(Charge.station_id == station_uuid)

    charges = charges_query.all()

    for charge in charges:
        montant = float(charge.montant or 0)
        item = JournalOperationItem(
            id=charge.id,
            type_operation="charge",
            date_operation=charge.date,
            montant=montant,
            devise="XOF",  # Valeur par défaut car le champ n'existe pas dans le modèle
            description=f"Charge: {charge.description}",
            station_id=charge.station_id,
            reference=str(charge.id),
            module_origine="charges",
            details={
                "categorie": charge.categorie,
                "fournisseur": charge.fournisseur if charge.fournisseur else "N/A"
            }
        )
        items.append(item)
        total_montant += montant

    # 4. Récupérer les salaires
    from ..models.salaire import Salaire
    salaires_query = db.query(Salaire).filter(
        Salaire.date_paiement >= date_debut_obj,
        Salaire.date_paiement <= date_fin_obj
    )

    if station_uuid:
        salaires_query = salaires_query.filter(Salaire.station_id == station_uuid)

    salaires = salaires_query.all()

    for salaire in salaires:
        montant = float(salaire.montant_total or 0)
        item = JournalOperationItem(
            id=salaire.id,
            type_operation="salaire",
            date_operation=salaire.date_paiement,
            montant=montant,
            devise="XOF",  # Valeur par défaut car le champ n'existe pas dans le modèle
            description=f"Salaire: {salaire.employe.nom if salaire.employe else 'N/A'}",
            station_id=salaire.station_id,
            reference=str(salaire.id),
            module_origine="salaires",
            details={
                "employe": salaire.employe.nom if salaire.employe else "N/A",
                "periode": f"{salaire.mois}/{salaire.annee}"
            }
        )
        items.append(item)
        total_montant += montant

    # 5. Récupérer les mouvements de trésorerie
    from ..models.tresorerie import MouvementTresorerie, TresorerieStation
    mouvements_query = db.query(MouvementTresorerie).join(
        TresorerieStation,
        MouvementTresorerie.tresorerie_station_id == TresorerieStation.id
    ).filter(
        MouvementTresorerie.date_mouvement >= date_debut_obj,
        MouvementTresorerie.date_mouvement <= date_fin_obj
    )

    if station_uuid:
        mouvements_query = mouvements_query.filter(TresorerieStation.station_id == station_uuid)

    mouvements = mouvements_query.all()

    for mouvement in mouvements:
        montant = float(mouvement.montant or 0)
        item = JournalOperationItem(
            id=mouvement.id,
            type_operation=f"mouvement_trésorerie_{mouvement.type_mouvement}",
            date_operation=mouvement.date_mouvement,
            montant=montant,
            devise="XOF",  # Valeur par défaut car le champ n'existe pas dans le modèle
            description=f"Mouvement trésorerie: {mouvement.description}",
            station_id=mouvement.tresorerie_station.station_id if mouvement.tresorerie_station else None,
            reference=str(mouvement.id),
            module_origine="trésorerie",
            details={
                "type_mouvement": mouvement.type_mouvement,
                "trésorerie": mouvement.tresorerie_station.trésorerie.nom if mouvement.tresorerie_station and mouvement.tresorerie_station.trésorerie else "N/A"
            }
        )
        items.append(item)
        total_montant += montant

    # Filtrer par type d'opération si spécifié
    if type_operation:
        items = [item for item in items if type_operation.lower() in item.type_operation.lower()]

    # Trier par date d'opération
    items.sort(key=lambda x: x.date_operation)

    response = JournalOperationsResponse(
        date_debut=date_debut_obj,
        date_fin=date_fin_obj,
        station_id=station_uuid,
        type_operation=type_operation,
        items=items,
        total_items=len(items),
        total_montant=total_montant
    )

    return response