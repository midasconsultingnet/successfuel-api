# Cahier des Charges - SuccessFuel ERP (Mis à Jour)

## Présentation du projet

**SuccessFuel** est un ERP (Enterprise Resource Planning) spécialement conçu pour la gestion complète des stations-service. Ce système informatisé permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

Notre solution s'adresse aux gestionnaires de stations-service qui souhaitent moderniser leur gestion, réduire les erreurs humaines, améliorer leur traçabilité et optimiser leurs performances.

---

## Modules du système

### 1. Gestion des Structures
Ce module permet de gérer tous les éléments physiques de votre station-service :

#### 1.1. Stations-service
- Création / édition des stations
- Saisie des adresses, responsables et contacts
- Gestion des stations par compagnie
- Accès restreint aux données selon la compagnie de l'utilisateur

#### 1.2. Gestion du personnel
- Gestion des employés et de leurs affectations
- Attribution des droits selon le profil de l'utilisateur

### 2. Gestion des stocks
- Suivi des stocks de carburant et de produits boutique
- Gestion des entrées et sorties de stock
- Contrôle des écarts et des mouvements
- Accès restreint aux données selon la compagnie de l'utilisateur

### 3. Gestion des achats
- Création et suivi des achats de carburant et de produits
- Gestion des fournisseurs
- Validation des livraisons avec mesures avant/après
- Calcul des écarts de livraison
- Accès restreint aux données selon la compagnie de l'utilisateur

### 4. Gestion des ventes
- Enregistrement des ventes de carburant (avec index de pistolets)
- Enregistrement des ventes de produits boutique
- Gestion des services annexes
- Suivi des performances des employés
- Accès restreint aux données selon la compagnie de l'utilisateur

### 5. Gestion de la trésorerie
- Suivi des encaissements et décaissements
- Gestion des diverses caisses et comptes
- Contrôle des écarts de caisse
- Accès restreint aux données selon la compagnie de l'utilisateur

### 6. Gestion comptable
- Plan comptable complet
- Écritures comptables automatiques
- États financiers (bilan, compte de résultat, grand livre, balance, journal)
- Accès restreint aux données selon la compagnie de l'utilisateur

### 7. Gestion des rapports
- États financiers et de gestion
- KPIs opérationnels
- Analyses de performance
- Accès restreint aux données selon la compagnie de l'utilisateur

---

## Types d'utilisateurs et permissions

Le système distingue 4 types d'utilisateurs avec des droits d'accès spécifiques :

### 1. Super Administrateur
- Accès complet à toutes les fonctionnalités du système
- Gestion globale du système
- Création et gestion des autres administrateurs
- Gestion des gérants de compagnie
- Surveillance complète des opérations
- Endpoint : administrateur

### 2. Administrateur
- Accès selon les permissions définies par le super administrateur
- Gestion des aspects opérationnels selon ses permissions
- Supervision des stations selon ses droits
- Endpoint : administrateur

### 3. Gérant de Compagnie
- Accès à toutes les opérations de sa propre compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
- Supervision de toutes les stations de sa compagnie
- Gestion des utilisateurs de sa compagnie
- Accès limité aux données de sa propre compagnie
- Endpoint : utilisateur

### 4. Utilisateur de Compagnie
- Accès limité selon ses permissions spécifiques
- Opérations quotidiennes selon ses droits
- Responsabilité limitée à ses tâches assignées
- Endpoint : utilisateur

---

## Contrôles d'accès

### Séparation des endpoints
- Endpoint administrateur : Réservé aux super administrateurs et administrateurs
- Endpoint utilisateur : Réservé aux gérants compagnie et utilisateurs compagnie
- Blocage automatique : Les utilisateurs ne peuvent pas accéder à l'endpoint qui ne leur est pas destiné

### Contrôles de sécurité
- Validation hiérarchique selon le montant ou le type d'opération
- Journalisation des tentatives d'accès non autorisés
- Contrôle d'accès basé sur les rôles (RBAC)
- Gestion fine des stations auxquelles chaque utilisateur a accès
- Filtrage automatique des données selon la compagnie de l'utilisateur