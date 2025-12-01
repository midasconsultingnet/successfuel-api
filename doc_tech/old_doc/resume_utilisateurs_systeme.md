# Résumé des Types d'Utilisateurs dans le Système SuccessFuel

## Types d'Utilisateurs

Le système SuccessFuel distingue **4 types d'utilisateurs**, chacun avec des rôles et responsabilités spécifiques :

### 1. Super Administrateur
- **Rôle principal** : Accès complet à toutes les fonctionnalités du système
- **Responsabilités** :
  - Gestion globale du système
  - Création et gestion des autres administrateurs
  - Gestion des gérants de compagnie
  - Surveillance complète des opérations
  - Configuration des paramètres système
- **Accès** : Endpoint administrateur
- **Permissions** : Accès à toutes les fonctionnalités sans restriction

### 2. Administrateur
- **Rôle principal** : Gestion selon les permissions définies par le super administrateur
- **Responsabilités** :
  - Gestion des aspects opérationnels selon ses permissions
  - Supervision des stations selon ses droits
  - Gestion des utilisateurs en fonction de ses autorisations
- **Accès** : Endpoint administrateur
- **Permissions** : Définies par le super administrateur, limitées à certains modules/sections

### 3. Gérant Compagnie
- **Rôle principal** : Gestion des utilisateurs de sa compagnie et définition de leurs permissions
- **Responsabilités** :
  - Gestion des utilisateurs de sa compagnie
  - Définition des permissions des utilisateurs de sa compagnie
  - Supervision des opérations de sa compagnie
  - Gestion des stations de sa compagnie
- **Accès** : Endpoint utilisateur
- **Permissions** : Limitées à sa compagnie respective, avec droits de gestion des utilisateurs

### 4. Utilisateur Compagnie
- **Rôle principal** : Accès limité selon ses permissions spécifiques
- **Responsabilités** :
  - Opérations quotidiennes selon ses droits
  - Saisie et traitement des données selon ses permissions
  - Responsabilité limitée à ses tâches assignées
- **Accès** : Endpoint utilisateur
- **Permissions** : Définies par le gérant de sa compagnie, limitées à certaines fonctionnalités

## Contrôles d'Accès

### Séparation des Endpoints
- **Endpoint administrateur** : Réservé aux super administrateurs et administrateurs
- **Endpoint utilisateur** : Réservé aux gérants compagnie et utilisateurs compagnie
- **Blocage automatique** : Les utilisateurs ne peuvent pas accéder à l'endpoint qui ne leur est pas destiné

### Contrôles de Sécurité
- Validation hiérarchique selon le montant ou le type d'opération
- Journalisation des tentatives d'accès non autorisés
- Contrôle d'accès basé sur les rôles (RBAC)
- Gestion fine des stations auxquelles chaque utilisateur a accès