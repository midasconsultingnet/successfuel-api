from sqlalchemy.orm import Session
from models.securite import TentativeAccesNonAutorise, TentativeConnexion, EvenementSecurite
from datetime import datetime
import uuid


def log_unauthorized_access_attempt(
    db: Session,
    utilisateur_id: str,
    endpoint_accesse: str,
    endpoint_autorise: str,
    ip_connexion: str = None,
    compagnie_id: str = None,
    details: str = None
):
    """
    Enregistre une tentative d'accès non autorisé
    """
    tentative = TentativeAccesNonAutorise(
        utilisateur_id=utilisateur_id,
        endpoint_accesse=endpoint_accesse,
        endpoint_autorise=endpoint_autorise,
        ip_connexion=ip_connexion,
        compagnie_id=compagnie_id,
        created_at=datetime.utcnow()
    )

    db.add(tentative)
    db.commit()


def log_security_event(
    db: Session,
    type_evenement: str,
    utilisateur_id: str,
    description: str = None,
    ip_utilisateur: str = None,
    poste_utilisateur: str = None,
    donnees_supplementaires: dict = None,
    compagnie_id: str = None
):
    """
    Enregistre un événement de sécurité
    """
    evenement = EvenementSecurite(
        type_evenement=type_evenement,
        utilisateur_id=utilisateur_id,
        description=description,
        ip_utilisateur=ip_utilisateur,
        poste_utilisateur=poste_utilisateur,
        donnees_supplementaires=donnees_supplementaires,
        compagnie_id=compagnie_id,
        created_at=datetime.utcnow()
    )

    db.add(evenement)
    db.commit()