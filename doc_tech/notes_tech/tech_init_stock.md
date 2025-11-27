# Technical Specification - Initialisation des stocks (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de configurer les stocks au démarrage du système SuccessFuel. Cela inclut l'initialisation des stocks de carburant dans les cuves avec les index des pistolets, ainsi que l'initialisation des stocks de produits dans la boutique. L'objectif est de permettre une prise en main rapide et correcte du système par les gestionnaires de station-service.

### Problème à résoudre
Actuellement, il n'existe pas de mécanisme permettant d'initialiser les stocks réels de la station-service dans le système informatique. Cela pose problème car :
- Les mouvements de stock ne peuvent pas être correctement suivis sans un point de départ
- Les rapports de gestion ne reflètent pas la réalité des stocks
- Les calculs de rentabilité sont biaisés
- L'historique des stocks n'est pas disponible

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des initialisations que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Initialisation des stocks de carburant par cuve
- Initialisation des index des pistolets
- Historisation automatique des stocks initiaux
- Analyse de la qualité du carburant initial
- Initialisation des stocks de produits boutique
- Valorisation initiale des stocks
- Analyse des coûts logistique initiaux
- Génération des écritures comptables pour l'initialisation
- Contrôle de la cohérence des données initiales

## 2. User Stories & Critères d'acceptation

### US-INIT-001: En tant que gestionnaire, je veux initialiser les stocks de carburant
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales de carburant par cuve
  - Pouvoir spécifier la date d'initialisation
  - Pouvoir associer des informations sur la qualité du carburant
  - Vérifier la cohérence avec les mesures de hauteur dans la cuve
  - Générer automatiquement les écritures comptables d'ouverture
  - Conserver un historique des données initiales
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer l'initialisation
  - Les gérants de compagnie peuvent initialiser les stocks pour toutes les stations de leur compagnie

### US-INIT-002: En tant que gestionnaire, je veux initialiser les index des pistolets
- **Critères d'acceptation :**
  - Pouvoir saisir les index initiaux pour chaque pistolet
  - Associer les index aux pistolets et cuves appropriés
  - Vérifier la cohérence avec les stocks de carburant correspondants
  - Enregistrer les index comme point de départ pour les futures ventes
  - Les gérants de compagnie peuvent initialiser tous les index pour leur compagnie

### US-INIT-003: En tant que gestionnaire, je veux initialiser les stocks de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales pour chaque produit
  - Pouvoir spécifier les prix d'achat et de vente initiaux
  - Valoriser les stocks selon la méthode appropriée
  - Générer les écritures comptables correspondantes
  - Conserver l'historique des mouvements d'initialisation
  - Les gérants de compagnie peuvent initialiser les stocks boutique pour toutes les stations de leur compagnie

### US-INIT-004: En tant que gestionnaire, je veux analyser la qualité du carburant initial
- **Critères d'acceptation :**
  - Pouvoir enregistrer les paramètres de qualité du carburant
  - Associer les analyses de qualité aux stocks de carburant
  - Suivre les spécifications techniques du carburant
  - Générer des rapports sur la qualité du stock initial
  - Les gérants de compagnie peuvent effectuer toutes les analyses de qualité pour leur compagnie

### US-INIT-005: En tant que gestionnaire, je veux contrôler la cohérence des données initiales
- **Critères d'acceptation :**
  - Vérifier la cohérence entre les différentes initialisations
  - Identifier les incohérences possibles
  - Proposer des corrections pour les anomalies détectées
  - Valider l'ensemble des données avant validation finale
  - Les gérants de compagnie peuvent contrôler la cohérence pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations d'initialisation dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'initialisation pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les stations concernées doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module des structures
- Les initialisations sont liées aux cuves, pistolets, stations et produits
- Les données des structures sont utilisées pour les validations

### Module comptable
- L'initialisation génère des écritures comptables d'ouverture
- Le plan comptable est utilisé pour les écritures d'initialisation

### Module des stocks
- Les données d'initialisation deviennent le point de départ pour le suivi des stocks
- L'historique des mouvements commence à partir des données initiales

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'initialisation pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement