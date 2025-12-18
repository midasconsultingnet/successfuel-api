from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Inventaire as InventaireModel
from . import schemas
from ..services.inventaires.inventaire_service import InventaireService
from ..services.inventaires.ecart_inventaire_service import EcartInventaireService
from ..auth.auth_handler import get_current_user_security
from ..rbac_decorators import require_permission
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[schemas.InventaireResponse],
           summary="Récupérer la liste des inventaires",
           description="Permet de récupérer la liste des inventaires appartenant à la compagnie de l'utilisateur connecté")
async def get_inventaires(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "lire"))
):
    inventaire_service = InventaireService(db)
    # Filtrer les inventaires par la compagnie de l'utilisateur
    inventaires = db.query(InventaireModel).filter(
        InventaireModel.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()
    return inventaires

@router.post("/", response_model=schemas.InventaireResponse,
            summary="Créer un nouvel inventaire",
            description="Permet de créer un nouvel inventaire pour la compagnie de l'utilisateur connecté")
async def create_inventaire(
    inventaire: schemas.InventaireCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "creer"))
):
    inventaire_service = InventaireService(db)
    created_inventaire = inventaire_service.create_inventaire(inventaire, current_user)
    return created_inventaire

@router.get("/{inventaire_id}", response_model=schemas.InventaireResponse,
           summary="Récupérer un inventaire par son ID",
           description="Permet de récupérer les détails d'un inventaire spécifique par son identifiant")
async def get_inventaire_by_id(
    inventaire_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "lire"))
):
    inventaire_service = InventaireService(db)
    inventaire = inventaire_service.get_by_id(inventaire_id)

    if not inventaire or inventaire.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Inventaire not found")
    return inventaire

@router.put("/{inventaire_id}", response_model=schemas.InventaireResponse,
           summary="Mettre à jour un inventaire",
           description="Permet de modifier les informations d'un inventaire existant")
async def update_inventaire(
    inventaire_id: str,
    inventaire: schemas.InventaireUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "modifier"))
):
    inventaire_service = InventaireService(db)
    updated_inventaire = inventaire_service.update_inventaire(inventaire_id, inventaire, current_user)
    return updated_inventaire

@router.delete("/{inventaire_id}",
               summary="Supprimer un inventaire",
               description="Permet de supprimer un inventaire existant")
async def delete_inventaire(
    inventaire_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "supprimer"))
):
    inventaire_service = InventaireService(db)
    inventaire = inventaire_service.get_by_id(inventaire_id)

    if not inventaire or inventaire.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Inventaire not found")

    inventaire_service.delete(inventaire_id)
    return {"message": "Inventaire deleted successfully"}

@router.get("/{inventaire_id}/ecarts", response_model=List[schemas.EcartInventaireResponse],
           summary="Récupérer les écarts d'un inventaire",
           description="Permet de récupérer la liste des écarts identifiés pour un inventaire spécifique")
async def get_inventaire_ecarts(
    inventaire_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "lire"))
):
    inventaire_service = InventaireService(db)
    inventaire = inventaire_service.get_by_id(inventaire_id)

    if not inventaire or inventaire.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Inventaire not found")

    ecart_inventaire_service = EcartInventaireService(db)
    ecarts = ecart_inventaire_service.get_ecarts_by_inventaire(inventaire_id)
    return ecarts

# Endpoint pour créer un écart d'inventaire manuellement
@router.post("/ecarts", response_model=schemas.EcartInventaireResponse,
             summary="Créer un écart d'inventaire",
             description="Permet de créer manuellement un écart d'inventaire")
async def create_ecart_inventaire(
    ecart_inventaire: schemas.EcartInventaireCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "creer"))
):
    # Vérifier que l'utilisateur a le droit d'accéder aux ressources liées à l'écart
    if ecart_inventaire.station_id not in [str(s.id) for s in current_user.stations] or \
       ecart_inventaire.compagnie_id != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Vous n'avez pas le droit de créer un écart pour cette station ou cette compagnie")

    ecart_inventaire_service = EcartInventaireService(db)
    created_ecart = ecart_inventaire_service.create_ecart_inventaire(ecart_inventaire)
    return created_ecart

@router.get("/ecarts/", response_model=List[schemas.EcartInventaireResponse],
           summary="Récupérer la liste des écarts d'inventaire",
           description="Permet de récupérer la liste des écarts d'inventaire appartenant à la compagnie de l'utilisateur connecté")
async def get_ecarts_inventaire(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "lire"))
):
    # Filtrer les écarts par la compagnie de l'utilisateur
    ecarts = db.query(InventaireModel.__table__.columns).filter(
        InventaireModel.compagnie_id == current_user.compagnie_id
    ).join(InventaireModel.ecarts).offset(skip).limit(limit).all()

    # Récupérer les écarts d'inventaire via le service
    ecart_inventaire_service = EcartInventaireService(db)
    ecarts_inventaire = db.query(ecart_inventaire_service.model).filter(
        ecart_inventaire_service.model.compagnie_id == current_user.compagnie_id
    ).offset(skip).limit(limit).all()

    return ecarts_inventaire

@router.get("/ecarts/{ecart_id}", response_model=schemas.EcartInventaireResponse,
           summary="Récupérer un écart d'inventaire par son ID",
           description="Permet de récupérer les détails d'un écart d'inventaire spécifique par son identifiant")
async def get_ecart_inventaire_by_id(
    ecart_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "lire"))
):
    ecart_inventaire_service = EcartInventaireService(db)
    ecart = ecart_inventaire_service.get_by_id(ecart_id)

    if not ecart or ecart.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Écart d'inventaire not found")
    return ecart

@router.put("/ecarts/{ecart_id}", response_model=schemas.EcartInventaireResponse,
           summary="Mettre à jour un écart d'inventaire",
           description="Permet de modifier les informations d'un écart d'inventaire existant")
async def update_ecart_inventaire(
    ecart_id: str,
    ecart_inventaire: schemas.EcartInventaireUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "modifier"))
):
    ecart_inventaire_service = EcartInventaireService(db)
    ecart = ecart_inventaire_service.get_by_id(ecart_id)

    if not ecart or ecart.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Écart d'inventaire not found")

    updated_ecart = ecart_inventaire_service.update_ecart_inventaire(ecart_id, ecart_inventaire)
    return updated_ecart

@router.delete("/ecarts/{ecart_id}",
               summary="Supprimer un écart d'inventaire",
               description="Permet de supprimer un écart d'inventaire existant")
async def delete_ecart_inventaire(
    ecart_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("inventaire", "supprimer"))
):
    ecart_inventaire_service = EcartInventaireService(db)
    ecart = ecart_inventaire_service.get_by_id(ecart_id)

    if not ecart or ecart.compagnie_id != current_user.compagnie_id:
        raise HTTPException(status_code=404, detail="Écart d'inventaire not found")

    ecart_inventaire_service.delete_ecart_inventaire(ecart_id)
    return {"message": "Écart d'inventaire deleted successfully"}
