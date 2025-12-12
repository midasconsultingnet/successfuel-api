# Modèle de données - Module Ventes Boutique

## Entités principales

### Vente_Boutique
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - client_id (UUID, référence à Tiers de type client, optionnel)
  - date_vente (datetime, obligatoire)
  - montant_total (decimal, calculé)
  - type_vente (string: "produit", "service", "hybride", obligatoire)
  - statut (string: "en_cours", "terminée", "annulée", default "en_cours")
  - trésorerie_id (UUID, référence à Trésorerie_Station)
  - utilisateur_id (UUID, référence à Utilisateur)
  - remise_globale (decimal, default 0)
  - numero_piece_comptable (string)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Tiers (client, optionnel)
  - N..1 avec Trésorerie_Station
  - N..1 avec Utilisateur
  - 1..* avec Ligne_Vente
  - 1..* avec Mouvement_Tresorerie
  - 1..* avec Avoir (via module Mouvements Financiers pour annulations)

### Ligne_Vente
- **Champs**:
  - id (UUID)
  - vente_boutique_id (UUID, référence à Vente_Boutique)
  - produit_id (UUID, référence à Produit)
  - quantite (decimal, obligatoire)
  - prix_unitaire (decimal, obligatoire)
  - montant (decimal, calculé)
  - remise_ligne (decimal, default 0)

- **Relations**:
  - N..1 avec Vente_Boutique
  - N..1 avec Produit

### Promotion
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - description (text)
  - type_promotion (string: "pourcentage", "montant_fixe", "achat_groupé", "quantité", etc., obligatoire)
  - valeur_promotion (decimal, obligatoire)
  - date_debut (datetime, obligatoire)
  - date_fin (datetime, obligatoire)
  - statut (string: "active", "inactive", "expirée", default "inactive")
  - conditions (jsonb)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - 1..* avec Application_Promotion

### Application_Promotion
- **Champs**:
  - id (UUID)
  - promotion_id (UUID, référence à Promotion)
  - vente_boutique_id (UUID, référence à Vente_Boutique, optionnel)
  - ligne_vente_id (UUID, référence à Ligne_Vente, optionnel)
  - montant_applique (decimal, obligatoire)
  - date_application (datetime, obligatoire)

- **Relations**:
  - N..1 avec Promotion
  - N..1 avec Vente_Boutique (optionnel)
  - N..1 avec Ligne_Vente (optionnel)

### Historique_Vente
- **Champs**:
  - id (UUID)
  - vente_boutique_id (UUID, référence à Vente_Boutique)
  - utilisateur_id (UUID, référence à Utilisateur)
  - type_historique (string: "création", "modification", "validation", "annulation", obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - date_historique (datetime, obligatoire)
  - motif_modification (text, optionnel)

- **Relations**:
  - N..1 avec Vente_Boutique
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Tiers**: Les ventes peuvent être associées à des clients
- **Module Produits et Stocks**: Les ventes concernent des produits de type boutique, gaz, lubrifiant
- **Module Trésoreries**: Les ventes affectent les trésoreries
- **Module Mouvements Financiers**: Pour les avoirs en cas d'annulation
- **Module Utilisateurs**: Les utilisateurs effectuent les ventes
- **Module États, Bilans et Comptabilité**: Pour les rapports de ventes
- **Module Structure de la Compagnie**: Les ventes sont liées à une station spécifique

## Contraintes d'intégrité
- Une vente est liée à une seule trésorerie de station
- Les produits vendus doivent être disponibles en stock (sauf pour les services)
- Les modifications de vente peuvent entraîner des avoirs
- Le type de vente peut être produit, service ou hybride (produit + service)
- Les annulations partielles ou totales génèrent des avoirs dans le module Mouvements Financiers

## Vues de reporting

### vue_ventes_boutique
- **Description**: Vue consolidée des ventes boutique avec détails des stations, clients, utilisateurs et trésoreries
- **Jointures**:
  - vente_boutique JOIN station ON (vente_boutique.station_id = station.id)
  - vente_boutique LEFT JOIN tiers ON (vente_boutique.client_id = tiers.id)
  - vente_boutique JOIN utilisateur ON (vente_boutique.utilisateur_id = utilisateur.id)
  - vente_boutique JOIN trésorerie_station ON (vente_boutique.trésorerie_id = trésorerie_station.id)
  - trésorerie_station JOIN trésorerie ON (trésorerie_station.trésorerie_id = trésorerie.id)
- **Champs**:
  - vb.id
  - vb.station_id
  - s.nom AS station_nom
  - vb.client_id
  - t.nom AS client_nom
  - vb.date_vente
  - vb.montant_total
  - vb.type_vente
  - vb.statut
  - vb.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
  - vb.trésorerie_id
  - trs.nom AS trésorerie_nom