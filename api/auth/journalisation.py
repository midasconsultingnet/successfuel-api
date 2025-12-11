import json
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import JournalActionUtilisateur


def make_serializable_for_json(obj):
    """Convert non-serializable objects to serializable types for JSON storage"""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float for JSON serialization
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    elif isinstance(obj, dict):
        # Recursively process dictionary values
        return {key: make_serializable_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        # Recursively process list items
        return [make_serializable_for_json(item) for item in obj]
    else:
        return obj


def log_user_action(
    db: Session,
    utilisateur_id: str,
    type_action: str,  # create, update, delete, read
    module_concerne: str,
    donnees_avant: dict = None,
    donnees_apres: dict = None,
    ip_utilisateur: str = None,
    user_agent: str = None
):
    """
    Enregistre une action effectuée par un utilisateur dans le journal
    """
    # Convertir les données en JSON pour s'assurer qu'elles sont stockables dans la base de données
    donnees_avant_json = json.dumps(make_serializable_for_json(donnees_avant)) if donnees_avant else None
    donnees_apres_json = json.dumps(make_serializable_for_json(donnees_apres)) if donnees_apres else None

    journal_action = JournalActionUtilisateur(
        utilisateur_id=utilisateur_id,
        type_action=type_action,
        module_concerne=module_concerne,
        donnees_avant=donnees_avant_json,
        donnees_apres=donnees_apres_json,
        ip_utilisateur=ip_utilisateur,
        user_agent=user_agent
    )

    db.add(journal_action)
    db.commit()
    db.refresh(journal_action)

    return journal_action