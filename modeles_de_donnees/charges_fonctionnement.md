# Modèle de données - Module Charges de Fonctionnement

## Entités principales

### Categorie_Charge
- **Champs**:
  - id (UUID)
  - nom (string, obligatoire)
  - description (text)
  - type (string: "fixe", "variable", obligatoire)
  - seuil_alerte (decimal, optionnel)
  - compte_comptable_associe (string, optionnel)
  - hierarchie_parente_id (UUID, référence à Categorie_Charge, optionnel)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - 1..* avec Charge_Fonctionnement
  - N..1 avec elle-même (hierarchie_parente_id)

### Charge_Fonctionnement
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - categorie_id (UUID, référence à Categorie_Charge)
  - fournisseur_id (UUID, référence à Tiers de type fournisseur, optionnel)
  - date_charge (datetime, obligatoire)
  - montant (decimal, obligatoire)
  - description (text)
  - date_echeance (date, obligatoire)
  - statut (string: "prévu", "échu", "en_cours_paiement", "payé", default "prévu")
  - methode_paiement (string)
  - numero_piece_comptable (string)
  - utilisateur_id (UUID, référence à Utilisateur)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Categorie_Charge
  - N..1 avec Tiers (fournisseur, optionnel)
  - N..1 avec Utilisateur
  - 1..* avec Paiement_Charge
  - 1..* avec Mouvement_Tresorerie (via module Mouvements Financiers)

### Paiement_Charge
- **Champs**:
  - id (UUID)
  - charge_fonctionnement_id (UUID, référence à Charge_Fonctionnement)
  - trésorerie_station_id (UUID, référence à Trésorerie_Station)
  - montant_paye (decimal, obligatoire)
  - date_paiement (datetime, obligatoire)
  - utilisateur_id (UUID, référence à Utilisateur)
  - description (text)
  - numero_piece_comptable (string)

- **Relations**:
  - N..1 avec Charge_Fonctionnement
  - N..1 avec Trésorerie_Station
  - N..1 avec Utilisateur

### Historique_Charge
- **Champs**:
  - id (UUID)
  - charge_fonctionnement_id (UUID, référence à Charge_Fonctionnement)
  - utilisateur_id (UUID, référence à Utilisateur)
  - type_historique (string: "création", "modification", "paiement", "annulation", obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - date_historique (datetime, obligatoire)

- **Relations**:
  - N..1 avec Charge_Fonctionnement
  - N..1 avec Utilisateur

### Solde_Fournisseur_Charges
- **Champs**:
  - id (UUID)
  - fournisseur_id (UUID, référence à Tiers)
  - montant_du (decimal, calculé)
  - montant_paye (decimal, calculé)
  - solde_net (decimal, calculé)
  - date_dernier_calcul (datetime)

- **Relations**:
  - N..1 avec Tiers (fournisseur)

## Relations avec d'autres modules
- **Module Tiers**: Les charges peuvent être associées à des fournisseurs
- **Module Trésoreries**: Les paiements de charges affectent les trésoreries
- **Module Mouvements Financiers**: Pour la gestion des paiements et soldes
- **Module Utilisateurs**: Les utilisateurs effectuent les paiements
- **Module États, Bilans et Comptabilité**: Pour les rapports de charges
- **Module Structure de la Compagnie**: Les charges sont liées à une station spécifique

## Contraintes d'intégrité
- Une charge est liée à une seule station
- Les paiements successifs sont enregistrés séparément pour chaque charge
- Le solde dû est calculé à partir des montants des charges et des paiements effectués
- Les charges peuvent être classées dans des catégories hiérarchisées
- Les charges récurrentes peuvent être configurées selon une périodicité