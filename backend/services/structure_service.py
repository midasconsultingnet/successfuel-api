from sqlalchemy.orm import Session
from models.structures import Station, Cuve, Carburant, Pistolet, Article, Client, Fournisseur, Employe, Tresorerie

def get_station_by_id(db: Session, station_id: str):
    return db.query(Station).filter(Station.id == station_id).first()

def get_all_stations(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    query = db.query(Station)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_station(db: Session, station_data):
    db_station = Station(**station_data)
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

def get_cuve_by_id(db: Session, cuve_id: str):
    return db.query(Cuve).filter(Cuve.id == cuve_id).first()

def get_all_cuves(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Cuve).join(Station, Cuve.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_cuve(db: Session, cuve_data):
    db_cuve = Cuve(**cuve_data)
    db.add(db_cuve)
    db.commit()
    db.refresh(db_cuve)
    return db_cuve

def get_carburant_by_id(db: Session, carburant_id: str):
    return db.query(Carburant).filter(Carburant.id == carburant_id).first()

def get_all_carburants(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Carburant).join(Station, Carburant.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_carburant(db: Session, carburant_data):
    db_carburant = Carburant(**carburant_data)
    db.add(db_carburant)
    db.commit()
    db.refresh(db_carburant)
    return db_carburant

def get_pistolet_by_id(db: Session, pistolet_id: str):
    return db.query(Pistolet).filter(Pistolet.id == pistolet_id).first()

def get_all_pistolets(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Pistolet).join(Station, Pistolet.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_pistolet(db: Session, pistolet_data):
    db_pistolet = Pistolet(**pistolet_data)
    db.add(db_pistolet)
    db.commit()
    db.refresh(db_pistolet)
    return db_pistolet

def get_article_by_id(db: Session, article_id: str):
    return db.query(Article).filter(Article.id == article_id).first()

def get_all_articles(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Article).join(Station, Article.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_article(db: Session, article_data):
    db_article = Article(**article_data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_client_by_id(db: Session, client_id: str):
    return db.query(Client).filter(Client.id == client_id).first()

def get_all_clients(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Client).join(Station, Client.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_client(db: Session, client_data):
    db_client = Client(**client_data)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_fournisseur_by_id(db: Session, fournisseur_id: str):
    return db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()

def get_all_fournisseurs(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Fournisseur).join(Station, Fournisseur.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_fournisseur(db: Session, fournisseur_data):
    db_fournisseur = Fournisseur(**fournisseur_data)
    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)
    return db_fournisseur

def get_employe_by_id(db: Session, employe_id: str):
    return db.query(Employe).filter(Employe.id == employe_id).first()

def get_all_employes(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Employe).join(Station, Employe.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_employe(db: Session, employe_data):
    db_employe = Employe(**employe_data)
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    return db_employe

def get_tresorerie_by_id(db: Session, tresorerie_id: str):
    return db.query(Tresorerie).filter(Tresorerie.id == tresorerie_id).first()

def get_all_tresoreries(db: Session, compagnie_id: str = None, skip: int = 0, limit: int = 100):
    from models.structures import Compagnie
    query = db.query(Tresorerie).join(Station, Tresorerie.station_id == Station.id)
    if compagnie_id:
        query = query.filter(Station.compagnie_id == compagnie_id)
    return query.offset(skip).limit(limit).all()

def create_tresorerie(db: Session, tresorerie_data):
    db_tresorerie = Tresorerie(**tresorerie_data)
    db.add(db_tresorerie)
    db.commit()
    db.refresh(db_tresorerie)
    return db_tresorerie