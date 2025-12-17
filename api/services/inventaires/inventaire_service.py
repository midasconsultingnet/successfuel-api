from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.inventaire import Inventaire
from ...models.ecart_inventaire import EcartInventaire, ClassificationEcart
from ...inventaires.schemas import InventaireCreate, InventaireUpdate
from ..database_service import DatabaseService
from .ecart_inventaire_service import EcartInventaireService
from ..stock_service import calculer_cout_moyen_pondere, mettre_a_jour_stock_produit
from datetime import datetime, date
import uuid


class InventaireService(DatabaseService):
    def __init__(self, db: Session):
        super().__init__(db, Inventaire)

    def create_inventaire(self, inventaire: InventaireCreate, current_user) -> Inventaire:
        """Crée un nouvel inventaire et détecte automatiquement les écarts significatifs"""

        # Vérifier que l'utilisateur a le droit de créer un inventaire pour cette station
        if inventaire.station_id not in [s.id for s in current_user.stations]:
            raise ValueError("Vous n'avez pas le droit de créer un inventaire pour cette station")

        # Créer l'inventaire
        db_inventaire = Inventaire(
            station_id=inventaire.station_id,
            produit_id=inventaire.produit_id,
            cuve_id=inventaire.cuve_id,
            quantite_reelle=inventaire.quantite_reelle,
            date=inventaire.date,
            statut=inventaire.statut,
            utilisateur_id=inventaire.utilisateur_id,
            commentaires=inventaire.commentaires,
            seuil_tolerance=inventaire.seuil_tolerance,
            methode_mesure=inventaire.methode_mesure,
            compagnie_id=current_user.compagnie_id
        )

        created_inventaire = self.create(db_inventaire)

        # Si c'est un inventaire de produit (boutique), on détecte les écarts
        if created_inventaire.produit_id and created_inventaire.quantite_reelle is not None:
            self._detecter_ecarts_inventaire(created_inventaire, current_user)

        # Si c'est un inventaire de cuve (carburant), on détecte les écarts
        elif created_inventaire.cuve_id and created_inventaire.quantite_reelle is not None:
            self._detecter_ecarts_inventaire_cuve(created_inventaire, current_user)

        return created_inventaire

    def update_inventaire(self, inventaire_id: str, inventaire: InventaireUpdate, current_user) -> Inventaire:
        """Met à jour un inventaire existant"""
        update_data = inventaire.dict(exclude_unset=True)

        # Vérifier que l'utilisateur a le droit de modifier cet inventaire
        existing_inventaire = self.get_by_id(inventaire_id)
        if existing_inventaire.compagnie_id != current_user.compagnie_id:
            raise ValueError("Vous n'avez pas le droit de modifier cet inventaire")

        return self.update(inventaire_id, update_data)

    def _detecter_ecarts_inventaire(self, inventaire: Inventaire, current_user):
        """Détecte automatiquement les écarts dans un inventaire de produit"""
        # Récupérer la quantité théorique depuis le stock actuel
        # Pour l'instant, utiliser une fonction directement sur la base de données
        from ...models import StockProduit
        produit_id = str(inventaire.produit_id) if inventaire.produit_id else None

        if produit_id:
            # Récupérer le stock théorique depuis la table StockProduit
            stock_produit = self.db.query(StockProduit).filter(
                StockProduit.produit_id == produit_id,
                StockProduit.station_id == str(inventaire.station_id)
            ).first()
            stock_theorique = float(stock_produit.quantite_theorique) if stock_produit else 0

            # Calculer l'écart
            ecart = inventaire.quantite_reelle - stock_theorique if stock_theorique is not None else 0

            # Vérifier si l'écart est significatif (en fonction du seuil d'alerte)
            seuil_alerte = self._get_seuil_alerte_produit(produit_id, inventaire.date)

            if abs(ecart) > seuil_alerte:
                # Déterminer la classification de l'écart
                classification = self._classer_ecart(ecart, inventaire.produit_id, inventaire.date)

                # Créer l'écart d'inventaire
                ecart_inventaire_service = EcartInventaireService(self.db)
                ecart_inventaire_service.create_ecart_inventaire({
                    "inventaire_id": str(inventaire.id),
                    "produit_id": produit_id,
                    "station_id": str(inventaire.station_id),
                    "compagnie_id": str(current_user.compagnie_id),
                    "quantite_theorique": float(stock_theorique) if stock_theorique is not None else 0,
                    "quantite_reelle": float(inventaire.quantite_reelle),
                    "ecart": float(ecart),
                    "classification": classification,
                    "seuil_alerte": float(seuil_alerte),
                    "seuil_saison": self._get_seuil_saison(produit_id, inventaire.date),
                    "motif_anomalie": None  # Peut être défini manuellement plus tard
                })

    def _detecter_ecarts_inventaire_cuve(self, inventaire: Inventaire, current_user):
        """Détecte automatiquement les écarts dans un inventaire de cuve"""
        # Récupérer la quantité théorique depuis le stock actuel de la cuve
        from ...models import MouvementStockCuve
        cuve_id = str(inventaire.cuve_id) if inventaire.cuve_id else None

        if cuve_id:
            # Calculer le stock théorique de la cuve à partir des mouvements de stock
            # Pour simplifier, on suppose que le stock est la somme des entrées moins les sorties
            from sqlalchemy import func
            result = self.db.query(
                func.coalesce(func.sum(MouvementStockCuve.quantite), 0)
            ).filter(
                MouvementStockCuve.cuve_id == cuve_id
            ).first()

            stock_theorique = float(result[0]) if result else 0

            # Calculer l'écart
            ecart = inventaire.quantite_reelle - stock_theorique if stock_theorique is not None else 0

            # Vérifier si l'écart est significatif (en fonction du seuil d'alerte)
            seuil_alerte = self._get_seuil_alerte_cuve(cuve_id, inventaire.date)

            if abs(ecart) > seuil_alerte:
                # Déterminer la classification de l'écart
                classification = self._classer_ecart_cuve(ecart, inventaire.cuve_id, inventaire.date)

                # Créer l'écart d'inventaire (lié au produit de la cuve)
                ecart_inventaire_service = EcartInventaireService(self.db)

                # On associe l'écart à un produit, mais pour un inventaire de cuve,
                # on associe l'écart au produit de la cuve
                produit_id = self._get_produit_from_cuve_id(cuve_id)

                if produit_id:
                    ecart_inventaire_service.create_ecart_inventaire({
                        "inventaire_id": str(inventaire.id),
                        "produit_id": produit_id,
                        "station_id": str(inventaire.station_id),
                        "compagnie_id": str(current_user.compagnie_id),
                        "quantite_theorique": float(stock_theorique) if stock_theorique is not None else 0,
                        "quantite_reelle": float(inventaire.quantite_reelle),
                        "ecart": float(ecart),
                        "classification": classification,
                        "seuil_alerte": float(seuil_alerte),
                        "seuil_saison": self._get_seuil_saison(produit_id, inventaire.date),
                        "motif_anomalie": None  # Peut être défini manuellement plus tard
                    })

    def _get_produit_from_cuve_id(self, cuve_id: str):
        """Récupère le produit associé à une cuve"""
        from ...models.cuve import Cuve
        cuve = self.db.query(Cuve).filter(Cuve.id == cuve_id).first()
        if cuve:
            return str(cuve.produit_id) if cuve.produit_id else None
        return None

    def _get_seuil_alerte_produit(self, produit_id: str, date_inventaire: date = None) -> float:
        """Récupère le seuil d'alerte pour un produit spécifique avec gestion saisonnière"""
        # Récupérer le seuil par défaut pour ce type de produit
        from ...models.produit import Produit
        produit = self.db.query(Produit).filter(Produit.id == produit_id).first()

        # Si on a un produit avec une catégorie, on pourrait avoir un seuil par catégorie
        if produit and produit.categorie:
            # Pour l'instant, retourne une valeur par défaut en fonction de la catégorie
            # Cette logique pourrait être améliorée avec une table de configuration
            if produit.categorie == "carburant":
                return 10.0  # seuil plus permissif pour les carburants
            else:
                return 5.0  # seuil par défaut pour les autres produits

        return 5.0  # Seuil par défaut

    def _get_seuil_alerte_cuve(self, cuve_id: str, date_inventaire: date = None) -> float:
        """Récupère le seuil d'alerte pour une cuve avec gestion saisonnière"""
        # Pour l'instant, retourne une valeur par défaut
        # Cette logique pourrait être améliorée avec une table de configuration
        return 10.0  # Seuil par défaut pour les cuves

    def _get_seuil_saison(self, produit_id: str, date_inventaire: date) -> str:
        """Récupère les informations de seuil saisonnier pour un produit à une date donnée"""
        saison = self._determiner_saison(date_inventaire)
        seuil_alerte = self._get_seuil_alerte_produit(produit_id, date_inventaire)

        return f"Saison: {saison}, Seuil: {seuil_alerte}"

    def _determiner_saison(self, date_inventaire: date) -> str:
        """Détermine la saison à partir d'une date"""
        mois = date_inventaire.month

        if mois in [12, 1, 2]:
            return "hiver"
        elif mois in [3, 4, 5]:
            return "printemps"
        elif mois in [6, 7, 8]:
            return "ete"
        else:
            return "automne"

    def _classer_ecart(self, ecart: float, produit_id: str, date_inventaire: date) -> ClassificationEcart:
        """Classe automatiquement un écart pour un produit (boutique)"""
        # Récupérer le seuil d'alerte pour déterminer la gravité de l'écart
        seuil_alerte = self._get_seuil_alerte_produit(produit_id, date_inventaire)

        if ecart < 0:
            # Quantité réelle inférieure à la quantité théorique
            if abs(ecart) <= 1:  # Petits écarts pouvant être dus à des erreurs de mesure
                return ClassificationEcart.ANOMALIE
            elif abs(ecart) <= seuil_alerte * 0.5:  # Écarts modérés peuvent être dus à l'évaporation ou pertes mineures
                return ClassificationEcart.EVAPORATION
            else:  # Écarts plus importants sont considérés comme des pertes
                return ClassificationEcart.PERTE
        elif ecart > 0:
            # Quantité réelle supérieure à la quantité théorique
            if ecart <= seuil_alerte * 0.5:
                return ClassificationEcart.ANOMALIE
            else:
                return ClassificationEcart.SURPLUS
        else:
            # Aucun écart
            return ClassificationEcart.ANOMALIE  # On considère cela aussi comme une anomalie

    def _classer_ecart_cuve(self, ecart: float, cuve_id: str, date_inventaire: date) -> ClassificationEcart:
        """Classe automatiquement un écart pour une cuve (carburant)"""
        # Récupérer le seuil d'alerte pour déterminer la gravité de l'écart
        seuil_alerte = self._get_seuil_alerte_cuve(cuve_id, date_inventaire)

        if ecart < 0:
            # Quantité réelle inférieure à la quantité théorique
            if abs(ecart) <= 2:  # Petits écarts pouvant être dus à des erreurs de mesure
                return ClassificationEcart.ANOMALIE
            elif abs(ecart) <= seuil_alerte * 0.3:  # Évaporation naturelle dans les cuves
                return ClassificationEcart.EVAPORATION
            else:  # Écarts plus importants sont considérés comme des pertes
                return ClassificationEcart.PERTE
        elif ecart > 0:
            # Quantité réelle supérieure à la quantité théorique
            if ecart <= seuil_alerte * 0.3:
                return ClassificationEcart.ANOMALIE
            else:
                return ClassificationEcart.SURPLUS
        else:
            # Aucun écart
            return ClassificationEcart.ANOMALIE  # On considère cela aussi comme une anomalie