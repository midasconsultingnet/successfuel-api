from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional
from ..models.plan_comptable import PlanComptableModel
from ..plan_comptable.schemas import PlanComptableCreate
from ..services.plan_comptable.plan_comptable_service import PlanComptableService


class PlanComptableHelper:
    """
    Classe utilitaire pour gérer les opérations liées au plan comptable
    pour les clients, fournisseurs et employés
    """
    
    @staticmethod
    def get_compte_parent(db: Session, numero_compte_parent: str, compagnie_id: UUID) -> Optional[PlanComptableModel]:
        """
        Récupérer un compte parent par son numéro
        Cherche d'abord les comptes partagés (compagnie_id NULL), puis ceux spécifiques à la compagnie
        """
        # D'abord, chercher un compte parent partagé (sans compagnie_id)
        compte_parent = db.query(PlanComptableModel).filter(
            PlanComptableModel.numero_compte == numero_compte_parent,
            PlanComptableModel.compagnie_id.is_(None)  # Comptes partagés
        ).first()

        if not compte_parent:
            # Si pas trouvé, chercher un compte spécifique à la compagnie
            compte_parent = db.query(PlanComptableModel).filter(
                PlanComptableModel.numero_compte == numero_compte_parent,
                PlanComptableModel.compagnie_id == compagnie_id
            ).first()

        return compte_parent
    
    @staticmethod
    def creer_compte_enfant(
        db: Session,
        numero_compte_parent: str,
        libelle_compte: str,
        categorie: str,
        compagnie_id: UUID,
        type_compte: str = "Bilan"
    ) -> PlanComptableModel:
        """
        Créer un nouveau compte enfant dans le plan comptable
        avec un numéro généré automatiquement
        """
        # Récupérer le compte parent
        compte_parent = PlanComptableHelper.get_compte_parent(db, numero_compte_parent, compagnie_id)

        if not compte_parent:
            raise ValueError(f"Compte parent {numero_compte_parent} non trouvé")

        # Compter le nombre de comptes enfants déjà enregistrés avec ce parent
        nombre_comptes_enfants = db.query(func.count(PlanComptableModel.id)).filter(
            PlanComptableModel.parent_id == compte_parent.id,
            PlanComptableModel.compagnie_id == compagnie_id
        ).scalar()

        # Générer le numéro de compte selon la formule : numéro_parent + (nombre + 1)
        numero_compte_genere = f"{compte_parent.numero_compte}{nombre_comptes_enfants + 1:03d}"

        # Vérifier si le numéro de compte existe déjà
        existing_account = db.query(PlanComptableModel).filter(
            PlanComptableModel.numero_compte == numero_compte_genere
        ).first()

        if existing_account:
            raise ValueError(f"Le numéro de compte {numero_compte_genere} existe déjà.")

        # Créer directement le nouveau compte dans la session existante
        nouveau_plan = PlanComptableModel(
            numero_compte=numero_compte_genere,
            libelle_compte=libelle_compte,
            categorie=categorie,
            type_compte=type_compte,
            parent_id=compte_parent.id,
            compagnie_id=compagnie_id
        )

        # Ajouter à la session existante
        db.add(nouveau_plan)
        # Faire un flush pour que l'ID soit généré
        db.flush()

        return nouveau_plan