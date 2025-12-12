# Modèle de données - Module Produits et Stocks Complet

## Entités principales

### Famille_Produit
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - description (text)
  - code (string)
  - famille_parente_id (UUID, référence à Famille_Produit, optionnel)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - 1..* avec Produit
  - N..1 avec elle-même (famille_parente_id)

### Produit
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - code (string, obligatoire)
  - description (text)
  - unite_mesure (string: "litre", "unité", "kg", etc., obligatoire)
  - famille_id (UUID, référence à Famille_Produit)
  - type (string: "boutique", "lubrifiant", "gaz", "service", obligatoire)
  - prix_vente (decimal, obligatoire)
  - seuil_stock_minimum (decimal, optionnel)
  - est_avec_stock (boolean, default true - faux pour services)
  - station_id (UUID, référence à Station)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Famille_Produit
  - N..1 avec Station
  - 1..* avec Mouvement_Stock
  - 1..* avec Ligne_Commande_Achat
  - 1..* avec Ligne_Vente
  - 1..* avec Inventaire_Produit

### Mouvement_Stock
- **Champs**:
  - id (UUID)
  - produit_id (UUID, référence à Produit)
  - type_mouvement (string: "entrée", "sortie", "ajustement", "inventaire", obligatoire)
  - quantite (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - description (text)
  - module_origine (string, obligatoire)
  - reference_origine (string, obligatoire)
  - utilisateur_id (UUID, référence à Utilisateur)
  - cout_unitaire (decimal, pour calcul du coût moyen pondéré)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Produit
  - N..1 avec Utilisateur

### Stock_Produit
- **Champs**:
  - id (UUID)
  - produit_id (UUID, référence à Produit)
  - quantite_theorique (decimal, calculé)
  - quantite_reelle (decimal, calculé)
  - date_dernier_calcul (datetime)
  - cout_moyen_pondere (decimal, calculé)

- **Relations**:
  - 1..1 avec Produit (via produit_id)

### Lot_Produit
- **Champs**:
  - id (UUID)
  - produit_id (UUID, référence à Produit)
  - numero_lot (string, obligatoire)
  - quantite (decimal, obligatoire)
  - date_production (date)
  - date_peremption (date, obligatoire pour produits avec DLC)
  - date_creation (datetime)

- **Relations**:
  - N..1 avec Produit

### Unite_Mesure
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - symbole (string, obligatoire)
  - facteur_conversion (decimal, default 1)

- **Relations**:
  - 1..* avec Produit (via champ unite_mesure)

## Relations avec d'autres modules
- **Module Structure de la Compagnie**: Les produits sont associés à une station
- **Module Ventes Boutique**: Les produits sont vendus dans les ventes boutique
- **Module Achats Boutique**: Les produits sont achetés dans les commandes d'achat
- **Module Inventaires Boutique**: Les produits font l'objet d'inventaires physiques
- **Module États, Bilans et Comptabilité**: Pour les rapports de stock

## Contraintes d'intégrité
- Un produit appartient à une seule station
- Le seuil de stock minimum ne s'applique que pour les produits avec stock
- Les produits de type service n'ont pas de stock physique
- La quantité en stock ne peut pas être négative
- Le coût moyen pondéré est recalculé à chaque mouvement d'entrée
- Les lots sont utilisés selon la méthode FIFO pour les produits avec DLC