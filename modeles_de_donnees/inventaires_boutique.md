# Modèle de données - Module Inventaires Boutique

## Entités principales

### Inventaire_Boutique
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - produit_id (UUID, référence à Produit)
  - quantite_reelle (decimal, obligatoire)
  - date_inventaire (datetime, obligatoire)
  - statut (string: "brouillon", "en_cours", "terminé", "validé", "rapproché", "clôturé", default "brouillon")
  - utilisateur_id (UUID, référence à Utilisateur)
  - commentaire (text)
  - seuil_tolerance (decimal, default provenant des paramètres)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Produit
  - N..1 avec Utilisateur
  - 1..* avec Ecart_Inventaire
  - 1..* avec Mouvement_Stock (via ajustements)

### Ecart_Inventaire
- **Champs**:
  - id (UUID)
  - inventaire_boutique_id (UUID, référence à Inventaire_Boutique)
  - quantite_theorique (decimal, calculée)
  - quantite_reelle (decimal, provenant de l'inventaire)
  - ecart (decimal, calculé: quantite_reelle - quantite_theorique)
  - type_ecart (string: "perte", "anomalie", "erreur", "surplus", obligatoire)
  - seuil_tolerance (decimal, provenant de l'inventaire ou paramètres)
  - est_significatif (boolean, calculé)
  - commentaire (text)

- **Relations**:
  - N..1 avec Inventaire_Boutique

### Mouvement_Stock
- **Champs**:
  - id (UUID)
  - inventaire_boutique_id (UUID, référence à Inventaire_Boutique)
  - produit_id (UUID, référence à Produit)
  - type_mouvement (string: "ajustement", obligatoire)
  - quantite (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - description (text)
  - utilisateur_id (UUID, référence à Utilisateur)
  - reference_origine (string, obligatoire)
  - module_origine (string: "inventaire_boutique", obligatoire)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Inventaire_Boutique
  - N..1 avec Produit
  - N..1 avec Utilisateur

### Parametre_Inventaire
- **Champs**:
  - id (UUID)
  - type_produit (string, obligatoire: "boutique", "lubrifiant", "gaz", etc.)
  - seuil_tolerance (decimal, obligatoire)
  - categorie_produit (string, optionnel)
  - saison (string, optionnel)
  - produit_id (UUID, référence à Produit, optionnel)
  - station_id (UUID, référence à Station, optionnel)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Produit (optionnel)
  - N..1 avec Station (optionnel)

## Relations avec d'autres modules
- **Module Produits et Stocks**: Les inventaires concernent les produits de type boutique, gaz, lubrifiant
- **Module Structure de la Compagnie**: Les inventaires sont liés à une station spécifique
- **Module Utilisateurs**: Les utilisateurs effectuent les inventaires
- **Module États, Bilans et Comptabilité**: Pour les rapports d'inventaires
- **Module Mouvements Financiers**: Pour les ajustements financiers si écarts significatifs
- **Module Ventes Boutique**: Pour comparaison avec les quantités vendues

## Contraintes d'intégrité
- Un inventaire est lié à un seul produit spécifique dans une station
- La quantité réelle est mesurée physiquement et comparée à la quantité théorique
- Les écarts significatifs sont classifiés selon des règles prédéfinies
- Les ajustements de stock sont effectués automatiquement après validation de l'inventaire
- Les utilisateurs ne peuvent pas modifier un inventaire une fois qu'il est validé