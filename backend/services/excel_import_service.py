from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import pandas as pd
import io
from models.structures import BarremageCuve, Cuve, Station
from datetime import datetime


def import_barremage_from_excel(db: Session, file: UploadFile, current_user, cuve_id: str, station_id: str) -> Dict[str, Any]:
    """
    Import barremage data from an Excel file
    """
    # Vérifier le type de fichier
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être au format Excel (.xlsx ou .xls)"
        )

    try:
        # Lire le contenu du fichier
        contents = file.file.read()
        excel_data = pd.read_excel(io.BytesIO(contents))

        # Vérifier que la cuve et la station existent
        cuve = db.query(Cuve).filter(Cuve.id == cuve_id).first()
        if not cuve:
            raise HTTPException(
                status_code=404,
                detail=f"Cuve avec ID {cuve_id} non trouvée"
            )

        station = db.query(Station).filter(Station.id == station_id).first()
        if not station:
            raise HTTPException(
                status_code=404,
                detail=f"Station avec ID {station_id} non trouvée"
            )

        # Vérifier que la cuve et la station appartiennent à la même compagnie
        if str(cuve.compagnie_id) != str(station.compagnie_id):
            raise HTTPException(
                status_code=400,
                detail="La cuve et la station n'appartiennent pas à la même compagnie"
            )

        # Récupérer la compagnie de l'utilisateur pour vérification
        user_company_id = str(current_user.compagnie_id) if current_user.compagnie_id else None
        if not user_company_id:
            raise HTTPException(
                status_code=403,
                detail="L'utilisateur n'est associé à aucune compagnie"
            )

        # Vérifier que la cuve et la station appartiennent à la compagnie de l'utilisateur
        if str(cuve.compagnie_id) != user_company_id:
            raise HTTPException(
                status_code=403,
                detail="La cuve et la station n'appartiennent pas à la compagnie de l'utilisateur"
            )

        # Vérifier les colonnes requises dans le fichier (seulement hauteur et volume)
        required_columns = ['hauteur', 'volume']
        for col in required_columns:
            if col not in excel_data.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Colonne requise manquante: {col}"
                )

        # Compter les lignes traitées et les erreurs
        total_rows = len(excel_data)
        successful_imports = 0
        errors = []

        for index, row in excel_data.iterrows():
            try:
                # Créer l'entrée de barremage dans la base de données
                # Convertir les types numpy en types Python standard pour éviter les erreurs d'adaptation
                hauteur = float(row['hauteur']) if pd.notna(row['hauteur']) else 0.0
                volume = float(row['volume']) if pd.notna(row['volume']) else 0.0

                barremage = BarremageCuve(
                    cuve_id=cuve_id,
                    station_id=station_id,
                    hauteur=hauteur,
                    volume=volume,
                    compagnie_id=user_company_id,
                    statut='Actif'
                )

                db.add(barremage)
                successful_imports += 1

            except Exception as e:
                errors.append(f"Ligne {index + 1}: Erreur lors de l'import - {str(e)}")

        # Commit toutes les transactions
        db.commit()

        # Retourner les résultats
        return {
            "success": True,
            "total_rows": total_rows,
            "successful_imports": successful_imports,
            "failed_imports": total_rows - successful_imports,
            "errors": errors
        }

    except HTTPException:
        # Ré-émettre les erreurs HTTP pour ne pas les envelopper
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'importation du fichier Excel: {str(e)}"
        )