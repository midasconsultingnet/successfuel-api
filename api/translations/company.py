TRANSLATIONS = {
    "company": {
        "company_not_found": {
            "fr": "Compagnie introuvable",
            "en": "Company not found"
        },
        "company_created_successfully": {
            "fr": "Compagnie créée avec succès",
            "en": "Company created successfully"
        },
        "company_updated_successfully": {
            "fr": "Compagnie mise à jour avec succès",
            "en": "Company updated successfully"
        },
        "company_deleted_successfully": {
            "fr": "Compagnie supprimée avec succès",
            "en": "Company deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="company"):
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