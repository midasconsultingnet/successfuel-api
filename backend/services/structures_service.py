from typing import List, Optional
from sqlalchemy.orm import Session
from models.structures import (
    Pays, Compagnie, Station, BarremageCuve, Pompe, Pistolet,
    HistoriquePrixCarburant, HistoriquePrixArticle, HistoriqueIndexPistolet,
    Cuve, Carburant, FamilleArticle, Article, Fournisseur, Client, Employe, Tresorerie, TypeTiers
)
from datetime import datetime, date
import uuid


def create_pays(
    db: Session, 
    code_pays: str, 
    nom_pays: str, 
    devise_principale: str = 'MGA',
    taux_tva_par_defaut: float = 20.00,
    systeme_comptable: str = 'IFRS',
    date_application_tva: Optional[str] = None,
    statut: str = 'Actif'
) -> Pays:
    """
    Create a new country
    """
    existing_pays = db.query(Pays).filter(Pays.code_pays == code_pays).first()
    if existing_pays:
        raise ValueError(f"Country with code {code_pays} already exists")
    
    db_pays = Pays(
        code_pays=code_pays,
        nom_pays=nom_pays,
        devise_principale=devise_principale,
        taux_tva_par_defaut=taux_tva_par_defaut,
        systeme_comptable=systeme_comptable,
        date_application_tva=date_application_tva,
        statut=statut
    )
    
    db.add(db_pays)
    db.commit()
    db.refresh(db_pays)
    
    return db_pays


def get_pays_by_id(db: Session, pays_id: str) -> Optional[Pays]:
    """
    Get a country by ID
    """
    return db.query(Pays).filter(Pays.id == pays_id).first()


def get_pays_by_code(db: Session, code_pays: str) -> Optional[Pays]:
    """
    Get a country by code
    """
    return db.query(Pays).filter(Pays.code_pays == code_pays).first()


def get_all_pays(db: Session, statut: Optional[str] = None, search: Optional[str] = None) -> List[Pays]:
    """
    Get all countries with optional filters
    """
    query = db.query(Pays)
    
    if statut:
        query = query.filter(Pays.statut == statut)
    
    if search:
        query = query.filter(Pays.nom_pays.ilike(f"%{search}%"))
    
    return query.all()


def update_pays(db: Session, pays_id: str, **kwargs) -> Optional[Pays]:
    """
    Update a country
    """
    pays = db.query(Pays).filter(Pays.id == pays_id).first()
    if not pays:
        return None
    
    for key, value in kwargs.items():
        if hasattr(pays, key):
            setattr(pays, key, value)
    
    pays.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pays)
    
    return pays


def create_compagnie(
    db: Session,
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    nif: Optional[str] = None,
    pays_id: Optional[str] = None,
    devise_principale: str = 'MGA'
) -> Compagnie:
    """
    Create a new company
    """
    existing_compagnie = db.query(Compagnie).filter(Compagnie.code == code).first()
    if existing_compagnie:
        raise ValueError(f"Company with code {code} already exists")
    
    db_compagnie = Compagnie(
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        email=email,
        nif=nif,
        pays_id=pays_id,
        devise_principale=devise_principale
    )
    
    db.add(db_compagnie)
    db.commit()
    db.refresh(db_compagnie)
    
    return db_compagnie


def get_compagnie_by_id(db: Session, compagnie_id: str) -> Optional[Compagnie]:
    """
    Get a company by ID
    """
    return db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()


def get_compagnie_by_code(db: Session, code: str) -> Optional[Compagnie]:
    """
    Get a company by code
    """
    return db.query(Compagnie).filter(Compagnie.code == code).first()


def get_all_compagnies(
    db: Session, 
    statut: Optional[str] = None, 
    pays_id: Optional[str] = None
) -> List[Compagnie]:
    """
    Get all companies with optional filters
    """
    query = db.query(Compagnie)
    
    if statut:
        query = query.filter(Compagnie.statut == statut)
    
    if pays_id:
        query = query.filter(Compagnie.pays_id == pays_id)
    
    return query.all()


