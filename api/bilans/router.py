from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/operationnels")
async def get_bilan_operationnel(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would aggregate data from multiple modules:
    # - Ventes: total sales between the dates
    # - Achats: total purchases between the dates
    # - Calculate the net result
    
    # For now, return a placeholder response
    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "total_ventes": 1500000,
        "total_achats": 900000,
        "resultat": 600000,
        "message": "This endpoint would aggregate operational data from ventes, achats, and other modules"
    }

@router.get("/tresorerie")
async def get_bilan_tresorerie(
    date_debut: str,  # Format: YYYY-MM-DD
    date_fin: str,    # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from ..auth.auth_handler import get_current_user_security
    current_user = get_current_user_security(credentials, db)

    from datetime import datetime
    from sqlalchemy import and_

    # Conversion des dates
    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")

    # Récupération des trésoreries station appartenant aux stations de l'utilisateur
    from ..models import Station
    from ..models.tresorerie import TresorerieStation, MouvementTresorerie
    trésoreries_station = db.query(TresorerieStation).join(
        Station,
        TresorerieStation.station_id == Station.id
    ).filter(
        Station.compagnie_id == current_user.compagnie_id
    ).all()

    # Calcul des totaux pour chaque trésorerie
    total_solde_initial = 0
    total_solde_final = 0
    total_entrees = 0
    total_sorties = 0

    details = []

    for trésorerie in trésoreries_station:
        # Solde initial
        solde_initial = float(trésorerie.solde_initial or 0)

        # Récupération des mouvements dans la période
        mouvements = db.query(MouvementTresorerie).filter(
            MouvementTresorerie.trésorerie_station_id == trésorerie.id,
            MouvementTresorerie.date_mouvement >= date_debut_obj,
            MouvementTresorerie.date_mouvement <= date_fin_obj,
            MouvementTresorerie.statut == "validé"
        ).all()

        total_entrees_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "entrée")
        total_sorties_per = sum(float(m.montant) for m in mouvements if m.type_mouvement == "sortie")

        # Calcul du solde final
        solde_final = solde_initial + total_entrees_per - total_sorties_per

        details.append({
            "trésorerie_id": str(trésorerie.id),
            "nom": trésorerie.trésorerie.nom if trésorerie.trésorerie else "N/A",
            "station": str(trésorerie.station_id),
            "solde_initial": solde_initial,
            "solde_final": solde_final,
            "total_entrees": total_entrees_per,
            "total_sorties": total_sorties_per
        })

        # Ajout aux totaux généraux
        total_solde_initial += solde_initial
        total_solde_final += solde_final
        total_entrees += total_entrees_per
        total_sorties += total_sorties_per

    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "solde_initial": total_solde_initial,
        "solde_final": total_solde_final,
        "total_entrees": total_entrees,
        "total_sorties": total_sorties,
        "details": details,
        "message": "Bilan de trésorerie calculé à partir des données de trésorerie"
    }

@router.get("/stocks")
async def get_bilan_stocks(
    date: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would aggregate stock data from produits/stocks modules
    
    # For now, return a placeholder response
    return {
        "date": date,
        "details": {
            "carburant": {"essence": 10000, "diesel": 8000},
            "boutique": {"total_value": 500000},
            "gaz": {"total_value": 200000}
        },
        "message": "This endpoint would aggregate stock data from produits and stocks modules"
    }

@router.get("/tiers")
async def get_bilan_tiers(
    date: str,  # Format: YYYY-MM-DD
    type_tiers: str = None,  # client, fournisseur, employe
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would aggregate tiers data from tiers, mouvements_financiers, and other modules
    
    # For now, return a placeholder response
    return {
        "date": date,
        "type_tiers": type_tiers or "all",
        "details": {
            "total": 50,
            "actif": 45,
            "solde_total": 2500000
        },
        "message": "This endpoint would aggregate tiers data from tiers and mouvements_financiers modules"
    }

@router.get("/export")
async def export_bilans(
    format: str = "pdf",  # pdf, excel, csv
    date_debut: str = None,  # Format: YYYY-MM-DD
    date_fin: str = None,    # Format: YYYY-MM-DD
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # This is a placeholder implementation
    # In a real application, this would generate a report in the specified format
    
    # For now, return a placeholder response
    return {
        "format": format,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "message": f"Bilans exported in {format} format",
        "file_url": "/api/v1/bilans/reports/rapport.pdf"  # Placeholder URL
    }
