from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..auth.auth_handler import get_current_user_security
from ..auth.schemas import UserWithPermissions
from ..rbac_decorators import require_permission
from .schemas import (
    ChargeCreate,
    ChargeUpdate,
    ChargeResponse,
    PaiementChargeCreate,
    PaiementChargeUpdate,
    PaiementChargeResponse
)
from ..services.charges.charge_service import (
    ChargeService,
    SeuilAlerteService,
    GestionEcheancesService,
    SystemeArretCompteService
)


router = APIRouter(prefix="/charges", tags=["Charges"])


@router.post("/", response_model=ChargeResponse,
            summary="Créer une nouvelle charge",
            description="Permet de créer une nouvelle charge pour la compagnie de l'utilisateur connecté")
def create_charge(
    charge: ChargeCreate,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "create"))
):
    """
    Créer une nouvelle charge
    """
    # Vérifier que l'utilisateur a le droit d'accès à la station
    # (implémentation spécifique à votre système d'autorisation)

    return ChargeService.create_charge(db, charge, str(current_user.id))


@router.get("/{charge_id}", response_model=ChargeResponse,
            summary="Récupérer une charge par son ID",
            description="Permet de récupérer les détails d'une charge spécifique par son identifiant")
def get_charge_by_id(
    charge_id: str,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Récupérer une charge par son ID
    """
    charge = ChargeService.get_charge_by_id(db, charge_id, current_user.compagnie_id)
    if not charge:
        raise HTTPException(status_code=404, detail="Charge non trouvée")
    return charge


@router.get("/", response_model=List[ChargeResponse],
            summary="Récupérer la liste des charges",
            description="Permet de récupérer la liste des charges appartenant à la compagnie de l'utilisateur connecté")
def get_charges(
    skip: int = 0,
    limit: int = 100,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Récupérer la liste des charges
    """
    return ChargeService.get_charges_by_company(
        db, current_user.compagnie_id, skip, limit, statut
    )


@router.put("/{charge_id}", response_model=ChargeResponse,
            summary="Mettre à jour une charge existante",
            description="Permet de modifier les informations d'une charge existante")
def update_charge(
    charge_id: str,
    charge_update: ChargeUpdate,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "update"))
):
    """
    Mettre à jour une charge existante
    """
    updated_charge = ChargeService.update_charge(
        db, charge_id, charge_update, current_user.compagnie_id
    )
    if not updated_charge:
        raise HTTPException(status_code=404, detail="Charge non trouvée")
    return updated_charge


@router.delete("/{charge_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer une charge",
               description="Permet de supprimer une charge existante")
def delete_charge(
    charge_id: str,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "delete"))
):
    """
    Supprimer une charge
    """
    success = ChargeService.delete_charge(db, charge_id, current_user.compagnie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Charge non trouvée")
    return


@router.post("/paiements/", response_model=PaiementChargeResponse,
             summary="Créer un paiement pour une charge",
             description="Permet de créer un paiement pour une charge spécifique")
def create_paiement_charge(
    paiement: PaiementChargeCreate,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "create"))
):
    """
    Créer un paiement pour une charge
    """
    return ChargeService.create_paiement_charge(db, paiement, str(current_user.id))


@router.get("/{charge_id}/paiements", response_model=List[PaiementChargeResponse],
            summary="Récupérer les paiements d'une charge",
            description="Permet de récupérer la liste des paiements effectués pour une charge spécifique")
def get_paiements_for_charge(
    charge_id: str,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Récupérer les paiements d'une charge
    """
    return ChargeService.get_paiements_for_charge(db, charge_id, current_user.compagnie_id)


@router.post("/gerer_recurrentes",
             summary="Générer les charges récurrentes",
             description="Permet de générer automatiquement les charges récurrentes selon leur fréquence")
def gerer_charges_recurrentes(
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "update"))
):
    """
    Générer les charges récurrentes
    """
    ChargeService.gerer_charges_recurrentes(db, current_user.compagnie_id)
    return {"message": "Charges récurrentes gérées avec succès"}


@router.get("/seuils_alerte",
            summary="Vérifier les seuils d'alerte des charges",
            description="Permet de vérifier si certaines charges dépassent les seuils d'alerte configurables")
def verifier_seuils_alerte(
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Vérifier les seuils d'alerte
    """
    alertes = SeuilAlerteService.verifier_seuils_alerte(db, current_user.compagnie_id)
    return {"alertes": alertes}


@router.get("/echeances",
            summary="Vérifier les échéances des charges",
            description="Permet de vérifier les échéances des charges et générer les rappels en fonction des dates configurées")
def verifier_echeances(
    jours_avant_rappel: int = 7,
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Vérifier les échéances et générer les rappels
    """
    rappels = GestionEcheancesService.verifier_echeances(
        db, current_user.compagnie_id, jours_avant_rappel
    )
    return {"rappels": rappels}


@router.get("/arrets_compte",
            summary="Vérifier les arrêts de compte",
            description="Permet de vérifier et mettre à jour les arrêts de compte en fonction des charges impayées")
def verifier_arrets_compte(
    db: Session = Depends(get_db),
    current_user: UserWithPermissions = Depends(require_permission("charges", "read"))
):
    """
    Vérifier les arrêts de compte
    """
    fournisseurs_a_arreter = SystemeArretCompteService.mettre_a_jour_arrets_compte(
        db, current_user.compagnie_id
    )
    return {"fournisseurs_a_arreter": fournisseurs_a_arreter}