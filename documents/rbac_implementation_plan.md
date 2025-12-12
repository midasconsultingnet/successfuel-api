# Plan d'implémentation du système RBAC

## Analyse des besoins et conception

### 1. Modules existants dans le système

1. **Module Utilisateurs et Authentification**
2. **Module Structure de la Compagnie**
3. **Module Tiers**
4. **Module Produits et Stocks Complet**
5. **Module Trésoreries**
6. **Module Achats Carburant**
7. **Module Achats Boutique**
8. **Module Ventes Carburant**
9. **Module Ventes Boutique**
10. **Module Livraisons Carburant**
11. **Module Inventaires Carburant**
12. **Module Inventaires Boutique**
13. **Module Mouvements Financiers**
14. **Module Salaires et Rémunérations**
15. **Module Charges de Fonctionnement**
16. **Module Immobilisations**
17. **Module États, Bilans et Comptabilité**

### 2. Profils types nécessaires

1. **Responsable boutique**
   - Modules associés : Produits et Stocks Complet, Achats Boutique, Ventes Boutique, Inventaires Boutique

2. **Responsable carburant**
   - Modules associés : Structure de la Compagnie, Achats Carburant, Ventes Carburant, Livraisons Carburant, Inventaires Carburant

3. **Responsable comptable**
   - Modules associés : Charges de Fonctionnement, Mouvements Financiers, Salaires et Rémunérations, États, Bilans et Comptabilité

4. **Gestionnaire de trésorerie**
   - Modules associés : Trésoreries, Mouvements Financiers, États, Bilans et Comptabilité

5. **Responsable immobilisation**
   - Modules associés : Immobilisations, États, Bilans et Comptabilité

6. **Gestionnaire de stock**
   - Modules associés : Produits et Stocks Complet, Inventaires Boutique, Inventaires Carburant

### 3. Définition des permissions

Chaque module autorisé via un profil donnera à l'utilisateur l'accès complet aux fonctionnalités de ce module (CRUD) selon les restrictions de station déjà en place.

### 4. Schémas de base de données pour les tables RBAC

#### Table Profils
```sql
CREATE TABLE profils (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    compagnie_id UUID NOT NULL REFERENCES compagnie(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(compagnie_id, nom)  -- Contrainte d'unicité pour le nom de profil par compagnie
);
```

#### Table Profil_Module
```sql
CREATE TABLE profil_module (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    module_nom VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profil_id, module_nom),
    -- Validation que le module_nom est dans la liste des modules valides
    CONSTRAINT check_module_nom CHECK (
        module_nom IN (
            'Module Utilisateurs et Authentification',
            'Module Structure de la Compagnie',
            'Module Tiers',
            'Module Produits et Stocks Complet',
            'Module Trésoreries',
            'Module Achats Carburant',
            'Module Achats Boutique',
            'Module Ventes Carburant',
            'Module Ventes Boutique',
            'Module Livraisons Carburant',
            'Module Inventaires Carburant',
            'Module Inventaires Boutique',
            'Module Mouvements Financiers',
            'Module Salaires et Rémunérations',
            'Module Charges de Fonctionnement',
            'Module Immobilisations',
            'Module États, Bilans et Comptabilité'
        )
    )
);
```

#### Table Utilisateur_Profil
```sql
CREATE TABLE utilisateur_profil (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id) ON DELETE CASCADE,
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    date_affectation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    utilisateur_affectation_id UUID NOT NULL REFERENCES utilisateur(id), -- utilisateur qui a fait l'affectation
    UNIQUE(utilisateur_id)  -- Un utilisateur ne peut avoir qu'un seul profil à la fois
);
```

#### Index nécessaires
```sql
-- Pour optimiser les requêtes d'autorisation
CREATE INDEX idx_profil_module_profil_id ON profil_module(profil_id);
CREATE INDEX idx_profil_module_module_nom ON profil_module(module_nom);
CREATE INDEX idx_utilisateur_profil_utilisateur_id ON utilisateur_profil(utilisateur_id);
CREATE INDEX idx_utilisateur_profil_profil_id ON utilisateur_profil(profil_id);
```