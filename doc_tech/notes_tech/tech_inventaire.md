# Technical Specification - Inventaires (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de contrôler les stocks de la station-service SuccessFuel. Cela inclut l'inventaire physique des stocks de carburant (mesure de hauteur dans les cuves avec calcul via barème) et des stocks de produits boutique, avec une comparaison systématique entre les stocks réels mesurés et les stocks théoriques du système, ainsi que l'analyse et la justification des écarts.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet d'inventaire qui permet :
- De mesurer la hauteur de carburant dans les cuves
- De calculer le volume via le barème de jauge
- De comparer les stocks réels avec les stocks théoriques
- De justifier les écarts constatés
- De suivre les tendances d'écart
- De gérer les inventaires boutique
- De produire des rapports d'analyse des écarts

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des inventaires que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des inventaires de carburant (mesure de hauteur, calcul via barème)
- Gestion des inventaires boutique (saisie de quantités réelles)
- Comparaison écart réel/théorique
- Analyse des écarts anormaux
- Suivi des températures (pour la correction volumétrique)
- Inventaires partiels ou complets
- Justification des écarts
- Analyse des tendances d'écart
- Génération de rapports d'inventaire
- Contrôles de validation selon le montant des écarts

## 2. User Stories & Critères d'acceptation

### US-INVT-001: En tant que gestionnaire, je veux effectuer des inventaires de carburant
- **Critères d'acceptation :**
  - Pouvoir mesurer la hauteur de carburant dans les cuves
  - Calculer automatiquement le volume via le barème de jauge
  - Enregistrer les mesures de température pour correction volumétrique
  - Comparer les volumes mesurés avec les volumes théoriques
  - Identifier les écarts constatés
  - Justifier les écarts importants
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer les inventaires
  - Les gérants de compagnie peuvent effectuer tous les inventaires de carburant pour leur compagnie

### US-INVT-002: En tant que gestionnaire, je veux effectuer des inventaires de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités réelles de chaque produit
  - Comparer les quantités réelles avec les quantités théoriques
  - Identifier les écarts de stock pour les produits
  - Justifier les écarts constatés
  - Générer des rapports d'inventaire détaillés
  - Les gérants de compagnie peuvent effectuer tous les inventaires boutique pour leur compagnie

### US-INVT-003: En tant que gestionnaire, je veux analyser les écarts constatés
- **Critères d'acceptation :**
  - Calculer automatiquement les écarts entre réel et théorique
  - Classifier les écarts par seuils (normal, anormal, critique)
  - Proposer des catégories pour expliquer les écarts
  - Suivre l'évolution des écarts dans le temps
  - Identifier les sources récurrentes d'écart
  - Les gérants de compagnie peuvent analyser tous les écarts pour leur compagnie

### US-INVT-004: En tant que gestionnaire, je veux justifier les écarts constatés
- **Critères d'acceptation :**
  - Pouvoir associer des motifs aux écarts d'inventaire
  - Enregistrer les preuves ou justifications des écarts
  - Appliquer des corrections aux stocks après validation
  - Générer les écritures comptables pour les ajustements
  - Conserver un historique des justifications
  - Les gérants de compagnie peuvent justifier tous les écarts pour leur compagnie

### US-INVT-005: En tant que gestionnaire, je veux produire des rapports d'inventaire
- **Critères d'acceptation :**
  - Générer des rapports d'inventaire détaillés
  - Créer des rapports comparatifs entre réel et théorique
  - Produire des analyses des tendances d'écart
  - Exporter les rapports dans différents formats
  - Planifier des rapports réguliers d'inventaire
  - Les gérants de compagnie peuvent produire tous les rapports d'inventaire pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations d'inventaire dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'inventaire pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les stations concernées doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module des stocks
- Les inventaires comparent les stocks réels et théoriques
- Les ajustements d'inventaire modifient les niveaux de stock
- L'historique des mouvements est utilisé pour l'analyse des écarts

### Module des structures
- Les inventaires sont liés aux cuves, stations et produits
- Les données des structures sont utilisées pour les validations

### Module comptable
- Les ajustements d'inventaire génèrent des écritures comptables
- Le plan comptable est utilisé pour les écritures d'ajustement

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'inventaire pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement