from sqlalchemy.orm import Session
from typing import List, Optional
from ...models.ecart_inventaire import EcartInventaire
from ...inventaires.schemas import EcartInventaireCreate, EcartInventaireUpdate
from ..database_service import DatabaseService
from datetime import datetime


class EcartInventaireService(DatabaseService):
    def __init__(self, db: Session):
        super().__init__(db, EcartInventaire)

    def create_ecart_inventaire(self, ecart_inventaire: EcartInventaireCreate) -> EcartInventaire:
        """Crée un nouvel écart d'inventaire"""
        db_ecart_inventaire = EcartInventaire(
            inventaire_id=ecart_inventaire.inventaire_id,
            produit_id=ecart_inventaire.produit_id,
            station_id=ecart_inventaire.station_id,
            compagnie_id=ecart_inventaire.compagnie_id,
            quantite_theorique=ecart_inventaire.quantite_theorique,
            quantite_reelle=ecart_inventaire.quantite_reelle,
            ecart=ecart_inventaire.ecart,
            classification=ecart_inventaire.classification,
            seuil_alerte=ecart_inventaire.seuil_alerte,
            seuil_saison=ecart_inventaire.seuil_saison,
            motif_anomalie=ecart_inventaire.motif_anomalie
        )
        return self.create(db_ecart_inventaire)

    def update_ecart_inventaire(self, ecart_id: str, ecart_inventaire: EcartInventaireUpdate) -> EcartInventaire:
        """Met à jour un écart d'inventaire existant"""
        update_data = ecart_inventaire.dict(exclude_unset=True)
        return self.update(ecart_id, update_data)

    def delete_ecart_inventaire(self, ecart_id: str) -> EcartInventaire:
        """Supprime un écart d'inventaire (soft delete)"""
        return self.delete(ecart_id)

    def get_ecarts_by_inventaire(self, inventaire_id: str) -> List[EcartInventaire]:
        """Récupère tous les écarts d'un inventaire spécifique"""
        return self.db.query(EcartInventaire).filter(
            EcartInventaire.inventaire_id == inventaire_id,
            EcartInventaire.est_actif == True
        ).all()

    def get_ecarts_by_produit(self, produit_id: str) -> List[EcartInventaire]:
        """Récupère tous les écarts pour un produit spécifique"""
        return self.db.query(EcartInventaire).filter(
            EcartInventaire.produit_id == produit_id,
            EcartInventaire.est_actif == True
        ).all()

    def get_ecarts_by_classification(self, classification: str) -> List[EcartInventaire]:
        """Récupère tous les écarts d'une classification spécifique"""
        return self.db.query(EcartInventaire).filter(
            EcartInventaire.classification == classification,
            EcartInventaire.est_actif == True
        ).all()

    def get_ecarts_by_station(self, station_id: str) -> List[EcartInventaire]:
        """Récupère tous les écarts pour une station spécifique"""
        return self.db.query(EcartInventaire).filter(
            EcartInventaire.station_id == station_id,
            EcartInventaire.est_actif == True
        ).all()