def update_compagnie(db: Session, compagnie_id: str, **kwargs) -> Optional[Compagnie]:
    """
    Update a company
    """
    compagnie = db.query(Compagnie).filter(Compagnie.id == compagnie_id).first()
    if not compagnie:
        return None
    
    for key, value in kwargs.items():
        if hasattr(compagnie, key):
            setattr(compagnie, key, value)
    
    compagnie.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(compagnie)
    
    return compagnie


def create_station(
    db: Session,
    compagnie_id: str,
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    pays_id: Optional[str] = None
) -> Station:
    """
    Create a new station
    """
    existing_station = db.query(Station).filter(Station.code == code).first()
    if existing_station:
        raise ValueError(f"Station with code {code} already exists")
    
    db_station = Station(
        compagnie_id=compagnie_id,
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        email=email,
        pays_id=pays_id
    )
    
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    
    return db_station


def get_station_by_id(db: Session, station_id: str) -> Optional[Station]:
    """
    Get a station by ID
    """
    return db.query(Station).filter(Station.id == station_id).first()


def get_station_by_code(db: Session, code: str) -> Optional[Station]:
    """
    Get a station by code
    """
    return db.query(Station).filter(Station.code == code).first()


def get_all_stations(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None,
    pays_id: Optional[str] = None
) -> List[Station]:
    """
    Get all stations with optional filters
    """
    query = db.query(Station)
    
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    
    if statut:
        query = query.filter(Station.statut == statut)
    
    if pays_id:
        query = query.filter(Station.pays_id == pays_id)
    
    return query.all()


def update_station(db: Session, station_id: str, **kwargs) -> Optional[Station]:
    """
    Update a station
    """
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        return None

    for key, value in kwargs.items():
        if hasattr(station, key):
            setattr(station, key, value)

    db.commit()
    db.refresh(station)

    return station


from models.structures import BarremageCuve, Cuve

def get_cuve_by_id(db: Session, cuve_id: str) -> Optional[Cuve]:
    """
    Get a cuve by ID
    """
    return db.query(Cuve).filter(Cuve.id == cuve_id).first()


def create_cuve(
    db: Session,
    station_id: str,
    code: str,
    capacite: float,
    carburant_id: Optional[str] = None,
    compagnie_id: Optional[str] = None,
    temperature: float = 0.0,
    statut: str = 'Actif'
) -> Cuve:
    """
    Create a new cuve
    """
    from models.structures import Cuve
    db_cuve = Cuve(
        station_id=station_id,
        code=code,
        capacite=capacite,
        carburant_id=carburant_id,
        compagnie_id=compagnie_id,
        temperature=temperature,
        statut=statut
    )

    db.add(db_cuve)
    db.commit()
    db.refresh(db_cuve)

    return db_cuve


def get_all_cuves(
    db: Session,
    station_id: Optional[str] = None,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Cuve]:
    """
    Get all cuves with optional filters
    """
    query = db.query(Cuve)

    if station_id:
        query = query.filter(Cuve.station_id == station_id)
    if compagnie_id:
        query = query.filter(Cuve.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Cuve.statut == statut)

    return query.all()


def update_cuve(db: Session, cuve_id: str, **kwargs) -> Optional[Cuve]:
    """
    Update a cuve
    """
    from models.structures import Cuve
    cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
    if cuve:
        for key, value in kwargs.items():
            setattr(cuve, key, value)
        db.commit()
        db.refresh(cuve)
    return cuve


def delete_cuve(db: Session, cuve_id: str) -> bool:
    """
    Delete a cuve
    """
    from models.structures import Cuve
    cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
    if cuve:
        db.delete(cuve)
        db.commit()
        return True
    return False


def get_station_by_id(db: Session, station_id: str) -> Optional[Station]:
    """
    Get a station by ID
    """
    return db.query(Station).filter(Station.id == station_id).first()

def create_barremage_cuves(
    db: Session,
    cuve_id: str,
    station_id: str,
    hauteur: float,
    volume: float,
    compagnie_id: str,
    statut: str = 'Actif'
) -> BarremageCuve:
    """
    Create a new barremage cuve entry
    """
    db_barremage = BarremageCuve(
        cuve_id=cuve_id,
        station_id=station_id,
        hauteur=hauteur,
        volume=volume,
        statut=statut,
        compagnie_id=compagnie_id
    )

    db.add(db_barremage)
    db.commit()
    db.refresh(db_barremage)

    return db_barremage


