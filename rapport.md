# Rapport Complet sur le Système de Gestion des Stations-Service - Succès Fuel

## Table des Matières
1. [Architecture Générale du Système](#architecture-générale-du-système)
2. [Modules de l'Application](#modules-de-lapplication)
3. [Structure de la Base de Données](#structure-de-la-base-de-données)
4. [Spécifications Techniques](#spécifications-techniques)
5. [Fonctionnalités Clés](#fonctionnalités-clés)
6. [Intégrations Inter-Modules](#intégrations-inter-modules)
7. [Sécurité et Gestion des Accès](#sécurité-et-gestion-des-accès)

## Architecture Générale du Système

Le système Succès Fuel est une application de gestion complète pour les stations-service, construite avec FastAPI et PostgreSQL. Il suit une architecture modulaire avec des modules spécialisés interconnectés.

### Technologies Utilisées :
- **Backend** : Python, FastAPI
- **Base de données** : PostgreSQL
- **Authentification** : JWT, bcrypt
- **ORM** : SQLAlchemy
- **Déploiement** : Gunicorn

## Modules de l'Application

### 1. Authentification et Utilisateurs (`api/auth/`)
Gère l'authentification, les utilisateurs et les rôles dans le système.

- **auth_handler.py** : Gère la création et la validation des tokens JWT
- **permission_check.py** : Vérifie les droits d'accès aux ressources
- **schemas.py** : Définit les modèles Pydantic pour les utilisateurs et authentification
- **router.py** : Endpoints pour l'inscription, connexion, gestion des utilisateurs

### 2. Structure de la Compagnie (`api/compagnie/`)
Gère les compagnies, stations, cuves, pistolets et équipements.

- **Models** : Compagnie, Station, Cuve, Pistolet, EtatInitialCuve, MouvementStockCuve
- **Fonctionnalités** : Gestion de la structure de la compagnie, initialisation des stocks
- **Intégration** : Liens avec les modules Carburant, Produits, Stocks

### 3. Produits et Stocks (`api/produits/`, `api/stocks/`)
Gère les produits de la boutique et leurs stocks.

- **Models** : Produit, FamilleProduit, StockProduit, MouvementStock
- **Fonctionnalités** : Gestion des produits, stocks, mouvements de stock
- **Calculs** : Coût moyen pondéré, historique des mouvements

### 4. Carburant (`api/carburant/`)
Gère les types de carburant et leur distribution.

- **Models** : Carburant, PrixCarburant
- **Fonctionnalités** : Consultation des carburants, gestion des prix

### 5. Achats (`api/achats/`, `api/achats_carburant/`)
Gère les achats de carburant et de produits.

- **Models** : Achat, AchatCarburant, LigneAchatCarburant, CompensationFinanciere
- **Fonctionnalités** : Commandes, livraisons, facturations, compensations financières

### 6. Ventes (`api/ventes/`)
Gère les ventes de carburant et de produits boutique.

- **Models** : Vente, VenteCarburant, VenteDetail, CreanceEmploye
- **Fonctionnalités** : Gestion des ventes, calcul des créances employés

### 7. Tiers (`api/tiers/`)
Gère les relations avec les clients, fournisseurs et employés.

- **Models** : Tiers, SoldeTiers, MouvementTiers
- **Fonctionnalités** : Gestion des comptes clients/fournisseurs/employés

### 8. Trésoreries (`api/tresoreries/`)
Gère les trésoreries (caisse, banque, etc.) et leurs mouvements.

- **Models** : Tresorerie, TresorerieStation, MouvementTresorerie, TransfertTresorerie, EtatInitialTresorerie
- **Fonctionnalités** : Gestion des trésoreries, mouvements, transferts
- **Nouvelle fonctionnalité** : Gestion des méthodes de paiement spécifiques par trésorerie

### 9. Mouvements Financiers (`api/mouvements_financiers/`)
Gère les règlements, recouvrements et avoirs.

- **Models** : Reglement, Creance, Avoir
- **Fonctionnalités** : Paiements, créances, avoirs, pénalités

### 10. Charges et Salaires (`api/charges/`, `api/salaires/`)
Gère les charges de fonctionnement et la gestion des salaires.

- **Models** : Charge, CategorieCharge, Salaire, Prime, Avance
- **Fonctionnalités** : Gestion des charges, paie des employés

### 11. Immobilisations (`api/immobilisations/`)
Gère les immobilisations de la compagnie.

- **Models** : Immobilisation, MouvementImmobilisation
- **Fonctionnalités** : Acquisition, amortissement, cession des immobilisations

### 12. Inventaires (`api/inventaires/`)
Gère les inventaires de carburant et de produits boutique.

- **Models** : Inventaire, EcartInventaire
- **Fonctionnalités** : Comptages physiques, écarts, rapprochements

### 13. Bilans (`api/bilans/`)
Gère les bilans de trésorerie et les états financiers.

- **Models** : BilanOperationnel
- **Fonctionnalités** : Génération de bilans opérationnels

### 14. Config (`api/config/`)
Gère les paramètres système et d'entreprise.

### 15. Health (`api/health/`)
Points de terminaison pour la surveillance et la santé de l'application.

## Structure de la Base de Données

Le schéma de base de données complet comprend 45 tables interconnectées :

### Tables Principales :
- **utilisateur** : Gestion des utilisateurs du système
- **compagnie** : Informations sur les compagnies
- **station** : Stations-service appartenant aux compagnies
- **tiers** : Clients, fournisseurs et employés
- **tresorerie** : Trésoreries de la compagnie
- **carburant** : Types de carburant (gazole, essence, etc.)
- **produit** : Produits de la boutique

### Tables de Gestion :
- **achat_carburant** : Achats de carburant
- **commande_achat** : Commandes d'achat de produits
- **vente_carburant** : Ventes de carburant
- **vente_boutique** : Ventes de produits boutique
- **mouvement_tresorerie** : Mouvements d'argent
- **transfert_tresorerie** : Transferts entre trésoreries
- **mouvement_financier** : Règlements et recouvrements
- **charge_fonctionnement** : Charges de fonctionnement

### Tables de Suivi :
- **inventaire_carburant** : Inventaires de cuves
- **inventaire_boutique** : Inventaires de produits
- **bilan_operations** : Bilans opérationnels
- **etat_financier** : États financiers générés

### Tables d'Historique :
- **historique_vente** : Historique des modifications de ventes
- **historique_livraison** : Historique des livraisons
- **journal_action_utilisateur** : Journalisation des actions

## Spécifications Techniques

### Modèle de Trésorerie Avancé
Le système de trésorerie a été récemment mis à jour avec une architecture sophistiquée :

- **Trésorerie globale** → **TrésorerieStation (par station)** avec `solde_initial` et `solde_actuel`
- **EtatInitialTresorerie** : Stocke le solde initial avec une contrainte d'unicité
- **MouvementTresorerie** : Enregistre les entrées/sorties avec `type_mouvement` et `methode_paiement_id`
- **TransfertTresorerie** : Gère les transferts entre trésoreries avec création automatique de deux mouvements
- **Solde calculé** : `solde_initial + Σ(entrées) - Σ(sorties) + Σ(recus) - Σ(envoyes)`
- **Méthodes de paiement spécifiques** : Système avec `MethodePaiement` et `TresorerieMethodePaiement`

### Gestion des Méthodes de Paiement
Le nouveau système de méthodes de paiement permet :

- Configurations spécifiques par type de trésorerie
- Activation/désactivation des méthodes
- Gestion des droits d'accès par utilisateur
- Association avec les mouvements de trésorerie

### Vues et Index
Le système inclut plusieurs vues pour faciliter les rapports et analyses :

- `vue_ventes_carburant` : Détails des ventes de carburant
- `vue_ventes_boutique` : Détails des ventes boutique
- `vue_mouvements_tresorerie` : Détails des mouvements de trésorerie
- `vue_stock_cuve` : Vue consolidée des stocks de cuves
- `vue_materia_sldes_tresorerie` : Vue matérialisée pour les soldes de trésorerie

## Fonctionnalités Clés

### 1. Gestion Complète des Stations-Service
- Création, gestion et suivi des stations
- Configuration des cuves de carburant avec barremage
- Gestion des pistolets de distribution
- Suivi des niveaux de carburant par cuve

### 2. Gestion des Stocks
- Stocks de produits boutique
- Stocks de carburant par cuve
- Mouvements de stock (entrée, sortie, ajustement)
- Calcul de coût moyen pondéré

### 3. Gestion Financière Complète
- Trésoreries multiples (caisse, banque, mobile money, etc.)
- Suivi des soldes initiaux
- Transferts entre trésoreries
- Méthodes de paiement spécifiques par trésorerie
- Gestion des règlements et recouvrements

### 4. Gestion Commerciale
- Ventes de carburant avec pistolets
- Ventes boutique avec gestion de stock
- Gestion des clients, fournisseurs, employés
- Avoirs et compensations

### 5. Gestion des Ressources Humaines
- Gestion des employés
- Calcul des salaires
- Gestion des créances employés
- Paie des employés

### 6. Gestion des Achats
- Achats de carburant
- Achats de produits boutique
- Commandes et livraisons
- Compensations financières

## Intégrations Inter-Modules

Le système utilise une architecture fortement intégrée :

### Ventes ↔ Stocks
- Les ventes déclenchent les mouvements de stock
- Vérification de la disponibilité avant validation
- Mise à jour automatique des quantités

### Ventes ↔ Trésoreries
- Attribution automatique des recettes aux trésoreries
- Génération de mouvements de trésorerie
- Utilisation des méthodes de paiement configurées

### Achats ↔ Trésoreries
- Paiement des achats via les trésoreries
- Compensation financière en cas d'écarts
- Génération d'avoirs

### Tiers ↔ Mouvements Financiers
- Suivi des soldes des tiers
- Gestion des dettes et créances
- Règlements et recouvrements

### Inventaires ↔ Stocks
- Comparaison entre stocks théoriques et réels
- Calcul des écarts
- Justification des écarts

## Sécurité et Gestion des Accès

### Contrôle d'Accès
- Niveaux d'utilisateur : administrateur, gérant_compagnie, utilisateur_compagnie
- Accès restreint par compagnie et station
- Sécurité basée sur les tokens JWT

### Journalisation
- Journalisation complète des actions (JournalActionUtilisateur)
- Historique des modifications
- Suivi des connexions et activités

### Validation
- Validation des droits avant chaque opération
- Contrôles de cohérence
- Contraintes d'intégrité référentielle

## Nouveautés Récentes

### Système de Méthodes de Paiement
Récemment implémenté selon les spécifications du sprint des trésoreries :
- Table `methode_paiement` pour les méthodes de paiement
- Table `tresorerie_methode_paiement` pour les associations
- Référence dans `mouvement_tresorerie` via `methode_paiement_id`
- Gestion des droits d'accès et activation/désactivation