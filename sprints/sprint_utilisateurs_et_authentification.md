# Sprint: Module Utilisateurs et Authentification

## Objectif
Implémenter un système complet de gestion des utilisateurs internes avec authentification, rôles et permissions basés sur les stations.

## Spécifications détaillées

### 1. Gestion des utilisateurs
- Création, modification et suppression d'utilisateurs internes
- Champs obligatoires: nom, prénom, email, login, mot de passe, rôle
- Validation de l'email, du login et du mot de passe (complexité)
- Mot de passe chiffré (bcrypt)

### 1.1 Suggestions d'amélioration pour la gestion des utilisateurs
- Implémenter la récupération de mot de passe via email
- Prévoir un champ de date de dernière connexion pour le suivi de l'activité
- Ajouter une fonctionnalité de désactivation temporaire d'un compte utilisateur
- Gestion des sessions multiples pour un même utilisateur
- Tableau de bord utilisateur pour visualiser ses informations personnelles et paramètres
- Notifications lors des modifications des informations de compte
- Mécanisme de consentement pour les conditions d'utilisation ou la politique de confidentialité

### 2. Système d'authentification
- Login/logout avec login et mot de passe
- Clarification: Le login se fait avec le login (identifiant unique) et le mot de passe associé
- Génération de token JWT avec expiration
- Gestion du refresh token pour le renouvellement automatique de la session
- Récupération de mot de passe (email de réinitialisation)
- Sécurité brute force (limitation des tentatives)
- Changement de mot de passe par l'utilisateur connecté

### 3. Gestion des rôles et permissions (RBAC)
- Rôles prédéfinis: Gérant compagnie, Utilisateur compagnie
- Attribution des permissions selon le rôle
- Permissions granulaires (lecture, écriture, suppression) selon les stations
- Restriction: Les rôles "gerant_compagnie" et "utilisateur_compagnie" n'ont pas la permission de créer une nouvelle compagnie

### 3.1 Suggestions d'amélioration pour les rôles et permissions
- Définir un rôle "Administrateur système" avec accès global
- Prévoir un système de permissions personnalisées pour des cas spécifiques
- Créer un mécanisme d'héritage des rôles pour simplifier la gestion
- Les utilisateurs de compagnie ne peuvent pas gérer (créer/modifier/supprimer) les types de carburant

### 4. Affectation d'utilisateurs aux stations
- Possibilité d'affecter un utilisateur à une ou plusieurs stations
- Gestion des accès selon les stations attribuées
- Validation que l'utilisateur n'a accès qu'aux données autorisées

### 4.1 Relation entre utilisateurs et compagnie
- Une compagnie peut avoir un ou plusieurs utilisateurs (gerant_compagnie ou utilisateur_compagnie)
- Chaque utilisateur est lié à une seule compagnie
- Les utilisateurs d'une compagnie n'ont accès qu'aux données de leur propre compagnie
- Interdiction stricte pour un utilisateur d'une compagnie d'accéder aux données d'une autre compagnie

### 5. Sécurité
- Validation des tokens JWT à chaque requête
- Autorisation basée sur les rôles et les stations
- Audit des connexions et déconnexions

### 5.1 Suggestions d'amélioration pour la sécurité
- Mettre en place une deuxième forme d'authentification (2FA) pour les comptes administrateurs
- Implémenter un mécanisme de verrouillage de compte après plusieurs échecs de connexion
- Ajouter un système de journalisation détaillé pour les événements de sécurité

### 6. Historique des actions par utilisateur
- Journalisation de toutes les actions effectuées par les utilisateurs
- Chaque action enregistrée contient: utilisateur, date/heure, type d'action, module concerné, données avant et après modification
- Types d'actions enregistrées: création, modification, suppression, consultation (selon les permissions)
- Système de journalisation (logging) centralisé pour toutes les interactions avec le système
- Accès restreint à l'historique des actions selon les rôles (gerant_compagnie, utilisateur_compagnie)
- Conservation des historiques pendant une période définie (paramétrable)
- Possibilité d'export des historiques pour audit
- Distinction entre les actions de consultation, modification, suppression et création

### 5.2 Gestion centralisée des carburants
- Les carburants sont prédéfinis dans une table "carburants" avec des UUID uniques
- Cette table est gérée au niveau système/administrateur
- Les prix et affectations aux cuves se font par référence aux UUID des carburants
- Cette approche évite la redondance des données de carburant dans chaque compagnie
- Les utilisateurs de compagnie n'ont pas le droit de modifier les types de carburant

## Livrables
- API RESTful pour la gestion des utilisateurs
- API d'authentification (login, logout, token refresh)
- Interface d'administration des utilisateurs
- Système d'autorisation pour les endpoints
- Tests unitaires et d'intégration