from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..models import AuditExport, User
from fastapi import HTTPException
import uuid


def log_export_action(
    db: Session,
    utilisateur_id: str,
    type_bilan: str,
    format_export: str,
    fichier_genere: str = None,
    taille_fichier: int = None,
    ip_utilisateur: str = None,
    user_agent: str = None,
    details: str = None,
    statut: str = "complet"
):
    """
    Enregistrer une action d'export dans l'audit
    """
    try:
        utilisateur_uuid = uuid.UUID(utilisateur_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID d'utilisateur invalide")
    
    # Vérifier que l'utilisateur existe
    utilisateur = db.query(User).filter(User.id == utilisateur_uuid).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Créer l'entrée d'audit
    audit_export = AuditExport(
        utilisateur_id=utilisateur_uuid,
        type_bilan=type_bilan,
        format_export=format_export,
        date_export=datetime.now(timezone.utc),
        fichier_genere=fichier_genere,
        taille_fichier=taille_fichier,
        ip_utilisateur=ip_utilisateur,
        user_agent=user_agent,
        details=details,
        statut=statut
    )
    
    db.add(audit_export)
    db.commit()
    db.refresh(audit_export)
    
    return audit_export