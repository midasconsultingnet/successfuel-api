# Modèle de données - Module Achats Carburant

## Entités principales

### Achat_Carburant
- **Champs**:
  - id (UUID)
  - fournisseur_id (UUID, référence à Tiers de type fournisseur)
  - date_achat (datetime, obligatoire)
  - numero_bl (string, obligatoire)
  - numero_facture (string, obligatoire)
  - montant_total (decimal, obligatoire)
  - statut (string: "brouillon", "validé", "facturé", "annulé", default "brouillon")
  - station_id (UUID, référence à Station)
  - utilisateur_id (UUID, référence à Utilisateur)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Tiers (fournisseur)
  - N..1 avec Station
  - N..1 avec Utilisateur
  - 1..* avec Ligne_Achat_Carburant
  - 1..* avec Mouvement_Tresorerie (via module Mouvements Financiers)
  - 1..* avec Avoir_Compensation (via module Mouvements Financiers)

### Ligne_Achat_Carburant
- **Champs**:
  - id (UUID)
  - achat_carburant_id (UUID, référence à Achat_Carburant)
  - carburant_id (UUID, référence à Carburant)
  - quantite (decimal, obligatoire)
  - prix_unitaire (decimal, obligatoire)
  - montant (decimal, calculé)
  - cuve_id (UUID, référence à Cuve)

- **Relations**:
  - N..1 avec Achat_Carburant
  - N..1 avec Carburant
  - N..1 avec Cuve

### Compensation_Financiere
- **Champs**:
  - id (UUID)
  - achat_carburant_id (UUID, référence à Achat_Carburant)
  - type_compensation (string: "avoir_reçu", "avoir_dû", obligatoire)
  - quantite_theorique (decimal, obligatoire)
  - quantite_reelle (decimal, obligatoire)
  - difference (decimal, calculé)
  - montant_compensation (decimal, obligatoire)
  - motif (text)
  - statut (string: "émis", "utilisé", "partiellement_utilisé", "expiré", default "émis")
  - date_creation (datetime)
  - date_expiration (datetime, optionnel)

- **Relations**:
  - N..1 avec Achat_Carburant
  - 1..* avec Avoir_Compensation

### Avoir_Compensation
- **Champs**:
  - id (UUID)
  - compensation_financiere_id (UUID, référence à Compensation_Financiere)
  - tiers_id (UUID, référence à Tiers)
  - montant (decimal, obligatoire)
  - date_emission (datetime, obligatoire)
  - date_utilisation (datetime, optionnel)
  - statut (string: "émis", "utilisé", "partiellement_utilisé", "expiré", default "émis")
  - utilisateur_emission_id (UUID, référence à Utilisateur)
  - utilisateur_utilisation_id (UUID, référence à Utilisateur, optionnel)

- **Relations**:
  - N..1 avec Compensation_Financiere
  - N..1 avec Tiers
  - N..1 avec Utilisateur (utilisateur_emission_id)
  - N..1 avec Utilisateur (utilisateur_utilisation_id, optionnel)

## Relations avec d'autres modules
- **Module Tiers**: Les achats sont effectués auprès de fournisseurs (tiers de type fournisseur)
- **Module Structure de la Compagnie**: Les achats affectent les cuves de carburant
- **Module Produits et Stocks**: Les achats concernent des produits de type carburant
- **Module Mouvements Financiers**: Les paiements sont gérés via ce module
- **Module Trésoreries**: Les règlements affectent les trésoreries
- **Module États, Bilans et Comptabilité**: Pour les rapports d'achats
- **Module Livraisons Carburant**: Les achats peuvent être liés aux livraisons

## Contraintes d'intégrité
- Un achat de carburant est toujours associé à un fournisseur
- Les quantités achetées affectent les stocks via les cuves
- Les compensations financières sont créées automatiquement quand la quantité réelle diffère de la quantité théorique
- Les avoirs de compensation sont liés à des tiers (fournisseurs)
- Les achats validés affectent le coût moyen pondéré des produits concernés

## Vues de reporting

### vue_achats_carburant
- **Description**: Vue consolidée des achats de carburant avec détails des stations, fournisseurs, carburants et utilisateurs
- **Jointures**:
  - achat_carburant JOIN tiers ON (achat_carburant.fournisseur_id = tiers.id)
  - achat_carburant JOIN station ON (achat_carburant.station_id = station.id)
  - achat_carburant JOIN utilisateur ON (achat_carburant.utilisateur_id = utilisateur.id)
  - ligne_achat_carburant ON (achat_carburant.id = ligne_achat_carburant.achat_carburant_id)
  - carburant ON (ligne_achat_carburant.carburant_id = carburant.id)
- **Champs**:
  - ac.id
  - ac.fournisseur_id
  - t.nom AS fournisseur_nom
  - ac.date_achat
  - ac.numero_bl
  - ac.numero_facture
  - ac.montant_total
  - ac.statut
  - ac.station_id
  - s.nom AS station_nom
  - ac.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
  - lac.carburant_id
  - c.nom AS carburant_libelle
  - lac.quantite
  - lac.prix_unitaire
  - lac.montant