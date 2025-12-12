# Spécification RBAC - Gestion des Permissions Utilisateurs

## Introduction

Ce document décrit le système de contrôle d'accès basé sur les rôles (RBAC - Role-Based Access Control) pour le système Succès Fuel. Il définit les règles métier concernant les permissions applicables aux utilisateurs de type "utilisateur_compagnie", permettant une gestion flexible des droits d'accès par les gérants de compagnie.

## Concepts Clés

- **Utilisateur** : Personne physique utilisant le système, identifiée par un login et un mot de passe
- **Rôle** : Ensemble prédéfini de permissions (ex: "utilisateur_compagnie", "gerant_compagnie")
- **Profil personnalisé** : Ensemble configurable de modules autorisés, créé par un gérant de compagnie
- **Module** : Ensemble fonctionnel cohérent de fonctionnalités (ex: "Module Ventes Boutique")
- **Permission** : Droit d'accéder à un module spécifique

## Architecture du Système RBAC

### Entités Principales

1. **Utilisateur**
   - Appartient à une seule compagnie
   - Peut être affecté à une ou plusieurs stations
   - Possède un rôle de base ("utilisateur_compagnie" ou "gerant_compagnie")
   - Peut être associé à zéro ou un profil personnalisé

2. **Rôle de Base**
   - `gerant_compagnie` : Accès complet à tous les modules de sa compagnie
   - `utilisateur_compagnie` : Accès limité selon son profil personnalisé

3. **Profil Personnalisé**
   - Créé et géré par un `gerant_compagnie`
   - Composition de modules spécifiques
   - Unique par compagnie
   - Attribuable à plusieurs utilisateurs de type "utilisateur_compagnie"

4. **Module**
   - Ensemble fonctionnel unique du système
   - Liste complète des modules dans le système

## Modules du Système

1. Module Utilisateurs et Authentification
2. Module Structure de la Compagnie
3. Module Tiers
4. Module Produits et Stocks Complet
5. Module Trésoreries
6. Module Achats Carburant
7. Module Achats Boutique
8. Module Ventes Carburant
9. Module Ventes Boutique
10. Module Livraisons Carburant
11. Module Inventaires Carburant
12. Module Inventaires Boutique
13. Module Mouvements Financiers
14. Module Salaires et Rémunérations
15. Module Charges de Fonctionnement
16. Module Immobilisations
17. Module États, Bilans et Comptabilité

## Règles de Gestion des Permissions

### Pour les Utilisateurs de Type "utilisateur_compagnie"

1. **Accès Conditionnel**
   - Un utilisateur avec le rôle "utilisateur_compagnie" n'accède aux modules que s'il est affecté à un profil personnalisé
   - Sans profil personnalisé, l'utilisateur "utilisateur_compagnie" n'a accès à aucun module fonctionnel

2. **Accès Basé sur les Modules**
   - Les permissions sont attribuées au niveau du module, pas des actions spécifiques
   - Un utilisateur avec accès à un module dispose automatiquement de toutes les fonctionnalités du module (CRUD complet)
   - Les modules accessibles sont strictement limités à ceux inclus dans son profil personnalisé

3. **Restriction d'Affectation**
   - Seul le `gerant_compagnie` de la même compagnie peut créer ou modifier un profil personnalisé
   - Un `gerant_compagnie` ne peut pas affecter un utilisateur à un profil d'une autre compagnie
   - Les affectations sont limitées aux stations dont le `gerant_compagnie` a la responsabilité

4. **Héritage des Restrictions de Station**
   - Quel que soit le profil personnalisé, un utilisateur ne peut accéder qu'aux données des stations auxquelles il est affecté
   - Même si un module est accessible via le profil, l'utilisateur ne voit que les données des stations pertinentes

### Pour les Gérants de Compagnie (`gerant_compagnie`)

1. **Accès Global**
   - Le `gerant_compagnie` a accès à tous les modules de sa compagnie
   - Peut créer, modifier et supprimer des profils personnalisés
   - Peut attribuer des utilisateurs à des profils personnalisés
   - Peut modifier les affectations station/utilisateur

2. **Restriction de Données**
   - Même avec accès global aux modules, le `gerant_compagnie` n'accède qu'aux données de sa propre compagnie
   - Ne peut pas visualiser ou manipuler les données d'une autre compagnie

## Processus de Création de Profils Personnalisés

### Par un `gerant_compagnie`

1. **Création d'un nouveau profil**
   - Nom du profil (unique par compagnie)
   - Sélection des modules autorisés (checkboxes multiples)
   - Sauvegarde des configurations

2. **Modification d'un profil existant**
   - Accès à la liste des profils de la compagnie
   - Modification des modules inclus
   - Mise à jour avec validation des changements

