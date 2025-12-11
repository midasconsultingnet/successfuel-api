TRANSLATIONS = {
    "user": {
        "user_updated_successfully": {
            "fr": "Utilisateur mis à jour avec succès",
            "en": "User updated successfully"
        },
        "user_deleted_successfully": {
            "fr": "Utilisateur supprimé avec succès",
            "en": "User deleted successfully"
        },
        "user_created_successfully": {
            "fr": "Utilisateur créé avec succès",
            "en": "User created successfully"
        }
    }
}

def get_translation(key, lang="fr", module="user"):
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