# Sprint - Section mémorisation : Sécurité du système

## Objectif
Développer les fonctionnalités permettant d'assurer la sécurité du système informatique et des données.

## Étapes du sprint
1. **Protection contre les injections SQL**
   - Requêtes préparées : Toutes les requêtes utilisent des paramètres positionnels ou nommés
   - Validation des entrées : Tous les champs utilisateur sont validés avant insertion dans la base
   - Types de données stricts : Utilisation de types spécifiques (UUID, NUMERIC, etc.) pour chaque champ
   - Contrôle d'accès à la base : Utilisation de rôles PostgreSQL avec permissions limitées

2. **Authentification et autorisation**
   - Authentification sécurisée : Jetons d'authentification chiffrés avec hachage et durée de vie limitée
   - Hachage des mots de passe : Utilisation de bcrypt ou équivalent avec sel (salt)
   - Système RBAC : Gestion des permissions granulaires avec profils personnalisables
   - Validation hiérarchique : Système de validation pour les opérations sensibles
   - Classification des utilisateurs : Distinction entre super administrateur, administrateur, gérant compagnie et utilisateur compagnie
   - Séparation des endpoints : Authentification distincte pour administrateurs et utilisateurs standards

3. **Protection des données sensibles**
   - Chiffrement des données critiques : Mots de passe, données financières, etc.
   - Masquage des données sensibles : Numéros de compte partiellement masqués
   - Journalisation sécurisée : Les traces d'audit ne contiennent pas les données sensibles en clair

4. **Journalisation et surveillance**
   - Journalisation détaillée : Toutes les actions critiques sont enregistrées
   - Surveillance proactive : Détection des anomalies et comportements suspects
   - Table des tentatives de connexion : Suivi des connexions réussies/échouées
   - Table des événements de sécurité : Suivi des incidents de sécurité
   - Suivi des accès non autorisés : Journalisation des tentatives d'accès aux endpoints non autorisés

5. **Contrôles d'accès**
   - Accès limité aux stations : Chaque utilisateur est limité à des stations spécifiques
   - Validation hiérarchique : Processus de validation selon le montant/type d'opération
   - Contrôle des modifications sensibles : Surveillance des opérations critiques
   - Politiques de sécurité configurables : Paramètres de sécurité personnalisables
   - Contrôle d'accès par endpoint : Blocage des accès croisés entre endpoints administrateur et utilisateur

6. **Sécurité des communications**
   - Utilisation du protocole HTTPS : Toutes les communications sont chiffrées
   - Protection contre les attaques CSRF : Jetons CSRF pour les opérations sensibles
   - Validation des origines des requêtes : Vérification de la provenance des appels

7. **Gestion des erreurs sécurisée**
   - Messages d'erreur non divulguants : Ne révèlent pas d'informations internes
   - Journalisation des erreurs : Toutes les erreurs sont enregistrées pour surveillance
   - Gestion personnalisée des exceptions : Évite les fuites d'informations

8. **Sauvegarde et récupération**
   - Sauvegardes cryptées : Données sauvegardées de manière sécurisée
   - Politique de rotation : Gestion sécurisée des versions de sauvegarde
   - Procédures de récupération testées : Processus validés régulièrement

## Notes techniques pour les développeurs

### Tables impliquées dans la sécurité du système :

#### 1. Gestion des utilisateurs et authentification
- **utilisateurs** (`id`, `login`, `mot_de_passe`, `profil_id`, `stations_user`, `statut`, `last_login`, `compagnie_id`, `type_utilisateur`)
  - Stocke les informations de base des utilisateurs
  - Le champ `mot_de_passe` doit être haché avec bcrypt
  - Le champ `stations_user` (JSONB) contrôle l'accès aux stations
  - Le champ `profil_id` relie l'utilisateur à ses permissions via la table `profils`
  - Le champ `type_utilisateur` distingue les super administrateurs, administrateurs, gérants compagnie et utilisateurs compagnie

- **auth_tokens** (`id`, `token_hash`, `user_id`, `expires_at`, `is_active`, `type_endpoint`)
  - Stocke les jetons d'authentification
  - Les jetons doivent avoir une durée de vie limitée
  - Le champ `token_hash` stocke le hachage du jeton
  - Le champ `type_endpoint` indique si le jeton est pour l'endpoint administrateur ou utilisateur
  - Utilisée pour l'authentification sécurisée

- **profils** (`id`, `code`, `libelle`, `compagnie_id`, `description`, `statut`)
  - Gestion des profils utilisateurs dans le système RBAC
  - Lié aux permissions via la table `profil_permissions`

- **profil_permissions** (`id`, `profil_id`, `permission_id`)
  - Table d'association entre profils et permissions
  - Implémente le système RBAC

- **modules** (`id`, `libelle`, `statut`)
  - Regroupe les fonctionnalités par modules (ventes, achats, stocks, etc.)

- **permissions** (`id`, `libelle`, `description`, `module_id`, `statut`)
  - Définit les actions spécifiques (lire, créer, modifier, supprimer, annuler)

