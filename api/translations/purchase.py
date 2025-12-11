TRANSLATIONS = {
    "purchase": {
        "purchase_not_found": {
            "fr": "Achat introuvable",
            "en": "Purchase not found"
        },
        "purchase_created_successfully": {
            "fr": "Achat créé avec succès",
            "en": "Purchase created successfully"
        },
        "purchase_updated_successfully": {
            "fr": "Achat mis à jour avec succès",
            "en": "Purchase updated successfully"
        },
        "purchase_deleted_successfully": {
            "fr": "Achat supprimé avec succès",
            "en": "Purchase deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="purchase"):
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