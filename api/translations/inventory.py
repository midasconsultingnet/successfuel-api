TRANSLATIONS = {
    "inventory": {
        "inventory_not_found": {
            "fr": "Inventaire introuvable",
            "en": "Inventory not found"
        },
        "inventory_created_successfully": {
            "fr": "Inventaire créé avec succès",
            "en": "Inventory created successfully"
        },
        "inventory_updated_successfully": {
            "fr": "Inventaire mis à jour avec succès",
            "en": "Inventory updated successfully"
        },
        "inventory_deleted_successfully": {
            "fr": "Inventaire supprimé avec succès",
            "en": "Inventory deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="inventory"):
    """
    Récupère une traduction pour une clé donnée
    """
    module_translations = TRANSLATIONS.get(module, {})
    translation_dict = module_translations.get(key, {})
    
    # Essayer d'obtenir la traduction dans la langue demandée
    result = translation_dict.get(lang)
    
    # Si pas trouvée, essayer la traduction française par défaut
    if result is None:
        result = translation_dict.get("fr")
    
    # Si toujours pas trouvée, retourner la clé elle-même
    if result is None:
        result = key
        
    return result