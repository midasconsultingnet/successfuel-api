# Modèle de données - Module Livraisons Carburant

## Entités principales

### Livraison_Carburant
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - cuve_id (UUID, référence à Cuve)
  - carburant_id (UUID, référence à Carburant)
  - quantite_livree (decimal, obligatoire)
  - date_livraison (datetime, obligatoire)
  - fournisseur_id (UUID, référence à Tiers de type fournisseur, optionnel)
  - numero_bl (string)
  - numero_facture (string)
  - jauge_avant_livraison (decimal)
  - jauge_apres_livraison (decimal)
  - utilisateur_id (UUID, référence à Utilisateur)
  - statut (string: "enregistrée", "validée", "annulée", default "enregistrée")
  - description (text)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Cuve
  - N..1 avec Carburant
  - N..1 avec Tiers (fournisseur, optionnel)
  - N..1 avec Utilisateur
  - 1..* avec Mouvement_Stock_Cuve (via module Structure de la Compagnie)

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

### Historique_Livraison
- **Champs**:
  - id (UUID)
  - livraison_carburant_id (UUID, référence à Livraison_Carburant)
  - utilisateur_id (UUID, référence à Utilisateur)
  - type_historique (string: "création", "modification", "validation", "annulation", obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - date_historique (datetime, obligatoire)
  - description (text)

- **Relations**:
  - N..1 avec Livraison_Carburant
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Les livraisons affectent les cuves de carburant
- **Module Tiers**: Les livraisons peuvent être associées à des fournisseurs
- **Module Produits et Stocks**: Les livraisons concernent des produits de type carburant
- **Module Utilisateurs**: Les utilisateurs effectuent les livraisons
- **Module États, Bilans et Comptabilité**: Pour les rapports de livraisons
- **Module Achats Carburant**: Les livraisons peuvent être liées aux achats
- **Module Ventes Carburant**: Les ajustements de stock sont liés aux mouvements de stock de ventes et livraisons

## Contraintes d'intégrité
- Une livraison affecte une seule cuve spécifique
- La quantité livrée affecte directement le niveau de la cuve
- Le stock après livraison ne peut pas dépasser la capacité de la cuve
- L'historique des modifications est conservé pour chaque livraison
- Les mouvements de stock sont liés à la livraison qui les a générés
- Un mouvement de stock de type "entrée" est créé automatiquement lors de la validation de la livraison