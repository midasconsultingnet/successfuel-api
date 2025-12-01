# Résumé des Types d'Utilisateurs dans le Système SuccessFuel (Mis à Jour)

## Types d'Utilisateurs

Le système SuccessFuel distingue **4 types d'utilisateurs**, chacun avec des rôles et responsabilités spécifiques :

### 1. Super Administrateur
- **Rôle principal** : Gestion globale du système et gestion des administrateurs et gérants de compagnie
- **Responsabilités** :
  - Gestion globale du système
  - Création et gestion des administrateurs
  - Gestion des gérants de compagnie
  - Gestion des pays
  - Gestion des compagnies
  - Gestion des modules
  - Gestion des types tiers
  - Gestion des configurations_pays et specifications_locales
  - Gestion du plan comptable
  - Configuration des paramètres système
  - Surveillance globale du système
- **Accès** : Endpoint administrateur
- **Permissions** : Accès à toutes les fonctionnalités de gestion globale mais PAS aux opérations propres à chaque compagnie (structures, bilan initial, achats, ventes, stocks, trésorerie, etc.)

### 2. Administrateur
- **Rôle principal** : Gestion selon les permissions définies par le super administrateur
- **Responsabilités** :
  - Gestion des aspects opérationnels selon ses permissions
  - Supervision des stations selon ses droits
  - Gestion des utilisateurs en fonction de ses autorisations
- **Accès** : Endpoint administrateur
- **Permissions** : Définies par le super administrateur, limitées à certains modules/sections

### 3. Gérant Compagnie
- **Rôle principal** : Accès à toutes les opérations de sa compagnie
- **Responsabilités** :
  - Gestion complète des opérations de sa compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
  - Supervision de toutes les stations de sa compagnie
  - Gestion des utilisateurs de sa compagnie
  - Accès à tous les modules fonctionnels pour sa compagnie
- **Accès** : Endpoint utilisateur
- **Permissions** : Accès à toutes les fonctionnalités mais limité aux données de sa propre compagnie

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
- Gestion fine des données auxquelles chaque utilisateur a accès (limité par compagnie)
- Le gérant compagnie bénéficie de toutes les permissions fonctionnelles mais ne peut accéder qu'aux données de sa propre compagnie