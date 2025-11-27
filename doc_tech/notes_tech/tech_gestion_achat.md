# Technical Specification - Gestion des achats (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer tous les approvisionnements de la station-service dans le système SuccessFuel. Cela inclut la gestion des achats de carburant (processus complet avec mesures avant/après, écarts, qualité) et des achats de produits pour la boutique, avec des fonctionnalités de suivi des coûts logistique, d'évaluation des fournisseurs et d'intégration comptable.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet de gestion des achats qui permet :
- De suivre l'approvisionnement en carburant avec les mesures de cuve avant/après
- De gérer les écarts de livraison
- De contrôler la qualité du carburant reçu
- De suivre les coûts logistique
- D'évaluer les performances des fournisseurs
- D'intégrer automatiquement les achats dans le système comptable
- De gérer les achats de produits pour la boutique
- De produire des rapports d'analyse des achats

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des achats que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des achats de carburant avec mesures avant/après livraison
- Gestion des achats de produits pour la boutique
- Gestion des bons de commande
- Calcul et suivi des écarts de livraison
- Analyse de la qualité du carburant
- Suivi des coûts logistique
- Génération automatique des écritures comptables
- Gestion des paiements fournisseurs
- Mise à jour des stocks après livraison
- Évaluation des fournisseurs
- Génération de rapports liés aux achats
- Contrôles de validation selon le montant ou le type d'achat

## 2. User Stories & Critères d'acceptation

### US-ACH-001: En tant que gestionnaire, je veux gérer les achats de carburant avec mesures avant/après
- **Critères d'acceptation :**
  - Pouvoir créer un bon de commande pour les achats de carburant
  - Enregistrer les mesures de cuve avant la livraison
  - Enregistrer les mesures de cuve après la livraison
  - Calculer automatiquement les écarts de livraison
  - Vérifier la qualité du carburant reçu
  - Mettre à jour les stocks après la livraison
  - Générer les écritures comptables automatiquement
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer ces opérations
  - Les gérants de compagnie peuvent effectuer tous les achats de carburant pour leur compagnie

### US-ACH-002: En tant que gestionnaire, je veux gérer les achats de produits boutique
- **Critères d'acceptation :**
  - Pouvoir créer un bon de commande pour les produits boutique
  - Enregistrer les détails des produits commandés (référence, quantité, prix)
  - Valider la livraison des produits
  - Mettre à jour les stocks après livraison
  - Générer les écritures comptables correspondantes
  - Les gérants de compagnie peuvent effectuer tous les achats de produits pour leur compagnie

### US-ACH-003: En tant que gestionnaire, je veux suivre les coûts logistique
- **Critères d'acceptation :**
  - Pouvoir enregistrer les coûts logistiques associés à chaque livraison
  - Attribuer les coûts logistiques aux achats concernés
  - Calculer le coût total d'approvisionnement (prix d'achat + coûts logistiques)
  - Analyser les tendances des coûts logistiques
  - Les gérants de compagnie peuvent suivre tous les coûts logistiques pour leur compagnie

### US-ACH-004: En tant que gestionnaire, je veux évaluer les performances des fournisseurs
- **Critères d'acceptation :**
  - Pouvoir consulter les indicateurs de performance des fournisseurs
  - Analyser les délais de livraison
  - Évaluer la qualité des produits livrés
  - Suivre les écarts entre commandé et livré
  - Générer des rapports d'évaluation des fournisseurs
  - Les gérants de compagnie ont accès à toutes les données d'évaluation pour leur compagnie

### US-ACH-005: En tant que gestionnaire, je veux gérer les contrôles de validation hiérarchique
- **Critères d'acceptation :**
  - Les achats importants nécessitent une validation supplémentaire
  - Les validations sont tracées dans le système
  - Les seuils de validation peuvent être configurés
  - Le système identifie les achats nécessitant validation
  - Les gérants de compagnie peuvent valider les achats selon les règles de validation pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations d'achats dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'achats pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les fournisseurs et stations concernés doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module des stocks
- Les achats mettent à jour les niveaux de stock
- Les mouvements d'achat sont enregistrés dans l'historique des stocks
- Les calculs d'écart sont basés sur les mesures de stock

### Module des structures
- Les achats de carburant sont liés aux cuves et stations
- Les fournisseurs sont gérés dans le module des structures

### Module comptable
- Les achats génèrent des écritures comptables automatiques
- Le plan comptable est utilisé pour les écritures d'achat

### Module de trésorerie
- Les achats affectent les décaissements
- Les paiements aux fournisseurs sont enregistrés dans le module trésorerie

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'achats pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement