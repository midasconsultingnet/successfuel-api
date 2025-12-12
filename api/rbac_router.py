from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .rbac_schemas import ProfilCreate, ProfilUpdate, Profil, ProfilWithModules, ProfilModuleCreate, ProfilModule, UtilisateurProfilCreate, UtilisateurProfil
from pydantic import BaseModel
from .rbac_models import Profil as ProfilModel, ProfilModule as ProfilModuleModel, UtilisateurProfil as UtilisateurProfilModel
from .auth.auth_handler import get_current_user, get_current_user_security
from .models.user import User as UserModel
import uuid

router = APIRouter(prefix="", tags=["rbac"])

# Schéma spécifique pour la création de profil sans compagnie_id
class ProfilCreateWithoutCompanyId(BaseModel):
    nom: str
    description: str

# Endpoints pour la gestion des profils
@router.post("/profils", response_model=Profil)
def create_profil(profil: ProfilCreateWithoutCompanyId, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Créer un nouveau profil personnalisé
    Nécessite des droits de gérant de compagnie
    """
    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie":
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier que le nom de profil est unique pour la compagnie
    existing_profil = db.query(ProfilModel).filter(
        ProfilModel.nom == profil.nom,
        ProfilModel.compagnie_id == current_user.compagnie_id
    ).first()
    if existing_profil:
        raise HTTPException(status_code=400, detail="Un profil avec ce nom existe déjà pour cette compagnie")

    # Créer le profil avec la compagnie de l'utilisateur
    db_profil = ProfilModel(
        nom=profil.nom,
        description=profil.description,
        compagnie_id=current_user.compagnie_id
    )
    db.add(db_profil)
    db.commit()
    db.refresh(db_profil)
    return db_profil

@router.get("/profils/{profil_id}", response_model=ProfilWithModules)
def get_profil(profil_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Récupérer un profil spécifique avec ses modules associés
    Nécessite des droits de gérant de la même compagnie
    """
    profil = db.query(ProfilModel).filter(ProfilModel.id == profil_id).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    # Vérifier que l'utilisateur appartient à la même compagnie
    if current_user.role != "gerant_compagnie" or str(current_user.compagnie_id) != str(profil.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Charger explicitement les modules associés au profil pour éviter les problèmes de session
    modules_associes = db.query(ProfilModuleModel).filter(
        ProfilModuleModel.profil_id == profil.id
    ).all()

    # Construire manuellement la réponse pour éviter les problèmes de session
    profil_data = ProfilWithModules(
        id=profil.id,
        nom=profil.nom,
        description=profil.description,
        compagnie_id=profil.compagnie_id,
        created_at=profil.created_at,
        updated_at=profil.updated_at,
        modules=[
            ProfilModule(
                id=module.id,
                profil_id=module.profil_id,
                module_nom=module.module_nom,
                created_at=module.created_at
            )
            for module in modules_associes
        ]
    )

    return profil_data

@router.get("/profils", response_model=List[Profil])
def get_profils(db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Récupérer tous les profils de la compagnie de l'utilisateur
    Nécessite des droits de gérant de la même compagnie
    """
    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie":
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Récupérer les profils de la compagnie de l'utilisateur connecté
    profils = db.query(ProfilModel).filter(ProfilModel.compagnie_id == current_user.compagnie_id).all()
    return profils

@router.put("/profils/{profil_id}", response_model=Profil)
def update_profil(profil_id: uuid.UUID, profil: ProfilUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Mettre à jour un profil existant
    Nécessite des droits de gérant de la même compagnie
    """
    db_profil = db.query(ProfilModel).filter(ProfilModel.id == profil_id).first()
    if not db_profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie" or str(current_user.compagnie_id) != str(db_profil.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Mettre à jour les champs fournis
    update_data = profil.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profil, field, value)

    db.commit()
    db.refresh(db_profil)
    return db_profil

@router.delete("/profils/{profil_id}")
def delete_profil(profil_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Supprimer un profil
    Nécessite des droits de gérant de la même compagnie
    """
    db_profil = db.query(ProfilModel).filter(ProfilModel.id == profil_id).first()
    if not db_profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie" or str(current_user.compagnie_id) != str(db_profil.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(db_profil)
    db.commit()
    return {"message": "Profil supprimé avec succès"}

# Endpoints pour la gestion des associations Profil-Module
@router.post("/profil-modules", response_model=ProfilModule)
def create_profil_module(profil_module: ProfilModuleCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Associer un module à un profil
    Nécessite des droits de gérant de la même compagnie
    """
    # Récupérer le profil pour vérifier la compagnie
    profil = db.query(ProfilModel).filter(ProfilModel.id == profil_module.profil_id).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")

    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie" or str(current_user.compagnie_id) != str(profil.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier que l'association n'existe pas déjà
    existing = db.query(ProfilModuleModel).filter(
        ProfilModuleModel.profil_id == profil_module.profil_id,
        ProfilModuleModel.module_nom == profil_module.module_nom
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cette association profil-module existe déjà")

    db_profil_module = ProfilModuleModel(**profil_module.model_dump())
    db.add(db_profil_module)
    db.commit()
    db.refresh(db_profil_module)
    return db_profil_module

@router.delete("/profil-modules/{profil_module_id}")
def delete_profil_module(profil_module_id: uuid.UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Supprimer une association profil-module
    Nécessite des droits de gérant de la même compagnie
    """
    db_profil_module = db.query(ProfilModuleModel).filter(ProfilModuleModel.id == profil_module_id).first()
    if not db_profil_module:
        raise HTTPException(status_code=404, detail="Association profil-module non trouvée")

    # Récupérer le profil pour vérifier la compagnie
    profil = db.query(ProfilModel).filter(ProfilModel.id == db_profil_module.profil_id).first()

    # Vérifier que l'utilisateur est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie" or str(current_user.compagnie_id) != str(profil.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(db_profil_module)
    db.commit()
    return {"message": "Association profil-module supprimée avec succès"}

# Endpoints pour la gestion des attributions Utilisateur-Profils
@router.post("/utilisateur-profils", response_model=UtilisateurProfil)
def create_utilisateur_profil(utilisateur_profil: UtilisateurProfilCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_security)):
    """
    Attribuer un profil à un utilisateur
    Nécessite des droits de gérant de la même compagnie
    """
    # Vérifier que l'utilisateur qui affecte est un gérant de la même compagnie
    if current_user.role != "gerant_compagnie":
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier que le profil appartient à la même compagnie que l'utilisateur
    profil = db.query(ProfilModel).filter(ProfilModel.id == utilisateur_profil.profil_id).first()
    if not profil or str(profil.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier que l'utilisateur appartient à la même compagnie
    utilisateur = db.query(UserModel).filter(UserModel.id == utilisateur_profil.utilisateur_id).first()
    if not utilisateur or str(utilisateur.compagnie_id) != str(current_user.compagnie_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier qu'un profil n'est pas déjà attribué à cet utilisateur
    existing = db.query(UtilisateurProfilModel).filter(
        UtilisateurProfilModel.utilisateur_id == utilisateur_profil.utilisateur_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cet utilisateur a déjà un profil attribué")

    db_utilisateur_profil = UtilisateurProfilModel(
        **utilisateur_profil.model_dump(),
        utilisateur_affectation_id=current_user.id
    )
    db.add(db_utilisateur_profil)
    db.commit()
    db.refresh(db_utilisateur_profil)
    return db_utilisateur_profil