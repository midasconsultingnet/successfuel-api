# Technical Specification - Module Ajustements (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer les ajustements de stock et les réinitialisations d'index dans le système SuccessFuel. L'objectif est de permettre aux gestionnaires de gérer les écarts de stock boutique (périmés, cassés) et de réinitialiser les index de pistolets de manière sécurisée avec validation hiérarchique.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas de fonctionnalités adéquates pour :
- Gérer les sorties de stock boutique pour les articles périmés ou cassés
- Analyser les causes de péremption
- Réinitialiser les index de pistolets de manière sécurisée
- Appliquer des validations hiérarchiques pour les opérations sensibles
- Conserver un historique des actions critiques

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des ajustements que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des ajustements de stock boutique (entrée/sortie pour périmés/cassés)
- Analyse des causes de péremption
- Réinitialisation sécurisée des index de pistolets
- Suivi des validations hiérarchiques
- Journalisation des actions critiques
- Génération des écritures comptables liées aux ajustements
- Intégration avec les modules de gestion des stocks et des pistolets

## 2. User Stories & Critères d'acceptation

### US-AJUST-001: En tant que gestionnaire, je veux gérer les sorties de stock boutique pour les articles périmés ou cassés
- **Critères d'acceptation :**
  - Pouvoir créer un ajustement de stock pour les articles périmés ou cassés
  - Spécifier la quantité et le motif de l'ajustement
  - Sélectionner le type d'ajustement (périmé, cassé)
  - Associer l'ajustement à une station spécifique
  - Voir l'impact sur le stock disponible
  - Générer automatiquement les écritures comptables
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer ces ajustements
  - Les gérants de compagnie peuvent effectuer ces ajustements pour toutes les stations de leur compagnie

### US-AJUST-002: En tant que gestionnaire, je veux analyser les causes de péremption
- **Critères d'acceptation :**
  - Pouvoir consulter un historique des péremptions par produit
  - Générer des rapports sur les causes fréquentes de péremption
  - Identifier les produits les plus concernés par les péremptions
  - Accéder aux données de vente pour analyser la rotation des produits
  - Les gérants de compagnie ont accès à toutes les données de péremption de leur compagnie

### US-AJUST-003: En tant que gestionnaire, je veux réinitialiser les index de pistolets de manière sécurisée
- **Critères d'acceptation :**
  - Pouvoir demander la réinitialisation d'un index de pistolet
  - Spécifier l'ancien index et le nouvel index
  - Justifier le motif de la réinitialisation
  - Soumettre la demande à une validation hiérarchique
  - Être notifié une fois la réinitialisation validée ou rejetée
  - Conserver un historique des réinitialisations
  - Les gérants de compagnie peuvent initier et valider les réinitialisations pour leur compagnie

### US-AJUST-004: En tant que gestionnaire, je veux que les validations hiérarchiques soient appliquées pour les opérations sensibles
- **Critères d'acceptation :**
  - Les ajustements de stock importants nécessitent une validation supplémentaire
  - Les réinitialisations d'index sont soumises à validation hiérarchique
  - Le système identifie les seuils pour déclencher les validations
  - Les validations sont tracées dans le système
  - Les gérants de compagnie peuvent valider les opérations pour leur compagnie selon les règles de validation

### US-AJUST-005: En tant que gestionnaire, je veux conserver un historique des actions critiques
- **Critères d'acceptation :**
  - Toutes les opérations d'ajustement sont enregistrées
  - L'historique contient l'utilisateur, la date, l'opération effectuée
  - Les modifications d'index sont enregistrées avec justification
  - L'historique est accessible pour des audits
  - Les gérants de compagnie peuvent consulter l'historique complet pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations d'ajustement dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations d'ajustement pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation

## 4. Dépendances avec d'autres modules

### Module des stocks
- Les ajustements modifient les niveaux de stock
- Les mouvements d'ajustement sont enregistrés dans l'historique des stocks
- Le système de validation des stocks est affecté par les ajustements

### Module des structures
- Les pistolets et cuves sont liés aux réinitialisations d'index
- Les stations sont associées aux ajustements de stock

### Module comptable
- Les ajustements génèrent des écritures comptables automatiques
- Le plan comptable est utilisé pour les écritures d'ajustement

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités d'ajustement pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester les validations hiérarchiques selon les seuils définis

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que l'historisation fonctionne correctement