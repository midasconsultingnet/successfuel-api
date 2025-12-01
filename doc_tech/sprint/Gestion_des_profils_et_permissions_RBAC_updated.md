# Sprint - Section mémorisation : Gestion des profils et permissions RBAC (Mis à Jour)

## Objectif
Développer les fonctionnalités permettant de gérer les profils utilisateurs et les permissions selon le modèle RBAC. Ce sprint inclut la préparation complète du système pour permettre la gestion des utilisateurs avant leur connexion, avec une gestion spéciale des gérants de compagnie qui bénéficient de toutes les permissions fonctionnelles pour leur compagnie.

## Étapes du sprint
1. **Création des structures de base**
   - Création des pays (table `pays`) - entité géographique de base
   - Création des compagnies (table `compagnies`) - entité principale de regroupement
   - Création des stations-service (table `stations`) associées à une compagnie
   - Configuration des paramètres de base pour chaque structure

2. **Définition des modules et permissions fonctionnels**
   - Définition des modules fonctionnels (ventes, achats, stocks, trésorerie, comptabilité, etc.)
   - Création des permissions de base (lire, créer, modifier, supprimer, annuler) par module
   - Association des permissions aux modules fonctionnels
   - Structure de gestion des permissions (Modules → Permissions)

3. **Configuration des profils utilisateurs**
   - Création des profils (table `profils`) avec leurs permissions associées
   - Système d'attribution de permissions aux profils (table `profil_permissions`)
   - Gestion des associations profil-permission
   - Interface de configuration des profils selon les besoins spécifiques
   - Gestion spéciale pour le profil "Gérant de Compagnie" avec toutes les permissions fonctionnelles

4. **Création des utilisateurs avec accès restreints**
   - Création des utilisateurs (table `utilisateurs`) avec :
     - Login unique
     - Mot de passe haché (avec bcrypt)
     - Association à un profil spécifique
     - Restriction aux stations spécifiques via le champ `stations_user` (JSONB)
     - Attribution des droits selon le profil
     - Classification du type d'utilisateur (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)
   - Validation des données utilisateurs avant enregistrement
   - Gestion des statuts utilisateurs (Actif/Inactif/Supprimé)

5. **Gestion des stations et données par utilisateur**
   - Chaque utilisateur est limité à des stations spécifiques
   - Le champ `stations_user` (JSONB) permet de restreindre les opérations à certaines stations
   - Le filtrage des données se fait principalement par le champ `compagnie_id`
   - Permet une gestion géographique et organisationnelle fine des accès

6. **Architecture de la gestion des permissions**
   - Système RBAC (Role-Based Access Control) qui permet :
     - Aux gérants de compagnie d'avoir un accès complet à toutes les opérations de leur propre compagnie
     - Une gestion fine des droits d'accès basée sur les profils pour les autres types d'utilisateurs
     - Une attribution spécifique de stations aux utilisateurs
     - Un système de validation hiérarchique pour les opérations sensibles

7. **Hiérarchie des utilisateurs et responsabilités**
   - Super administrateur : Accès complet à toutes les fonctionnalités, création d'autres administrateurs, gestion des gérants compagnie
   - Administrateur : Accès limité selon les permissions définies par le super administrateur
   - Gérant compagnie : Accès complet à toutes les opérations de sa propre compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.), gestion des utilisateurs de sa compagnie
   - Utilisateur compagnie : Accès limité selon ses permissions spécifiques
   - Distinction des endpoints : Authentification séparée pour administrateurs et utilisateurs

8. **Système de permissions étendues pour les gérants de compagnie**
   - Les gérants de compagnie bénéficient implicitement de toutes les permissions fonctionnelles
   - Leur accès est limité aux données appartenant à leur propre compagnie
   - Ils peuvent effectuer toutes les opérations dans tous les modules pour leur compagnie
   - Aucune attribution manuelle de permissions individuelles nécessaire pour les gérants

9. **Suivi et validation des actions**
   - Journalisation : Toutes les actions des utilisateurs sont enregistrées avec détails
   - Validations hiérarchiques : Système de validation selon le montant ou le type d'opération
   - Contrôles d'accès : Système automatique de vérification des permissions et de filtrage des données

10. **Sécurité et surveillance**
    - Contrôles d'accès : Vérification des permissions et filtrage par compagnie
    - Journalisation : Toutes les actions sensibles sont enregistrées
    - Surveillance proactive : Système d'alertes pour les actions sensibles et écarts de comportement
    - Contrôle d'accès par endpoint : Séparation des endpoints administrateur et utilisateur avec blocage des accès croisés
    - Gestion des tentatives d'accès non autorisés aux données d'autres compagnies

## Livrables
- Interface de gestion des pays
- Interface de gestion des compagnies et stations
- Système de gestion des modules
- Interface de gestion des permissions
- Interface de gestion des profils utilisateurs
- Système d'attribution de permissions aux profils
- Interface d'attribution des stations aux utilisateurs
- Interface de création et gestion des utilisateurs
- Module de validation des données utilisateurs
- Module de gestion des statuts utilisateurs
- Module de validation hiérarchique
- Système de journalisation des actions
- Interface de gestion des contrôles d'accès
- Système de surveillance proactive
- Système de filtrage des données par compagnie
- Documentation spécifique pour les gérants de compagnie

## Tests
- Tests de création des structures de base
- Tests de gestion des modules et permissions
- Tests de configuration des profils
- Tests de création d'utilisateurs
- Tests d'attribution des stations
- Tests de validation hiérarchique
- Tests de journalisation
- Tests de sécurité des accès
- Tests de surveillance
- Tests des permissions étendues pour les gérants de compagnie
- Tests de filtrage des données par compagnie
- Tests de sécurité pour empêcher l'accès aux données d'autres compagnies