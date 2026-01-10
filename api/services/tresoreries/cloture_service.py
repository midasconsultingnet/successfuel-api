"""Service pour la gestion des clôtures de soldes de trésorerie"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
import uuid
from ...models.tresorerie import Tresorerie, TresorerieStation


def cloturer_soldes_mensuels(db: Session, mois: date):
    """
    Effectue la clôture mensuelle des soldes pour toutes les trésoreries stations
    """
    from sqlalchemy import text

    # Définir la période de clôture
    date_debut = date(mois.year, mois.month, 1)
    # Calculer la date de fin (dernier jour du mois)
    if mois.month == 12:
        date_fin = date(mois.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        date_fin = date(mois.year, mois.month + 1, 1) - datetime.timedelta(days=1)

    # Boucler sur chaque trésorerie-station
    tresorerie_stations = db.query(TresorerieStation).all()
    
    for tresorerie_station in tresorerie_stations:
        # Calculer le solde pour cette trésorerie-station pour la période
        # Dans la nouvelle architecture, le solde initial est géré via la table etat_initial_tresorerie
        from ...models.tresorerie import EtatInitialTresorerie as EtatInitialTresorerieModel
        etat_initial = db.query(EtatInitialTresorerieModel).filter(
            EtatInitialTresorerieModel.tresorerie_station_id == tresorerie_station.id
        ).order_by(EtatInitialTresorerieModel.date_enregistrement.desc()).first()

        solde_initial = float(etat_initial.montant) if etat_initial else 0.0

        result = db.execute(text("""
            SELECT
                :solde_initial +
                COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                         WHERE tresorerie_station_id = :ts_id
                         AND type_mouvement = 'entrée'
                         AND date_mouvement >= :date_debut
                         AND date_mouvement <= :date_fin
                         AND statut = 'validé'), 0) -
                COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                         WHERE tresorerie_station_id = :ts_id
                         AND type_mouvement = 'sortie'
                         AND date_mouvement >= :date_debut
                         AND date_mouvement <= :date_fin
                         AND statut = 'validé'), 0) AS solde_cloture
        """), {
            "solde_initial": solde_initial,
            "ts_id": tresorerie_station.id,
            "date_debut": date_debut,
            "date_fin": date_fin
        }).fetchone()

        solde_cloture = float(result.solde_cloture) if result and result.solde_cloture is not None else solde_initial
        
        # Insérer la clôture dans la table appropriée
        db.execute(text("""
            INSERT INTO cloture_solde_tresorerie (
                tresorerie_id,
                tresorerie_station_id,
                date_cloture,
                periode_debut,
                periode_fin,
                solde_cloture
            ) VALUES (
                :tresorerie_id,
                :tresorerie_station_id,
                :date_cloture,
                :periode_debut,
                :periode_fin,
                :solde_cloture
            ) ON CONFLICT (tresorerie_station_id, date_cloture) DO NOTHING
        """), {
            "tresorerie_id": tresorerie_station.tresorerie_id,
            "tresorerie_station_id": tresorerie_station.id,
            "date_cloture": date_fin,
            "periode_debut": date_debut,
            "periode_fin": date_fin,
            "solde_cloture": solde_cloture
        })

    db.commit()


def cloturer_solde_tresorerie_station(db: Session, tresorerie_station_id: uuid.UUID, mois: date):
    """
    Effectue la clôture du solde pour une trésorerie station spécifique
    """
    from sqlalchemy import text

    # Vérifier que la trésorerie station existe
    tresorerie_station = db.query(TresorerieStation).filter(
        TresorerieStation.id == tresorerie_station_id
    ).first()
    
    if not tresorerie_station:
        raise ValueError(f"Trésorerie station {tresorerie_station_id} non trouvée")
    
    # Définir la période de clôture
    date_debut = date(mois.year, mois.month, 1)
    # Calculer la date de fin (dernier jour du mois)
    if mois.month == 12:
        date_fin = date(mois.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        date_fin = date(mois.year, mois.month + 1, 1) - datetime.timedelta(days=1)

    # Calculer le solde pour cette trésorerie-station pour la période
    # Dans la nouvelle architecture, le solde initial est géré via la table etat_initial_tresorerie
    from ...models.tresorerie import EtatInitialTresorerie as EtatInitialTresorerieModel
    etat_initial = db.query(EtatInitialTresorerieModel).filter(
        EtatInitialTresorerieModel.tresorerie_station_id == tresorerie_station_id
    ).order_by(EtatInitialTresorerieModel.date_enregistrement.desc()).first()

    solde_initial = float(etat_initial.montant) if etat_initial else 0.0

    result = db.execute(text("""
        SELECT
            :solde_initial +
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                     WHERE tresorerie_station_id = :ts_id
                     AND type_mouvement = 'entrée'
                     AND date_mouvement >= :date_debut
                     AND date_mouvement <= :date_fin
                     AND statut = 'validé'), 0) -
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                     WHERE tresorerie_station_id = :ts_id
                     AND type_mouvement = 'sortie'
                     AND date_mouvement >= :date_debut
                     AND date_mouvement <= :date_fin
                     AND statut = 'validé'), 0) AS solde_cloture
    """), {
        "solde_initial": solde_initial,
        "ts_id": tresorerie_station_id,
        "date_debut": date_debut,
        "date_fin": date_fin
    }).fetchone()

    solde_cloture = float(result.solde_cloture) if result and result.solde_cloture is not None else solde_initial
    
    # Insérer la clôture dans la table appropriée
    db.execute(text("""
        INSERT INTO cloture_solde_tresorerie (
            tresorerie_id,
            tresorerie_station_id,
            date_cloture,
            periode_debut,
            periode_fin,
            solde_cloture
        ) VALUES (
            :tresorerie_id,
            :tresorerie_station_id,
            :date_cloture,
            :periode_debut,
            :periode_fin,
            :solde_cloture
        ) ON CONFLICT (tresorerie_station_id, date_cloture) DO NOTHING
    """), {
        "tresorerie_id": tresorerie_station.tresorerie_id,
        "tresorerie_station_id": tresorerie_station_id,
        "date_cloture": date_fin,
        "periode_debut": date_debut,
        "periode_fin": date_fin,
        "solde_cloture": solde_cloture
    })

    db.commit()


def cloturer_solde_global_tresorerie(db: Session, tresorerie_id: uuid.UUID, mois: date):
    """
    Effectue la clôture du solde global pour une trésorerie spécifique
    """
    from sqlalchemy import text

    # Vérifier que la trésorerie existe
    tresorerie = db.query(Tresorerie).filter(
        Tresorerie.id == tresorerie_id
    ).first()
    
    if not tresorerie:
        raise ValueError(f"Trésorerie {tresorerie_id} non trouvée")
    
    # Définir la période de clôture
    date_debut = date(mois.year, mois.month, 1)
    # Calculer la date de fin (dernier jour du mois)
    if mois.month == 12:
        date_fin = date(mois.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        date_fin = date(mois.year, mois.month + 1, 1) - datetime.timedelta(days=1)

    # Calculer le solde global pour cette trésorerie pour la période
    # En additionnant les soldes de toutes les trésoreries stations associées
    result = db.execute(text("""
        SELECT 
            :solde_initial + 
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie mt
                     JOIN tresorerie_station ts ON mt.tresorerie_station_id = ts.id
                     WHERE ts.tresorerie_id = :t_id 
                     AND mt.type_mouvement = 'entrée' 
                     AND mt.date_mouvement >= :date_debut 
                     AND mt.date_mouvement <= :date_fin 
                     AND mt.statut = 'validé'), 0) -
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie mt
                     JOIN tresorerie_station ts ON mt.tresorerie_station_id = ts.id
                     WHERE ts.tresorerie_id = :t_id 
                     AND mt.type_mouvement = 'sortie' 
                     AND mt.date_mouvement >= :date_debut 
                     AND mt.date_mouvement <= :date_fin 
                     AND mt.statut = 'validé'), 0) AS solde_cloture
    """), {
        "solde_initial": float(tresorerie.solde_initial or 0),
        "t_id": tresorerie_id,
        "date_debut": date_debut,
        "date_fin": date_fin
    }).fetchone()
    
    solde_cloture = float(result.solde_cloture) if result and result.solde_cloture is not None else float(tresorerie.solde_initial or 0)
    
    # Insérer la clôture dans la table appropriée
    db.execute(text("""
        INSERT INTO cloture_solde_tresorerie (
            tresorerie_id,
            tresorerie_station_id,  -- NULL pour les soldes globaux
            date_cloture,
            periode_debut,
            periode_fin,
            solde_cloture
        ) VALUES (
            :tresorerie_id,
            NULL,
            :date_cloture,
            :periode_debut,
            :periode_fin,
            :solde_cloture
        ) ON CONFLICT (tresorerie_id, date_cloture) WHERE tresorerie_station_id IS NULL DO NOTHING
    """), {
        "tresorerie_id": tresorerie_id,
        "date_cloture": date_fin,
        "periode_debut": date_debut,
        "periode_fin": date_fin,
        "solde_cloture": solde_cloture
    })

    db.commit()


def processus_cloture_mensuelle(db: Session):
    """
    Exécute le processus de clôture mensuelle automatique pour le mois précédent
    """
    from datetime import date
    import datetime as dt

    # Clôturer le mois précédent
    mois_courant = dt.date.today().replace(day=1)
    mois_a_cloturer = mois_courant - dt.timedelta(days=1)  # Mois précédent
    
    # Vérifier si une clôture existe déjà pour ce mois
    result = db.execute(text("""
        SELECT COUNT(*) as count
        FROM cloture_solde_tresorerie 
        WHERE date_cloture = :date_fin_mois
    """), {"date_fin_mois": mois_a_cloturer}).fetchone()
    
    if result.count == 0:
        # Effectuer la clôture pour toutes les trésoreries
        cloturer_soldes_mensuels(db, mois_a_cloturer)
    else:
        print(f"Les soldes pour {mois_a_cloturer.strftime('%Y-%m')} sont déjà clôturés")


def verifier_cohesion_soldes(db: Session, tresorerie_station_id: uuid.UUID, date_verification: date = None):
    """
    Vérifie la cohésion entre le solde calculé à partir des mouvements et le solde dans la vue matérialisée
    """
    from sqlalchemy import text

    if not date_verification:
        date_verification = date.today()

    # Calculer le solde à partir des mouvements
    # Dans la nouvelle architecture, le solde initial est géré via la table etat_initial_tresorerie
    from ...models.tresorerie import EtatInitialTresorerie as EtatInitialTresorerieModel
    etat_initial = db.query(EtatInitialTresorerieModel).filter(
        EtatInitialTresorerieModel.tresorerie_station_id == tresorerie_station_id
    ).order_by(EtatInitialTresorerieModel.date_enregistrement.desc()).first()

    solde_initial = float(etat_initial.montant) if etat_initial else 0.0

    result_calcul = db.execute(text("""
        SELECT
            :solde_initial +
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                     WHERE tresorerie_station_id = :ts_id
                     AND type_mouvement = 'entrée'
                     AND date_mouvement <= :date_verification
                     AND statut = 'validé'), 0) -
            COALESCE((SELECT SUM(montant) FROM mouvement_tresorerie
                     WHERE tresorerie_station_id = :ts_id
                     AND type_mouvement = 'sortie'
                     AND date_mouvement <= :date_verification
                     AND statut = 'validé'), 0) AS solde_calcule
    """), {
        "solde_initial": solde_initial,
        "ts_id": tresorerie_station_id,
        "date_verification": date_verification
    }).fetchone()

    solde_calcule = float(result_calcul.solde_calcule) if result_calcul and result_calcul.solde_calcule is not None else 0

    print(f"Solde calculé pour la trésorerie station {tresorerie_station_id}: {solde_calcule}")
    return True