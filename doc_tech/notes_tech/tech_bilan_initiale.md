# Technical Specification - Bilan initial (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant d'établir le bilan initial d'une station-service avant l'utilisation du système SuccessFuel. Ce bilan initial constitue le point de départ comptable et opérationnel du système, permettant de capturer l'état exact des actifs, passifs, capitaux propres et stocks au moment de l'activation du système informatique. L'objectif est de permettre une continuité des opérations et un suivi fiable des indicateurs financiers et opérationnels.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un mécanisme permettant d'enregistrer l'état initial des postes comptables et opérationnels avant l'utilisation du système. Cela pose problème car :
- Les comptes comptables n'ont pas de solde initial
- Les stocks de départ ne sont pas enregistrés
- Les immobilisations ne sont pas prises en compte
- Les créances clients et dettes fournisseurs ne sont pas initialisées
- L'analyse comparative entre l'état initial et l'état actuel est impossible
- Les états financiers ne reflètent pas la réalité initiale

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des initialisations que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Initialisation des postes de bilan (actifs et passifs)
- Enregistrement des immobilisations existantes
- Initialisation des stocks de carburant et de produits boutique
- Prise en compte des créances clients et dettes fournisseurs
- Saisie des capitaux propres et emprunts existants
- Création d'un point de départ pour la comptabilité
- Analyse comparative entre l'état initial et l'état actuel
- Historique des modifications du bilan initial

## 2. User Stories & Critères d'acceptation

### US-BI-001: En tant que gestionnaire, je veux initialiser les postes d'actif du bilan
- **Critères d'acceptation :**
  - Pouvoir saisir les soldes initiaux pour chaque poste d'actif
  - Associer les valeurs aux bons comptes du plan comptable
  - Vérifier l'équilibre comptable (actif = passif + capitaux propres)
  - Sauvegarder les données saisies dans le système
  - Générer un état du bilan initial
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer l'initialisation
  - Les gérants de compagnie peuvent initialiser l'ensemble des postes pour leur compagnie

### US-BI-002: En tant que gestionnaire, je veux initialiser les postes de passif du bilan
- **Critères d'acceptation :**
  - Pouvoir saisir les soldes initiaux pour chaque poste de passif
  - Intégrer les capitaux propres existants
  - Enregistrer les emprunts en cours
  - Assurer la cohérence avec les postes d'actif
  - Les gérants de compagnie peuvent initialiser tous les postes de passif pour leur compagnie

### US-BI-003: En tant que gestionnaire, je veux initialiser les stocks de carburant et de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités et valeurs des stocks existants
  - Associer les stocks aux cuves et aux références produits
  - Vérifier la correspondance entre les quantités physiques et les stocks enregistrés
  - Intégrer les données dans le module de gestion des stocks
  - Les gérants de compagnie peuvent initialiser les stocks pour toutes les stations de leur compagnie

### US-BI-004: En tant que gestionnaire, je veux enregistrer les créances clients et dettes fournisseurs existantes
- **Critères d'acceptation :**
  - Pouvoir saisir les montants des créances clients existantes
  - Enregistrer les dettes fournisseurs actuelles
  - Associer les montants aux tiers concernés
  - Intégrer les données dans les modules clients et fournisseurs
  - Les gérants de compagnie peuvent enregistrer toutes les créances et dettes pour leur compagnie

### US-BI-005: En tant que gestionnaire, je veux effectuer une analyse comparative entre l'état initial et l'état actuel
- **Critères d'acceptation :**
  - Pouvoir consulter le bilan initial à tout moment
  - Comparer les valeurs initiales avec les valeurs actuelles
  - Générer des rapports d'évolution
  - Analyser les variations de chaque poste
  - Les gérants de compagnie peuvent accéder à toutes les analyses pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de bilan initial dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de bilan initial pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation

## 4. Dépendances avec d'autres modules

### Module comptable
- Le bilan initial est intégré au plan comptable existant
- Les soldes initiaux sont enregistrés comme des écritures comptables spécifiques
- Les états financiers utilisent les données du bilan initial

### Module des structures
- Les données sont associées aux stations de la compagnie
- Les comptes sont liés au plan comptable de la compagnie

### Module des stocks
- Les stocks initiaux sont enregistrés dans le module de gestion des stocks
- Les données sont utilisées pour les calculs de valeur des stocks

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de bilan initial pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que la cohérence comptable est maintenue après les initialisations