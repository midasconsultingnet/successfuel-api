J'ai identifié que le fichier 'D:\succes_fuel_v2\api\produits\router.py' contient des doublons de fonctions qui causent des avertissements dans FastAPI. Après avoir supprimé l'un des doublons (la fonction get_lots), il reste encore une fonction create_lot dupliquée qui cause un avertissement.

Le problème est dû à un encodage incorrect dans le fichier qui empêche l'édition correcte.