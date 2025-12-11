# Ordre de réalisation des modules du système

## Ordre de priorité pour l'implémentation des modules

1. **Module Utilisateurs et Authentification**
   - Fichier sprint: `sprint_utilisateurs_et_authentification.md`
   - Fichier modèle de données: `modeles_de_donnees/utilisateurs_et_authentification.md`
   - Justification: Nécessaire pour la sécurité et l'accès aux autres modules

2. **Module Structure de la Compagnie**
   - Fichier sprint: `sprint_structure_de_la_compagnie.md`
   - Fichier modèle de données: `modeles_de_donnees/structure_de_la_compagnie.md`
   - Justification: Base pour la gestion des stations et de la structure organisationnelle

3. **Module Trésoreries**
   - Fichier sprint: `sprint_tresoreries.md`
   - Fichier modèle de données: `modeles_de_donnees/tresoreries.md`
   - Justification: Nécessaire pour les opérations financières et les soldes initiaux

4. **Module Tiers (Clients, Fournisseurs, Employés)**
   - Fichier sprint: `sprint_tiers_clients_fournisseurs_employes.md`
   - Fichier modèle de données: `modeles_de_donnees/tiers_clients_fournisseurs_employes.md`
   - Justification: Base pour les transactions avec les tiers

5. **Module Produits et Stocks Complet**
   - Fichier sprint: `sprint_produits_et_stocks_complet.md`
   - Fichier modèle de données: `modeles_de_donnees/produits_et_stocks_complet.md`
   - Justification: Base unifiée pour la gestion des produits (carburant et boutique) et de leurs stocks

6. **Module Immobilisations**
   - Fichier sprint: `sprint_immobilisations.md`
   - Fichier modèle de données: `modeles_de_donnees/immobilisations.md`
   - Justification: Nécessaire pour le bilan initial

7. **Module Stocks Initiaux**
   - Fichier sprint: `sprint_produits_et_stocks_complet.md`
   - Fichier modèle de données: `modeles_de_donnees/produits_et_stocks_complet.md`
   - Justification: Nécessaire pour le bilan initial

8. **Module Achats Carburant**
   - Fichier sprint: `sprint_achats_carburant.md`
   - Fichier modèle de données: `modeles_de_donnees/achats_carburant.md`
   - Justification: Suite logique à la gestion des stocks carburant

9. **Module Achats Boutique**
   - Fichier sprint: `sprint_achats_boutique.md`
   - Fichier modèle de données: `modeles_de_donnees/achats_boutique.md`
   - Justification: Suite logique à la gestion des stocks boutique

10. **Module Livraisons Carburant**
    - Fichier sprint: `sprint_livraisons_carburant.md`
    - Fichier modèle de données: `modeles_de_donnees/livraisons_carburant.md`
    - Justification: Suite logique à la gestion des stocks carburant

11. **Module Ventes Carburant**
    - Fichier sprint: `sprint_ventes_carburant.md`
    - Fichier modèle de données: `modeles_de_donnees/ventes_carburant.md`
    - Justification: Suite logique à la gestion des stocks carburant

12. **Module Ventes Boutique**
    - Fichier sprint: `sprint_ventes_boutique.md`
    - Fichier modèle de données: `modeles_de_donnees/ventes_boutique.md`
    - Justification: Suite logique à la gestion des stocks boutique

13. **Module Inventaires Carburant**
    - Fichier sprint: `sprint_inventaires_carburant.md`
    - Fichier modèle de données: `modeles_de_donnees/inventaires_carburant.md`
    - Justification: Suite logique à la gestion des stocks carburant

14. **Module Inventaires Boutique**
    - Fichier sprint: `sprint_inventaires_boutique.md`
    - Fichier modèle de données: `modeles_de_donnees/inventaires_boutique.md`
    - Justification: Suite logique à la gestion des stocks boutique

15. **Module Charges de Fonctionnement**
    - Fichier sprint: `sprint_charges_fonctionnement.md`
    - Fichier modèle de données: `modeles_de_donnees/charges_fonctionnement.md`
    - Justification: Suite logique aux trésoreries

16. **Module Salaires et Rémunérations**
    - Fichier sprint: `sprint_salaires_remunerations.md`
    - Fichier modèle de données: `modeles_de_donnees/salaires_remunerations.md`
    - Justification: Suite logique aux tiers employés

17. **Module Mouvements Financiers**
    - Fichier sprint: `sprint_mouvements_financiers.md`
    - Fichier modèle de données: `modeles_de_donnees/mouvements_financiers.md`
    - Justification: Suite logique aux tiers (clients et fournisseurs) et aux trésoreries

18. **Module États, Bilans et Comptabilité**
    - Fichier sprint: `sprint_etats_mouvements_bilans_comptabilite.md`
    - Fichier modèle de données: `modeles_de_donnees/etats_mouvements_bilans_comptabilite.md`
    - Justification: Module final pour la génération de rapports et de bilans à partir des autres modules