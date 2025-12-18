from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from ..models import Station
from ..models.tresorerie import TresorerieStation, MouvementTresorerie
from ..models.immobilisation import Immobilisation
from ..models.stock import StockProduit
from ..models.tiers import SoldeTiers
from fastapi import HTTPException


def get_bilan_global(
    db: Session,
    current_user,
    date_debut: str,
    date_fin: str,
    station_id: str = None
) -> Dict:
    """
    Générer un bilan global consolidé pour une période
    """
    from datetime import datetime
    import uuid
    
    try:
        date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide, utiliser YYYY-MM-DD")

    # Initialiser les totaux
    total_tresorerie = 0
    total_immobilisations = 0
    total_stocks_carburant = 0
    total_stocks_boutique = 0
    total_dettes = 0
    total_creances = 0
    total_ventes = 0
    total_achats = 0
    resultat = 0

    # Récupérer les stations de l'utilisateur
    stations_query = db.query(Station).filter(
        Station.compagnie_id == current_user.compagnie_id
    )
    
    if station_id:
        try:
            station_uuid = uuid.UUID(station_id)
            stations_query = stations_query.filter(Station.id == station_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de station invalide")
    
    stations = stations_query.all()

    # Calculer les totaux pour chaque station
    for station in stations:
        # 1. Calculer la trésorerie
        trésoreries_station = db.query(TresorerieStation).filter(
            TresorerieStation.station_id == station.id
        ).all()

        for trésorerie in trésoreries_station:
            # Solde initial
            solde_initial = float(trésorerie.solde_initial or 0)

            # Récupération des mouvements dans la période
            mouvements = db.query(MouvementTresorerie).filter(
                MouvementTresorerie.trésorerie_station_id == trésorerie.id,
                MouvementTresorerie.date_mouvement >= date_debut_obj,
                MouvementTresorerie.date_mouvement <= date_fin_obj,
                MouvementTresorerie.statut == "validé"
            ).all()

            total_entrees_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "entrée")
            total_sorties_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "sortie")

            # Calcul du solde final
            solde_final = solde_initial + total_entrees_per - total_sorties_per
            total_tresorerie += solde_final

        # 2. Calculer les immobilisations
        immobilisations = db.query(Immobilisation).filter(
            Immobilisation.station_id == station.id
        ).all()

        for immobilisation in immobilisations:
            total_immobilisations += float(immobilisation.valeur_nette or immobilisation.valeur_origine or 0)

        # 3. Calculer les stocks de carburant
        from ..models.compagnie import Cuve, EtatInitialCuve
        from ..models.carburant import Carburant
        
        cuves = db.query(Cuve).filter(Cuve.station_id == station.id).all()
        
        for cuve in cuves:
            etat_initial = db.query(EtatInitialCuve).filter(
                EtatInitialCuve.cuve_id == cuve.id
            ).first()
            
            if etat_initial:
                # On calcule en se basant sur le volume initial et le prix du carburant
                volume_initial = float(etat_initial.volume_initial_calcule or 0)

                # Récupérer le prix du carburant pour la station spécifique
                from ..models.prix_carburant import PrixCarburant
                prix_carburant = db.query(PrixCarburant).filter(
                    PrixCarburant.carburant_id == cuve.carburant_id,
                    PrixCarburant.station_id == cuve.station_id
                ).first()

                # Utiliser le prix de vente s'il existe, sinon le prix d'achat
                prix_unitaire = float(prix_carburant.prix_vente or prix_carburant.prix_achat or 0) if prix_carburant else 0
                valeur_stock = volume_initial * prix_unitaire
                total_stocks_carburant += valeur_stock

        # 4. Calculer les stocks de boutique
        stocks_boutique = db.query(StockProduit).filter(
            StockProduit.station_id == station.id
        ).all()

        for stock in stocks_boutique:
            from ..models.produit import Produit
            produit = db.query(Produit).filter(Produit.id == stock.produit_id).first()
            if produit and produit.type != "service":  # Ne pas inclure les services
                valeur_stock = float(stock.quantite_theorique or 0) * float(produit.prix_vente or 0)
                total_stocks_boutique += valeur_stock

        # 5. Calculer les dettes et créances
        soldes_tiers = db.query(SoldeTiers).filter(
            SoldeTiers.station_id == station.id
        ).all()

        for solde_tiers in soldes_tiers:
            montant = float(solde_tiers.montant_actuel)
            if montant < 0:
                total_dettes += abs(montant)  # Les dettes sont des montants négatifs
            else:
                total_creances += montant  # Les créances sont des montants positifs

    # Calcul des ventes et achats pour le résultat
    # On va récupérer les ventes et achats pour la période
    from ..models.vente import Vente
    from ..models.achat import Achat
    
    ventes_query = db.query(Vente).join(Station, Vente.station_id == Station.id).filter(
        Station.compagnie_id == current_user.compagnie_id,
        Vente.date >= date_debut_obj,
        Vente.date <= date_fin_obj
    )

    achats_query = db.query(Achat).join(Station, Achat.station_id == Station.id).filter(
        Station.compagnie_id == current_user.compagnie_id,
        Achat.date >= date_debut_obj,
        Achat.date <= date_fin_obj
    )
    
    if station_id:
        ventes_query = ventes_query.filter(Vente.station_id == station_uuid)
        achats_query = achats_query.filter(Achat.station_id == station_uuid)
    
    ventes = ventes_query.all()
    achats = achats_query.all()
    
    total_ventes = sum(float(vente.montant_total or 0) for vente in ventes)
    total_achats = sum(float(achat.montant_total or 0) for achat in achats)
    
    resultat = total_ventes - total_achats

    # Retourner le bilan consolidé
    bilan_consolidé = {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "station_id": station_id,
        "actif": {
            "tresorerie": total_tresorerie,
            "immobilisations": total_immobilisations,
            "stocks_carburant": total_stocks_carburant,
            "stocks_boutique": total_stocks_boutique,
            "creances": total_creances
        },
        "passif": {
            "dettes": total_dettes
        },
        "resultat_period": {
            "total_ventes": total_ventes,
            "total_achats": total_achats,
            "resultat": resultat
        },
        "total_actif": total_tresorerie + total_immobilisations + total_stocks_carburant + total_stocks_boutique + total_creances,
        "total_passif": total_dettes,
        "bilan_solde": (total_tresorerie + total_immobilisations + total_stocks_carburant + total_stocks_boutique + total_creances) - total_dettes + resultat
    }

    return bilan_consolidé