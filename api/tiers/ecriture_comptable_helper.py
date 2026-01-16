from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from ..models.ecriture_comptable import EcritureComptableModel


class EcritureComptableHelper:
    """
    Classe utilitaire pour gérer les écritures comptables
    """
    
    @staticmethod
    def creer_ecriture_comptable(
        db: Session,
        date_ecriture: datetime,
        libelle_ecriture: str,
        compte_debit_id: UUID,
        compte_credit_id: UUID,
        montant: float,
        devise: str = 'XOF',
        tiers_id: UUID = None,
        module_origine: str = None,
        reference_origine: str = None,
        utilisateur_id: UUID = None,
        est_validee: bool = True
    ) -> EcritureComptableModel:
        """
        Crée une écriture comptable
        
        Args:
            db: Session de base de données
            date_ecriture: Date de l'écriture
            libelle_ecriture: Libellé de l'écriture
            compte_debit_id: ID du compte à débiter
            compte_credit_id: ID du compte à créditer
            montant: Montant de l'écriture
            devise: Devise de l'écriture
            tiers_id: ID du tiers concerné (optionnel)
            module_origine: Module d'origine de l'écriture
            reference_origine: Référence de l'origine
            utilisateur_id: ID de l'utilisateur effectuant l'opération
            est_validee: Indique si l'écriture est validée
            
        Returns:
            EcritureComptableModel: L'écriture comptable créée
        """
        ecriture = EcritureComptableModel(
            date_ecriture=date_ecriture,
            libelle_ecriture=libelle_ecriture,
            compte_debit=compte_debit_id,
            compte_credit=compte_credit_id,
            montant=montant,
            devise=devise,
            tiers_id=tiers_id,
            module_origine=module_origine,
            reference_origine=reference_origine,
            utilisateur_id=utilisateur_id,
            est_validee=est_validee
        )
        
        db.add(ecriture)
        db.commit()
        db.refresh(ecriture)
        
        return ecriture
    
    @staticmethod
    def creer_ecriture_solde_initiale_tiers(
        db: Session,
        tiers_id: UUID,
        compte_associe_id: UUID,
        montant: float,
        devise: str = 'XOF',
        utilisateur_id: UUID = None,
        date_ecriture: datetime = None,
        compte_contrepartie_id: UUID = None
    ) -> EcritureComptableModel:
        """
        Crée une écriture comptable pour la solde initiale d'un tiers

        Args:
            db: Session de base de données
            tiers_id: ID du tiers
            compte_associe_id: ID du compte associé au tiers
            montant: Montant de la solde initiale
            devise: Devise de l'opération
            utilisateur_id: ID de l'utilisateur effectuant l'opération
            date_ecriture: Date de l'écriture (par défaut, maintenant)
            compte_contrepartie_id: ID du compte de contrepartie (caisse, banque, etc.)

        Returns:
            EcritureComptableModel: L'écriture comptable créée
        """
        if not date_ecriture:
            date_ecriture = datetime.now()

        # Pour une solde initiale, on débite un compte de caisse ou banque
        # et on crédite le compte du tiers

        # Si le compte de contrepartie n'est pas fourni, on devrait le récupérer
        # selon la station ou défini dans les paramètres
        if not compte_contrepartie_id:
            # Pour l'instant, on lève une exception pour forcer à fournir ce compte
            raise ValueError("Le compte de contrepartie est requis pour une écriture de solde initiale")

        return EcritureComptableHelper.creer_ecriture_comptable(
            db=db,
            date_ecriture=date_ecriture,
            libelle_ecriture=f"Solde initiale du tiers {tiers_id}",
            compte_debit=compte_contrepartie_id,  # Compte de contrepartie (caisse, banque, etc.)
            compte_credit=compte_associe_id,  # Compte associé au tiers
            montant=montant,
            devise=devise,
            tiers_id=tiers_id,
            module_origine="Tiers",
            reference_origine=f"SOLDE_INIT_{tiers_id}",
            utilisateur_id=utilisateur_id,
            est_validee=True
        )