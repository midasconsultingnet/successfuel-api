TRANSLATIONS = {
    "stock": {
        "stock_not_found": {
            "fr": "Stock introuvable",
            "en": "Stock not found"
        },
        "stock_created_successfully": {
            "fr": "Stock créé avec succès",
            "en": "Stock created successfully"
        },
        "stock_updated_successfully": {
            "fr": "Stock mis à jour avec succès",
            "en": "Stock updated successfully"
        },
        "stock_deleted_successfully": {
            "fr": "Stock supprimé avec succès",
            "en": "Stock deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="stock"):
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