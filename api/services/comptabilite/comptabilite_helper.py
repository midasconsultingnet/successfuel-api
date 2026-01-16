from sqlalchemy.orm import Session
from api.models.ecriture_comptable import EcritureComptableModel
from api.models.plan_comptable import PlanComptableModel
from sqlalchemy import text
from datetime import datetime
import uuid

class ComptabiliteHelper:
    @staticmethod
    def creer_ecriture_simple(
        db: Session,
        date_ecriture,
        libelle,
        compte_debit_id,
        compte_credit_id,
        montant,
        compagnie_id,
        tiers_id=None,
        module_origine=None,
        reference_origine=None,
        utilisateur_id=None
    ):
        """Créer une écriture comptable simple"""
        ecriture_data = {
            'date_ecriture': date_ecriture,
            'libelle_ecriture': libelle,
            'compte_debit': uuid.UUID(compte_debit_id) if isinstance(compte_debit_id, str) else compte_debit_id,
            'compte_credit': uuid.UUID(compte_credit_id) if isinstance(compte_credit_id, str) else compte_credit_id,
            'montant': montant,
            'compagnie_id': uuid.UUID(compagnie_id) if isinstance(compagnie_id, str) else compagnie_id,
            'tiers_id': uuid.UUID(tiers_id) if tiers_id and isinstance(tiers_id, str) else tiers_id,
            'module_origine': module_origine,
            'reference_origine': reference_origine,
            'utilisateur_id': uuid.UUID(utilisateur_id) if utilisateur_id and isinstance(utilisateur_id, str) else utilisateur_id,
            'est_validee': True  # Écriture immédiatement validée
        }
        
        from api.services.comptabilite.ecriture_comptable_service import EcritureComptableService
        service = EcritureComptableService()
        return service.creer_ecriture(ecriture_data, db)
    
    @staticmethod
    def calculer_solde_compte(db: Session, compte_id, date_limite):
        """Calculer le solde d'un compte à une date donnée"""
        # Appeler la fonction SQL calculer_solde_compte
        result = db.execute(text("""
            SELECT calculer_solde_compte(:compte_id, :date_limite)
        """), {"compte_id": str(compte_id), "date_limite": date_limite})
        
        return result.scalar()
    
    @staticmethod
    def generer_ecriture_pour_mouvement_financier(
        db: Session,
        mouvement_type: str,  # 'reglement', 'creance', 'avoir'
        mouvement_id: str,
        montant: float,
        tiers_id: str,
        compagnie_id: str,
        utilisateur_id: str,
        date_mouvement=None
    ):
        """
        Générer une écriture comptable pour un mouvement financier
        """
        # Trouver les comptes associés au tiers
        from api.models.tiers import TiersModel
        tiers = db.query(TiersModel).filter(TiersModel.id == uuid.UUID(tiers_id)).first()
        
        if not tiers or not tiers.compte_associe:
            raise ValueError("Le tiers n'a pas de compte associé dans le plan comptable")
        
        # Déterminer les comptes de contrepartie selon le type de mouvement
        if mouvement_type == 'reglement':
            # Pour un règlement, on crédite le compte client/fournisseur
            compte_debit = tiers.compte_associe  # Compte banque ou caisse
            compte_credit = tiers.compte_associe  # Compte client/fournisseur
        elif mouvement_type == 'creance':
            # Pour une créance, on débite le compte client
            compte_debit = tiers.compte_associe  # Compte client
            compte_credit = "..."  # Compte de créance à déterminer
        elif mouvement_type == 'avoir':
            # Pour un avoir, on crédite le compte client
            compte_debit = "..."  # Compte avoir à déterminer
            compte_credit = tiers.compte_associe  # Compte client
        else:
            raise ValueError(f"Type de mouvement non supporté: {mouvement_type}")
        
        # Créer l'écriture comptable
        return ComptabiliteHelper.creer_ecriture_simple(
            db=db,
            date_ecriture=date_mouvement or datetime.now(),
            libelle=f"{mouvement_type.capitalize()} #{mouvement_id}",
            compte_debit_id=compte_debit,
            compte_credit_id=compte_credit,
            montant=montant,
            compagnie_id=compagnie_id,
            tiers_id=tiers_id,
            module_origine="mouvements_financiers",
            reference_origine=f"{mouvement_type}_{mouvement_id}",
            utilisateur_id=utilisateur_id
        )