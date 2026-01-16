from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from datetime import datetime


def get_journal_operations(db: Session, date_debut: str, date_fin: str, station_id: str = None, type_operation: str = None):
    """
    Récupérer le journal des opérations entre deux dates
    
    Args:
        db: Session de base de données
        date_debut: Date de début au format 'YYYY-MM-DD'
        date_fin: Date de fin au format 'YYYY-MM-DD'
        station_id: ID de la station (optionnel)
        type_operation: Type d'opération (optionnel)
    
    Returns:
        Liste des opérations
    """
    # Conversion des dates
    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    
    # Construction de la requête SQL
    query = """
        SELECT 
            e.id as ecriture_id,
            e.date_ecriture,
            e.libelle_ecriture,
            e.montant,
            e.devise,
            e.module_origine,
            e.reference_origine,
            t.nom as tiers_nom,
            c.numero_compte,
            c.intitule_compte
        FROM ecriture_comptable e
        LEFT JOIN tiers t ON e.tiers_id = t.id
        LEFT JOIN plan_comptable c ON (e.compte_debit = c.id OR e.compte_credit = c.id)
        WHERE e.est_validee = TRUE
          AND e.date_ecriture BETWEEN :debut AND :fin
    """
    
    params = {
        "debut": date_debut_obj,
        "fin": date_fin_obj
    }
    
    # Ajout des filtres optionnels
    if station_id:
        query += " AND e.station_id = :station_id"
        params["station_id"] = station_id
    
    if type_operation:
        query += " AND e.module_origine = :type_operation"
        params["type_operation"] = type_operation
    
    query += " ORDER BY e.date_ecriture, e.id"
    
    # Exécution de la requête
    result = db.execute(text(query), params)
    rows = result.fetchall()
    
    # Conversion des résultats en dictionnaires
    operations = []
    for row in rows:
        operation = {
            "ecriture_id": row.ecriture_id,
            "date_ecriture": row.date_ecriture,
            "libelle_ecriture": row.libelle_ecriture,
            "montant": float(row.montant) if row.montant else 0,
            "devise": row.devise,
            "module_origine": row.module_origine,
            "reference_origine": row.reference_origine,
            "tiers_nom": row.tiers_nom,
            "numero_compte": row.numero_compte,
            "intitule_compte": row.intitule_compte
        }
        operations.append(operation)
    
    return {
        "date_debut": date_debut_obj,
        "date_fin": date_fin_obj,
        "operations": operations,
        "total_operations": len(operations)
    }


def get_journal_comptable(db: Session, date_debut: str, date_fin: str):
    """
    Récupérer le journal comptable entre deux dates
    
    Args:
        db: Session de base de données
        date_debut: Date de début au format 'YYYY-MM-DD'
        date_fin: Date de fin au format 'YYYY-MM-DD'
    
    Returns:
        Liste des écritures comptables
    """
    # Conversion des dates
    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
    
    # Construction de la requête SQL
    query = """
        SELECT 
            e.id as ecriture_id,
            e.date_ecriture,
            e.libelle_ecriture,
            c.numero_compte,
            c.intitule_compte,
            CASE WHEN e.compte_debit = c.id THEN e.montant ELSE 0 END AS debit,
            CASE WHEN e.compte_credit = c.id THEN e.montant ELSE 0 END AS credit
        FROM ecriture_comptable e
        JOIN plan_comptable c ON (e.compte_debit = c.id OR e.compte_credit = c.id)
        WHERE e.est_validee = TRUE
          AND e.date_ecriture BETWEEN :debut AND :fin
        ORDER BY e.date_ecriture, c.numero_compte, e.id
    """
    
    # Exécution de la requête
    result = db.execute(text(query), {
        "debut": date_debut_obj,
        "fin": date_fin_obj
    })
    rows = result.fetchall()
    
    # Conversion des résultats en dictionnaires
    ecritures = []
    for row in rows:
        ecriture = {
            "ecriture_id": row.ecriture_id,
            "date_ecriture": row.date_ecriture,
            "libelle_ecriture": row.libelle_ecriture,
            "numero_compte": row.numero_compte,
            "intitule_compte": row.intitule_compte,
            "debit": float(row.debit) if row.debit else 0,
            "credit": float(row.credit) if row.credit else 0
        }
        ecritures.append(ecriture)
    
    return {
        "date_debut": date_debut_obj,
        "date_fin": date_fin_obj,
        "ecritures": ecritures,
        "total_ecritures": len(ecritures)
    }