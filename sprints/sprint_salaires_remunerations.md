# Sprint: Module Salaires et Rémunérations

## Objectif
Implémenter la gestion complète des salaires, paiements, primes, avances et retenues par station, incluant le suivi des employés, les dates d'échéance, les dettes impayées et l'intégration avec les trésoreries.

## Spécifications détaillées

### 1. Gestion des salaires
- Création, modification et suppression de paies
- Champs: employé, période, date d'échéance, date de paiement, salaire de base, montant total, statut (prévu, échu, payé, dû), méthode de paiement
- Calcul automatique des cotisations sociales et impôts (optionnel - dépend du paramétrage local)
- Historique des paies par employé
- Génération automatique de créances en cas de non-paiement à la date d'échéance
- Calcul automatique du montant dû après la date d'échéance
- Gestion des pénalités ou intérêts éventuels pour les retards de paiement

### 2. Gestion des primes et avances
- Enregistrement des primes ponctuelles ou récurrentes
- Enregistrement des avances sur salaire
- Suivi des retenues (emprunts, sanctions, etc.)
- Association avec les employés
- Calcul automatique du remboursement des avances sur plusieurs mois si applicable

### 3. Gestion des dettes d'employés
- Génération automatique d'une dette envers l'employé si le salaire n'est pas payé à la date d'échéance
- Suivi des montants dus aux employés
- Calcul des intérêts de retard si applicable
- Historique des dettes et des règlements partiels
- Intégration avec le module Mouvements Financiers pour:
  - La gestion des créances employés
  - La mise à jour des soldes nets des employés
  - La génération des écritures comptables
  - Le reporting des dettes envers les employés

### 4. Lien avec les employés
- Association avec les tiers de type employé (via le module Tiers)
- Historique des paiements par employé
- Historique des dettes accumulées par employé
- Calcul des soldes nets (à payer ou dus) par employé via le module Tiers
- Distinction claire avec la gestion des fournisseurs et clients (autres types de tiers)

### 5. Historique des paiements
- Suivi des montants versés par période
- Historique des primes, avances et retenues
- Données de paie détaillées
- Historique des paiements en retard et des règlements effectués après la date d'échéance

### 6. Intégration avec les autres modules
- Intégration avec le module Mouvements Financiers pour la gestion des dettes employés
- Intégration avec le module Trésoreries pour l'impact sur les soldes
- Intégration avec le module Tiers pour la gestion des employés
- Intégration avec le module États, Bilans et Comptabilité pour les rapports financiers

### 7. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes
- Contrôle des montants et seuils selon les rôles

## Livrables
- API RESTful pour la gestion des salaires et rémunérations
- API RESTful pour la gestion des dettes employés
- Modèles de données pour les paies, les paiements et les dettes
- Interface d'administration des salaires et rémunérations
- Système de calcul automatique des charges sociales (optionnel - dépend du paramétrage local)
- Système de gestion des dates d'échéance et des retards
- Système de génération automatique des dettes employés
- Système de suivi des primes, avances et retenues
- Système d'intégration avec les modules Mouvements Financiers, Trésoreries et Tiers
- Système d'alertes pour les dates d'échéance et les retards de paiement
- Tests unitaires et d'intégration