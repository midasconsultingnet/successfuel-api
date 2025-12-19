from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime, timezone
from ...models.demande_achat import DemandeAchat, LigneDemandeAchat, StatutDemande
from ...models.validation_achat import ValidationDemande, RegleValidation, NiveauValidation
from ..database_service import DatabaseService
from ...utils.pagination import PaginationParams
from ...exceptions import NotFoundException, ValidationException


class DemandeAchatService(DatabaseService):
    def __init__(self, db: Session):
        super().__init__(db, DemandeAchat)

    def create_demande_achat(self, utilisateur_id: UUID, data: dict):
        """Créer une nouvelle demande d'achat"""
        # Générer un numéro unique pour la demande
        numero = f"DQA-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # Calculer le montant total à partir des lignes
        montant_total = sum(
            ligne_data.get('quantite', 0) * ligne_data.get('prix_unitaire', 0.0)
            for ligne_data in data.get('lignes_demande', [])
        )

        # Préparer les données pour la création
        demande_data = {
            'numero': numero,
            'objet': data['objet'],
            'statut': StatutDemande.EN_ATTENTE,
            'utilisateur_id': utilisateur_id,
            'tiers_id': data['tiers_id'],
            'montant_total': montant_total
        }

        # Créer la demande d'achat
        demande = self.create(demande_data)

        # Créer les lignes de la demande
        for ligne_data in data.get('lignes_demande', []):
            ligne_data['montant_total'] = ligne_data['quantite'] * ligne_data['prix_unitaire']
            ligne_data['demande_achat_id'] = demande.id
            ligne = LigneDemandeAchat(**ligne_data)
            self.db.add(ligne)

        # Initialiser les validations en fonction des règles
        self.initialiser_validations(demande)

        self.db.commit()
        self.db.refresh(demande)

        return demande

    def initialiser_validations(self, demande: DemandeAchat):
        """Initialiser les validations requises pour la demande d'achat en fonction des règles"""
        # Récupérer les règles de validation applicables
        regles = self.db.query(RegleValidation).filter(
            RegleValidation.compagnie_id == demande.utilisateur.compagnie_id,
            RegleValidation.est_active == True
        ).all()

        # Identifier les validations requises en fonction du montant et des règles
        validations_requises = []

        for regle in regles:
            # Si le seuil de montant est spécifié et que le montant de la demande dépasse ce seuil
            if (regle.seuil_montant is not None and
                float(demande.montant_total) >= float(regle.seuil_montant)):
                validations_requises.append({
                    'niveau': regle.niveau_validation_requis,
                    'utilisateur_valideur_id': regle.utilisateur_valideur_id,
                    'regle_id': regle.id
                })

        # Si aucune règle spécifique ne s'applique, une validation de base est requise
        if not validations_requises:
            # On peut définir une validation de base (niveau 1) par défaut
            from ..models.user import User
            premier_valideur = self.db.query(User).filter(
                User.compagnie_id == demande.utilisateur.compagnie_id
            ).first()  # Vous pouvez définir une logique plus précise pour identifier le premier valideur

            if premier_valideur:
                validations_requises.append({
                    'niveau': NiveauValidation.NIVEAU_1,
                    'utilisateur_valideur_id': premier_valideur.id,
                    'regle_id': None
                })

        # Créer les validations requises
        for validation_data in validations_requises:
            validation = ValidationDemande(
                niveau=validation_data['niveau'],
                utilisateur_id=validation_data['utilisateur_valideur_id'],
                demande_achat_id=demande.id,
                statut='en_attente'
            )
            self.db.add(validation)

    def update_demande_achat(self, demande_id: UUID, data: dict):
        """Mettre à jour une demande d'achat existante"""
        demande = self.get_by_id(demande_id)
        if not demande:
            raise NotFoundException(f"Demande d'achat avec ID {demande_id} non trouvée")

        # Si le statut change, mettre à jour la date de validation
        if 'statut' in data and data['statut'] != demande.statut.value:
            data['date_validation'] = datetime.now(timezone.utc)

        # Mettre à jour les données de base
        for key, value in data.items():
            if hasattr(demande, key) and key != 'lignes_demande':
                setattr(demande, key, value)

        # Gérer les mises à jour des lignes de demande si fournies
        if 'lignes_demande' in data:
            # Supprimer les anciennes lignes
            for ligne in demande.lignes_demande:
                self.db.delete(ligne)

            # Ajouter les nouvelles lignes
            montant_total = 0
            for ligne_data in data['lignes_demande']:
                montant_total += ligne_data['quantite'] * ligne_data['prix_unitaire']
                ligne_data['demande_achat_id'] = demande.id
                ligne_data['montant_total'] = ligne_data['quantite'] * ligne_data['prix_unitaire']
                ligne = LigneDemandeAchat(**ligne_data)
                self.db.add(ligne)

            demande.montant_total = montant_total

        self.db.commit()
        self.db.refresh(demande)

        return demande

    def valider_demande_achat(self, demande_id: UUID, utilisateur_id: UUID):
        """Valider une demande d'achat ou effectuer une validation intermédiaire"""
        demande = self.db.query(DemandeAchat).filter(DemandeAchat.id == demande_id).first()
        if not demande:
            raise NotFoundException(f"Demande d'achat avec ID {demande_id} non trouvée")

        if demande.statut != StatutDemande.EN_ATTENTE:
            raise ValidationException("La demande d'achat n'est pas en attente de validation")

        # Vérifier si l'utilisateur est autorisé à valider à ce niveau
        validation_en_attente = self.db.query(ValidationDemande).filter(
            ValidationDemande.demande_achat_id == demande_id,
            ValidationDemande.utilisateur_id == utilisateur_id,
            ValidationDemande.statut == 'en_attente'
        ).first()

        if not validation_en_attente:
            raise ValidationException("Vous n'êtes pas autorisé à valider cette demande d'achat")

        # Mettre à jour la validation
        validation_en_attente.statut = 'approuve'
        validation_en_attente.date_validation = datetime.now(timezone.utc)

        # Vérifier si toutes les validations sont terminées
        validations_restantes = self.db.query(ValidationDemande).filter(
            ValidationDemande.demande_achat_id == demande_id,
            ValidationDemande.statut == 'en_attente'
        ).count()

        if validations_restantes == 0:
            # Toutes les validations sont terminées, on approuve la demande
            demande.statut = StatutDemande.APPROUVEE
            demande.date_validation = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(demande)

        return demande

    def rejeter_demande_achat(self, demande_id: UUID, utilisateur_id: UUID):
        """Rejeter une demande d'achat"""
        demande = self.db.query(DemandeAchat).filter(DemandeAchat.id == demande_id).first()
        if not demande:
            raise NotFoundException(f"Demande d'achat avec ID {demande_id} non trouvée")

        if demande.statut != StatutDemande.EN_ATTENTE:
            raise ValidationException("La demande d'achat n'est pas en attente de validation")

        # Vérifier si l'utilisateur est autorisé à rejeter (souvent, c'est une personne avec un rôle élevé ou le premier validateur)
        validation_en_attente = self.db.query(ValidationDemande).filter(
            ValidationDemande.demande_achat_id == demande_id,
            ValidationDemande.utilisateur_id == utilisateur_id,
            ValidationDemande.statut == 'en_attente'
        ).first()

        if not validation_en_attente:
            raise ValidationException("Vous n'êtes pas autorisé à rejeter cette demande d'achat")

        # Rejeter la demande et toutes les validations en attente
        demande.statut = StatutDemande.REJETEE
        demande.date_validation = datetime.now(timezone.utc)

        validations_en_attente = self.db.query(ValidationDemande).filter(
            ValidationDemande.demande_achat_id == demande_id,
            ValidationDemande.statut == 'en_attente'
        ).all()

        for validation in validations_en_attente:
            validation.statut = 'rejete'
            validation.date_validation = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(demande)

        return demande

    def get_demande_achat_with_details(self, demande_id: UUID):
        """Récupérer une demande d'achat avec ses détails"""
        demande = self.db.query(DemandeAchat).filter(DemandeAchat.id == demande_id).first()
        if not demande:
            raise NotFoundException(f"Demande d'achat avec ID {demande_id} non trouvée")

        return demande