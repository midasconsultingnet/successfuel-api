TRANSLATIONS = {
    "delivery": {
        "delivery_not_found": {
            "fr": "Livraison introuvable",
            "en": "Delivery not found"
        },
        "delivery_created_successfully": {
            "fr": "Livraison créée avec succès",
            "en": "Delivery created successfully"
        },
        "delivery_updated_successfully": {
            "fr": "Livraison mise à jour avec succès",
            "en": "Delivery updated successfully"
        },
        "delivery_deleted_successfully": {
            "fr": "Livraison supprimée avec succès",
            "en": "Delivery deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="delivery"):
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