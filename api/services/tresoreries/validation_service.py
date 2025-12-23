"""
Service de validation pour les opérations de trésorerie
Ce module contient des fonctions pour valider les opérations de trésorerie
telles que les paiements d'achats de carburant.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from uuid import UUID
from fastapi import HTTPException


def verifier_solde_tresorerie_suffisant(
    db: Session,
    tresorerie_station_id: UUID,
    montant_paiement: float
) -> Dict[str, Any]:
    """
    Vérifie si le solde de la trésorerie est suffisant pour effectuer un paiement.

    Args:
        db: Session de base de données
        tresorerie_station_id: ID de la trésorerie station concernée
        montant_paiement: Montant du paiement à effectuer

    Returns:
        Dict contenant le solde actuel, le montant du paiement et si le solde est suffisant
    """
    # Récupérer le solde de la trésorerie station à partir de la table tresorerie
    from ...models.tresorerie import Tresorerie
    tresorerie = db.query(Tresorerie).filter(Tresorerie.id == tresorerie_station_id).first()

    solde_actuel = float(tresorerie.solde_tresorerie) if tresorerie and tresorerie.solde_tresorerie is not None else 0.0

    # Vérifier si le solde est suffisant
    solde_suffisant = solde_actuel >= montant_paiement

    return {
        "solde_actuel": solde_actuel,
        "montant_paiement": montant_paiement,
        "solde_suffisant": solde_suffisant
    }


def valider_paiement_achat_carburant(
    db: Session,
    tresorerie_station_id: UUID,
    montant_paiement: float
) -> bool:
    """
    Valide qu'un paiement d'achat de carburant peut être effectué avec la trésorerie spécifiée.
    
    Args:
        db: Session de base de données
        tresorerie_station_id: ID de la trésorerie station concernée
        montant_paiement: Montant du paiement à effectuer
    
    Returns:
        bool: True si le paiement est valide, lève une exception sinon
    """
    validation_result = verifier_solde_tresorerie_suffisant(
        db,
        tresorerie_station_id,
        montant_paiement
    )

    if not validation_result["solde_suffisant"]:
        raise HTTPException(
            status_code=400,
            detail=f"Solde de trésorerie insuffisant. Solde actuel: {validation_result['solde_actuel']}, Montant du paiement: {validation_result['montant_paiement']}"
        )

    return True