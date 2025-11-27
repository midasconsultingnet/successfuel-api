# Technical Specification - Dépôt de garantie (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer les dépôts de garantie des clients dans le système SuccessFuel. L'objectif est de permettre aux gestionnaires de suivre les dépôts de garantie effectués par les clients, leurs utilisations éventuelles, et les remboursements associés. Le système doit également permettre de suivre les contrats de fidélité liés à ces dépôts.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas de fonctionnalités adéquates pour :
- Enregistrer les dépôts de garantie des clients
- Suivre l'utilisation des dépôts (paiement de dette/vente/écart)
- Gérer les remboursements de dépôts
- Afficher l'historique complet des transactions
- Afficher le solde visible client en temps réel
- Suivre les contrats de fidélité liés aux dépôts

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des opérations sur les dépôts que pour les clients appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Gestion des dépôts de garantie (enregistrement, utilisation, remboursement)
- Historique complet des transactions liées aux dépôts
- Affichage du solde visible client
- Suivi des contrats de fidélité
- Génération des écritures comptables liées aux dépôts
- Intégration avec les modules clients et trésorerie
- Génération de rapports liés aux dépôts de garantie

## 2. User Stories & Critères d'acceptation

### US-DG-001: En tant que gestionnaire, je veux enregistrer un dépôt de garantie d'un client
- **Critères d'acceptation :**
  - Pouvoir enregistrer un dépôt de garantie avec les informations essentielles (client, montant, date)
  - Associer le dépôt à une méthode de paiement spécifique
  - Générer automatiquement une écriture comptable au passif
  - Mettre à jour le solde du client
  - Conserver un historique des dépôts
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer cette opération
  - Les gérants de compagnie peuvent enregistrer des dépôts pour tous les clients de leur compagnie

### US-DG-002: En tant que gestionnaire, je veux suivre l'utilisation des dépôts de garantie
- **Critères d'acceptation :**
  - Pouvoir utiliser un dépôt pour le paiement d'une dette client
  - Pouvoir utiliser un dépôt pour régler une vente
  - Pouvoir utiliser un dépôt pour compenser un écart
  - Mettre à jour le solde du dépôt en conséquence
  - Enregistrer l'historique des utilisations
  - Les gérants de compagnie peuvent utiliser les dépôts pour toutes les opérations de leur compagnie

### US-DG-003: En tant que gestionnaire, je veux gérer les remboursements de dépôts
- **Critères d'acceptation :**
  - Pouvoir initier un remboursement de dépôt de garantie
  - Spécifier le mode de remboursement
  - Mettre à jour le solde du dépôt
  - Générer les écritures comptables appropriées
  - Conserver un historique des remboursements
  - Les gérants de compagnie peuvent effectuer des remboursements pour les clients de leur compagnie

### US-DG-004: En tant que gestionnaire, je veux afficher l'historique complet des transactions
- **Critères d'acceptation :**
  - Pouvoir consulter l'historique complet des dépôts pour chaque client
  - Voir les utilisations et remboursements effectués
  - Afficher les soldes au fil du temps
  - Générer des rapports détaillés
  - Les gérants de compagnie ont accès à l'historique complet pour leur compagnie

### US-DG-005: En tant que gestionnaire, je veux afficher le solde visible client en temps réel
- **Critères d'acceptation :**
  - Afficher le solde de dépôt de garantie sur la fiche client
  - Mettre à jour le solde en temps réel après chaque transaction
  - Permettre la consultation du solde par le client s'il y a autorisation
  - Intégrer le solde dans les écrans de vente et de règlement
  - Les gérants de compagnie peuvent voir tous les soldes des clients de leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de dépôts de garantie dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de dépôts de garantie pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les clients concernés doivent appartenir à la même compagnie que l'utilisateur

## 4. Dépendances avec d'autres modules

### Module clients
- Les dépôts sont associés aux clients existants
- Les soldes sont intégrés à la fiche client
- Les transactions affectent les soldes clients

### Module trésorerie
- Les dépôts affectent les mouvements de trésorerie
- Les remboursements sont enregistrés comme des décaissements
- Les utilisations de dépôts peuvent être des modes de paiement

### Module comptable
- Les dépôts génèrent des écritures comptables (passif)
- Les utilisations et remboursements modifient les soldes comptables
- Le plan comptable est utilisé pour les écritures

## 5. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de dépôts pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les écritures comptables sont générées correctement