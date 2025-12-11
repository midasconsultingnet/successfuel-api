TRANSLATIONS = {
    "auth": {
        "invalid_credentials": {
            "fr": "Identifiants invalides",
            "en": "Invalid credentials"
        },
        "access_denied": {
            "fr": "Accès refusé",
            "en": "Access denied"
        },
        "insufficient_permissions": {
            "fr": "Permissions insuffisantes pour créer des utilisateurs",
            "en": "Insufficient permissions to create users"
        },
        "logged_out_successfully": {
            "fr": "Déconnecté avec succès",
            "en": "Successfully logged out"
        },
        "login_already_registered": {
            "fr": "Login déjà enregistré",
            "en": "Login already registered"
        },
        "email_already_registered": {
            "fr": "Email déjà enregistré",
            "en": "Email already registered"
        },
        "email_already_registered_by_another_user": {
            "fr": "Email déjà enregistré par un autre utilisateur",
            "en": "Email already registered by another user"
        },
        "login_already_registered_by_another_user": {
            "fr": "Login déjà enregistré par un autre utilisateur",
            "en": "Login already registered by another user"
        }
    }
}

def get_translation(key, lang="fr", module="auth"):
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