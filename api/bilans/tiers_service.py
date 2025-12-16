from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
from ..models.tiers import Tiers, SoldeTiers, MouvementTiers
from fastapi import HTTPException


def get_bilan_tiers_etendu(
    db: Session,
    current_user,
    date: str,
    type_tiers: Optional[str] = None,
    tri: Optional[str] = "nom",  # "nom", "solde", "date"
    station_id: Optional[str] = None
) -> Dict:
    """
    Générer un bilan des tiers étendu avec plus d'options de filtrage
    """
    from datetime import datetime
    import uuid
    
    # Conversion de la date
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide, utiliser YYYY-MM-DD")

    # Construction de la requête pour récupérer les tiers
    query = db.query(Tiers).filter(
        Tiers.compagnie_id == current_user.compagnie_id
    )

    # Appliquer le filtre par type de tiers si spécifié
    if type_tiers:
        query = query.filter(Tiers.type == type_tiers)

    # Appliquer le filtre par statut (exclure les supprimés)
    query = query.filter(Tiers.statut != "supprimé")

    tiers_list = query.all()

    details = []
    total_solde = 0

    for tier in tiers_list:
        # Vérifier les associations de station
        if station_id:
            try:
                station_uuid = uuid.UUID(station_id)
                # Convertir station_ids qui est stocké en JSONB en liste
                tier_station_ids = tier.station_ids if tier.station_ids else []
                if str(station_uuid) not in [str(id) for id in tier_station_ids]:
                    continue  # Ce tiers n'est pas associé à la station demandée
            except ValueError:
                raise HTTPException(status_code=400, detail="ID de station invalide")

        # Calcul du solde du tiers
        # Récupérer le solde initial
        solde_initial = db.query(SoldeTiers).filter(
            SoldeTiers.tiers_id == tier.id
        ).first()

        solde_actuel = float(solde_initial.montant_actuel if solde_initial else 0)

        # Récupérer les mouvements depuis la date spécifiée
        mouvements = db.query(MouvementTiers).filter(
            MouvementTiers.tiers_id == tier.id,
            MouvementTiers.date_mouvement <= date_obj
        ).all()

        # Ajouter les mouvements pour calculer le solde à la date donnée
        for mvt in mouvements:
            if mvt.type_mouvement == "crédit":
                solde_actuel += float(mvt.montant)
            elif mvt.type_mouvement == "débit":
                solde_actuel -= float(mvt.montant)

        details.append({
            "tiers_id": str(tier.id),
            "nom": tier.nom,
            "type": tier.type,
            "email": tier.email,
            "telephone": tier.telephone,
            "adresse": tier.adresse,
            "statut": tier.statut,
            "solde": solde_actuel,
            "donnees_personnelles": tier.donnees_personnelles,
            "station_ids": tier.station_ids,
            "metadonnees": tier.metadonnees,
            "mouvements": [
                {
                    "id": str(mvt.id),
                    "type": mvt.type_mouvement,
                    "montant": float(mvt.montant),
                    "date": mvt.date_mouvement.isoformat(),
                    "description": mvt.description,
                    "module_origine": mvt.module_origine,
                    "reference_origine": mvt.reference_origine
                }
                for mvt in mouvements
            ]
        })

        total_solde += solde_actuel

    # Trier les détails selon le paramètre de tri
    if tri == "nom":
        details.sort(key=lambda x: x["nom"])
    elif tri == "solde":
        details.sort(key=lambda x: x["solde"], reverse=True)
    elif tri == "date":
        # Trier par date du dernier mouvement
        details.sort(key=lambda x: max([mvt["date"] for mvt in x["mouvements"]] or [date]), reverse=True)

    result = {
        "date": date,
        "type_tiers": type_tiers or "all",
        "tri": tri,
        "station_id": station_id,
        "details": details,
        "total_tiers": len(details),
        "solde_total": total_solde,
        "message": "Bilan des tiers calculé à partir des données de tiers et mouvements"
    }

    return result