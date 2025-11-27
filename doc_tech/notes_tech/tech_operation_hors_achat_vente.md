# Technical Specification - Opérations hors achat vente (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer toutes les opérations qui ne relèvent ni des achats, ni des ventes dans le système SuccessFuel. Cela inclut la gestion des dépenses opérationnelles, des immobilisations, des ajustements de stock, des déclarations fiscales, des assurances, des contrats de maintenance, des programmes de fidélisation, et autres opérations périphériques mais essentielles à la gestion d'une station-service.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet pour gérer les opérations périphériques qui ne sont ni des achats ni des ventes, ce qui pose problème car :
- Les dépenses opérationnelles ne sont pas correctement enregistrées
- Les immobilisations ne sont pas suivies de façon structurée
- Les ajustements de stock sont mal gérés
- Les déclarations fiscales doivent être faites en dehors du système
- Les assurances et contrats de maintenance ne sont pas suivis
- Les programmes de fidélisation ne sont pas intégrés
- L'analyse commerciale et les prévisions de demande ne sont pas disponibles

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des opérations que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des dépenses opérationnelles
- Gestion des immobilisations et de leur amortissement
- Gestion des ajustements de stock (entrées/sorties non liées à achats/ventes)
- Gestion des déclarations fiscales
- Gestion des assurances
- Gestion des contrats de maintenance
- Gestion des services annexes
- Gestion des programmes de fidélisation
- Gestion des cartes de carburant
- Gestion des contrats clients
- Gestion de la qualité du carburant
- Contrôles de validation pour les opérations sensibles
- Génération des écritures comptables automatiques

## 2. User Stories & Critères d'acceptation

### US-OHV-001: En tant que gestionnaire, je veux gérer les dépenses opérationnelles
- **Critères d'acceptation :**
  - Pouvoir enregistrer toutes les dépenses opérationnelles
  - Catégoriser les dépenses selon des classifications définies
  - Associer les dépenses à des modes de paiement spécifiques
  - Générer automatiquement les écritures comptables
  - Suivre les tendances des dépenses dans le temps
  - Seuls les utilisateurs avec les permissions appropriées peuvent enregistrer les dépenses
  - Les gérants de compagnie peuvent gérer toutes les dépenses pour leur compagnie

### US-OHV-002: En tant que gestionnaire, je veux gérer les immobilisations
- **Critères d'acceptation :**
  - Pouvoir enregistrer les immobilisations acquises
  - Calculer automatiquement les amortissements
  - Suivre la valeur nette comptable des immobilisations
  - Enregistrer les cessions d'immobilisations
  - Générer des rapports sur les immobilisations
  - Les gérants de compagnie peuvent gérer toutes les immobilisations pour leur compagnie

### US-OHV-003: En tant que gestionnaire, je veux gérer les déclarations fiscales
- **Critères d'acceptation :**
  - Pouvoir préparer les déclarations fiscales
  - Calculer automatiquement les taxes dues
  - Suivre les échéances fiscales
  - Générer les documents de déclaration
  - Archiver les déclarations historiques
  - Les gérants de compagnie peuvent gérer toutes les déclarations fiscales pour leur compagnie

### US-OHV-004: En tant que gestionnaire, je veux gérer les assurances
- **Critères d'acceptation :**
  - Enregistrer les contrats d'assurance
  - Suivre les dates d'échéance
  - Gérer les sinistres déclarés
  - Calculer les coûts annuels des assurances
  - Générer des alertes pour les renouvellements
  - Les gérants de compagnie peuvent gérer toutes les assurances pour leur compagnie

### US-OHV-005: En tant que gestionnaire, je veux gérer les programmes de fidélisation
- **Critères d'acceptation :**
  - Configurer les programmes de fidélisation
  - Suivre les points ou avantages accumulés par les clients
  - Gérer les échanges de points contre récompenses
  - Analyser l'efficacité des programmes
  - Intégrer les programmes avec les modules de vente
  - Les gérants de compagnie peuvent gérer tous les programmes de fidélisation pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations hors achats/ventes dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations hors achats/ventes pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les validations hiérarchiques s'appliquent selon les seuils établis

## 4. Dépendances avec d'autres modules

### Module comptable
- Les opérations génèrent des écritures comptables automatiques
- Le plan comptable est utilisé pour les écritures spécifiques

### Module de trésorerie
- Les dépenses affectent les mouvements de trésorerie
- Les paiements sont gérés dans le module trésorerie

### Module des structures
- Les immobilisations sont liées aux stations et équipements
- Les assurances sont associées aux actifs de la compagnie

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement