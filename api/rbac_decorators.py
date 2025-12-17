from fastapi import Depends, HTTPException, status
from .auth.auth_handler import get_current_user_security
from .auth.schemas import UserWithPermissions
from .rbac_utils import check_permission
import uuid

def require_permission(*args):
    """
    Dépendance pour vérifier les permissions
    Accepte soit un seul paramètre (module_nom) soit deux paramètres (module_nom, action)
    Utilise la fonction get_current_user_security qui retourne un objet Pydantic
    """
    # Gérer les deux cas d'utilisation
    if len(args) == 1:
        # Un seul argument : nom du module
        module_nom = args[0]

        # Vérifier si le format est "Module Nom Complet" et le convertir
        if module_nom.startswith("Module "):
            # Convertir "Module Ventes Boutique" en "ventes_boutique"
            module_nom = convert_module_format(module_nom)
        # Pour les modules simples sans action, pas besoin de spécifier d'action
        action = None
    elif len(args) == 2:
        # Deux arguments : nom du module et action
        module_nom, action = args

        # Vérifier si le premier paramètre est au format "Module XX"
        if module_nom.startswith("Module "):
            module_nom = convert_module_format(module_nom)
    else:
        # Autre cas : lever une exception
        raise ValueError("require_permission prend 1 ou 2 arguments")

    async def permission_dependency(
        current_user: UserWithPermissions = Depends(get_current_user_security)
    ):
        # Vérifier si l'utilisateur est un gérant
        if current_user.role == "gerant_compagnie":
            return current_user  # Permission accordée

        # Vérifier si le module est dans les modules autorisés
        if module_nom not in current_user.modules_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé : permission nécessaire pour {module_nom}"
            )

        # Si une action est spécifiée, on pourrait vérifier les permissions spécifiques à l'action
        # Pour le moment, on se contente de vérifier la présence du module
        # Des vérifications d'action plus fines pourraient être ajoutées ici

        return current_user

    return permission_dependency


def convert_module_format(module_nom_complet):
    """
    Convertit un nom de module au format "Module XX" vers le format standard
    Ex: "Module Ventes Boutique" -> "ventes_boutique"
        "Module Achats Carburant" -> "achats_carburant"
    """
    # Retirer le préfixe "Module "
    module_clean = module_nom_complet[7:]  # Enlever "Module "

    # Convertir en minuscules et remplacer les espaces par des underscores
    module_standard = module_clean.lower().replace(" ", "_")

    return module_standard