from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
from ..models.tresorerie import TresorerieStation, MouvementTresorerie
from ..models.compagnie import Station
from fastapi import HTTPException


def get_bilan_tresorerie_etendu(
    db: Session,
    current_user,
    date_debut: str,
    date_fin: str,
    station_id: Optional[str] = None,
    type_tresorerie: Optional[str] = None,
    tri: Optional[str] = "date"  # "date", "nom", "solde"
) -> Dict:
    """
    Générer un bilan de trésorerie étendu avec plus d'options de filtrage
    """
    from datetime import datetime
    from sqlalchemy import and_
    import uuid

    # Conversion des dates
    try:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide, utiliser YYYY-MM-DD")

    # Construction de la requête pour récupérer les trésoreries
    query = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    )

    # Appliquer le filtre par station si spécifié
    if station_id:
        try:
            station_uuid = uuid.UUID(station_id)
            query = query.filter(Station.id == station_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de station invalide")

    # Import nécessaire pour le filtre par type de trésorerie
    from ..models.tresorerie import Tresorerie

    # Appliquer le filtre par type de trésorerie si spécifié
    if type_tresorerie:
        query = query.join(
            Tresorerie,
            TresorerieStation.trésorerie_id == Tresorerie.id
        ).filter(
            Tresorerie.type == type_tresorerie
        )

    trésoreries_station = query.all()

    # Calcul des totaux pour chaque trésorerie
    total_solde_initial = 0
    total_solde_final = 0
    total_entrees = 0
    total_sorties = 0

    details = []

    for trésorerie in trésoreries_station:
        # Solde initial
        solde_initial = float(trésorerie.solde_initial or 0)

        # Récupération des mouvements dans la période
        mouvements = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.trésorerie_station_id == trésorerie.id,
            MouvementTresorerie.date_mouvement >= date_debut_obj,
            MouvementTresorerie.date_mouvement <= date_fin_obj,
            MouvementTresorerie.statut == "validé"
        ).order_by(MouvementTresorerie.date_mouvement if tri == "date" else MouvementTresorerie.montant).all()

        total_entrees_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "entrée")
        total_sorties_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "sortie")

        # Calcul du solde final
        solde_final = solde_initial + total_entrees_per - total_sorties_per

        details.append({
            "trésorerie_id": str(trésorerie.id),
            "nom": trésorerie.trésorerie.nom if trésorerie.trésorerie else "N/A",
            "type": trésorerie.trésorerie.type if trésorerie.trésorerie else "N/A",
            "station": str(trésorerie.station_id),
            "station_nom": trésorerie.station.nom if trésorerie.station else "N/A",
            "solde_initial": solde_initial,
            "solde_final": solde_final,
            "total_entrees": total_entrees_per,
            "total_sorties": total_sorties_per,
            "mouvements": [
                {
                    "id": str(mvt.id),
                    "type": mvt.type_mouvement,
                    "montant": float(mvt.montant),
                    "date": mvt.date_mouvement.isoformat(),
                    "description": mvt.description,
                    "module_origine": mvt.module_origine
                }
                for mvt in mouvements
            ]
        })

        # Ajout aux totaux généraux
        total_solde_initial += solde_initial
        total_solde_final += solde_final
        total_entrees += total_entrees_per
        total_sorties += total_sorties_per

    # Trier les détails selon le paramètre de tri
    if tri == "nom":
        details.sort(key=lambda x: x["nom"])
    elif tri == "solde":
        details.sort(key=lambda x: x["solde_final"], reverse=True)

    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "station_id": station_id,
        "type_tresorerie": type_tresorerie,
        "tri": tri,
        "solde_initial": total_solde_initial,
        "solde_final": total_solde_final,
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "details": details,
        "message": "Bilan de trésorerie calculé à partir des données de trésorerie"
    }