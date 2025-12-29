"""
Service pour la gestion des soldes des tiers (fournisseurs, clients, etc.)

Ce module contient les fonctions pour calculer, mettre à jour et gérer
les soldes des tiers dans l'application Succès Fuel.
"""

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ...models.tiers import Tiers, SoldeTiers, MouvementTiers
from ...models.achat_carburant import AchatCarburant, PaiementAchatCarburant
from ...models.mouvement_financier import Avoir


def calculer_solde_fournisseur(db: Session, tiers_id: UUID, station_id: UUID = None) -> float:
    """
    Calcule le solde actuel d'un fournisseur en fonction des achats et des paiements.
    
    Args:
        db: Session de base de données
        tiers_id: ID du fournisseur
        station_id: ID de la station (facultatif, pour filtrer par station)
    
    Returns:
        float: Solde du fournisseur (positif = dette du fournisseur, négatif = créance du fournisseur)
    """
    # Calcul du montant total des achats
    achats_query = db.query(AchatCarburant).filter(
        AchatCarburant.fournisseur_id == tiers_id,
        AchatCarburant.statut != "annulé"
    )
    
    if station_id:
        achats_query = achats_query.filter(
            AchatCarburant.compagnie_id == station_id
        )
    
    achats = achats_query.all()
    
    # Calcul du montant total des achats
    montant_total_achats = sum(achat.montant_total for achat in achats if achat.montant_total)
    
    # Calcul du montant total des paiements effectués
    paiements_query = db.query(PaiementAchatCarburant).join(
        AchatCarburant
    ).filter(
        AchatCarburant.fournisseur_id == tiers_id,
        AchatCarburant.statut != "annulé",
        PaiementAchatCarburant.statut != "annulé"
    )
    
    if station_id:
        paiements_query = paiements_query.filter(
            AchatCarburant.compagnie_id == station_id
        )
    
    paiements = paiements_query.all()
    
    montant_total_paiements = sum(paiement.montant for paiement in paiements if paiement.montant)
    
    # Calcul du solde : montant_total_achats - montant_total_paiements
    # Si positif : dette du fournisseur (on lui doit de l'argent)
    # Si négatif : créance du fournisseur (il nous doit de l'argent)
    solde = montant_total_achats - montant_total_paiements
    
    return solde


def mettre_a_jour_solde_fournisseur(db: Session, tiers_id: UUID, station_id: UUID, utilisateur_id: UUID) -> SoldeTiers:
    """
    Met à jour le solde d'un fournisseur dans la table SoldeTiers.
    
    Args:
        db: Session de base de données
        tiers_id: ID du fournisseur
        station_id: ID de la station
        utilisateur_id: ID de l'utilisateur effectuant la mise à jour
    
    Returns:
        SoldeTiers: L'objet SoldeTiers mis à jour
    """
    # Calculer le solde actuel
    nouveau_solde = calculer_solde_fournisseur(db, tiers_id, station_id)
    
    # Vérifier si un solde existe déjà pour ce tiers et cette station
    solde_existant = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id,
        SoldeTiers.station_id == station_id
    ).first()
    
    if solde_existant:
        # Mettre à jour le solde existant
        solde_existant.montant_actuel = nouveau_solde
        solde_existant.date_derniere_mise_a_jour = db.query(AchatCarburant).filter(
            AchatCarburant.fournisseur_id == tiers_id
        ).order_by(AchatCarburant.date_modification.desc()).first().date_modification if db.query(AchatCarburant).filter(
            AchatCarburant.fournisseur_id == tiers_id
        ).first() else None
    else:
        # Créer un nouveau solde
        solde_existant = SoldeTiers(
            tiers_id=tiers_id,
            station_id=station_id,
            montant_initial=0,  # Le solde initial est souvent zéro pour les nouveaux tiers
            montant_actuel=nouveau_solde,
            devise="XOF"  # Devise par défaut
        )
        db.add(solde_existant)
    
    db.commit()
    
    from datetime import datetime

    # Créer un mouvement pour enregistrer cette mise à jour
    mouvement = MouvementTiers(
        tiers_id=tiers_id,
        station_id=station_id,
        type_mouvement="débit" if nouveau_solde > 0 else "crédit",  # "débit" si dette, "crédit" si créance
        montant=abs(nouveau_solde),
        date_mouvement=datetime.now(),  # Ajouter la date du mouvement
        description="Mise à jour du solde fournisseur",
        reference="SOLDE_UPDATE",
        statut="validé",
        module_origine="tiers",  # Ajouter le module d'origine
        reference_origine="SOLDE_UPDATE",  # Ajouter la référence d'origine
        utilisateur_id=utilisateur_id,  # Ajouter l'ID de l'utilisateur
        est_annule=False,  # Par défaut, le mouvement n'est pas annulé
        transaction_source_id=None,  # ID de la transaction source (achat, vente, etc.)
        type_transaction_source=None  # Type de la transaction source
    )
    db.add(mouvement)
    db.commit()
    
    return solde_existant


def obtenir_solde_fournisseur(db: Session, tiers_id: UUID, station_id: UUID = None) -> Optional[SoldeTiers]:
    """
    Récupère le solde enregistré d'un fournisseur.
    
    Args:
        db: Session de base de données
        tiers_id: ID du fournisseur
        station_id: ID de la station (facultatif)
    
    Returns:
        SoldeTiers: L'objet SoldeTiers ou None s'il n'existe pas
    """
    query = db.query(SoldeTiers).filter(
        SoldeTiers.tiers_id == tiers_id
    )
    
    if station_id:
        query = query.filter(
            SoldeTiers.station_id == station_id
        )
    
    return query.first()


