# Technical Specification - Gestion des ventes (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer toutes les ventes effectuées dans la station-service SuccessFuel. Cela inclut les ventes de carburant (avec index de pistolets), les ventes de produits en boutique, et les services annexes, avec une intégration complète du processus de paiement, des mouvements de stock, des écritures comptables, et des analyses de performance des employés.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet de gestion des ventes qui permet :
- De suivre les ventes de carburant avec les index de pistolets
- De gérer les paiements clients (cash, crédit, écart pompiste)
- De générer les écritures comptables automatiques
- De suivre les performances des pompistes/caissiers
- De produire des tickets de caisse
- De faire les arrêts de compte caissier
- De surveiller les écarts anormaux
- De gérer les ventes de services annexes

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des ventes que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des ventes de carburant avec index de pistolet
- Gestion des ventes en boutique
- Gestion des ventes de services
- Processus de paiement intégré
- Génération automatique des écritures comptables
- Mise à jour des stocks après vente
- Génération des tickets de caisse
- Arrêts de compte caissier
- Suivi des performances des employés
- Suivi des écarts anormaux
- Gestion des validations hiérarchiques pour les opérations sensibles
- Intégration avec les modules clients et trésorerie

## 2. User Stories & Critères d'acceptation

### US-VNT-001: En tant que gestionnaire, je veux gérer les ventes de carburant avec index de pistolets
- **Critères d'acceptation :**
  - Pouvoir enregistrer une vente de carburant avec les index de début et de fin
  - Calculer automatiquement la quantité vendue à partir des index
  - Associer la vente à un pistolet et une cuve spécifiques
  - Mettre à jour les stocks en conséquence
  - Suivre les écarts entre index et quantité vendue
  - Seuls les utilisateurs avec les permissions appropriées peuvent enregistrer des ventes
  - Les gérants de compagnie peuvent effectuer toutes les ventes de carburant pour leur compagnie

### US-VNT-002: En tant que gestionnaire, je veux gérer les paiements clients
- **Critères d'acceptation :**
  - Prendre en charge les paiements en espèces
  - Gérer les paiements par carte de crédit
  - Enregistrer les paiements différés ou à crédit
  - Suivre les écarts de caisse
  - Générer les écritures comptables pour les paiements
  - Les gérants de compagnie peuvent gérer tous les paiements pour leur compagnie

### US-VNT-003: En tant que gestionnaire, je veux produire des tickets de caisse
- **Critères d'acceptation :**
  - Générer automatiquement un ticket pour chaque vente
  - Inclure toutes les informations de la vente sur le ticket
  - Numéroter séquentiellement les tickets
  - Permettre l'impression des tickets
  - Conserver un historique des tickets émis
  - Les gérants de compagnie peuvent générer et consulter tous les tickets pour leur compagnie

### US-VNT-004: En tant que gestionnaire, je veux effectuer les arrêts de compte caissier
- **Critères d'acceptation :**
  - Calculer automatiquement le total des ventes par mode de paiement
  - Comparer les montants théoriques et réels
  - Identifier les écarts éventuels
  - Enregistrer les écarts avec justifications
  - Générer les rapports d'arrêt de caisse
  - Les gérants de compagnie peuvent effectuer les arrêts de compte pour toutes les stations de leur compagnie

### US-VNT-005: En tant que gestionnaire, je veux suivre les performances des employés
- **Critères d'acceptation :**
  - Calculer la productivité de chaque pompiste/caissier
  - Suivre les indicateurs de performance (nombre de ventes, montant total, etc.)
  - Identifier les écarts anormaux dans les performances
  - Générer des rapports de performance
  - Les gérants de compagnie peuvent suivre toutes les performances pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de ventes dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de ventes pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les clients, stations et employés concernés doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module des stocks
- Les ventes modifient les niveaux de stock
- Les mouvements de vente sont enregistrés dans l'historique des stocks
- La disponibilité des produits est vérifiée avant la vente

### Module des structures
- Les ventes de carburant sont liées aux pistolets et cuves
- Les stations sont associées aux ventes
- Les clients sont gérés dans le module des structures

### Module comptable
- Les ventes génèrent des écritures comptables automatiques
- Le plan comptable est utilisé pour les écritures de vente

### Module de trésorerie
- Les ventes affectent les encaissements
- Les modes de paiement sont gérés dans le module trésorerie

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de ventes pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement