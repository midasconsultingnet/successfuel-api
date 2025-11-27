# Ordre de réalisation des sprints - SuccessFuel ERP (Mis à Jour)

## Ordre de développement recommandé

En tant qu'expert en développement, voici l'ordre de réalisation des sprints pour le projet SuccessFuel, basé sur les dépendances fonctionnelles et techniques :

### Phase 1 : Fondations du système
1. **[Sécurité_du_système.md]** - Mise en place de l'architecture de sécurité (authentification, autorisation, journalisation)
2. **[Gestion_des_profils_et_permissions_RBAC.md]** - Gestion des utilisateurs, rôles et permissions (dépend de la sécurité)

### Phase 2 : Infrastructure de base
3. **[Gestion_des_structures.md]** - Création des entités de base : stations, cuves, carburants, produits, employés, clients, fournisseurs
4. **[Initialisation_des_stocks.md]** - Configuration initiale des stocks et des index de pistolets

### Phase 3 : Fonctionnalités comptables de base
5. **[Plan_comptable_et_ecritures.md]** - Gestion du plan comptable et des écritures comptables
6. **[Bilan_initial.md]** - Mise en place de la structure comptable (bilan, actifs, passifs)
7. **[Rapports.md]** - Développement des fonctionnalités de reporting de base

### Phase 4 : Opérations principales
8. **[Gestion_des_achats.md]** - Achats de carburant et de produits boutique (nécessite les structures de base)
9. **[Gestion_des_ventes.md]** - Ventes de carburant, boutique et services (nécessite les structures et les achats)
10. **[Inventaires.md]** - Contrôle des stocks et mesures (nécessite les fonctionnalités d'achats/ventes)

### Phase 5 : Fonctionnalités avancées
11. **[Operations_hors_achats_ventes.md]** - Gestion des autres opérations (dépenses, paie, immobilisations)
12. **[Ajustements.md]** - Ajustements de stock et réinitialisation des index (nécessite l'inventaire)
13. **[Depot_de_garantie.md]** - Gestion des dépôts de garantie (nécessite la gestion des clients)
14. **[Gestion_des_indicateurs_de_performance.md]** - KPIs et analyses (nécessite toutes les opérations)

### Phase 6 : Internationalisation
15. **[Internationalisation.md]** - Adaptation aux différents pays francophones (couche d'abstraction finale)

## Justification de l'ordre de développement

### Sécurité en premier
La sécurité est placée en priorité absolue car :
- Elle conditionne l'accès à toutes les fonctionnalités
- Toute modification ultérieure de l'architecture de sécurité est complexe
- Les modules suivants doivent s'intégrer à ce système de base

### Structures de base ensuite
Les modules de structure sont fondamentaux car :
- Toutes les autres fonctionnalités dépendent de ces entités
- Les stations, produits, employés, clients, etc. sont nécessaires partout
- Ils ne dépendent d'aucun autre module fonctionnel

### Comptabilité
Avant d'implémenter des opérations complexes, on établit :
- La structure comptable de base (bilan)
- Les rapports fondamentaux

### Opérations métier
Puis les modules principaux :
- Achats : nécessaires pour approvisionner les stocks
- Ventes : cœur du métier de la station-service
- Inventaires : contrôle des stocks et validation des mouvements

### Fonctionnalités complémentaires
Ensuite les modules secondaires :
- Gestion des autres opérations (dépenses, paie, etc.)
- Ajustements pour corriger les écarts
- Dépôt de garantie pour la relation client

### Analyse et optimisation
Enfin :
- Indicateurs de performance qui nécessitent des données opérationnelles
- Internationalisation qui s'appuie sur l'ensemble du système

## Dépendances critiques

- **Sécurité** → Tous les autres modules
- **Structures** → Achats, Ventes, Inventaires, etc.
- **Achats** → Ventes, Inventaires
- **Ventes** → Rapports, Indicateurs de performance
- **Inventaires** → Ajustements
- **Tous les modules opérationnels** → Indicateurs de performance

## Recommandations d'implémentation

1. **Itérations courtes** : Mise en place de versions minimales fonctionnelles (MVP) de chaque module
2. **Tests intégrés** : Chaque module testé en isolation puis en intégration avec les modules précédents
3. **Déploiement progressif** : Livraison incrémentale des fonctionnalités
4. **Validation utilisateur** : Retours fréquents des utilisateurs finaux à chaque sprint
5. **Documentation continue** : Documentation mise à jour à chaque module

## Risques et mitigation

- **Risque** : Changements de spécifications tardifs dans les modules de base
- **Mitigation** : Revue des spécifications avant chaque sprint, architecture modulaire
- **Risque** : Dépendances non anticipées entre modules
- **Mitigation** : Revue technique fréquente, documentation des interfaces

## Mise à jour concernant les permissions

Le module de Gestion des Profils et Permissions RBAC a été mis à jour pour permettre aux **gérants de compagnie** d'avoir toutes les permissions fonctionnelles pour toutes les opérations de leur propre compagnie, tout en limitant leur accès aux données de cette même compagnie. Cela signifie que les gérants de compagnie n'ont plus besoin d'avoir des permissions spécifiques assignées manuellement - ils ont automatiquement accès à toutes les fonctionnalités mais seulement pour les données de leur compagnie.