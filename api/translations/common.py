TRANSLATIONS = {
    "common": {
        "welcome_message": {
            "fr": "Bienvenue sur notre plateforme !",
            "en": "Welcome to our platform!"
        },
        "hello_world": {
            "fr": "Bonjour le monde",
            "en": "Hello World"
        },
        "user_not_found": {
            "fr": "Utilisateur introuvable",
            "en": "User not found"
        }
    }
}

def get_translation(key, lang="fr", module="common"):
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