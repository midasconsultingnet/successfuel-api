import csv
import json
from datetime import datetime, timezone
from io import StringIO
from typing import Dict, Any
from fastapi.responses import StreamingResponse


def generate_export_data(data: Dict[str, Any], export_format: str = "csv") -> StreamingResponse:
    """
    Générer un fichier d'export à partir des données fournies
    """
    if export_format.lower() == "csv":
        # Convertir les données en CSV
        output = StringIO()
        writer = csv.writer(output)

        # Écrire l'en-tête
        headers = []

        # Pour simplifier, on suppose que les données contiennent un tableau de lignes
        if "details" in data and isinstance(data["details"], list) and len(data["details"]) > 0:
            # Extraire les clés du premier élément comme en-têtes
            headers = list(data["details"][0].keys())
            writer.writerow(headers)

            # Écrire les lignes
            for item in data["details"]:
                row = [item.get(key, "") for key in headers]
                writer.writerow(row)
        else:
            # Si pas de détails, exporter les autres données
            headers = list(data.keys())
            writer.writerow(headers)
            row = [data.get(key, "") for key in headers]
            writer.writerow(row)

        output.seek(0)
        response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename=export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        return response

    elif export_format.lower() == "json":
        # Convertir les données en JSON
        json_content = json.dumps(data, default=str, ensure_ascii=False, indent=2)
        response = StreamingResponse(iter([json_content]), media_type="application/json")
        response.headers["Content-Disposition"] = f"attachment; filename=export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        return response

    else:
        raise ValueError(f"Format d'export non supporté: {export_format}")


def export_bilan_tresorerie(
    data: Dict[str, Any], 
    export_format: str = "csv"
) -> StreamingResponse:
    """
    Exporter le bilan de trésorerie dans le format spécifié
    """
    return generate_export_data(data, export_format)


def export_bilan_tiers(
    data: Dict[str, Any], 
    export_format: str = "csv"
) -> StreamingResponse:
    """
    Exporter le bilan des tiers dans le format spécifié
    """
    return generate_export_data(data, export_format)


def export_bilan_operations(
    data: Dict[str, Any], 
    export_format: str = "csv"
) -> StreamingResponse:
    """
    Exporter le bilan des opérations dans le format spécifié
    """
    return generate_export_data(data, export_format)


def export_journal_operations(
    data: Dict[str, Any], 
    export_format: str = "csv"
) -> StreamingResponse:
    """
    Exporter le journal des opérations dans le format spécifié
    """
    return generate_export_data(data, export_format)


def export_journal_comptable(
    data: Dict[str, Any], 
    export_format: str = "csv"
) -> StreamingResponse:
    """
    Exporter le journal comptable dans le format spécifié
    """
    return generate_export_data(data, export_format)