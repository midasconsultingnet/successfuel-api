from sqlalchemy.orm import Session
from sqlalchemy import text
from api.models.ecriture_comptable import EcritureComptableModel
from api.services.database_service import DatabaseService
import uuid
from datetime import datetime

class EcritureComptableService(DatabaseService):
    def __init__(self):
        super().__init__(EcritureComptableModel)
    
    def creer_ecriture(self, ecriture_data: dict, db: Session):
        """Créer une nouvelle écriture comptable"""
        self._valider_ecriture(ecriture_data)
        ecriture = EcritureComptableModel(**ecriture_data)
        db.add(ecriture)
        db.flush()
        return ecriture
    
    def valider_ecriture(self, ecriture_id: uuid.UUID, db: Session):
        """Valider une écriture comptable"""
        ecriture = self.get_by_id(ecriture_id, db)
        if not ecriture:
            raise ValueError("Écriture non trouvée")
        if ecriture.est_validee:
            raise ValueError("Écriture déjà validée")
        
        ecriture.est_validee = True
        ecriture.date_validation = datetime.now()
        return ecriture
    
    def corriger_ecriture(self, ecriture_id: uuid.UUID, correction_data: dict, db: Session):
        """Créer une écriture de correction pour une écriture existante"""
        # Récupérer l'écriture originale
        ecriture_originale = self.get_by_id(ecriture_id, db)
        
        if not ecriture_originale:
            raise ValueError("Écriture originale non trouvée")
        
        # Créer l'écriture d'annulation
        ecriture_annulation = EcritureComptableModel(
            date_ecriture=datetime.now(),
            libelle_ecriture=f"Annulation - {ecriture_originale.libelle_ecriture}",
            compte_debit=ecriture_originale.compte_credit,  # Inversion
            compte_credit=ecriture_originale.compte_debit,  # Inversion
            montant=ecriture_originale.montant,
            devise=ecriture_originale.devise,
            tiers_id=ecriture_originale.tiers_id,
            module_origine=ecriture_originale.module_origine,
            reference_origine=ecriture_originale.reference_origine,
            utilisateur_id=correction_data.get('utilisateur_id'),
            compagnie_id=ecriture_originale.compagnie_id,
            est_validee=True
        )
        
        db.add(ecriture_annulation)
        
        # Créer la nouvelle écriture corrigée
        ecriture_corrigee = EcritureComptableModel(**correction_data)
        ecriture_corrigee.est_validee = True
        db.add(ecriture_corrigee)
        
        # Rafraîchir la vue matérialisée
        db.execute(text("SELECT refresh_grand_livre()"))
        
        return {"annulation": ecriture_annulation, "correction": ecriture_corrigee}
    
    def _valider_ecriture(self, ecriture_data: dict):
        """Valider les règles métier d'une écriture"""
        # Vérifier que le montant est positif
        if ecriture_data['montant'] <= 0:
            raise ValueError("Le montant doit être positif")
        
        # Vérifier que les comptes appartiennent à la même compagnie
        # Implémentation de la vérification
        pass