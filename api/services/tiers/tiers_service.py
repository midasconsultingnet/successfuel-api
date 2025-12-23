"""
Service pour la gestion des tiers (fournisseurs, clients, employés, etc.)

Ce module contient les fonctions pour créer, lire, mettre à jour et supprimer
des tiers dans l'application Succès Fuel.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...models.tiers import Tiers
from ...models.journal_action_utilisateur import JournalActionUtilisateur
from ...services.utilisateurs.utilisateur_service import get_utilisateur_by_id
from ...translations import get_message  # Importation du système de traduction


def creer_tiers(
    db: Session,
    compagnie_id: UUID,
    type_tiers: str,
    nom: str,
    email: Optional[str] = None,
    telephone: Optional[str] = None,
    adresse: Optional[str] = None,
    donnees_personnelles: Optional[dict] = None,
    utilisateur_id: Optional[UUID] = None,
    station_ids: Optional[List[str]] = None,
    metadonnees: Optional[dict] = None,
    type_paiement: Optional[str] = None,
    delai_paiement: Optional[str] = None,
    acompte_requis: Optional[float] = None,
    seuil_credit: Optional[float] = None
) -> Tiers:
    """
    Crée un nouveau tiers (fournisseur, client, employé, etc.).

    Args:
        db: Session de base de données
        compagnie_id: ID de la compagnie à laquelle appartient le tiers
        type_tiers: Type de tiers ('client', 'fournisseur', 'employé')
        nom: Nom du tiers
        email: Email du tiers (optionnel)
        telephone: Téléphone du tiers (optionnel)
        adresse: Adresse du tiers (optionnel)
        donnees_personnelles: Données spécifiques selon le type (optionnel)
        utilisateur_id: ID de l'utilisateur effectuant l'action (optionnel)
        station_ids: Liste des IDs des stations associées (optionnel)
        metadonnees: Métadonnées additionnelles (optionnel)
        type_paiement: Type de paiement pour les fournisseurs (optionnel)
        delai_paiement: Délai de paiement pour les fournisseurs (optionnel)
        acompte_requis: Pourcentage d'acompte requis (optionnel)
        seuil_credit: Montant maximum de crédit autorisé (optionnel)

    Returns:
        Tiers: Le tiers nouvellement créé
    """
    # Vérifier que le type est valide
    if type_tiers not in ['client', 'fournisseur', 'employé']:
        raise ValueError(get_message("INVALID_TIERS_TYPE", "Le type de tiers doit être 'client', 'fournisseur' ou 'employé'"))

    # Vérifier que le nom n'est pas vide
    if not nom or not nom.strip():
        raise ValueError(get_message("TIERS_NAME_REQUIRED", "Le nom du tiers est requis"))

    # Créer le tiers
    tiers = Tiers(
        compagnie_id=compagnie_id,
        type=type_tiers,
        nom=nom.strip(),
        email=email,
        telephone=telephone,
        adresse=adresse,
        donnees_personnelles=donnees_personnelles or {},
        station_ids=station_ids or [],
        metadonnees=metadonnees or {},
        type_paiement=type_paiement,
        delai_paiement=delai_paiement,
        acompte_requis=acompte_requis,
        seuil_credit=seuil_credit
    )

    db.add(tiers)
    db.commit()
    db.refresh(tiers)

    # Enregistrer l'action dans le journal
    if utilisateur_id:
        journal = JournalActionUtilisateur(
            utilisateur_id=utilisateur_id,
            action="création",
            type_ressource="tiers",
            ressource_id=tiers.id,
            description=f"Création du tiers {tiers.nom} ({tiers.type})"
        )
        db.add(journal)
        db.commit()

    return tiers


def obtenir_tiers_par_id(db: Session, tiers_id: UUID) -> Optional[Tiers]:
    """
    Récupère un tiers par son ID.

    Args:
        db: Session de base de données
        tiers_id: ID du tiers à récupérer

    Returns:
        Tiers: Le tiers correspondant ou None s'il n'existe pas
    """
    return db.query(Tiers).filter(Tiers.id == tiers_id).first()


def obtenir_tiers_par_compagnie(db: Session, compagnie_id: UUID, type_tiers: Optional[str] = None) -> List[Tiers]:
    """
    Récupère tous les tiers d'une compagnie spécifique, optionnellement filtrés par type.

    Args:
        db: Session de base de données
        compagnie_id: ID de la compagnie
        type_tiers: Type de tiers à filtrer (optionnel)

    Returns:
        List[Tiers]: Liste des tiers correspondant aux critères
    """
    query = db.query(Tiers).filter(Tiers.compagnie_id == compagnie_id, Tiers.est_actif == True)

    if type_tiers:
        query = query.filter(Tiers.type == type_tiers)

    return query.all()


def mettre_a_jour_tiers(
    db: Session,
    tiers_id: UUID,
    nom: Optional[str] = None,
    email: Optional[str] = None,
    telephone: Optional[str] = None,
    adresse: Optional[str] = None,
    statut: Optional[str] = None,
    donnees_personnelles: Optional[dict] = None,
    utilisateur_id: Optional[UUID] = None,
    station_ids: Optional[List[str]] = None,
    metadonnees: Optional[dict] = None,
    type_paiement: Optional[str] = None,
    delai_paiement: Optional[str] = None,
    acompte_requis: Optional[float] = None,
    seuil_credit: Optional[float] = None
) -> Optional[Tiers]:
    """
    Met à jour les informations d'un tiers existant.

    Args:
        db: Session de base de données
        tiers_id: ID du tiers à mettre à jour
        nom: Nouveau nom du tiers (optionnel)
        email: Nouvel email du tiers (optionnel)
        telephone: Nouveau téléphone du tiers (optionnel)
        adresse: Nouvelle adresse du tiers (optionnel)
        statut: Nouveau statut ('actif', 'inactif', 'supprimé') (optionnel)
        donnees_personnelles: Nouvelles données spécifiques (optionnel)
        utilisateur_id: ID de l'utilisateur effectuant l'action (optionnel)
        station_ids: Nouvelle liste des IDs des stations associées (optionnel)
        metadonnees: Nouvelles métadonnées (optionnel)
        type_paiement: Nouveau type de paiement (optionnel)
        delai_paiement: Nouveau délai de paiement (optionnel)
        acompte_requis: Nouveau pourcentage d'acompte requis (optionnel)
        seuil_credit: Nouveau montant maximum de crédit autorisé (optionnel)

    Returns:
        Tiers: Le tiers mis à jour ou None s'il n'existe pas
    """
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()

    if not tiers:
        return None

    # Mettre à jour les champs si des valeurs sont fournies
    if nom is not None:
        tiers.nom = nom.strip()
    if email is not None:
        tiers.email = email
    if telephone is not None:
        tiers.telephone = telephone
    if adresse is not None:
        tiers.adresse = adresse
    if statut is not None:
        if statut in ['actif', 'inactif', 'supprimé']:
            tiers.statut = statut
        else:
            raise ValueError(get_message("INVALID_TIERS_STATUS", "Le statut doit être 'actif', 'inactif' ou 'supprimé'"))
    if donnees_personnelles is not None:
        tiers.donnees_personnelles = donnees_personnelles
    if station_ids is not None:
        tiers.station_ids = station_ids
    if metadonnees is not None:
        tiers.metadonnees = metadonnees
    if type_paiement is not None:
        tiers.type_paiement = type_paiement
    if delai_paiement is not None:
        tiers.delai_paiement = delai_paiement
    if acompte_requis is not None:
        tiers.acompte_requis = acompte_requis
    if seuil_credit is not None:
        tiers.seuil_credit = seuil_credit

    db.commit()
    db.refresh(tiers)

    # Enregistrer l'action dans le journal
    if utilisateur_id:
        utilisateur = get_utilisateur_by_id(db, utilisateur_id)
        nom_utilisateur = utilisateur.nom if utilisateur else "Inconnu"
        
        journal = JournalActionUtilisateur(
            utilisateur_id=utilisateur_id,
            action="mise à jour",
            type_ressource="tiers",
            ressource_id=tiers.id,
            description=f"Mise à jour du tiers {tiers.nom} par {nom_utilisateur}"
        )
        db.add(journal)
        db.commit()

    return tiers


def supprimer_tiers(db: Session, tiers_id: UUID, utilisateur_id: Optional[UUID] = None) -> bool:
    """
    Supprime un tiers (soft delete) en mettant son statut à 'supprimé'.

    Args:
        db: Session de base de données
        tiers_id: ID du tiers à supprimer
        utilisateur_id: ID de l'utilisateur effectuant l'action (optionnel)

    Returns:
        bool: True si le tiers a été supprimé, False s'il n'existait pas
    """
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()

    if not tiers:
        return False

    # Soft delete - changer le statut à 'supprimé' et désactiver
    tiers.statut = "supprimé"
    tiers.est_actif = False

    db.commit()

    # Enregistrer l'action dans le journal
    if utilisateur_id:
        utilisateur = get_utilisateur_by_id(db, utilisateur_id)
        nom_utilisateur = utilisateur.nom if utilisateur else "Inconnu"
        
        journal = JournalActionUtilisateur(
            utilisateur_id=utilisateur_id,
            action="suppression",
            type_ressource="tiers",
            ressource_id=tiers.id,
            description=f"Suppression du tiers {tiers.nom} par {nom_utilisateur}"
        )
        db.add(journal)
        db.commit()

    return True


def rechercher_tiers(
    db: Session,
    compagnie_id: UUID,
    recherche: str,
    type_tiers: Optional[str] = None
) -> List[Tiers]:
    """
    Recherche des tiers par nom ou email dans une compagnie spécifique.

    Args:
        db: Session de base de données
        compagnie_id: ID de la compagnie
        recherche: Terme de recherche
        type_tiers: Type de tiers à filtrer (optionnel)

    Returns:
        List[Tiers]: Liste des tiers correspondant à la recherche
    """
    query = db.query(Tiers).filter(
        Tiers.compagnie_id == compagnie_id,
        Tiers.est_actif == True,
        (Tiers.nom.ilike(f"%{recherche}%")) | (Tiers.email.ilike(f"%{recherche}%"))
    )

    if type_tiers:
        query = query.filter(Tiers.type == type_tiers)

    return query.all()


def activer_tiers(db: Session, tiers_id: UUID, utilisateur_id: Optional[UUID] = None) -> Optional[Tiers]:
    """
    Réactive un tiers en mettant son statut à 'actif'.

    Args:
        db: Session de base de données
        tiers_id: ID du tiers à activer
        utilisateur_id: ID de l'utilisateur effectuant l'action (optionnel)

    Returns:
        Tiers: Le tiers réactivé ou None s'il n'existait pas
    """
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()

    if not tiers:
        return None

    tiers.statut = "actif"
    tiers.est_actif = True

    db.commit()
    db.refresh(tiers)

    # Enregistrer l'action dans le journal
    if utilisateur_id:
        utilisateur = get_utilisateur_by_id(db, utilisateur_id)
        nom_utilisateur = utilisateur.nom if utilisateur else "Inconnu"
        
        journal = JournalActionUtilisateur(
            utilisateur_id=utilisateur_id,
            action="activation",
            type_ressource="tiers",
            ressource_id=tiers.id,
            description=f"Activation du tiers {tiers.nom} par {nom_utilisateur}"
        )
        db.add(journal)
        db.commit()

    return tiers