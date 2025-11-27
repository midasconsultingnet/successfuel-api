# Manuel utilisateur SuccessFuel

## Introduction

SuccessFuel est un ERP complet conçu pour la gestion des stations-service. Ce système informatisé permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

## Types d'utilisateurs et accès

Le système distingue 4 types d'utilisateurs avec des rôles et responsabilités spécifiques. L'accès aux fonctionnalités dépend du type d'utilisateur et de la compagnie à laquelle l'utilisateur appartient.

### Super Administrateur
- Accès complet à toutes les fonctionnalités du système
- Gestion globale du système
- Création et gestion des autres administrateurs
- Accès à l'endpoint administrateur

### Administrateur
- Accès selon les permissions définies par le super administrateur
- Gestion des aspects opérationnels selon ses permissions
- Accès à l'endpoint administrateur

### Gérant de Compagnie (nouvellement mis à jour)
- Accès à **toutes les opérations de sa propre compagnie** (achats, ventes, stocks, trésorerie, comptabilité, etc.)
- Accès limité aux données de **sa propre compagnie**
- Accès à l'endpoint utilisateur standard
- **Avantage important** : Le gérant de compagnie bénéficie automatiquement de toutes les permissions fonctionnelles pour sa propre compagnie, ce qui lui permet de gérer toutes les opérations sans avoir besoin de permissions spécifiques assignées manuellement

### Utilisateur de Compagnie
- Accès limité selon ses permissions spécifiques
- Opérations quotidiennes selon ses droits
- Accès à l'endpoint utilisateur standard

## Connexion au système

### Pour les gérants et utilisateurs de compagnie
1. Accédez à l'interface de connexion
2. Entrez vos identifiants (login et mot de passe)
3. Vous serez connecté à votre espace utilisateur
4. Vous aurez accès à toutes les fonctionnalités de votre compagnie

### Pour les administrateurs
1. Accédez à l'interface de connexion pour administrateurs
2. Entrez vos identifiants d'administrateur
3. Vous aurez accès à l'interface d'administration

## Fonctionnalités disponibles pour le Gérant de Compagnie

Grâce à la nouvelle règle de permissions, le gérant de compagnie a accès à toutes les fonctionnalités suivantes pour sa propre compagnie :

### Gestion des structures
- Consultation et gestion des stations de sa compagnie
- Gestion des cuves, carburants, pistolets de distribution
- Gestion des produits et familles de produits
- Gestion des employés de sa compagnie

### Gestion des achats
- Création et suivi des achats de carburant
- Création et suivi des achats de produits boutique
- Gestion des fournisseurs
- Suivi des coûts logistique

### Gestion des ventes
- Enregistrement des ventes de carburant avec index de pistolets
- Enregistrement des ventes de produits boutique
- Gestion des modes de paiement
- Suivi des performances des employés

### Gestion des stocks
- Suivi des niveaux de stock
- Gestion des entrées et sorties de stock
- Réalisation des inventaires

### Gestion de la trésorerie
- Suivi des encaissements et décaissements
- Gestion des différentes caisses
- Contrôle des écarts de caisse

### Gestion comptable
- Accès aux états financiers
- Génération des écritures comptables
- Suivi de la conformité fiscale

### Gestion des rapports
- Accès à tous les rapports de gestion
- Génération d'analyses de performance
- Suivi des indicateurs KPIs

## Limitations pour le Gérant de Compagnie

Malgré l'accès à toutes les fonctionnalités, le gérant de compagnie a certaines limitations importantes :

1. **Accès limité par compagnie** : Vous ne pouvez voir et modifier que les données appartenant à votre propre compagnie
2. **Aucun accès aux endpoints administrateurs** : Vous ne pouvez pas accéder aux fonctionnalités d'administration du système
3. **Gestion des utilisateurs limitée** : Vous pouvez gérer les utilisateurs de votre propre compagnie mais pas ceux d'autres compagnies

## Exemples d'utilisation

### Consultation des ventes
1. Allez dans le module "Ventes"
2. Vous verrez uniquement les ventes effectuées par les stations de votre compagnie
3. Vous pouvez filtrer par station, date, produit, etc.

### Gestion des achats
1. Allez dans le module "Achats"
2. Vous pouvez créer et suivre les achats pour votre compagnie
3. Vous ne verrez que les achats de votre propre compagnie

### Génération de rapports
1. Allez dans le module "Rapports"
2. Tous les rapports générés seront limités aux données de votre compagnie
3. Vous aurez accès à toutes les analyses et indicateurs pour votre compagnie

## Sécurité et bonnes pratiques

### Pour tous les utilisateurs
- Utilisez des mots de passe forts et uniques
- Déconnectez-vous toujours en fin de session
- Ne partagez jamais vos identifiants

### Pour les gérants de compagnie
- Vous avez un accès étendu à toutes les fonctionnalités de votre compagnie
- Utilisez cette puissance avec responsabilité
- Vérifiez toujours que les données que vous consultez/approuvez appartiennent à votre compagnie

## Support et assistance

En cas de problème ou de question :
- Contactez votre administrateur système
- Consultez la documentation technique pour les détails avancés
- Pour les problèmes techniques, contactez l'équipe de développement

## Mises à jour récentes

### Nouvelle règle pour les gérants de compagnie
- **Avant** : Les gérants de compagnie avaient besoin de permissions spécifiques assignées manuellement
- **Maintenant** : Les gérants de compagnie bénéficient automatiquement de toutes les permissions fonctionnelles pour leur propre compagnie
- **Résultat** : Moins de configuration, plus de flexibilité, tout en maintenant la sécurité par isolement des données entre compagnies