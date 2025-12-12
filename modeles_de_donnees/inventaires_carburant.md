# Modèle de données - Module Inventaires Carburant

## Entités principales

### Inventaire_Carburant
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - cuve_id (UUID, référence à Cuve)
  - carburant_id (UUID, référence à Carburant)
  - quantite_reelle (decimal, obligatoire)
  - date_inventaire (datetime, obligatoire)
  - statut (string: "brouillon", "en_cours", "terminé", "validé", "rapproché", "clôturé", default "brouillon")
  - utilisateur_id (UUID, référence à Utilisateur)
  - commentaire (text)
  - methode_mesure (string: "manuel", "jauge_digitale", "sonde_automatique", obligatoire)
  - seuil_tolerance (decimal, default provenant des paramètres)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Cuve
  - N..1 avec Carburant
  - N..1 avec Utilisateur
  - 1..* avec Ecart_Inventaire
  - 1..* avec Mouvement_Stock_Cuve (via ajustements)

### Ecart_Inventaire
- **Champs**:
  - id (UUID)
  - inventaire_carburant_id (UUID, référence à Inventaire_Carburant)
  - quantite_theorique (decimal, calculée)
  - quantite_reelle (decimal, provenant de l'inventaire)
  - ecart (decimal, calculé: quantite_reelle - quantite_theorique)
  - type_ecart (string: "perte", "évaporation", "anomalie", "erreur", "surplus", obligatoire)
  - seuil_tolerance (decimal, provenant de l'inventaire ou paramètres)
  - est_significatif (boolean, calculé)
  - commentaire (text)

- **Relations**:
  - N..1 avec Inventaire_Carburant

### Mouvement_Stock_Cuve
- **Champs**:
  - id (UUID)
  - livraison_carburant_id (UUID, référence à Livraison_Carburant, optionnel)
  - vente_carburant_id (UUID, référence à Vente_Carburant, optionnel)
  - inventaire_carburant_id (UUID, référence à Inventaire_Carburant, optionnel)
  - cuve_id (UUID, référence à Cuve)
  - type_mouvement (string: "entrée", "sortie", "ajustement", obligatoire)
  - quantite (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - stock_avant (decimal)
  - stock_apres (decimal)
  - utilisateur_id (UUID, référence à Utilisateur)
  - reference_origine (string, obligatoire)
  - module_origine (string, obligatoire)
  - statut (string: "validé", "annulé", default "validé")

- **Contraintes**:
  - Une seule référence possible : (livraison_carburant_id NOT NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id IS NULL)
    OR (livraison_carburant_id IS NULL AND vente_carburant_id NOT NULL AND inventaire_carburant_id IS NULL)
    OR (livraison_carburant_id IS NULL AND vente_carburant_id IS NULL AND inventaire_carburant_id NOT NULL)

- **Relations**:
  - N..1 avec Livraison_Carburant (optionnel)
  - N..1 avec Vente_Carburant (optionnel)
  - N..1 avec Inventaire_Carburant (optionnel)
  - N..1 avec Cuve
  - N..1 avec Utilisateur

### Parametre_Inventaire
- **Champs**:
  - id (UUID)
  - type_carburant (string, obligatoire)
  - seuil_tolerance (decimal, obligatoire)
  - saison (string, optionnel)
  - capacite_cuve (decimal, optionnel)
  - produit_id (UUID, référence à Produit, optionnel)
  - station_id (UUID, référence à Station, optionnel)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Produit (optionnel)
  - N..1 avec Station (optionnel)

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Les inventaires concernent les cuves de carburant
- **Module Produits et Stocks**: Les inventaires concernent des produits de type carburant
- **Module Utilisateurs**: Les utilisateurs effectuent les inventaires
- **Module États, Bilans et Comptabilité**: Pour les rapports d'inventaires
- **Module Mouvements Financiers**: Pour les ajustements financiers si écarts significatifs
- **Module Ventes Carburant**: Pour comparaison avec les quantités vendues

## Contraintes d'intégrité
- Un inventaire est lié à une seule cuve spécifique
- La quantité réelle est mesurée physiquement et comparée à la quantité théorique
- Les écarts significatifs sont classifiés selon des règles prédéfinies
- Les ajustements de stock sont effectués automatiquement après validation de l'inventaire
- Les utilisateurs ne peuvent pas modifier un inventaire une fois qu'il est validé