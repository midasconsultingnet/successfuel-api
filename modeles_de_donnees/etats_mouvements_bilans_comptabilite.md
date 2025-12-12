# Modèle de données - Module États, Bilans et Comptabilité

## Entités principales

### Etat_Financier
- **Champs**:
  - id (UUID)
  - type_etat (string: "tresorerie", "tiers", "stocks", "bilan_operations", "journal_operations", "journal_comptable", "bilan_initial", "etat_resultat", obligatoire)
  - nom_etat (string, obligatoire)
  - periode_debut (date, obligatoire)
  - periode_fin (date, obligatoire)
  - station_id (UUID, référence à Station, optionnel - NULL pour consolidé)
  - utilisateur_generation_id (UUID, référence à Utilisateur)
  - date_generation (datetime, obligatoire)
  - parametres_filtrage (jsonb)
  - statut (string: "en_cours", "genere", "valide", default "en_cours")
  - fichier_export (string, optionnel)

- **Relations**:
  - N..1 avec Station (optionnel)
  - N..1 avec Utilisateur (utilisateur_generation_id)

### Bilan_Initial_Depart
- **Champs**:
  - id (UUID)
  - compagnie_id (UUID, référence à Compagnie)
  - station_id (UUID, référence à Station, optionnel)
  - date_bilan (date, obligatoire)
  - actif_immobilise (decimal, obligatoire)
  - actif_circulant (decimal, obligatoire)
  - total_actif (decimal, calculé)
  - capitaux_propres (decimal, obligatoire)
  - dettes (decimal, obligatoire)
  - provisions (decimal, obligatoire)
  - total_passif (decimal, calculé)
  - utilisateur_generation_id (UUID, référence à Utilisateur)
  - date_generation (datetime, obligatoire)
  - est_valide (boolean, default false)

- **Relations**:
  - N..1 avec Compagnie
  - N..1 avec Station (optionnel)
  - N..1 avec Utilisateur (utilisateur_generation_id)

### Journal_Operations
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station, optionnel - NULL pour consolidé)
  - periode_debut (date, obligatoire)
  - periode_fin (date, obligatoire)
  - nombre_operations (integer, calculé)
  - total_debit (decimal, calculé)
  - total_credit (decimal, calculé)
  - utilisateur_generation_id (UUID, référence à Utilisateur)
  - date_generation (datetime, obligatoire)

- **Relations**:
  - N..1 avec Station (optionnel)
  - N..1 avec Utilisateur (utilisateur_generation_id)

### Operation_Journal
- **Champs**:
  - id (UUID)
  - journal_operations_id (UUID, référence à Journal_Operations)
  - date_operation (date, obligatoire)
  - libelle_operation (text, obligatoire)
  - compte_debit (string, obligatoire)
  - compte_credit (string, obligatoire)
  - montant (decimal, obligatoire)
  - devise (string, default "XOF")
  - reference_operation (string, obligatoire)
  - module_origine (string, obligatoire)
  - utilisateur_enregistrement_id (UUID, référence à Utilisateur)

- **Relations**:
  - N..1 avec Journal_Operations
  - N..1 avec Utilisateur (utilisateur_enregistrement_id)

### Bilan_Operations
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station, optionnel - NULL pour consolidé global)
  - date_bilan (date, obligatoire)
  - situation_tresoreries (decimal, calculé)
  - immobilisations (decimal, calculé)
  - stocks_carburant (decimal, calculé)
  - stocks_boutique (decimal, calculé)
  - creances (decimal, calculé)
  - dettes (decimal, calculé)
  - resultat_operations (decimal, calculé)
  - utilisateur_generation_id (UUID, référence à Utilisateur)
  - date_generation (datetime, obligatoire)

- **Relations**:
  - N..1 avec Station (optionnel)
  - N..1 avec Utilisateur (utilisateur_generation_id)

### Export_Etat
- **Champs**:
  - id (UUID)
  - etat_financier_id (UUID, référence à Etat_Financier)
  - type_export (string: "CSV", "Excel", "PDF", "XML", obligatoire)
  - utilisateur_export_id (UUID, référence à Utilisateur)
  - date_export (datetime, obligatoire)
  - chemin_fichier (string, obligatoire)
  - nom_fichier (string, obligatoire)

- **Relations**:
  - N..1 avec Etat_Financier
  - N..1 avec Utilisateur (utilisateur_export_id)

## Relations avec d'autres modules
- **Tous les modules opérationnels**: Les données proviennent de modules comme Ventes, Achats, Salaires, Charges, etc.
- **Module Structure de la Compagnie**: Pour les rapports consolidés par station ou compagnie
- **Module Tiers**: Pour les états de tiers
- **Module Trésoreries**: Pour les états de trésoreries
- **Module Produits et Stocks**: Pour les états de stocks
- **Module Immobilisations**: Pour les états d'immobilisations
- **Module Mouvements Financiers**: Pour les soldes de tiers

## Contraintes d'intégrité
- Les bilans doivent être équilibrés (Actif = Passif + Capitaux Propres)
- Les données proviennent des modules opérationnels à travers des interfaces définies
- Les états peuvent être générés à différents niveaux (station, compagnie, consolidé global)
- Les exports sont liés aux états financiers générés
- L'historique des générations d'états est conservé