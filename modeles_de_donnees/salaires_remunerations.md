# Modèle de données - Module Salaires et Rémunérations

## Entités principales

### Paie_Employe
- **Champs**:
  - id (UUID)
  - employe_id (UUID, référence à Tiers de type employé)
  - periode (string, format "YYYY-MM", obligatoire)
  - date_echeance (date, obligatoire)
  - date_paiement (date, optionnel)
  - salaire_base (decimal, obligatoire)
  - montant_total (decimal, calculé)
  - statut (string: "prévu", "échu", "payé", "dû", "en_retard", default "prévu")
  - methode_paiement (string)
  - utilisateur_gestion_id (UUID, référence à Utilisateur, optionnel)
  - commentaire (text)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Tiers (employé)
  - N..1 avec Utilisateur (utilisateur_gestion_id)
  - 1..* avec Element_Paie
  - 1..* avec Mouvement_Tresorerie (via paiements)
  - 1..* avec Creance_Employe (si non-paiement)

### Element_Paie
- **Champs**:
  - id (UUID)
  - paie_employe_id (UUID, référence à Paie_Employe)
  - type_element (string: "prime", "avance", "retenue", "cotisation", "impot", obligatoire)
  - libelle (string, obligatoire)
  - montant (decimal, obligatoire)
  - est_calcul_automatique (boolean, default false)
  - date_creation (datetime)

- **Relations**:
  - N..1 avec Paie_Employe

### Creance_Employe
- **Champs**:
  - id (UUID)
  - employe_id (UUID, référence à Tiers de type employé)
  - type_creance (string: "salaire_impaye", "avance", "pret", "autre", obligatoire)
  - montant_initial (decimal, obligatoire)
  - montant_restant (decimal, calculé)
  - date_creation (date, obligatoire)
  - date_echeance (date, optionnel)
  - taux_interet (decimal, optionnel)
  - statut (string: "en_cours", "payé", "partiellement_payé", default "en_cours")
  - utilisateur_gestion_id (UUID, référence à Utilisateur)
  - commentaire (text)

- **Relations**:
  - N..1 avec Tiers (employé)
  - N..1 avec Utilisateur (utilisateur_gestion_id)
  - 1..* avec Paiement_Creance

### Paiement_Creance
- **Champs**:
  - id (UUID)
  - creance_employe_id (UUID, référence à Creance_Employe)
  - trésorerie_station_id (UUID, référence à Trésorerie_Station)
  - montant_paye (decimal, obligatoire)
  - date_paiement (datetime, obligatoire)
  - utilisateur_id (UUID, référence à Utilisateur)
  - commentaire (text)

- **Relations**:
  - N..1 avec Creance_Employe
  - N..1 avec Trésorerie_Station
  - N..1 avec Utilisateur

### Historique_Paie
- **Champs**:
  - id (UUID)
  - paie_employe_id (UUID, référence à Paie_Employe)
  - utilisateur_id (UUID, référence à Utilisateur)
  - type_historique (string: "création", "modification", "paiement", "relance", "mise_en_demeure", obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - date_historique (datetime, obligatoire)

- **Relations**:
  - N..1 avec Paie_Employe
  - N..1 avec Utilisateur

### Parametre_Salaire
- **Champs**:
  - id (UUID)
  - employe_id (UUID, référence à Tiers de type employé)
  - taux_cotisations_sociales (decimal)
  - taux_impots (decimal)
  - periodicite_paiement (string: "mensuel", "hebdomadaire", "quotidien", default "mensuel")
  - date_derniere_mise_a_jour (datetime)

- **Relations**:
  - N..1 avec Tiers (employé)

## Relations avec d'autres modules
- **Module Tiers**: Les employés sont des tiers de type employé
- **Module Trésoreries**: Les paiements de salaires affectent les trésoreries
- **Module Mouvements Financiers**: Pour la gestion des créances employés
- **Module Utilisateurs**: Les utilisateurs effectuent les paiements
- **Module États, Bilans et Comptabilité**: Pour les rapports de salaires
- **Module Structure de la Compagnie**: Les employés peuvent être liés à une station spécifique

## Contraintes d'intégrité
- Une paie est liée à un seul employé
- En cas de non-paiement à la date d'échéance, une créance employé est automatiquement créée
- Les paiements de créances sont enregistrés séparément
- Le solde restant d'une créance est mis à jour après chaque paiement
- Les modifications de paramètres de salaire sont historisées