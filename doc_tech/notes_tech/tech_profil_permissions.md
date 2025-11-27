# Technical Specification - Gestion des profils et permissions RBAC (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter un système complet de gestion des profils utilisateurs et des permissions selon le modèle RBAC (Role-Based Access Control) pour le système SuccessFuel. Ce système permettra aux administrateurs de gérer les droits d'accès des utilisateurs de manière fine, avec une distinction claire entre les rôles, les permissions attachées à ces rôles, et les données auxquelles les utilisateurs ont accès.

### Problème à résoudre
Le système SuccessFuel a besoin d'un mécanisme de gestion des autorisations qui permet :
- De créer des profils avec des permissions spécifiques
- D'assigner des utilisateurs à des profils
- De restreindre l'accès des utilisateurs à certaines données (par compagnie)
- De gérer des permissions par module fonctionnel
- De permettre une gestion différenciée selon les types d'utilisateurs
- De permettre aux gérants de compagnie d'avoir un accès complet aux opérations de leur compagnie

### Définition du périmètre
Le périmètre inclut :
- Gestion des structures de base (pays, compagnies, stations)
- Gestion des modules fonctionnels et des permissions
- Gestion des profils et des permissions associées
- Gestion des utilisateurs et de leurs attributions
- Contrôle d'accès basé sur les profils et les compagnies
- Journalisation des actions liées à la gestion des accès
- Distinction des endpoints pour administrateurs et utilisateurs
- Classification des types d'utilisateurs avec contrôles d'accès distincts
- Attribution automatique de toutes les permissions fonctionnelles aux gérants de compagnie

## 2. User Stories & Critères d'acceptation

### US-RBAC-001: En tant qu'administrateur, je veux gérer les pays
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver un pays
  - Chaque pays a un code unique (ISO 3 caractères)
  - Pouvoir configurer les spécifications locales par pays (devise, TVA, système comptable)

### US-RBAC-002: En tant qu'administrateur, je veux gérer les compagnies
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver une compagnie
  - Chaque compagnie a un code unique
  - Pouvoir associer des stations à une compagnie
  - Pouvoir associer une compagnie à un pays

### US-RBAC-003: En tant qu'administrateur, je veux gérer les stations-service
- **Critères d'acceptation :**
  - Pouvoir créer, modifier une station
  - Chaque station est liée à une seule compagnie
  - Pouvoir activer/désactiver une station
  - Pouvoir associer une station à un pays

### US-RBAC-004: En tant qu'administrateur, je veux gérer les modules fonctionnels
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver un module fonctionnel
  - Les modules représentent les grandes fonctionnalités du système (achats, ventes, stocks, trésorerie, etc.)

### US-RBAC-005: En tant qu'administrateur, je veux gérer les permissions fonctionnelles
- **Critères d'acceptation :**
  - Pouvoir créer des permissions de base pour chaque module (lire, créer, modifier, supprimer, annuler)
  - Pouvoir associer des permissions à des modules fonctionnels
  - Pouvoir activer/désactiver des permissions

### US-RBAC-006: En tant qu'administrateur, je veux gérer les profils d'utilisateurs
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des profils
  - Chaque profil a un code unique
  - Pouvoir associer des permissions à un profil
  - Pouvoir associer un profil à une compagnie
  - Pouvoir spécifier un type de profil (administrateur, gérant compagnie, utilisateur compagnie)

### US-RBAC-007: En tant qu'administrateur, je veux associer des permissions à des profils
- **Critères d'acceptation :**
  - Pouvoir attribuer/retirer des permissions à un profil
  - Pouvoir gérer les associations permission-profil en masse
  - Pouvoir visualiser toutes les permissions d'un profil

### US-RBAC-008: En tant que gérant de compagnie, je veux avoir un accès complet aux opérations de ma compagnie
- **Critères d'acceptation :**
  - Avoir automatiquement toutes les permissions fonctionnelles (achats, ventes, stocks, trésorerie, etc.)
  - Accéder uniquement aux données de ma propre compagnie
  - Pouvoir effectuer toutes les opérations dans tous les modules pour ma compagnie
  - Ne pas avoir accès aux données d'autres compagnies

### US-RBAC-009: En tant qu'administrateur, je veux gérer les utilisateurs et leurs attributions
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver un utilisateur
  - Chaque utilisateur a un login unique
  - Pouvoir assigner un utilisateur à un profil
  - Pouvoir limiter les stations auxquelles un utilisateur a accès (via le champ stations_user)
  - Pouvoir assigner un utilisateur à une compagnie
  - Pouvoir spécifier le type d'utilisateur (super_administrateur, administrateur, gérant_compagnie, utilisateur_compagnie)

### US-RBAC-010: En tant qu'administrateur, je veux contrôler l'accès des utilisateurs par type
- **Critères d'acceptation :**
  - Les super administrateurs ont accès à tous les endpoints et données
  - Les administrateurs ont accès aux endpoints administrateur et à leurs données selon permissions
  - Les gérants de compagnie ont accès à tous les endpoints utilisateur et à toutes les opérations de leur compagnie
  - Les utilisateurs de compagnie ont accès limité selon leurs permissions spécifiques

### US-RBAC-011: En tant qu'utilisateur système, je veux que le système vérifie mes permissions automatiquement
- **Critères d'acceptation :**
  - Le système vérifie les permissions à chaque accès à une fonctionnalité
  - Les données sont automatiquement filtrées selon la compagnie de l'utilisateur
  - Les tentatives d'accès non autorisé sont journalisées
  - Les gérants de compagnie ont implicitement accès à toutes les permissions fonctionnelles

