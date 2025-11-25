"""
Service de validation hiérarchique pour les opérations sensibles
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.structures import Utilisateur
from models.securite import ModificationSensible
from services.rbac_service import RBACService
from services.journalisation_service import JournalisationService


class ValidationHierarchiqueService:
    """
    Service pour la validation hiérarchique des opérations sensibles
    Permet de soumettre des opérations pour approbation par un supérieur hiérarchique
    """
    
    @staticmethod
    def soumettre_operation_pour_validation(
        db: Session,
        utilisateur_demandeur_id: str,
        operation_type: str,
        objet_modifie: str,
        objet_id: str,
        valeur_proposee: Dict,
        seuil_validation: Optional[str] = None,  # Niveau de validation requis
        commentaire: str = ""
    ) -> ModificationSensible:
        """
        Soumet une opération sensible pour validation hiérarchique
        """
        # Créer une entrée dans modifications_sensibles avec statut 'Enquete'
        modification = ModificationSensible(
            utilisateur_id=utilisateur_demandeur_id,
            type_operation=operation_type,
            objet_modifie=objet_modifie,
            objet_id=objet_id,
            ancienne_valeur=None,  # Pas encore modifié
            nouvelle_valeur=valeur_proposee,
            seuil_alerte=True,  # Marquer comme nécessitant validation
            commentaire=commentaire,
            statut='Enquete'  # En attente de validation
        )
        
        db.add(modification)
        db.commit()
        db.refresh(modification)
        
        # Enregistrer l'événement de sécurité
        JournalisationService.log_security_event(
            db,
            type_evenement="operation_soumise_validation",
            description=f"Opération {operation_type} sur {objet_modifie} ID:{objet_id} soumise pour validation",
            utilisateur_id=utilisateur_demandeur_id
        )
        
        return modification
    
    @staticmethod
    def verifier_autorisation_validation(
        db: Session,
        utilisateur_validateur: Utilisateur,
        operation_id: str
    ) -> bool:
        """
        Vérifie si l'utilisateur validateur a le droit d'approuver l'opération
        """
        # Récupérer la modification sensible
        modification = db.query(ModificationSensible).filter(
            ModificationSensible.id == operation_id
        ).first()
        
        if not modification or modification.statut != 'Enquete':
            return False
        
        # Règles de validation hiérarchique :
        # 1. L'utilisateur doit avoir la permission "valider_operations_sensibles"
        has_permission = RBACService.check_permission_by_user_obj(
            db, utilisateur_validateur, "valider_operations_sensibles"
        )
        
        if not has_permission:
            return False
        
        # 2. Pour certaines opérations sensibles, on peut avoir des règles spécifiques
        #    selon la hiérarchie ou les montants impliqués
        return True
    
    @staticmethod
    def approuver_operation(
        db: Session,
        utilisateur_validateur: Utilisateur,
        operation_id: str,
        commentaire_validation: str = ""
    ) -> bool:
        """
        Approuve une opération sensible après validation
        """
        if not ValidationHierarchiqueService.verifier_autorisation_validation(
            db, utilisateur_validateur, operation_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour approuver cette opération"
            )
        
        # Récupérer la modification
        modification = db.query(ModificationSensible).filter(
            ModificationSensible.id == operation_id
        ).first()
        
        if not modification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opération de modification non trouvée"
            )
        
        # Mettre à jour le statut
        modification.statut = 'Traite'
        modification.commentaire += f" - Validé par {utilisateur_validateur.login}: {commentaire_validation}"
        
        db.commit()
        
        # Enregistrer l'événement de sécurité
        JournalisationService.log_security_event(
            db,
            type_evenement="operation_approuvee",
            description=f"Opération ID:{operation_id} approuvée par {utilisateur_validateur.login}",
            utilisateur_id=utilisateur_validateur.id
        )
        
        return True
    
    @staticmethod
    def rejeter_operation(
        db: Session,
        utilisateur_validateur: Utilisateur,
        operation_id: str,
        motif_rejet: str = ""
    ) -> bool:
        """
        Rejette une opération sensible après validation
        """
        if not ValidationHierarchiqueService.verifier_autorisation_validation(
            db, utilisateur_validateur, operation_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour rejeter cette opération"
            )
        
        # Récupérer la modification
        modification = db.query(ModificationSensible).filter(
            ModificationSensible.id == operation_id
        ).first()
        
        if not modification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opération de modification non trouvée"
            )
        
        # Mettre à jour le statut
        modification.statut = 'Ferme'
        modification.commentaire += f" - Rejetée par {utilisateur_validateur.login}: {motif_rejet}"
        
        db.commit()
        
        # Enregistrer l'événement de sécurité
        JournalisationService.log_security_event(
            db,
            type_evenement="operation_rejetee",
            description=f"Opération ID:{operation_id} rejetée par {utilisateur_validateur.login}",
            utilisateur_id=utilisateur_validateur.id
        )
        
        return True
    
    @staticmethod
    def get_operations_en_attente_validation(
        db: Session,
        utilisateur_validateur: Utilisateur,
        skip: int = 0,
        limit: int = 10
    ) -> list:
        """
        Récupère les opérations en attente de validation pour l'utilisateur
        """
        # Vérifier que l'utilisateur a la permission de valider
        has_permission = RBACService.check_permission_by_user_obj(
            db, utilisateur_validateur, "valider_operations_sensibles"
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour consulter les validations en attente"
            )
        
        operations = db.query(ModificationSensible).filter(
            ModificationSensible.statut == 'Enquete'
        ).offset(skip).limit(limit).all()
        
        return operations