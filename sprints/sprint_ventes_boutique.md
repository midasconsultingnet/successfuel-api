# Sprint: Module Ventes Boutique

## Objectif
Implémenter la gestion des ventes boutique par station, incluant la gestion des remises, promotions et ventes en lot.

## Spécifications détaillées

### 1. Gestion des ventes
- Création, modification et suppression de ventes boutique
- Champs: client (optionnel), date/heure, montant total, trésorerie (attribuée selon le type de vente)
- La station est automatiquement déterminée selon l'utilisateur connecté
- Détails des ventes: produit, quantité, prix unitaire, montant
- Type de vente: produit, service, hybride (produit + service)
- Statut de la vente (en cours, terminée, annulée)
- Attribution automatique de la trésorerie selon le type de vente:
  - Ventes de produits: affectation automatique à la trésorerie produits configurée pour la station
  - Ventes de services: affectation automatique à la trésorerie services configurée pour la station
  - Ventes hybrides: deux mouvements de trésorerie distincts (produits et services)
- Validation de la disponibilité et du solde de la trésorerie avant la vente
- Intégration avec le module Trésoreries pour l'utilisation des caisses configurées

### 2. Gestion des remises et promotions
- Application de remises globales ou par produit
- Système de promotions (achats groupés, quantité, etc.)
- Historique des promotions appliquées

### 3. Lien avec les produits et stocks
- Association avec les produits boutique, gaz, lubrifiants et services
- Validation de la disponibilité en stock via l'API du module Produits et Stocks (uniquement pour les produits avec stock)
- Mise à jour automatique des stocks après validation via l'API du module Produits et Stocks (uniquement pour les produits avec stock)
- Gestion des services comme produits sans stock (lavages, réparations pneus, etc.)
- Gestion des ventes hybrides: combinaison de produits et services
- Gestion des avoirs via le module Mouvements Financiers pour les annulations et modifications
- Intégration avec le module États, Bilans et Comptabilité pour les rapports de ventes

### 4. Gestion des trésoreries, arrêts de compte et annulations
- Utilisation des trésoreries existantes configurées dans le module Trésoreries
- Association de types de trésorerie aux types de vente via paramétrage:
  - Trésorerie produits: configurée dans le module Trésoreries pour les ventes de produits
  - Trésorerie services: configurée dans le module Trésoreries pour les ventes de services
- Validation que les trésoreries configurées existent et sont actives pour la station
- Gestion des contraintes de disponibilité et de solde minimum
- Intégration avec le module Trésoreries pour l'utilisation et la validation des caisses
- Mécanisme de substitution en cas de trésorerie indisponible
- Gestion des arrêts de compte:
  - Opération de clôture de caisse avec transfert des recettes vers une autre trésorerie
  - Processus: calcul du solde, transfert vers la trésorerie destination, réinitialisation de la caisse
  - Utilisation du système de transferts du module Trésoreries
  - Intégration avec le module États, Bilans et Comptabilité pour les rapports
- Gestion des annulations et modifications:
  - Annulation totale: suppression de la vente et restitution du stock pour les produits avec stock (appel au module Produits et Stocks)
  - Annulation partielle: suppression d'articles spécifiques et restitution du stock concerné pour les produits avec stock (appel au module Produits et Stocks)
  - Modification: ajustement de quantités, prix ou produits avec appel aux modules concernés pour recalcul des impacts
  - Génération automatique d'avoirs à traiter par le module Mouvements Financiers
  - Réversion des mouvements de trésorerie via le module Mouvements Financiers
  - Contrôle de disponibilité du stock via le module Produits et Stocks

### 5. Historique des ventes
- Suivi des ventes par période
- Historique des produits vendus
- Calcul des montants et quantités par produit
- Historique des mouvements de trésorerie par type de vente et par trésorerie configurée
- Rapport de rapprochement entre ventes et mouvements de trésorerie
- Historique des arrêts de compte avec détails chronologiques
- Contrôle de cohérence : comparaison entre le solde calculé et le montant transféré
- Identification des écarts éventuels lors des arrêts de compte
- Suivi des transferts effectués pour chaque trésorerie de vente

### 6. Gestion des erreurs et exceptions
- Journalisation complète des erreurs avec détails (date, heure, utilisateur, type d'erreur)
- Messages d'erreur clairs et explicatifs pour l'utilisateur
- Gestion des pannes techniques et pertes de connexion
- Gestion des erreurs de saisie et de validation
- Processus de correction ou de contournement
- Gestion des stocks insuffisants ou indisponibles
- Gestion des paiements refusés ou insuffisants
- Gestion des erreurs de synchronisation avec les modules externes
- Procédures de relance pour les opérations échouées
- Contrôle des erreurs récurrentes et alertes correspondantes

### 7. Sécurité
- Accès restreint selon les rôles (gerant_compagnie, utilisateur_compagnie) et stations
- Validation des droits d'accès avant les opérations
- Audit des validations importantes
- Contrôle d'accès spécifique pour les arrêts de compte (rôles autorisés)
- Contrôles spécifiques pour les annulations et modifications:
  - Validation des droits avant annulation/modification (rôles autorisés)
  - Journalisation des motifs d'annulation/modification
  - Gestion des limites de temps et de montant pour les annulations
  - Exigence d'autorisation pour les montants supérieurs à un seuil
  - Journalisation complète des modifications de ventes
- Intégration avec le module Utilisateurs et Authentification pour la gestion des rôles et permissions

## Livrables
- API RESTful pour la gestion des ventes boutique
- API RESTful pour les arrêts de compte
- API RESTful pour les annulations et modifications de ventes
- API RESTful pour la gestion des erreurs et exceptions
- Modèles de données pour les ventes et leurs détails
- Modèles de données pour les erreurs et exceptions
- Interface d'administration des ventes boutique
- Système de gestion des remises et promotions
- Système d'arrêt de compte et de transfert des recettes
- Système d'annulation et de modification des ventes
- Système de journalisation des erreurs et exceptions
- Calcul automatique des impacts sur le stock via l'API du module Produits et Stocks
- Calcul automatique des mouvements de trésorerie selon le type de vente
- Système de génération d'avoirs pour les annulations via le module Mouvements Financiers
- Système d'intégration avec le module Trésoreries
- Système de validation des trésoreries avant les ventes
- Système de rapprochement et de contrôle des arrêts de compte
- Intégration avec le module États, Bilans et Comptabilité pour les rapports
- Intégration avec le module Utilisateurs et Authentification pour la gestion des rôles
- Tests unitaires et d'intégration