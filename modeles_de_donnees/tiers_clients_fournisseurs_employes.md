# Modèle de données - Module Tiers (Clients, Fournisseurs, Employés)

## Entités principales

### Tiers
- **Champs**:
  - id (UUID)
  - type (string: "client", "fournisseur", "employé", obligatoire)
  - nom (string, obligatoire)
  - adresse (string)
  - telephone (string)
  - email (string)
  - identifiant_fiscal (string)
  - date_creation (datetime)
  - date_modification (datetime)
  - compagnie_id (UUID, référence à Compagnie)

- **Relations**:
  - N..1 avec Compagnie
  - 1..* avec Mouvement_Tiers
  - 1..* avec Solde_Tiers
  - 1..* avec Journal_Modification_Tiers

### Solde_Tiers
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - montant_initial (decimal, obligatoire)
  - montant_actuel (decimal, calculé)
  - devise (string, default "XOF")
  - date_creation (datetime)

- **Relations**:
  - N..1 avec Tiers

### Mouvement_Tiers
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - type_mouvement (string: "débit", "crédit", obligatoire)
  - montant (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - description (text)
  - module_origine (string, obligatoire)
  - reference_origine (string, obligatoire)
  - utilisateur_id (UUID, référence à Utilisateur)
  - numero_piece_comptable (string)
  - statut (string: "validé", "annulé", default "validé")

- **Relations**:
  - N..1 avec Tiers
  - N..1 avec Utilisateur

### Client
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - type_client (string: "particulier", "professionnel", etc.)
  - seuil_credit (decimal, default 0)
  - conditions_paiement (string)
  - categorie_client (string)
  - date_creation (datetime)

- **Relations**:
  - 1..1 avec Tiers (via tiers_id)

### Fournisseur
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - conditions_livraison (string)
  - delai_paiement (integer, jours)
  - mode_reglement_par_defaut (string)
  - date_creation (datetime)

- **Relations**:
  - 1..1 avec Tiers (via tiers_id)

### Employé
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - poste (string)
  - date_embauche (date)
  - statut (string: "actif", "inactif", etc.)
  - station_id (UUID, référence à Station, optionnel)
  - date_creation (datetime)

- **Relations**:
  - 1..1 avec Tiers (via tiers_id)
  - N..1 avec Station (optionnel)

### Journal_Modification_Tiers
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - utilisateur_id (UUID, référence à Utilisateur)
  - date_modification (datetime, obligatoire)
  - type_modification (string, obligatoire)
  - donnees_avant (jsonb)
  - donnees_apres (jsonb)
  - champs_modifies (jsonb: [string])

- **Relations**:
  - N..1 avec Tiers
  - N..1 avec Utilisateur

## Relations avec d'autres modules
- **Module Compagnie**: Les tiers sont liés à une compagnie spécifique
- **Module Mouvements Financiers**: Les mouvements de tiers sont gérés dans ce module
- **Module Ventes Boutique et Carburant**: Les clients effectuent des achats
- **Module Achats Boutique et Carburant**: Les fournisseurs effectuent des ventes
- **Module Salaires**: Les employés reçoivent des paiements
- **Module Charges de Fonctionnement**: Les fournisseurs facturent des charges

## Contraintes d'intégrité
- Un tiers appartient à une seule compagnie
- Le solde d'un tiers est calculé à partir de tous les mouvements associés
- L'historique des modifications est conservé pour chaque tiers
- Les employés peuvent être liés à une station spécifique, mais ce n'est pas obligatoire