### US-RBAC-012: En tant qu'administrateur, je veux que le système distingue les endpoints pour chaque type d'utilisateur
- **Critères d'acceptation :**
  - Endpoint administrateur accessible aux super administrateurs et administrateurs
  - Endpoint utilisateur accessible aux gérants de compagnie et utilisateurs de compagnie
  - Accès automatique bloqué aux endpoints non autorisés pour chaque type d'utilisateur

## 3. Modèles et Relations

### 3.1 Modèles de base
- **pays** : Informations sur les pays où l'ERP est déployé
- **compagnies** : Regroupements d'entités (stations, utilisateurs, etc.)
- **stations** : Les stations-service individuelles appartenant à une compagnie
- **modules** : Les différentes sections fonctionnelles du système (achats, ventes, etc.)
- **permissions** : Les actions spécifiques qui peuvent être effectuées dans chaque module
- **profils** : Ensembles de permissions pouvant être assignés aux utilisateurs
- **profil_permissions** : Relations many-to-many entre profils et permissions
- **utilisateurs** : Les utilisateurs finaux du système avec leurs types et associations

### 3.2 Modèle RBAC étendu
- Le type d'utilisateur est stocké dans le champ `type_utilisateur` de la table `utilisateurs`
- Pour les gérants de compagnie, le système attribue implicitement toutes les permissions fonctionnelles
- Le filtrage des données se fait par le champ `compagnie_id` dans les tables des entités métier
- Le champ `stations_user` continue à fournir un filtrage plus fin au niveau des stations

## 4. Règles de Gestion des Permissions

### 4.1 Gérant de Compagnie
- Bénéficie automatiquement de toutes les permissions fonctionnelles (achats, ventes, stocks, trésorerie, comptabilité, etc.)
- Accès restreint aux données appartenant à sa propre compagnie
- Peut effectuer toutes les opérations dans tous les modules pour sa compagnie
- Ne peut pas accéder aux données d'autres compagnies

### 4.2 Utilisateur de Compagnie
- Permissions spécifiques définies par le gérant de la compagnie via les profils
- Accès limité aux données selon ses permissions et sa compagnie
- Restrictions possibles au niveau des stations via le champ `stations_user`

### 4.3 Administrateur
- Permissions définies par le super administrateur
- Accès limité aux données selon ses droits attribués

### 4.4 Super Administrateur
- Accès complet à toutes les fonctionnalités et données du système

## 5. Contrôles d'Accès et Sécurité

### 5.1 Contrôles de Niveau Fonctionnel
- Vérification des permissions pour chaque action dans le système
- Pour les gérants de compagnie : accès implicite à toutes les permissions fonctionnelles
- Pour les autres types : vérification basée sur les permissions du profil

### 5.2 Contrôles de Niveau Données
- Filtrage automatique des données selon la compagnie de l'utilisateur
- Application du filtre `compagnie_id` dans toutes les requêtes
- Vérification que les objets manipulés appartiennent à la compagnie de l'utilisateur

### 5.3 Contrôles de Niveau Interface
- Séparation des endpoints administrateur et utilisateur
- Accès restreint selon le type d'utilisateur
- Validation de l'endpoint approprié avant chaque opération

## 6. Journalisation et Suivi

### 6.1 Journalisation des Accès
- Toutes les tentatives d'accès sont enregistrées
- Les échecs de vérification de permission sont journalisés
- Les accès réussis aux opérations sensibles sont enregistrés

### 6.2 Journalisation des Modifications
- Les modifications des permissions sont journalisées
- Les changements de type d'utilisateur sont tracés
- Les accès non autorisés sont enregistrés dans les logs de sécurité

## 7. Dépendances et Intégration

### 7.1 Modules Dépendants
- Ce module est requis par tous les autres modules fonctionnels
- Fournit les services de vérification des permissions
- Intégration avec les modules de sécurité pour la journalisation

### 7.2 Intégration avec Autres Fonctionnalités
- Intégration avec le système d'authentification pour l'attribution des jetons
- Intégration avec les modules métier pour le filtrage des données
- Interface avec les services de journalisation pour les événements de sécurité

## 8. Tests et Validation

### 8.1 Tests de Validation des Permissions
- Vérification que les gérants de compagnie ont toutes les permissions fonctionnelles
- Validation du filtrage par compagnie pour tous les types d'utilisateurs
- Tests d'accès non autorisés et vérification de la journalisation

### 8.2 Tests de Sécurité
- Tests d'intrusion tentant d'accéder à des données d'autres compagnies
- Vérification des contrôles d'endpoint
- Tests de la journalisation des accès non autorisés

## 9. Performance et Scalabilité

### 9.1 Optimisation des Requêtes
- Index sur les champs de filtre (compagnie_id, type_utilisateur)
- Jointures optimisées pour la vérification des permissions
- Caching des permissions pour les utilisateurs actifs

### 9.2 Gestion de la Charge
- Gestion efficace des requêtes de vérification de permissions
- Gestion des sessions avec jetons d'authentification
- Scalabilité horizontale pour les services de vérification

## 10. Déploiement et Maintenance

### 10.1 Déploiement
- Intégration dans le processus de déploiement existant
- Migration des données pour s'assurer de la cohérence des permissions
- Formation des administrateurs sur la nouvelle gestion des gérants de compagnie

### 10.2 Maintenance
- Surveillance des accès anormaux
- Mise à jour des permissions en fonction des évolutions métier
- Audit régulier des permissions et des accès