#### 2. Journalisation et surveillance
- **tentatives_connexion** (`id`, `login`, `ip_connexion`, `resultat_connexion`, `utilisateur_id`, `type_endpoint`, `type_utilisateur`)
  - Suivi des tentatives de connexion (réussies/échouées)
  - Permet la surveillance proactive des accès
  - Le champ `type_endpoint` indique l'endpoint utilisé
  - Le champ `type_utilisateur` identifie le type de l'utilisateur

- **evenements_securite** (`id`, `type_evenement`, `description`, `utilisateur_id`, `ip_utilisateur`, `poste_utilisateur`, `session_id`, `donnees_supplementaires`, `statut`, `compagnie_id`)
  - Journalisation des événements de sécurité
  - Stocke les incidents de sécurité avec détails

- **modifications_sensibles** (`id`, `utilisateur_id`, `type_operation`, `objet_modifie`, `objet_id`, `ancienne_valeur`, `nouvelle_valeur`, `seuil_alerte`, `commentaire`, `ip_utilisateur`, `poste_utilisateur`, `statut`, `compagnie_id`)
  - Suivi des modifications critiques
  - Journalisation des changements sensibles avec valeurs avant/après

- **tentatives_acces_non_autorise** (`id`, `utilisateur_id`, `endpoint_accesse`, `endpoint_autorise`, `ip_connexion`, `statut`, `compagnie_id`, `created_at`)
  - Suivi des tentatives d'accès aux endpoints non autorisés
  - Journalisation des violations de sécurité concernant l'accès aux endpoints

#### 3. Contrôles d'accès
- **stations** (`id`, `compagnie_id`, `code`, `nom`, `pays_id`, `statut`)
  - Gestion des stations auxquelles les utilisateurs ont accès
  - Les contrôles d'accès sont basés sur cette table

- **permissions_tresorerie** (`id`, `utilisateur_id`, `tresorerie_id`, `droits`)
  - Gestion des droits spécifiques pour les opérations de trésorerie
  - Contrôle des accès niveau objet (trésorerie)

#### 4. Données sensibles et chiffrement
- Les données sensibles sont dispersées dans plusieurs tables :
  - `utilisateurs.mot_de_passe` : Doit être chiffré avec bcrypt
  - `tresoreries.solde` : Données financières sensibles
  - `clients.solde_comptable`, `fournisseurs.solde_comptable` : Informations financières
  - `achats.total`, `ventes.total` : Montants financiers
  - `employes.salaire_base` : Données personnelles sensibles

#### 5. Validation des entrées et prévention des injections SQL
Toutes les tables du système doivent implémenter :
- Des contraintes de validation (CHECK)
- Des types de données stricts (UUID, NUMERIC, etc.)
- Des longueurs de champs limitées pour éviter les dépassements

#### 6. Journalisation des actions critiques
- Utilisez les tables `journal_entries` et `journal_lines` pour les opérations comptables
- Utilisez les tables spécifiques de chaque module pour les autres opérations
- Mettez en place des triggers pour la journalisation automatique des opérations sensibles

## Fonctionnalités de gestion des utilisateurs

### 1. Cycle de vie des utilisateurs
- Création d'utilisateurs avec validation des informations
- Classification des utilisateurs (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)
- Activation/désactivation des comptes
- Réinitialisation de mot de passe
- Mise à jour des informations utilisateur
- Gestion des profils et permissions

### 2. Authentification
- Login avec validation des identifiants
- Sélection automatique de l'endpoint selon le type d'utilisateur
- Génération de jetons d'authentification sécurisés avec distinction d'endpoint
- Gestion des sessions utilisateur
- Déconnexion et invalidation des jetons
- Blocage des tentatives d'accès croisés entre endpoints

### 3. Autorisation (RBAC)
- Attribution de profils aux utilisateurs
- Assignation de permissions spécifiques
- Contrôle d'accès basé sur les rôles
- Validation hiérarchique pour les opérations sensibles
- Contrôle d'accès par endpoint (administrateur vs utilisateur)

## Livrables
- Système d'injection SQL prévention
- Système de validation des entrées
- Module d'authentification sécurisée
- Système de hachage des mots de passe
- Module de gestion RBAC
- Système de chiffrement des données
- Module de journalisation sécurisée
- Interface de gestion des tentatives de connexion
- Interface de gestion des événements de sécurité
- Module de contrôle d'accès
- Système de validation hiérarchique
- Module de surveillance proactive
- Système de sécurité des communications
- Module de gestion des erreurs sécurisée
- Système de sauvegarde et récupération

## Tests
- Tests d'injection SQL
- Tests de validation des entrées
- Tests d'authentification
- Tests de hachage des mots de passe
- Tests de RBAC
- Tests de chiffrement des données
- Tests de journalisation
- Tests de contrôle d'accès
- Tests de sécurité des communications
- Tests de gestion des erreurs
- Tests de sauvegarde et récupération