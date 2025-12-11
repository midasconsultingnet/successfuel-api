from .common import get_translation as get_common_translation
from .auth import get_translation as get_auth_translation
from .user import get_translation as get_user_translation
from .company import get_translation as get_company_translation
from .purchase import get_translation as get_purchase_translation
from .sale import get_translation as get_sale_translation
from .stock import get_translation as get_stock_translation
from .inventory import get_translation as get_inventory_translation
from .delivery import get_translation as get_delivery_translation

def get_translation(key, lang="fr", module="common"):
    """
    Fonction centrale pour récupérer une traduction à partir de n'importe quel module
    """
    # Dictionnaire des fonctions de traduction par module
    translation_functions = {
        "common": get_common_translation,
        "auth": get_auth_translation,
        "user": get_user_translation,
        "company": get_company_translation,
        "purchase": get_purchase_translation,
        "sale": get_sale_translation,
        "stock": get_stock_translation,
        "inventory": get_inventory_translation,
        "delivery": get_delivery_translation
    }
    
    # Vérifier si le module existe dans nos fonctions
    if module in translation_functions:
        return translation_functions[module](key, lang, module)
    else:
        # Si le module n'est pas reconnu, retourner la clé elle-même
        return key