# Technical Specification - Gestion des structures (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant la gestion des éléments physiques et organisationnels d'une station-service. Ce module se concentre sur les entités opérationnelles spécifiques à une station-service, basées sur les structures de base créées dans la phase 1. Cela inclut la gestion des cuves de stockage, des carburants, des pistolets de distribution, des produits, des fournisseurs, des clients, des employés et des trésoreries.

### Problème à résoudre
Le système SuccessFuel a besoin d'un module complet pour gérer les structures physiques et organisationnelles d'une station-service, y compris :
- Suivi des stocks et du volume dans les cuves
- Gestion des prix des carburants et produits
- Contrôle des équipements (pistolets, cuves)
- Gestion des fournisseurs, clients et employés
- Suivi des modes de paiement et des trésoreries

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des opérations que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des cuves de stockage avec barème de jauge
- Gestion des carburants et historique des prix
- Gestion des pistolets de distribution
- Gestion des familles de produits et des produits
- Gestion des fournisseurs et clients
- Gestion des employés
- Gestion des trésoreries et modes de paiement
- Suivi des indices de performance et des indicateurs
- Contrôles de validation selon l'importance des modifications

## 2. User Stories & Critères d'acceptation

### US-STR-001: En tant que gestionnaire, je veux gérer les cuves de stockage
- **Critères d'acceptation :**
  - Pouvoir enregistrer chaque cuve (type de carburant, capacité en litres)
  - Configurer le barème de jauge pour le calcul du volume selon la hauteur
  - Suivre la température pour correction volumétrique
  - Contrôler l'accès aux cuves
  - Enregistrer l'historique des mesures
  - Seuls les utilisateurs avec les permissions appropriées peuvent modifier les cuves
  - Les gérants de compagnie peuvent gérer toutes les cuves pour leur compagnie

### US-STR-002: En tant que gestionnaire, je veux gérer les carburants et leurs prix
- **Critères d'acceptation :**
  - Pouvoir gérer les différents types de carburant (essence, gasoil, pétrole)
  - Suivre les prix d'achat et de vente
  - Enregistrer l'historique des évolutions de prix
  - Suivre la qualité du carburant
  - Générer des rapports sur l'évolution des prix
  - Les gérants de compagnie peuvent gérer tous les carburants et prix pour leur compagnie

### US-STR-003: En tant que gestionnaire, je veux gérer les pistolets de distribution
- **Critères d'acceptation :**
  - Numéroter et associer chaque pistolet à une cuve spécifique
  - Suivre l'index initial et les relevés
  - Contrôler l'accès aux pistolets
  - Enregistrer l'historique des index
  - Suivre les performances de chaque pistolet
  - Les gérants de compagnie peuvent gérer tous les pistolets pour leur compagnie

### US-STR-004: En tant que gestionnaire, je veux gérer les produits et familles de produits
- **Critères d'acceptation :**
  - Créer et organiser les familles de produits
  - Gérer les produits de la boutique (alimentation, lubrifiants, etc.)
  - Suivre les prix d'achat et de vente
  - Enregistrer les historiques de prix
  - Les gérants de compagnie peuvent gérer tous les produits pour leur compagnie

### US-STR-005: En tant que gestionnaire, je veux gérer les clients, fournisseurs et employés
- **Critères d'acceptation :**
  - Enregistrer les informations des clients, fournisseurs et employés
  - Suivre les coordonnées et les informations contractuelles
  - Gérer les statuts (actif, inactif, etc.)
  - Mettre à jour les informations selon les changements
  - Les gérants de compagnie peuvent gérer tous les clients, fournisseurs et employés pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de gestion des structures dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de gestion des structures pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les stations, employés, clients et fournisseurs concernés doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module de sécurité
- Les structures sont soumises aux contrôles d'accès par compagnie
- Les validations de permissions sont requises pour les modifications

### Module des stocks
- Les cuves et carburants sont liés à la gestion des stocks
- Les produits sont utilisés dans les modules de vente et d'inventaire

### Module des ventes et achats
- Les structures fournissent les bases pour les opérations d'achat et de vente
- Les clients et fournisseurs sont gérés dans ce module

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de gestion des structures pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les modifications respectent les limites de permissions