def get_barremage_cuves_by_id(db: Session, barremage_id: str) -> Optional[BarremageCuve]:
    """
    Get a barremage cuve entry by ID
    """
    return db.query(BarremageCuve).filter(BarremageCuve.id == barremage_id).first()


def get_all_barremage_cuves(
    db: Session,
    cuve_id: Optional[str] = None,
    station_id: Optional[str] = None,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[BarremageCuve]:
    """
    Get all barremage cuve entries with optional filters
    """
    query = db.query(BarremageCuve)

    if cuve_id:
        query = query.filter(BarremageCuve.cuve_id == cuve_id)
    if station_id:
        query = query.filter(BarremageCuve.station_id == station_id)
    if compagnie_id:
        query = query.filter(BarremageCuve.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(BarremageCuve.statut == statut)

    return query.all()


def update_barremage_cuves(db: Session, barremage_id: str, **kwargs) -> Optional[BarremageCuve]:
    """
    Update a barremage cuve entry
    """
    barremage = db.query(BarremageCuve).filter(BarremageCuve.id == barremage_id).first()
    if not barremage:
        return None

    for key, value in kwargs.items():
        if hasattr(barremage, key):
            setattr(barremage, key, value)

    barremage.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(barremage)

    return barremage


def delete_barremage_cuves(db: Session, barremage_id: str) -> bool:
    """
    Delete a barremage cuve entry
    """
    barremage = db.query(BarremageCuve).filter(BarremageCuve.id == barremage_id).first()
    if not barremage:
        return False

    db.delete(barremage)
    db.commit()
    return True


from models.structures import Pompe, Pistolet

def create_pompe(
    db: Session,
    station_id: str,
    code: str,
    compagnie_id: str,
    statut: str = 'Actif'
) -> Pompe:
    """
    Create a new pompe
    """
    db_pompe = Pompe(
        station_id=station_id,
        code=code,
        compagnie_id=compagnie_id,
        statut=statut
    )

    db.add(db_pompe)
    db.commit()
    db.refresh(db_pompe)

    return db_pompe


def get_pompe_by_id(db: Session, pompe_id: str) -> Optional[Pompe]:
    """
    Get a pompe by ID
    """
    return db.query(Pompe).filter(Pompe.id == pompe_id).first()


def get_all_pompes(
    db: Session,
    station_id: Optional[str] = None,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Pompe]:
    """
    Get all pompes with optional filters
    """
    query = db.query(Pompe)

    if station_id:
        query = query.filter(Pompe.station_id == station_id)
    if compagnie_id:
        query = query.filter(Pompe.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Pompe.statut == statut)

    return query.all()


def update_pompe(db: Session, pompe_id: str, **kwargs) -> Optional[Pompe]:
    """
    Update a pompe
    """
    pompe = db.query(Pompe).filter(Pompe.id == pompe_id).first()
    if not pompe:
        return None

    for key, value in kwargs.items():
        if hasattr(pompe, key):
            setattr(pompe, key, value)

    db.commit()
    db.refresh(pompe)

    return pompe


def delete_pompe(db: Session, pompe_id: str) -> bool:
    """
    Delete a pompe
    """
    pompe = db.query(Pompe).filter(Pompe.id == pompe_id).first()
    if not pompe:
        return False

    db.delete(pompe)
    db.commit()
    return True


def create_pistolet(
    db: Session,
    code: str,
    pompe_id: str,
    cuve_id: str,
    index_initiale: float,
    compagnie_id: str,
    statut: str = 'Actif'
) -> Pistolet:
    """
    Create a new pistolet
    """
    db_pistolet = Pistolet(
        code=code,
        pompe_id=pompe_id,
        cuve_id=cuve_id,
        index_initiale=index_initiale,
        compagnie_id=compagnie_id,
        statut=statut
    )

    db.add(db_pistolet)
    db.commit()
    db.refresh(db_pistolet)

    return db_pistolet


def get_pistolet_by_id(db: Session, pistolet_id: str) -> Optional[Pistolet]:
    """
    Get a pistolet by ID
    """
    return db.query(Pistolet).filter(Pistolet.id == pistolet_id).first()


def get_all_pistolets(
    db: Session,
    pompe_id: Optional[str] = None,
    cuve_id: Optional[str] = None,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Pistolet]:
    """
    Get all pistolets with optional filters
    """
    query = db.query(Pistolet)

    if pompe_id:
        query = query.filter(Pistolet.pompe_id == pompe_id)
    if cuve_id:
        query = query.filter(Pistolet.cuve_id == cuve_id)
    if compagnie_id:
        query = query.filter(Pistolet.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Pistolet.statut == statut)

    return query.all()


def update_pistolet(db: Session, pistolet_id: str, **kwargs) -> Optional[Pistolet]:
    """
    Update a pistolet
    """
    pistolet = db.query(Pistolet).filter(Pistolet.id == pistolet_id).first()
    if not pistolet:
        return None

    for key, value in kwargs.items():
        if hasattr(pistolet, key):
            setattr(pistolet, key, value)

    db.commit()
    db.refresh(pistolet)

    return pistolet


def delete_pistolet(db: Session, pistolet_id: str) -> bool:
    """
    Delete a pistolet
    """
    pistolet = db.query(Pistolet).filter(Pistolet.id == pistolet_id).first()
    if not pistolet:
        return False

    db.delete(pistolet)
    db.commit()
    return True


def create_historique_prix_carburant(
    db: Session,
    carburant_id: str,
    prix_achat: float,
    prix_vente: float,
    date_application: date,
    utilisateur_id: Optional[str] = None
) -> HistoriquePrixCarburant:
    """
    Create a new historique prix carburant entry
    """
    db_historique = HistoriquePrixCarburant(
        carburant_id=carburant_id,
        prix_achat=prix_achat,
        prix_vente=prix_vente,
        date_application=date_application,
        utilisateur_id=utilisateur_id
    )

    db.add(db_historique)
    db.commit()
    db.refresh(db_historique)

    return db_historique


def get_historique_prix_carburant_by_id(db: Session, historique_id: str) -> Optional[HistoriquePrixCarburant]:
    """
    Get an historique prix carburant entry by ID
    """
    return db.query(HistoriquePrixCarburant).filter(HistoriquePrixCarburant.id == historique_id).first()


def get_all_historique_prix_carburant(
    db: Session,
    carburant_id: Optional[str] = None,
    date_application: Optional[date] = None
) -> List[HistoriquePrixCarburant]:
    """
    Get all historique prix carburant entries with optional filters
    """
    query = db.query(HistoriquePrixCarburant)

    if carburant_id:
        query = query.filter(HistoriquePrixCarburant.carburant_id == carburant_id)
    if date_application:
        query = query.filter(HistoriquePrixCarburant.date_application == date_application)

    return query.all()


def create_historique_prix_article(
    db: Session,
    article_id: str,
    prix_achat: float,
    prix_vente: float,
    date_application: date,
    utilisateur_id: Optional[str] = None
) -> HistoriquePrixArticle:
    """
    Create a new historique prix article entry
    """
    db_historique = HistoriquePrixArticle(
        article_id=article_id,
        prix_achat=prix_achat,
        prix_vente=prix_vente,
        date_application=date_application,
        utilisateur_id=utilisateur_id
    )

    db.add(db_historique)
    db.commit()
    db.refresh(db_historique)

    return db_historique


def get_historique_prix_article_by_id(db: Session, historique_id: str) -> Optional[HistoriquePrixArticle]:
    """
    Get an historique prix article entry by ID
    """
    return db.query(HistoriquePrixArticle).filter(HistoriquePrixArticle.id == historique_id).first()


def get_all_historique_prix_article(
    db: Session,
    article_id: Optional[str] = None,
    date_application: Optional[date] = None
) -> List[HistoriquePrixArticle]:
    """
    Get all historique prix article entries with optional filters
    """
    query = db.query(HistoriquePrixArticle)

    if article_id:
        query = query.filter(HistoriquePrixArticle.article_id == article_id)
    if date_application:
        query = query.filter(HistoriquePrixArticle.date_application == date_application)

    return query.all()


def create_historique_index_pistolet(
    db: Session,
    pistolet_id: str,
    index_releve: float,
    date_releve: date,
    utilisateur_id: Optional[str] = None,
    observation: Optional[str] = None
) -> HistoriqueIndexPistolet:
    """
    Create a new historique index pistolet entry
    """
    db_historique = HistoriqueIndexPistolet(
        pistolet_id=pistolet_id,
        index_releve=index_releve,
        date_releve=date_releve,
        utilisateur_id=utilisateur_id,
        observation=observation
    )

    db.add(db_historique)
    db.commit()
    db.refresh(db_historique)

    return db_historique


def get_historique_index_pistolet_by_id(db: Session, historique_id: str) -> Optional[HistoriqueIndexPistolet]:
    """
    Get an historique index pistolet entry by ID
    """
    return db.query(HistoriqueIndexPistolet).filter(HistoriqueIndexPistolet.id == historique_id).first()


def get_all_historique_index_pistolet(
    db: Session,
    pistolet_id: Optional[str] = None,
    date_releve: Optional[date] = None
) -> List[HistoriqueIndexPistolet]:
    """
    Get all historique index pistolet entries with optional filters
    """
    query = db.query(HistoriqueIndexPistolet)

    if pistolet_id:
        query = query.filter(HistoriqueIndexPistolet.pistolet_id == pistolet_id)
    if date_releve:
        query = query.filter(HistoriqueIndexPistolet.date_releve == date_releve)

    return query.all()


def create_carburant(
    db: Session,
    code: str,
    libelle: str,
    type_carburant: str,
    compagnie_id: str,
    prix_achat: float = 0,
    prix_vente: float = 0,
    statut: str = 'Actif'
) -> Carburant:
    """
    Create a new carburant
    """
    existing_carburant = db.query(Carburant).filter(Carburant.code == code).first()
    if existing_carburant:
        raise ValueError(f"Carburant with code {code} already exists")

    db_carburant = Carburant(
        code=code,
        libelle=libelle,
        type=type_carburant,
        compagnie_id=compagnie_id,
        prix_achat=prix_achat,
        prix_vente=prix_vente,
        statut=statut
    )

    db.add(db_carburant)
    db.commit()
    db.refresh(db_carburant)

    return db_carburant


def get_carburant_by_id(db: Session, carburant_id: str) -> Optional[Carburant]:
    """
    Get a carburant by ID
    """
    return db.query(Carburant).filter(Carburant.id == carburant_id).first()


def get_carburant_by_code(db: Session, code: str) -> Optional[Carburant]:
    """
    Get a carburant by code
    """
    return db.query(Carburant).filter(Carburant.code == code).first()


def get_all_carburants(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Carburant]:
    """
    Get all carburants with optional filters
    """
    query = db.query(Carburant)

    if compagnie_id:
        query = query.filter(Carburant.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Carburant.statut == statut)

    return query.all()


def update_carburant(db: Session, carburant_id: str, **kwargs) -> Optional[Carburant]:
    """
    Update a carburant
    """
    carburant = db.query(Carburant).filter(Carburant.id == carburant_id).first()
    if not carburant:
        return None

    for key, value in kwargs.items():
        if hasattr(carburant, key):
            setattr(carburant, key, value)

    carburant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(carburant)

    return carburant


def delete_carburant(db: Session, carburant_id: str) -> bool:
    """
    Delete a carburant (logical deletion by setting statut to 'Supprime')
    """
    carburant = db.query(Carburant).filter(Carburant.id == carburant_id).first()
    if not carburant:
        return False

    carburant.statut = "Supprime"
    db.commit()
    return True


def create_article(
    db: Session,
    code: str,
    libelle: str,
    codebarre: Optional[str] = None,
    famille_id: Optional[str] = None,
    unite: str = "Litre",
    compagnie_id: str = None,
    type_article: str = "produit",
    prix_achat: float = 0.0,
    prix_vente: float = 0.0,
    tva: float = 0.0,
    taxes_applicables: Optional[list] = None,
    stock_minimal: float = 0.0,
    statut: str = "Actif"
) -> Article:
    """
    Create a new article
    """
    if taxes_applicables is None:
        taxes_applicables = []

    # Check if an article with the same code already exists for this company
    existing_article = db.query(Article).filter(
        Article.code == code,
        Article.compagnie_id == compagnie_id
    ).first()
    if existing_article:
        raise ValueError(f"Article with code {code} already exists for this company")

    db_article = Article(
        code=code,
        libelle=libelle,
        codebarre=codebarre,
        famille_id=famille_id,
        unite=unite,
        compagnie_id=compagnie_id,
        type_article=type_article,
        prix_achat=prix_achat,
        prix_vente=prix_vente,
        tva=tva,
        taxes_applicables=taxes_applicables,
        stock_minimal=stock_minimal,
        statut=statut
    )

    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    return db_article


def get_article_by_code(db: Session, article_code: str, compagnie_id: Optional[str] = None) -> Optional[Article]:
    """
    Get an article by code, optionally filtered by company
    """
    query = db.query(Article).filter(Article.code == article_code)

    if compagnie_id:
        query = query.filter(Article.compagnie_id == compagnie_id)

    return query.first()


def get_article_by_id(db: Session, article_id: str) -> Optional[Article]:
    """
    Get an article by ID
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_all_carburants(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Carburant]:
    """
    Get all carburants with optional filters
    """
    query = db.query(Carburant)

    if compagnie_id:
        query = query.filter(Carburant.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Carburant.statut == statut)

    return query.all()


def get_all_articles(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Article]:
    """
    Get all articles with optional filters
    """
    query = db.query(Article)

    if compagnie_id:
        query = query.filter(Article.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Article.statut == statut)

    return query.all()


def create_client(
    db: Session,
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    nif: Optional[str] = None,
    email: Optional[str] = None,
    compagnie_id: str = None,
    station_ids: Optional[list] = None,
    type_tiers_id: Optional[str] = None,
    statut: str = "Actif",
    nb_jrs_creance: int = 0,
    devise_facturation: str = "MGA"
) -> Client:
    """
    Create a new client
    """
    if station_ids is None:
        station_ids = []

    # Check if a client with the same code already exists for this company
    existing_client = db.query(Client).filter(
        Client.code == code,
        Client.compagnie_id == compagnie_id
    ).first()
    if existing_client:
        raise ValueError(f"Client with code {code} already exists for this company")

    db_client = Client(
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        nif=nif,
        email=email,
        compagnie_id=compagnie_id,
        station_ids=station_ids,
        type_tiers_id=type_tiers_id,
        statut=statut,
        nb_jrs_creance=nb_jrs_creance,
        devise_facturation=devise_facturation
    )

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


def get_client_by_id(db: Session, client_id: str) -> Optional[Client]:
    """
    Get a client by ID
    """
    return db.query(Client).filter(Client.id == client_id).first()


def get_all_clients(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Client]:
    """
    Get all clients with optional filters
    """
    query = db.query(Client)

    if compagnie_id:
        query = query.filter(Client.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Client.statut == statut)

    return query.all()


def create_fournisseur(
    db: Session,
    code: str,
    nom: str,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    nif: Optional[str] = None,
    email: Optional[str] = None,
    compagnie_id: str = None,
    station_ids: Optional[list] = None,
    type_tiers_id: Optional[str] = None,
    statut: str = "Actif",
    nb_jrs_creance: int = 0
) -> Fournisseur:
    """
    Create a new fournisseur
    """
    if station_ids is None:
        station_ids = []

    # Check if a fournisseur with the same code already exists for this company
    existing_fournisseur = db.query(Fournisseur).filter(
        Fournisseur.code == code,
        Fournisseur.compagnie_id == compagnie_id
    ).first()
    if existing_fournisseur:
        raise ValueError(f"Fournisseur with code {code} already exists for this company")

    db_fournisseur = Fournisseur(
        code=code,
        nom=nom,
        adresse=adresse,
        telephone=telephone,
        nif=nif,
        email=email,
        compagnie_id=compagnie_id,
        station_ids=station_ids,
        type_tiers_id=type_tiers_id,
        statut=statut,
        nb_jrs_creance=nb_jrs_creance
    )

    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)

    return db_fournisseur


def get_fournisseur_by_id(db: Session, fournisseur_id: str) -> Optional[Fournisseur]:
    """
    Get a fournisseur by ID
    """
    return db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()


def get_all_fournisseurs(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Fournisseur]:
    """
    Get all fournisseurs with optional filters
    """
    query = db.query(Fournisseur)

    if compagnie_id:
        query = query.filter(Fournisseur.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Fournisseur.statut == statut)

    return query.all()


def create_employe(
    db: Session,
    code: str,
    nom: str,
    prenom: Optional[str] = None,
    adresse: Optional[str] = None,
    telephone: Optional[str] = None,
    poste: Optional[str] = None,
    salaire_base: float = 0.0,
    avances: float = 0.0,
    creances: float = 0.0,
    station_ids: Optional[list] = None,
    compagnie_id: str = None,
    statut: str = "Actif"
) -> Employe:
    """
    Create a new employe
    """
    if station_ids is None:
        station_ids = []

    # Check if an employe with the same code already exists for this company
    existing_employe = db.query(Employe).filter(
        Employe.code == code,
        Employe.compagnie_id == compagnie_id
    ).first()
    if existing_employe:
        raise ValueError(f"Employe with code {code} already exists for this company")

    db_employe = Employe(
        code=code,
        nom=nom,
        prenom=prenom,
        adresse=adresse,
        telephone=telephone,
        poste=poste,
        salaire_base=salaire_base,
        avances=avances,
        creances=creances,
        station_ids=station_ids,
        compagnie_id=compagnie_id,
        statut=statut
    )

    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)

    return db_employe


def get_employe_by_id(db: Session, employe_id: str) -> Optional[Employe]:
    """
    Get an employe by ID
    """
    return db.query(Employe).filter(Employe.id == employe_id).first()


def get_all_employes(
    db: Session,
    compagnie_id: Optional[str] = None,
    statut: Optional[str] = None
) -> List[Employe]:
    """
    Get all employes with optional filters
    """
    query = db.query(Employe)

    if compagnie_id:
        query = query.filter(Employe.compagnie_id == compagnie_id)
    if statut:
        query = query.filter(Employe.statut == statut)

    return query.all()


def get_client_by_code(db: Session, client_code: str, compagnie_id: Optional[str] = None) -> Optional[Client]:
    """
    Get a client by code, optionally filtered by company
    """
    query = db.query(Client).filter(Client.code == client_code)

    if compagnie_id:
        query = query.filter(Client.compagnie_id == compagnie_id)

    return query.first()


def get_fournisseur_by_code(db: Session, fournisseur_code: str, compagnie_id: Optional[str] = None) -> Optional[Fournisseur]:
    """
    Get a fournisseur by code, optionally filtered by company
    """
    query = db.query(Fournisseur).filter(Fournisseur.code == fournisseur_code)

    if compagnie_id:
        query = query.filter(Fournisseur.compagnie_id == compagnie_id)

    return query.first()


def get_employe_by_code(db: Session, employe_code: str, compagnie_id: Optional[str] = None) -> Optional[Employe]:
    """
    Get an employe by code, optionally filtered by company
    """
    query = db.query(Employe).filter(Employe.code == employe_code)

    if compagnie_id:
        query = query.filter(Employe.compagnie_id == compagnie_id)

    return query.first()


def create_type_tiers(
    db: Session,
    type: str,
    libelle: str,
    num_compte: Optional[str] = None
) -> TypeTiers:
    """
    Create a new type tiers
    """
    db_type_tiers = TypeTiers(
        type=type,
        libelle=libelle,
        num_compte=num_compte
    )

    db.add(db_type_tiers)
    db.commit()
    db.refresh(db_type_tiers)

    return db_type_tiers


def get_type_tiers_by_id(db: Session, type_tiers_id: str) -> Optional[TypeTiers]:
    """
    Get a type tiers by ID
    """
    return db.query(TypeTiers).filter(TypeTiers.id == type_tiers_id).first()


def get_all_types_tiers(
    db: Session
) -> List[TypeTiers]:
    """
    Get all types tiers
    """
    return db.query(TypeTiers).all()


def get_type_tiers_by_type(
    db: Session,
    type_filter: Optional[str] = None
) -> List[TypeTiers]:
    """
    Get types tiers by type filter
    """
    query = db.query(TypeTiers)

    if type_filter:
        query = query.filter(TypeTiers.type == type_filter)

    return query.all()