from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Vente as VenteModel, VenteDetail as VenteDetailModel
from ..models import VenteCarburant as VenteCarburantModel, CreanceEmploye as CreanceEmployeModel, PrixCarburant
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[schemas.VenteCreate])
async def get_ventes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    ventes = db.query(VenteModel).offset(skip).limit(limit).all()
    return ventes

@router.post("/", response_model=schemas.VenteCreate)
async def create_vente(
    vente: schemas.VenteCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Calculate total amount from details
    total_amount = sum(detail.montant for detail in vente.details)

    # Create the main vente record
    db_vente = VenteModel(
        # station_id=vente.station_id - Le champ station_id n'est pas défini dans VenteModel
        client_id=vente.client_id,
        date=vente.date,
        montant_total=total_amount,
        statut=vente.statut,
        type_vente=vente.type_vente,
        trésorerie_id=vente.trésorerie_id,
        numero_piece_comptable=vente.numero_piece_comptable
        # compagnie_id=vente.compagnie_id - Le champ compagnie_id n'est pas défini dans VenteModel
    )

    db.add(db_vente)
    db.flush()  # To get the ID before committing

    # Create the details
    for detail in vente.details:
        db_detail = VenteDetailModel(
            vente_id=str(db_vente.id),
            produit_id=detail.produit_id,
            quantite=detail.quantite,
            prix_unitaire=detail.prix_unitaire,
            montant=detail.montant,
            remise=detail.remise
        )
        db.add(db_detail)

    db.commit()
    db.refresh(db_vente)

    return db_vente

@router.get("/{vente_id}", response_model=schemas.VenteCreate)
async def get_vente_by_id(
    vente_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    vente = db.query(VenteModel).filter(VenteModel.id == vente_id).first()
    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")
    return vente

@router.put("/{vente_id}", response_model=schemas.VenteUpdate)
async def update_vente(
    vente_id: int,
    vente: schemas.VenteUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_vente = db.query(VenteModel).filter(VenteModel.id == vente_id).first()
    if not db_vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    update_data = vente.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente, field, value)

    db.commit()
    db.refresh(db_vente)
    return db_vente

@router.delete("/{vente_id}")
async def delete_vente(
    vente_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    vente = db.query(VenteModel).filter(VenteModel.id == vente_id).first()
    if not vente:
        raise HTTPException(status_code=404, detail="Vente not found")

    # Delete related details first
    db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == str(vente_id)).delete()

    db.delete(vente)
    db.commit()
    return {"message": "Vente deleted successfully"}

@router.get("/{vente_id}/details", response_model=List[schemas.VenteDetailCreate])
async def get_vente_details(
    vente_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    details = db.query(VenteDetailModel).filter(VenteDetailModel.vente_id == str(vente_id)).offset(skip).limit(limit).all()
    return details

# Endpoints pour les ventes de carburant
@router.get("/carburant", response_model=List[schemas.VenteCarburantCreate])
async def get_ventes_carburant(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    ventes_carburant = db.query(VenteCarburantModel).offset(skip).limit(limit).all()
    return ventes_carburant

@router.post("/carburant", response_model=schemas.VenteCarburantCreate)
async def create_vente_carburant(
    vente_carburant: schemas.VenteCarburantCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Récupérer les informations de la cuve pour déterminer le carburant_id
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT c.carburant_id, s.id as station_id
        FROM cuve c
        JOIN station s ON c.station_id = s.id
        WHERE c.id = :cuve_id
    """), {"cuve_id": vente_carburant.cuve_id})

    cuve_data = result.fetchone()

    if not cuve_data or not cuve_data.carburant_id:
        raise HTTPException(status_code=404, detail="Carburant de la cuve non trouvé")

    # Déterminer le carburant_id à utiliser
    carburant_id = vente_carburant.carburant_id or cuve_data.carburant_id

    # Récupérer le prix de vente depuis la table prix_carburant
    prix_carburant = db.query(PrixCarburant).filter(
        PrixCarburant.carburant_id == carburant_id,
        PrixCarburant.station_id == cuve_data.station_id
    ).first()

    if not prix_carburant or not prix_carburant.prix_vente:
        raise HTTPException(status_code=404, detail="Prix de vente non trouvé pour ce carburant et cette station")

    prix_unitaire = prix_carburant.prix_vente

    # Calculer le montant total
    montant_total = vente_carburant.quantite_vendue * prix_unitaire

    # Créer l'enregistrement de vente de carburant
    db_vente_carburant = VenteCarburantModel(
        station_id=vente_carburant.station_id,
        cuve_id=vente_carburant.cuve_id,
        pistolet_id=vente_carburant.pistolet_id,
        quantite_vendue=vente_carburant.quantite_vendue,
        prix_unitaire=prix_unitaire,
        montant_total=montant_total,
        date_vente=vente_carburant.date_vente,
        index_initial=vente_carburant.index_initial,
        index_final=vente_carburant.index_final,
        pompiste=vente_carburant.pompiste,
        qualite_marshalle_id=vente_carburant.qualite_marshalle_id,
        montant_paye=vente_carburant.montant_paye,
        mode_paiement=vente_carburant.mode_paiement,
        utilisateur_id=vente_carburant.utilisateur_id
    )

    # Si le montant payé est inférieur au montant dû, créer une créance employé
    if vente_carburant.montant_paye < montant_total:
        montant_creance = montant_total - vente_carburant.montant_paye

        creance_employe = CreanceEmployeModel(
            vente_carburant_id=str(db_vente_carburant.id),
            pompiste=vente_carburant.pompiste,
            montant_du=montant_creance,
            montant_paye=vente_carburant.montant_paye,
            solde_creance=montant_creance,
            created_at=vente_carburant.date_vente,
            utilisateur_gestion_id=vente_carburant.utilisateur_id
        )

        db.add(creance_employe)
        db_vente_carburant.creance_employe_id = str(creance_employe.id)

    db.add(db_vente_carburant)
    db.commit()
    db.refresh(db_vente_carburant)

    return db_vente_carburant

@router.get("/carburant/{vente_carburant_id}", response_model=schemas.VenteCarburantCreate)
async def get_vente_carburant_by_id(
    vente_carburant_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    vente_carburant = db.query(VenteCarburantModel).filter(VenteCarburantModel.id == vente_carburant_id).first()
    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")
    return vente_carburant

@router.put("/carburant/{vente_carburant_id}", response_model=schemas.VenteCarburantUpdate)
async def update_vente_carburant(
    vente_carburant_id: int,
    vente_carburant: schemas.VenteCarburantUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db_vente_carburant = db.query(VenteCarburantModel).filter(VenteCarburantModel.id == vente_carburant_id).first()
    if not db_vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    update_data = vente_carburant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vente_carburant, field, value)

    db.commit()
    db.refresh(db_vente_carburant)
    return db_vente_carburant

@router.delete("/carburant/{vente_carburant_id}")
async def delete_vente_carburant(
    vente_carburant_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    vente_carburant = db.query(VenteCarburantModel).filter(VenteCarburantModel.id == vente_carburant_id).first()
    if not vente_carburant:
        raise HTTPException(status_code=404, detail="Vente carburant not found")

    db.delete(vente_carburant)
    db.commit()
    return {"message": "Vente carburant deleted successfully"}

# Endpoints pour les créances employés
@router.get("/creances_employes", response_model=List[schemas.CreanceEmployeCreate])
async def get_creances_employes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    creances = db.query(CreanceEmployeModel).offset(skip).limit(limit).all()
    return creances

@router.get("/creances_employes/{creance_id}", response_model=schemas.CreanceEmployeCreate)
async def get_creance_employe_by_id(
    creance_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    creance = db.query(CreanceEmployeModel).filter(CreanceEmployeModel.id == creance_id).first()
    if not creance:
        raise HTTPException(status_code=404, detail="Creance employé not found")
    return creance
