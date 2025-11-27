from typing import List, Optional
from sqlalchemy.orm import Session
from models.structures import Pays, Compagnie, Station
from datetime import datetime
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