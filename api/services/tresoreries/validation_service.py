from sqlalchemy.orm import Session
from uuid import UUID
from ...models.tresorerie import TresorerieStation
from ...exceptions import InsufficientFundsException


def valider_paiement_achat_carburant(
    db: Session,
    tresorerie_station_id: UUID,
    montant: float
):
    """
    Valide qu'une trésorerie a suffisamment de fonds pour un paiement d'achat de carburant.

    Args:
        db: Session de base de données
        tresorerie_station_id: ID de la trésorerie station
        montant: Montant à valider
    """
    # Utiliser la fonction existante pour récupérer le solde actuel
    from .tresorerie_service import mettre_a_jour_solde_tresorerie

    solde_actuel = mettre_a_jour_solde_tresorerie(db, tresorerie_station_id)

    # Vérifier si le solde est suffisant pour le paiement
    if solde_actuel < montant:
        raise InsufficientFundsException(
            f"Solde insuffisant. Solde actuel: {solde_actuel}, Montant requis: {montant}"
        )