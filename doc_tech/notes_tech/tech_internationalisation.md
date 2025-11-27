# Technical Specification - Internationalisation (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant l'adaptation du système SuccessFuel à différents pays africains francophones. L'objectif est de rendre le système suffisamment flexible pour s'adapter aux spécificités légales, fiscales, comptables, monétaires et culturelles de chaque pays tout en maintenant une architecture cohérente et standardisée.

### Problème à résoudre
Actuellement, le système SuccessFuel est configuré pour fonctionner dans un contexte spécifique (Madagascar). Pour permettre son déploiement dans d'autres pays africains francophones, il est nécessaire de:
- Supporter différentes législations fiscales et systèmes comptables (OHADA, etc.)
- Gérer des devises multiples avec conversion automatique
- Adapter les unités de mesure selon les pratiques locales
- Générer des rapports conformes aux normes locales
- Configurer dynamiquement les spécifications locales sans modification du code

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des configurations que pour sa propre compagnie, et seulement dans les pays où sa compagnie opère.

### Définition du périmètre
Le périmètre inclut:
- Gestion multi-pays avec configuration des spécifications locales
- Support des différentes législations fiscales et systèmes comptables
- Gestion des devises multiples et historique des taux de change
- Système de taxation modulaire configurable par pays
- Gestion des unités de mesure locales et conversions
- Modèles de rapports spécifiques par pays
- Architecture modulaire pour l'adaptation internationale
- Support des spécificités locales via système de plugins/configurations
- Contrôle des accès selon les pays d'opération

## 2. User Stories & Critères d'acceptation

### US-INT-001: En tant qu'administrateur, je veux gérer les pays pris en charge par le système
- **Critères d'acceptation :**
  - Pouvoir ajouter/supprimer/modifier des pays dans le système
  - Configurer les spécifications locales pour chaque pays (devise, législation, etc.)
  - Attribuer des permissions d'accès aux pays selon les utilisateurs
  - Générer des rapports spécifiques par pays
  - Seuls les utilisateurs avec les permissions appropriées peuvent gérer les pays
  - Les gérants de compagnie peuvent voir les pays où leur compagnie opère

### US-INT-002: En tant qu'administrateur, je veux configurer les spécifications fiscales par pays
- **Critères d'acceptation :**
  - Pouvoir définir les taux de taxation pour chaque pays
  - Configurer les obligations fiscales spécifiques
  - Adapter les calculs fiscaux selon les législations locales
  - Générer les déclarations fiscales selon les normes locales
  - Les gérants de compagnie peuvent configurer les spécifications fiscales pour leur pays d'opération

### US-INT-003: En tant qu'administrateur, je veux gérer les devises multiples
- **Critères d'acceptation :**
  - Pouvoir ajouter de nouvelles devises au système
  - Gérer l'historique des taux de change
  - Convertir automatiquement les montants selon les taux en temps réel
  - Générer des rapports dans différentes devises
  - Les gérants de compagnie peuvent utiliser toutes les fonctionnalités de gestion des devises pour leur compagnie

### US-INT-004: En tant qu'administrateur, je veux configurer les systèmes comptables locaux
- **Critères d'acceptation :**
  - Adapter le plan comptable selon les systèmes locaux (OHADA, etc.)
  - Configurer les règles de comptabilité spécifiques à chaque pays
  - Générer les états financiers selon les normes locales
  - Valider les écritures comptables selon les règles locales
  - Les gérants de compagnie peuvent configurer les systèmes comptables pour leur pays d'opération

### US-INT-005: En tant qu'administrateur, je veux gérer les modèles de rapports par pays
- **Critères d'acceptation :**
  - Créer des modèles de rapports spécifiques pour chaque pays
  - Adapter les formats aux exigences locales
  - Intégrer les spécifications culturelles et linguistiques
  - Générer des rapports conformes aux normes locales
  - Les gérants de compagnie peuvent accéder à tous les rapports pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations d'internationalisation dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'internationalisation pour sa propre compagnie et les pays où elle opère
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie et les pays d'opération de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données des pays où leur compagnie opère
- Les configurations spécifiques à un pays sont restreintes aux utilisateurs concernés

## 4. Dépendances avec d'autres modules

### Module comptable
- L'internationalisation affecte le plan comptable et les écritures
- Les règles comptables varient selon les pays

### Module de gestion des structures
- Les structures sont liées aux pays d'implantation
- Les configurations locales varient selon les pays

### Module de gestion des rapports
- Les modèles de rapports sont spécifiques par pays
- Les formats sont adaptés aux exigences locales

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'internationalisation pour leur compagnie et pays concernés
- S'assurer que les utilisateurs ne peuvent pas accéder aux configurations d'autres pays sans autorisation
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie et les pays
- S'assurer que les conversions de devises fonctionnent correctement