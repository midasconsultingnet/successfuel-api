from .translations import get_translation as _get_translation

# Pour la rétrocompatibilité, on expose toujours la même interface
def get_translation(key, lang="fr", module="common"):
    """
    Récupère une traduction pour une clé donnée
    Cette fonction est conservée pour la rétrocompatibilité
    """
    return _get_translation(key, lang, module)