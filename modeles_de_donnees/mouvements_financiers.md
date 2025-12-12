# Modèle de données - Module Mouvements Financiers

## Entités principales

### Mouvement_Financier
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - type_mouvement (string: "reglement_dette", "recouvrement_creance", "avoir", "penalite", "divers", obligatoire)
  - montant (decimal, obligatoire)
  - date_mouvement (datetime, obligatoire)
  - date_echeance (date, optionnel)
  - methode_paiement (string)
  - statut (string: "en_attente", "payé", "partiellement_payé", "annulé", "en_retard", default "en_attente")
  - utilisateur_id (UUID, référence à Utilisateur)
  - numero_piece_comptable (string)
  - penalites (decimal, default 0)
  - motif (text, optionnel)
  - reference_origine (string, optionnel)
  - module_origine (string, optionnel)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Tiers
  - N..1 avec Utilisateur
  - 1..* avec Avoir (si type_mouvement = "avoir")
  - 1..* avec Mouvement_Tresorerie (via règlements/recouvrements)

### Avoir
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - montant_initial (decimal, obligatoire)
  - montant_utilise (decimal, default 0)
  - montant_restant (decimal, calculé)
  - date_emission (datetime, obligatoire)
  - date_utilisation (datetime, optionnel)
  - date_expiration (datetime, optionnel)
  - motif (text, obligatoire)
  - statut (string: "émis", "utilisé", "partiellement_utilisé", "expiré", default "émis")
  - utilisateur_emission_id (UUID, référence à Utilisateur)
  - utilisateur_utilisation_id (UUID, référence à Utilisateur, optionnel)
  - reference_origine (string, obligatoire)
  - module_origine (string: "ventes", "achats", "compensations", obligatoire)

- **Relations**:
  - N..1 avec Tiers
  - N..1 avec Utilisateur (utilisateur_emission_id)
  - N..1 avec Utilisateur (utilisateur_utilisation_id, optionnel)

### Solde_Tiers
- **Champs**:
  - id (UUID)
  - tiers_id (UUID, référence à Tiers)
  - montant_initial (decimal, obligatoire)
  - montant_actuel (decimal, calculé)
  - devise (string, default "XOF")
  - date_derniere_mise_a_jour (datetime)

- **Relations**:
  - N..1 avec Tiers


## Relations avec d'autres modules
- **Module Tiers**: Gestion des soldes pour tous les types de tiers (clients, fournisseurs, employés)
- **Module Trésoreries**: Les règlements affectent les trésoreries
- **Module Ventes Boutique et Carburant**: Pour la gestion des avoirs en cas d'annulation
- **Module Achats Boutique et Carburant**: Pour la gestion des avoirs de compensation
- **Module Salaires**: Pour la gestion des créances employés
- **Module États, Bilans et Comptabilité**: Pour les rapports financiers
- **Module Utilisateurs**: Les utilisateurs effectuent les mouvements financiers

## Contraintes d'intégrité
- Les mouvements financiers affectent les soldes des tiers
- Les avoirs peuvent être émis par différents modules et utilisés dans d'autres transactions
- Les pénalités sont calculées automatiquement selon les règles définies
- Les soldes sont mis à jour automatiquement après chaque mouvement
- L'historique des modifications de soldes est conservé pour chaque tiers

## Vues de reporting

### vue_mouvements_financiers
- **Description**: Vue pour les mouvements financiers
- **Jointures**:
  - mouvement_financier JOIN tiers ON (mouvement_financier.tiers_id = tiers.id)
  - mouvement_financier JOIN utilisateur ON (mouvement_financier.utilisateur_id = utilisateur.id)
- **Champs**:
  - mf.id
  - mf.tiers_id
  - t.nom AS tiers_nom
  - t.type AS tiers_type
  - mf.type_mouvement
  - mf.montant
  - mf.date_mouvement
  - mf.date_echeance
  - mf.methode_paiement
  - mf.statut
  - mf.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
  - mf.numero_piece_comptable
  - mf.penalites
  - mf.motif