TRANSLATIONS = {
    "sale": {
        "sale_not_found": {
            "fr": "Vente introuvable",
            "en": "Sale not found"
        },
        "sale_created_successfully": {
            "fr": "Vente créée avec succès",
            "en": "Sale created successfully"
        },
        "sale_updated_successfully": {
            "fr": "Vente mise à jour avec succès",
            "en": "Sale updated successfully"
        },
        "sale_deleted_successfully": {
            "fr": "Vente supprimée avec succès",
            "en": "Sale deleted successfully"
        }
    }
}

def get_translation(key, lang="fr", module="sale"):
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