3. **Affectation d'utilisateurs à un profil**
   - Sélection d'un ou plusieurs utilisateurs de type "utilisateur_compagnie"
   - Attribution au profil personnalisé
   - Confirmation des affectations

## Exemples de Profils Typiques

### Profil "Responsable Boutique"
Modules inclus :
- Module Produits et Stocks Complet
- Module Achats Boutique
- Module Ventes Boutique
- Module Inventaires Boutique
- Module Mouvements Financiers (partiellement, pour les opérations liées à la boutique)

### Profil "Responsable Carburant"
Modules inclus :
- Module Structure de la Compagnie
- Module Achats Carburant
- Module Ventes Carburant
- Module Livraisons Carburant
- Module Inventaires Carburant

### Profil "Responsable Comptable"
Modules inclus :
- Module Charges de Fonctionnement
- Module Mouvements Financiers
- Module Salaires et Rémunérations
- Module États, Bilans et Comptabilité

## Contraintes Techniques

1. **Validation des Accès**
   - Chaque requête vers une API est vérifiée contre les permissions de l'utilisateur
   - Les tentatives d'accès non autorisées sont journalisées

2. **Sécurité**
   - Les validations sont effectuées à la fois côté serveur (API) et côté client (interface)
   - Les routes non autorisées sont masquées dans l'interface utilisateur

3. **Performance**
   - Les permissions sont mises en cache pour éviter des consultations répétitives
   - Les mises à jour de permissions invalident automatiquement le cache concerné

## Gestion des Exceptions

### Accès Non Autorisé
- Si un utilisateur tente d'accéder à un module sans permission, une erreur HTTP 403 Forbidden est retournée
- Un message convivial indique à l'utilisateur qu'il n'a pas les droits nécessaires

### Modifications Dynamiques
- Si un profil est modifié pendant qu'un utilisateur est connecté, les modifications prennent effet à la prochaine requête ou après une actualisation de la session
- Une notification peut être envoyée à l'utilisateur pour l'informer des changements de permissions

## Surveillance et Audit

1. **Journalisation**
   - Toutes les modifications de profils sont tracées (qui, quand, quoi)
   - Les tentatives d'accès non autorisées sont enregistrées

2. **Rapports**
   - Disponibilité de rapports sur les affectations de profils
   - Suivi des modifications de permissions dans le temps

## Tables Nécessaires pour l'Implémentation RBAC

Le système RBAC décrit dans ce document nécessite les tables supplémentaires suivantes qui ne sont pas présentes dans la base de données actuelle :

### Table Profils
```sql
CREATE TABLE profils (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Cette table stocke les profils personnalisés créés par les gérants de compagnie.
- `nom` : Nom unique du profil au sein de la compagnie (ex: "Responsable boutique", "Responsable carburant")
- `description` : Description optionnelle du profil
- `compagnie_id` : Lien vers la compagnie propriétaire du profil

### Table Profil_Module
```sql
CREATE TABLE profil_module (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    module_nom VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profil_id, module_nom)
);
```

Cette table associe les modules autorisés à chaque profil.
- `profil_id` : Lien vers le profil concerné
- `module_nom` : Nom du module autorisé (ex: "Module Ventes Boutique", "Module Achats Carburant")

### Table Utilisateur_Profil
```sql
CREATE TABLE utilisateur_profil (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id) ON DELETE CASCADE,
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    date_affectation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    utilisateur_affectation_id UUID NOT NULL REFERENCES utilisateur(id), -- utilisateur qui a fait l'affectation
    UNIQUE(utilisateur_id)
);
```

Cette table attribue un profil à un utilisateur spécifique.
- `utilisateur_id` : Lien vers l'utilisateur concerné
- `profil_id` : Lien vers le profil attribué
- `utilisateur_affectation_id` : Lien vers l'utilisateur (gérant) qui a effectué l'affectation
- Contrainte d'unicité pour s'assurer qu'un utilisateur n'ait qu'un seul profil à la fois

## Index Nécessaires

```sql
-- Pour optimiser les requêtes d'autorisation
CREATE INDEX idx_profil_module_profil_id ON profil_module(profil_id);
CREATE INDEX idx_profil_module_module_nom ON profil_module(module_nom);
CREATE INDEX idx_utilisateur_profil_utilisateur_id ON utilisateur_profil(utilisateur_id);
CREATE INDEX idx_utilisateur_profil_profil_id ON utilisateur_profil(profil_id);
```

Ces tables permettront d'implémenter pleinement le système RBAC décrit dans ce document, permettant aux gérants de compagnie de créer des profils personnalisés avec des modules spécifiques pour les utilisateurs de type "utilisateur_compagnie".