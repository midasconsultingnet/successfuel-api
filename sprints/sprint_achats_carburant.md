# Sprint: Module Achats Carburant

## Objectif
Implémenter la gestion des achats de carburant auprès des fournisseurs, incluant le suivi des quantités, prix, BL et factures, avec intégration au stock carburant.

## Spécifications détaillées

### 1. Gestion des achats
- Création, modification et suppression d'achats de carburant
- Champs: fournisseur, date, numéro BL, numéro facture, montant total
- Détails des achats: carburant, quantité, prix unitaire, montant
- Statut de l'achat (brouillon, validé, facturé)

### 2. Lien avec les fournisseurs
- Association avec les tiers de type fournisseur
- Historique des achats par fournisseur
- Calcul des montants dus

### 3. Suivi des quantités et prix
- Quantité totale et prix unitaire d'achat par carburant
- Calcul automatique des montants
- Historique des prix d'achat par carburant et fournisseur
- Ces informations sont synchronisées avec le module Produits et Stocks pour le calcul des coûts moyens

### 4. Intégration avec les documents
- Numéro de bon de livraison (BL)
- Numéro de facture
- Date de facturation
- Lien avec les documents originaux (futur support de pièces jointes)

### 5. Intégration au stock carburant
- Mise à jour automatique des stocks via l'API du module Structure de la Compagnie après validation
- Association avec les cuves appropriées via l'API du module Structure de la Compagnie
- Le stock théorique d'une cuve est calculé à partir de l'état initial défini dans la table etat_initial_cuve plus les mouvements ultérieurs
- Impact sur le coût moyen du produit

### 6. Gestion des compensations financières
- Création automatique d'avoirs/notes de crédit suite aux écarts entre quantité théorique et réelle
- Si quantité réelle < quantité théorique → avoir reçu du fournisseur
- Si quantité réelle > quantité théorique → avoir dû au fournisseur
- Mise à jour automatique du solde du fournisseur via le module Mouvements Financiers
- Historique des compensations dans une table dédiée
- Traçabilité des ajustements financiers liés aux écarts de livraison

### 7. Gestion des annulations et modifications
- Création d'opérations inverses pour annuler ou modifier un achat
- Validation des droits avant annulation (rôles autorisés)
- Vérification de la disponibilité des cuves pour les ajustements de stock
- Vérification de la disponibilité de trésorerie pour les remboursements
- Gestion des annulations partielles et totales
- Génération automatique des écritures de compensation pour :
  - Restauration des quantités en stock
  - Remboursement ou ajustement de trésorerie
  - Mise à jour des soldes fournisseurs
  - Gestion des avoirs/notes de crédit existants
- Génération de factures de crédit si l'achat était facturé
- Historique complet des modifications et annulations
- Journalisation des motifs d'annulation
- Application des changements dans une transaction atomique
- Vérification des dépendances avant annulation

### 8. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes

## Livrables
- API RESTful pour la gestion des achats carburant
- Modèles de données pour les achats, les avoirs, les annulations et leurs détails
- Interface d'administration des achats carburant
- Système d'intégration avec le stock carburant
- Système de gestion des compensations financières
- Système de gestion des annulations et modifications
- Calcul automatique des impacts sur le stock
- Tests unitaires et d'intégration
- Interface d'administration des achats carburant
- Système d'intégration avec le stock carburant
- Système de gestion des compensations financières
- Calcul automatique des impacts sur le stock
- Tests unitaires et d'intégration