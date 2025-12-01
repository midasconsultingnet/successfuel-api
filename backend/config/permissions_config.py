"""
Configuration for permissions related to structure management features
"""
from typing import List, Dict
from models.structures import Module, Permission

# Define the new modules and permissions
STRUCTURE_MODULES_PERMISSIONS = {
    "barremage": {
        "permissions": [
            {"libelle": "barremage.creer", "description": "Créer des entrées de barremage cuves"},
            {"libelle": "barremage.lire", "description": "Lire les entrées de barremage cuves"},
            {"libelle": "barremage.modifier", "description": "Modifier les entrées de barremage cuves"},
            {"libelle": "barremage.supprimer", "description": "Supprimer les entrées de barremage cuves"},
            {"libelle": "barremage.importer", "description": "Importer des données de barremage cuves depuis Excel"}
        ]
    },
    "pompes": {
        "permissions": [
            {"libelle": "pompes.creer", "description": "Créer des pompes"},
            {"libelle": "pompes.lire", "description": "Lire les pompes"},
            {"libelle": "pompes.modifier", "description": "Modifier les pompes"},
            {"libelle": "pompes.supprimer", "description": "Supprimer les pompes"}
        ]
    },
    "pistolets": {
        "permissions": [
            {"libelle": "pistolets.creer", "description": "Créer des pistolets"},
            {"libelle": "pistolets.lire", "description": "Lire les pistolets"},
            {"libelle": "pistolets.modifier", "description": "Modifier les pistolets"},
            {"libelle": "pistolets.supprimer", "description": "Supprimer les pistolets"}
        ]
    },
    "historique_prix_carburants": {
        "permissions": [
            {"libelle": "historique_prix_carburants.creer", "description": "Créer des historiques de prix carburants"},
            {"libelle": "historique_prix_carburants.lire", "description": "Lire les historiques de prix carburants"}
        ]
    },
    "historique_prix_articles": {
        "permissions": [
            {"libelle": "historique_prix_articles.creer", "description": "Créer des historiques de prix articles"},
            {"libelle": "historique_prix_articles.lire", "description": "Lire les historiques de prix articles"}
        ]
    },
    "historique_index_pistolets": {
        "permissions": [
            {"libelle": "historique_index_pistolets.creer", "description": "Créer des historiques d'index pistolets"},
            {"libelle": "historique_index_pistolets.lire", "description": "Lire les historiques d'index pistolets"}
        ]
    }
}


def get_all_structure_permissions() -> List[Dict]:
    """Get all permissions for structure management features"""
    all_permissions = []
    for module_name, module_data in STRUCTURE_MODULES_PERMISSIONS.items():
        for perm_data in module_data["permissions"]:
            all_permissions.append({
                "module": module_name,
                "libelle": perm_data["libelle"],
                "description": perm_data["description"]
            })
    return all_permissions


def get_module_permissions(module_name: str) -> List[Dict]:
    """Get permissions for a specific module"""
    if module_name in STRUCTURE_MODULES_PERMISSIONS:
        return STRUCTURE_MODULES_PERMISSIONS[module_name]["permissions"]
    return []


# Default permissions for gerant_compagnie (they should have access to all structure features for their company)
GERANT_COMPAGNIE_DEFAULT_PERMISSIONS = [
    "barremage.creer",
    "barremage.lire", 
    "barremage.modifier",
    "barremage.supprimer",
    "barremage.importer",
    "pompes.creer",
    "pompes.lire",
    "pompes.modifier", 
    "pompes.supprimer",
    "pistolets.creer",
    "pistolets.lire",
    "pistolets.modifier",
    "pistolets.supprimer",
    "historique_prix_carburants.creer",
    "historique_prix_carburants.lire",
    "historique_prix_articles.creer", 
    "historique_prix_articles.lire",
    "historique_index_pistolets.creer",
    "historique_index_pistolets.lire"
]