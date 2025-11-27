from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from models.structures import Utilisateur
from models.securite import (
    TentativeConnexion,
    EvenementSecurite,
    ModificationSensible,
    AuthToken
)


class JournalisationService:
    @staticmethod
    def log_security_event(
        db: Session,
        type_evenement: str,
        description: str,
        utilisateur_id: str = None,
        ip_utilisateur: str = None,
        poste_utilisateur: str = None,
        session_id: str = None,
        donnees_supplementaires: Dict = None,
        statut: str = 'NonTraite'
    ) -> EvenementSecurite:
        """
        Enregistre un événement de sécurité
        """
        evenement = EvenementSecurite(
            type_evenement=type_evenement,
            description=description,
            utilisateur_id=utilisateur_id,
            ip_utilisateur=ip_utilisateur,
            poste_utilisateur=poste_utilisateur,
            session_id=session_id,
            donnees_supplementaires=donnees_supplementaires,
            statut=statut,
            created_at=datetime.utcnow()
        )
        
        db.add(evenement)
        db.commit()
        db.refresh(evenement)
        
        return evenement

    @staticmethod
    def log_sensitive_modification(
        db: Session,
        utilisateur_id: str,
        type_operation: str,
        objet_modifie: str,
        objet_id: str = None,
        ancienne_valeur: Dict = None,
        nouvelle_valeur: Dict = None,
        seuil_alerte: bool = False,
        commentaire: str = None,
        ip_utilisateur: str = None,
        poste_utilisateur: str = None
    ) -> ModificationSensible:
        """
        Enregistre une modification sensible
        """
        modification = ModificationSensible(
            utilisateur_id=utilisateur_id,
            type_operation=type_operation,
            objet_modifie=objet_modifie,
            objet_id=objet_id,
            ancienne_valeur=ancienne_valeur,
            nouvelle_valeur=nouvelle_valeur,
            seuil_alerte=seuil_alerte,
            commentaire=commentaire,
            ip_utilisateur=ip_utilisateur,
            poste_utilisateur=poste_utilisateur,
            created_at=datetime.utcnow()
        )
        
        db.add(modification)
        db.commit()
        db.refresh(modification)
        
        return modification

    @staticmethod
    def log_failed_login_attempt(
        db: Session,
        login: str,
        ip_connexion: str = None,
        utilisateur_id: str = None
    ) -> TentativeConnexion:
        """
        Enregistre une tentative de connexion échouée
        """
        tentative = TentativeConnexion(
            login=login,
            ip_connexion=ip_connexion,
            resultat_connexion='Echouee',
            utilisateur_id=utilisateur_id,
            created_at=datetime.utcnow()
        )
        
        db.add(tentative)
        db.commit()
        db.refresh(tentative)
        
        return tentative

    @staticmethod
    def log_successful_login(
        db: Session,
        login: str,
        utilisateur_id: str,
        ip_connexion: str = None
    ) -> TentativeConnexion:
        """
        Enregistre une tentative de connexion réussie
        """
        tentative = TentativeConnexion(
            login=login,
            ip_connexion=ip_connexion,
            resultat_connexion='Reussie',
            utilisateur_id=utilisateur_id,
            created_at=datetime.utcnow()
        )
        
        db.add(tentative)
        db.commit()
        db.refresh(tentative)
        
        return tentative

    @staticmethod
    def get_security_logs(
        db: Session,
        type_evenement: str = None,
        utilisateur_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        statut: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EvenementSecurite]:
        """
        Récupère les logs de sécurité avec filtres optionnels
        """
        query = db.query(EvenementSecurite)
        
        if type_evenement:
            query = query.filter(EvenementSecurite.type_evenement == type_evenement)
        if utilisateur_id:
            query = query.filter(EvenementSecurite.utilisateur_id == utilisateur_id)
        if start_date:
            query = query.filter(EvenementSecurite.created_at >= start_date)
        if end_date:
            query = query.filter(EvenementSecurite.created_at <= end_date)
        if statut:
            query = query.filter(EvenementSecurite.statut == statut)
            
        query = query.order_by(EvenementSecurite.created_at.desc())
        logs = query.offset(skip).limit(limit).all()
        
        return logs

    @staticmethod
    def get_sensitive_modifications(
        db: Session,
        utilisateur_id: str = None,
        type_operation: str = None,
        objet_modifie: str = None,
        seuil_alerte: bool = None,
        start_date: datetime = None,
        end_date: datetime = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModificationSensible]:
        """
        Récupère les modifications sensibles avec filtres optionnels
        """
        query = db.query(ModificationSensible)
        
        if utilisateur_id:
            query = query.filter(ModificationSensible.utilisateur_id == utilisateur_id)
        if type_operation:
            query = query.filter(ModificationSensible.type_operation == type_operation)
        if objet_modifie:
            query = query.filter(ModificationSensible.objet_modifie == objet_modifie)
        if seuil_alerte is not None:
            query = query.filter(ModificationSensible.seuil_alerte == seuil_alerte)
        if start_date:
            query = query.filter(ModificationSensible.created_at >= start_date)
        if end_date:
            query = query.filter(ModificationSensible.created_at <= end_date)
            
        query = query.order_by(ModificationSensible.created_at.desc())
        modifications = query.offset(skip).limit(limit).all()
        
        return modifications

    @staticmethod
    def monitor_login_attempts(
        db: Session,
        login: str,
        minutes: int = 15,
        max_attempts: int = 5
    ) -> bool:
        """
        Vérifie s'il y a eu trop de tentatives de connexion échouées récemment
        """
        count = db.query(TentativeConnexion).filter(
            TentativeConnexion.login == login,
            TentativeConnexion.created_at > datetime.utcnow() - timedelta(minutes=minutes),
            TentativeConnexion.resultat_connexion == 'Echouee'
        ).count()
        
        return count >= max_attempts

    @staticmethod
    def log_user_action(
        db: Session,
        utilisateur_id: str,
        action: str,
        details: Dict = None,
        objet_concerne: str = None,
        objet_id: str = None,
        ip_utilisateur: str = None,
        poste_utilisateur: str = None,
        seuil_alerte: bool = False
    ):
        """
        Enregistre une action utilisateur comme événement de sécurité
        """
        description = f"Action '{action}' effectuée par l'utilisateur {utilisateur_id}"
        if objet_concerne and objet_id:
            description += f" sur {objet_concerne} ID: {objet_id}"
        
        return JournalisationService.log_security_event(
            db,
            type_evenement="action_utilisateur",
            description=description,
            utilisateur_id=utilisateur_id,
            ip_utilisateur=ip_utilisateur,
            poste_utilisateur=poste_utilisateur,
            donnees_supplementaires=details,
            statut="Traite"  # Ces actions sont traitées immédiatement
        )