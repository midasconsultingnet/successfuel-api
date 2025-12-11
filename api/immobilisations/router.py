from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Immobilisation as ImmobilisationModel, MouvementImmobilisation as MouvementImmobilisationModel
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# Endpoints pour les immobilisations
@router.get("/", response_model=List[schemas.ImmobilisationCreate])
async def get_immobilisations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    immobilisations = db.query(ImmobilisationModel).offset(skip).limit(limit).all()
    return immobilisations

@router.post("/", response_model=schemas.ImmobilisationCreate)
async def create_immobilisation(
    immobilisation: schemas.ImmobilisationCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Vérifier que le code est unique pour la station
    existing_immobilisation = db.query(ImmobilisationModel).filter(
        ImmobilisationModel.code == immobilisation.code,
        ImmobilisationModel.station_id == immobilisation.station_id
    ).first()

    if existing_immobilisation:
        raise HTTPException(status_code=400, detail="Immobilisation avec ce code existe déjà pour cette station")

    # Créer l'immobilisation
    db_immobilisation = ImmobilisationModel(
        nom=immobilisation.nom,
        description=immobilisation.description,
        code=immobilisation.code,
        type=immobilisation.type,
        date_acquisition=immobilisation.date_acquisition,
        valeur_origine=immobilisation.valeur_origine,
        valeur_nette=immobilisation.valeur_origine,  # Initialement, la valeur nette est égale à la valeur d'origine
        station_id=immobilisation.station_id
    )

    db.add(db_immobilisation)
    db.commit()
    db.refresh(db_immobilisation)

    return db_immobilisation

@router.get("/{immobilisation_id}", response_model=schemas.ImmobilisationCreate)
async def get_immobilisation_by_id(
    immobilisation_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    immobilisation = db.query(ImmobilisationModel).filter(ImmobilisationModel.id == immobilisation_id).first()
    if not immobilisation:
        raise HTTPException(status_code=404, detail="Immobilisation not found")
    return immobilisation

@router.put("/{immobilisation_id}", response_model=schemas.ImmobilisationUpdate)
async def update_immobilisation(
    immobilisation_id: int,
    immobilisation: schemas.ImmobilisationUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_immobilisation = db.query(ImmobilisationModel).filter(ImmobilisationModel.id == immobilisation_id).first()
    if not db_immobilisation:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    update_data = immobilisation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_immobilisation, field, value)

    db.commit()
    db.refresh(db_immobilisation)
    return db_immobilisation

@router.delete("/{immobilisation_id}")
async def delete_immobilisation(
    immobilisation_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    immobilisation = db.query(ImmobilisationModel).filter(ImmobilisationModel.id == immobilisation_id).first()
    if not immobilisation:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    # Vérifier qu'il n'y a pas de mouvements associés avant de supprimer
    mouvements = db.query(MouvementImmobilisationModel).filter(
        MouvementImmobilisationModel.immobilisation_id == immobilisation_id
    ).count()

    if mouvements > 0:
        raise HTTPException(status_code=400, detail="Impossible de supprimer une immobilisation avec des mouvements associés")

    db.delete(immobilisation)
    db.commit()
    return {"message": "Immobilisation deleted successfully"}

# Endpoints pour les mouvements d'immobilisations
@router.get("/{immobilisation_id}/mouvements", response_model=List[schemas.MouvementImmobilisationCreate])
async def get_mouvements_immobilisation(
    immobilisation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    mouvements = db.query(MouvementImmobilisationModel).filter(
        MouvementImmobilisationModel.immobilisation_id == immobilisation_id
    ).offset(skip).limit(limit).all()
    return mouvements

@router.post("/{immobilisation_id}/mouvements", response_model=schemas.MouvementImmobilisationCreate)
async def create_mouvement_immobilisation(
    immobilisation_id: int,
    mouvement: schemas.MouvementImmobilisationCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Vérifier que l'immobilisation existe
    immobilisation = db.query(ImmobilisationModel).filter(ImmobilisationModel.id == immobilisation_id).first()
    if not immobilisation:
        raise HTTPException(status_code=404, detail="Immobilisation not found")

    # Créer le mouvement d'immobilisation
    db_mouvement = MouvementImmobilisationModel(
        immobilisation_id=immobilisation_id,
        type_mouvement=mouvement.type_mouvement,
        date_mouvement=mouvement.date_mouvement,
        description=mouvement.description,
        valeur_variation=mouvement.valeur_variation,
        valeur_apres_mouvement=mouvement.valeur_apres_mouvement,
        utilisateur_id=mouvement.utilisateur_id,
        reference_document=mouvement.reference_document
    )

    # Mettre à jour la valeur nette de l'immobilisation selon le type de mouvement
    if mouvement.type_mouvement == "amortissement":
        # Appliquer l'amortissement
        if mouvement.valeur_variation and immobilisation.valeur_nette:
            immobilisation.valeur_nette -= mouvement.valeur_variation
    elif mouvement.type_mouvement == "amélioration":
        # Ajouter la valeur de l'amélioration
        if mouvement.valeur_variation and immobilisation.valeur_nette:
            immobilisation.valeur_nette += mouvement.valeur_variation
    elif mouvement.type_mouvement == "cession" or mouvement.type_mouvement == "sortie":
        # Déprécier l'immobilisation lors d'une cession ou sortie
        immobilisation.statut = "cessionné" if mouvement.type_mouvement == "cession" else "hors_service"

    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)

    return db_mouvement