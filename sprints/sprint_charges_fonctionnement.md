# Sprint: Module Charges de Fonctionnement

## Objectif
Implémenter la gestion complète des charges de fonctionnement par station, incluant les catégories de charges, le suivi des dépenses courantes, les échéances, les paiements et l'intégration avec les trésoreries.

## Spécifications détaillées

### 1. Gestion des charges
- Création, modification et suppression de charges de fonctionnement
- Champs: catégorie, fournisseur (optionnel), date, montant, description, date échéance, statut (prévu, échu, payé), méthode de paiement, numéro pièce comptable
- La station est automatiquement déterminée selon l'utilisateur connecté
- Classification par catégorie (électricité, eau, fournitures, maintenance, etc.)
- Historique des charges par catégorie et période
- Gestion des charges récurrentes (mensuelles, trimestrielles, annuelles)

### 2. Catégories de charges
- Création, modification et suppression des catégories de charges
- Champs: nom, description, type (fixe, variable), seuil d'alerte, compte comptable associé
- Validation de l'unicité du nom de catégorie
- Hiérarchie possible des catégories
- Configuration des seuils d'alerte pour les dépassements budgétaires

### 3. Lien avec les fournisseurs
- Association avec les tiers de type fournisseur (via le module Tiers)
- Historique des charges par fournisseur
- Calcul des montants dus pour les charges de fonctionnement uniquement
- Gestion des échéances et rappels spécifiques aux charges de fonctionnement
- Historique des paiements par fournisseur (pour les charges de fonctionnement)

### 4. Gestion des paiements
- Association avec les trésoreries pour les paiements
- Historique des paiements effectués avec dates, montants et modes de paiement
- Rapprochement des charges et des paiements
- Génération automatique des écritures de trésorerie
- Gestion des acomptes et des paiements fractionnés
- Calcul automatique du solde restant dû après chaque paiement
- Suivi des paiements partiels:
  - Statut "en cours de paiement" tant que le solde dû > 0
  - Mise à jour du solde dû après chaque paiement partiel
  - Lien entre chaque paiement et la charge concernée
  - Impact immédiat sur le solde de la trésorerie
- Gestion des statuts de charge:
  - "prévu": charge créée mais pas encore échue
  - "échu": date d'échéance dépassée avec solde dû > 0
  - "en cours de paiement": paiement partiel reçu mais solde dû > 0
  - "payé": solde dû = 0
- Intégration avec le module Mouvements Financiers pour:
  - La mise à jour des soldes des fournisseurs
  - La génération des écritures comptables
  - La gestion des règlements de dettes
- Système d'alertes pour les parties impayées
- Distinction claire avec les achats d'approvisionnement (gérés par les modules Achats)

### 5. Historique des charges
- Suivi des dépenses par période
- Historique des catégories et montants
- Calcul des totaux par catégorie et station
- Analyse comparative entre périodes
- Export des données pour reporting

### 6. Intégration avec les autres modules
- Intégration avec le module Trésoreries pour l'impact sur les soldes
- Intégration avec le module États, Bilans et Comptabilité pour les rapports financiers
- Intégration avec le module Mouvements Financiers pour la gestion des dettes
- Intégration avec le module Tiers pour la gestion des fournisseurs

### 7. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes
- Contrôle des montants et seuils selon les rôles

## Livrables
- API RESTful pour la gestion des charges de fonctionnement
- API RESTful pour la gestion des catégories de charges
- Modèles de données pour les charges, les catégories et les paiements
- Interface d'administration des charges et catégories
- Système de classification et hiérarchie des charges
- Système de gestion des échéances et rappels
- Système de gestion des paiements et rapprochement
- Système d'intégration avec les trésoreries et autres modules
- Système d'alertes pour les dépassements budgétaires
- Tests unitaires et d'intégration