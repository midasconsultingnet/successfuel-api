# Technical Specification - Plan comptable et écritures (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer le plan comptable et les écritures comptables pour assurer la conformité fiscale et comptable de la station-service. L'objectif est de permettre une comptabilité rigoureuse et conforme aux systèmes locaux (OHADA, etc.), avec une journalisation automatique des opérations métier et la génération d'états financiers fiables.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module comptable complet permettant :
- De gérer un plan comptable selon les systèmes locaux (OHADA, etc.)
- De générer automatiquement des écritures comptables correctes
- De valider la cohérence des écritures comptables
- De produire des états financiers fiables

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des modifications comptables que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion du plan comptable avec hiérarchie et types appropriés
- Génération automatique des écritures comptables
- Validation des écritures selon les règles comptables
- Journalisation des opérations comptables
- Numérotation automatique des pièces comptables
- Contrôle de la cohérence des écritures
- Calcul des soldes des comptes
- Génération des états financiers
- Validation de l'équilibre comptable
- Gestion des périodes comptables
- Contrôle des accès aux modifications comptables

## 2. User Stories & Critères d'acceptation

### US-PCG-001: En tant que comptable, je veux gérer le plan comptable
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des comptes
  - Maintenir la hiérarchie des comptes (classes, généraux, auxiliaires)
  - Appliquer les règles de nomenclature selon le système local
  - Associer les comptes à des catégories (actif, passif, produit, charge)
  - Vérifier l'équilibre entre débit et crédit
  - Seuls les utilisateurs avec les permissions appropriées peuvent modifier le plan comptable
  - Les gérants de compagnie peuvent consulter et utiliser tous les comptes pour leur compagnie

### US-PCG-002: En tant que comptable, je veux générer automatiquement les écritures comptables
- **Critères d'acceptation :**
  - Générer automatiquement les écritures à partir des opérations métier
  - Appliquer les règles de ventilation comptable
  - Numéroter automatiquement les pièces comptables
  - Assurer l'équilibre entre débit et crédit pour chaque écriture
  - Conserver un historique des écritures générées
  - Les gérants de compagnie peuvent consulter toutes les écritures pour leur compagnie

### US-PCG-003: En tant que comptable, je veux valider la cohérence des écritures comptables
- **Critères d'acceptation :**
  - Vérifier l'équilibre débit/crédit pour chaque écriture
  - Contrôler la validité des comptes utilisés
  - Valider la cohérence avec les règles comptables locales
  - Identifier et signaler les écritures incorrectes
  - Appliquer des validations hiérarchiques pour les écritures sensibles
  - Les gérants de compagnie peuvent valider les écritures selon les règles de validation pour leur compagnie

### US-PCG-004: En tant que comptable, je veux calculer les soldes des comptes
- **Critères d'acceptation :**
  - Calculer les soldes au jour le jour
  - Calculer les soldes pour une période donnée
  - Afficher les soldes avec sens (débiteur/créditeur)
  - Générer des fiches de comptes détaillées
  - Calculer les soldes de clôture pour les états financiers
  - Les gérants de compagnie peuvent consulter tous les soldes pour leur compagnie

### US-PCG-005: En tant que comptable, je veux générer les états financiers
- **Critères d'acceptation :**
  - Générer le bilan comptable
  - Produire le compte de résultat
  - Créer le grand livre
  - Éditer la balance
  - Produire le journal
  - Les gérants de compagnie peuvent produire tous les états financiers pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations comptables dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations comptables pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les validations hiérarchiques s'appliquent selon les seuils établis pour la modification des écritures

## 4. Dépendances avec d'autres modules

### Module des ventes
- Les ventes génèrent des écritures comptables automatiques
- Les encaissements affectent les comptes de trésorerie

### Module des achats
- Les achats génèrent des écritures comptables automatiques
- Les dettes fournisseurs sont enregistrées dans les comptes appropriés

### Module de trésorerie
- Les mouvements de trésorerie affectent les comptes bancaires et caisses
- Les paiements et encaissements sont enregistrés comptablement

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités comptables pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que la cohérence comptable est maintenue