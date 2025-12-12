# Modèle de données - Module Achats Boutique

## Entités principales

### Demande_Achat
- **Champs**:
  - id (UUID)
  - station_id (UUID, référence à Station)
  - utilisateur_demandeur_id (UUID, référence à Utilisateur)
  - date_demande (datetime, obligatoire)
  - date_besoin (date, obligatoire)
  - urgence (boolean, default false)
  - statut (string: "en_attente", "approuvée", "rejetée", default "en_attente")
  - indicateur_traitee (boolean, default false)
  - description (text)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Station
  - N..1 avec Utilisateur (utilisateur_demandeur_id)
  - 1..* avec Ligne_Demande_Achat

### Ligne_Demande_Achat
- **Champs**:
  - id (UUID)
  - demande_achat_id (UUID, référence à Demande_Achat)
  - produit_id (UUID, référence à Produit)
  - quantite_demandee (decimal, obligatoire)
  - unite (string, default provenant du produit)

- **Relations**:
  - N..1 avec Demande_Achat
  - N..1 avec Produit

### Commande_Achat
- **Champs**:
  - id (UUID)
  - demande_achat_id (UUID, référence à Demande_Demande_Achat, optionnel)
  - tiers_id (UUID, référence à Tiers de type fournisseur)
  - station_id (UUID, référence à Station)
  - date_commande (datetime, obligatoire)
  - date_livraison_prevue (date, obligatoire)
  - statut (string: "brouillon", "confirmée", "en_cours", "reçue", "terminée", "annulée", default "brouillon")
  - type_paiement (string: "prépayé", "COD", "différé", "consignation", "mixte", "partiel", obligatoire)
  - delai_paiement (integer, jours)
  - pourcentage_acompte (decimal)
  - limite_credit (decimal)
  - mode_reglement (string)
  - documents_requis (jsonb)
  - config_produit (jsonb)
  - regles_stock (jsonb)
  - frequence_appro (string)
  - limites_budget_stock (jsonb)
  - niveaux_validation (jsonb)
  - utilisateur_id (UUID, référence à Utilisateur)
  - numero_piece_comptable (string)
  - date_creation (datetime)
  - date_modification (datetime)

- **Relations**:
  - N..1 avec Demande_Achat (optionnel)
  - N..1 avec Tiers (fournisseur)
  - N..1 avec Station
  - N..1 avec Utilisateur
  - 1..* avec Ligne_Commande_Achat
  - 1..* avec Mouvement_Tresorerie (via module Mouvements Financiers)

### Ligne_Commande_Achat
- **Champs**:
  - id (UUID)
  - commande_achat_id (UUID, référence à Commande_Achat)
  - produit_id (UUID, référence à Produit)
  - quantite_demandee (decimal, obligatoire)
  - quantite_recue (decimal, default 0)
  - quantite_facturee (decimal, default 0)
  - prix_unitaire_demande (decimal, obligatoire)
  - prix_unitaire_facture (decimal, optionnel)
  - montant (decimal, calculé)
  - ecart_prix (decimal, calculé)

- **Relations**:
  - N..1 avec Commande_Achat
  - N..1 avec Produit

### Historique_Prix_Achat
- **Champs**:
  - id (UUID)
  - produit_id (UUID, référence à Produit)
  - tiers_id (UUID, référence à Tiers)
  - prix_unitaire (decimal, obligatoire)
  - date_enregistrement (datetime, obligatoire)

- **Relations**:
  - N..1 avec Produit
  - N..1 avec Tiers

## Relations avec d'autres modules
- **Module Tiers**: Les commandes sont passées auprès de fournisseurs (tiers de type fournisseur)
- **Module Produits et Stocks**: Les achats concernent des produits de type boutique, gaz, lubrifiant
- **Module Mouvements Financiers**: Les paiements sont gérés via ce module
- **Module Trésoreries**: Les règlements affectent les trésoreries
- **Module États, Bilans et Comptabilité**: Pour les rapports d'achats
- **Module Structure de la Compagnie**: Les achats sont liés à une station spécifique

## Contraintes d'intégrité
- Une commande peut être créée à partir d'une demande approuvée ou directement
- Les quantités commandées, reçues et facturées sont suivies séparément
- Le prix unitaire facturé peut différer du prix unitaire demandé
- Les commandes affectent les stocks une fois reçues
- Les paiements sont gérés selon les conditions définies dans la commande

## Vues de reporting

### vue_achats_boutique
- **Description**: Vue pour les achats boutique avec détails
- **Jointures**:
  - commande_achat JOIN tiers ON (commande_achat.tiers_id = tiers.id)
  - commande_achat JOIN station ON (commande_achat.station_id = station.id)
  - commande_achat JOIN utilisateur ON (commande_achat.utilisateur_id = utilisateur.id)
- **Champs**:
  - ca.id
  - ca.tiers_id
  - t.nom AS tiers_nom
  - ca.date_commande
  - ca.date_livraison_prevue
  - ca.statut
  - ca.station_id
  - s.nom AS station_nom
  - ca.utilisateur_id
  - u.nom AS utilisateur_nom
  - u.prenom AS utilisateur_prenom
- **Note**: Cette vue n'inclut pas le montant_total car la table commande_achat ne possède pas ce champ.