def calculer_solde_achat(db: Session, achat_id: UUID) -> float:
    """
    Calcule le solde restant d'un achat spécifique (montant total - paiements).
    
    Args:
        db: Session de base de données
        achat_id: ID de l'achat
    
    Returns:
        float: Solde restant de l'achat (positif = dette, négatif = créance)
    """
    # Récupérer l'achat
    achat = db.query(AchatCarburant).filter(
        AchatCarburant.id == achat_id
    ).first()
    
    if not achat:
        raise ValueError(f"L'achat avec l'ID {achat_id} n'existe pas")
    
    # Calculer le total des paiements pour cet achat
    total_paiements = db.query(PaiementAchatCarburant).filter(
        PaiementAchatCarburant.achat_carburant_id == achat_id,
        PaiementAchatCarburant.statut != "annulé"
    ).with_entities(db.func.sum(PaiementAchatCarburant.montant)).scalar() or 0
    
    # Calcul du solde : montant_total - total_paiements
    solde_restant = achat.montant_total - total_paiements
    
    return solde_restant


def mettre_a_jour_solde_apres_paiement(db: Session, achat_id: UUID, utilisateur_id: UUID) -> None:
    """
    Met à jour le solde du fournisseur après un nouveau paiement.
    
    Args:
        db: Session de base de données
        achat_id: ID de l'achat concerné par le paiement
        utilisateur_id: ID de l'utilisateur effectuant le paiement
    """
    # Récupérer l'achat pour obtenir le fournisseur et la station
    achat = db.query(AchatCarburant).filter(
        AchatCarburant.id == achat_id
    ).first()
    
    if not achat:
        raise ValueError(f"L'achat avec l'ID {achat_id} n'existe pas")
    
    # Mettre à jour le solde du fournisseur
    mettre_a_jour_solde_fournisseur(
        db=db,
        tiers_id=achat.fournisseur_id,
        station_id=achat.station_id if hasattr(achat, 'station_id') else achat.ligne_achat_carburant[0].station_id if achat.ligne_achat_carburant else None,
        utilisateur_id=utilisateur_id
    )


def valider_montant_paiements_achat(db: Session, achat_id: UUID, montant_paiements: float) -> bool:
    """
    Valide que le montant total des paiements ne dépasse pas le montant total de l'achat.

    Args:
        db: Session de base de données
        achat_id: ID de l'achat
        montant_paiements: Montant total des paiements à valider

    Returns:
        bool: True si les paiements sont valides, False sinon
    """
    # Récupérer l'achat pour obtenir le montant total
    achat = db.query(AchatCarburant).filter(
        AchatCarburant.id == achat_id
    ).first()

    if not achat:
        raise ValueError(f"L'achat avec l'ID {achat_id} n'existe pas")

    # Calculer le solde restant de l'achat
    solde_restant = calculer_solde_achat(db, achat_id)

    # Vérifier si le montant des paiements dépasse le solde restant
    # Si le solde est négatif (créance), on peut accepter un paiement plus important
    if solde_restant > 0 and montant_paiements > solde_restant:
        return False  # Paiement trop important par rapport au solde

    return True


def mettre_a_jour_solde_apres_achat(db: Session, achat_id: UUID, utilisateur_id: UUID) -> None:
    """
    Met à jour le solde du fournisseur après la création d'un nouvel achat.

    Args:
        db: Session de base de données
        achat_id: ID du nouvel achat
        utilisateur_id: ID de l'utilisateur effectuant l'achat
    """
    # Récupérer l'achat pour obtenir le fournisseur et la station
    achat = db.query(AchatCarburant).filter(
        AchatCarburant.id == achat_id
    ).first()

    if not achat:
        raise ValueError(f"L'achat avec l'ID {achat_id} n'existe pas")

    # Mettre à jour le solde du fournisseur
    mettre_a_jour_solde_fournisseur(
        db=db,
        tiers_id=achat.fournisseur_id,
        station_id=achat.station_id if hasattr(achat, 'station_id') else achat.ligne_achat_carburant[0].station_id if achat.ligne_achat_carburant else None,
        utilisateur_id=utilisateur_id
    )


def enregistrer_mouvement_tiers(
    db: Session,
    tiers_id: UUID,
    station_id: UUID,
    type_mouvement: str,
    montant: float,
    utilisateur_id: UUID,
    description: str,
    module_origine: str,
    reference_origine: str,
    transaction_source_id: UUID = None,
    type_transaction_source: str = None,
    est_annule: bool = False
) -> MouvementTiers:
    """
    Enregistre un mouvement de tiers avec les informations de transaction source.

    Args:
        db: Session de base de données
        tiers_id: ID du tiers concerné
        station_id: ID de la station
        type_mouvement: Type de mouvement ('entrée' ou 'sortie')
        montant: Montant du mouvement
        utilisateur_id: ID de l'utilisateur effectuant le mouvement
        description: Description du mouvement
        module_origine: Module d'origine du mouvement
        reference_origine: Référence d'origine du mouvement
        transaction_source_id: ID de la transaction source (achat, vente, etc.)
        type_transaction_source: Type de la transaction source
        est_annule: Indique si le mouvement est annulé

    Returns:
        MouvementTiers: Le mouvement créé
    """
    from datetime import datetime

    mouvement = MouvementTiers(
        tiers_id=tiers_id,
        station_id=station_id,
        type_mouvement=type_mouvement,
        montant=montant,
        date_mouvement=datetime.now(),
        description=description,
        reference=f"{type_transaction_source}-{transaction_source_id}" if type_transaction_source and transaction_source_id else "MVT-UNDEF",
        statut="validé",
        module_origine=module_origine,
        reference_origine=reference_origine,
        utilisateur_id=utilisateur_id,
        est_annule=est_annule,
        transaction_source_id=transaction_source_id,
        type_transaction_source=type_transaction_source
    )

    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)

    return mouvement