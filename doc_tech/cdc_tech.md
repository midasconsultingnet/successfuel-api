# Cahier des Charges Technique - SuccessFuel ERP (Mis à Jour)

## 1. Présentation du projet

**SuccessFuel** est un ERP (Enterprise Resource Planning) spécialement conçu pour la gestion complète des stations-service. Ce système informatisé permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

Le système est construit avec une architecture modulaire permettant son extension à d'autres pays africains francophones.

---

## 2. Architecture technique

### 2.1 Technologies utilisées
- **Backend**: PostgreSQL (base de données relationnelle)
- **Langage de requêtes**: SQL standard avec extensions PostgreSQL
- **Identifiants uniques**: UUID (Universally Unique Identifier)
- **Gestion des dates/heures**: TIMESTAMPTZ (avec fuseau horaire)
- **Stocker des données semi-structurées**: JSONB pour certaines données flexibles

### 2.2 Structure de base de données
- **Normalisation**: Respect des normes de normalisation relationnelle (3NF)
- **Clés primaires**: Utilisation d'UUID pour toutes les clés primaires
- **Clés étrangères**: Relations avec contraintes d'intégrité référentielle
- **Indexation**: Index appropriés pour les performances
- **Sécurité**: Contraintes de validation et de sécurité intégrées

### 2.3 Modèle de conception
- **Modèle Entité-Relation**: Relations claires entre les différentes entités
- **Normalisation**: Respect des principes de normalisation pour minimiser la redondance
- **Extensibilité**: Architecture modulaire permettant l'ajout de fonctionnalités

---

## 3. Structure détaillée des tables

### 3.1 Tables de base

#### 3.1.1 Table `pays`
```sql
CREATE TABLE pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_pays CHAR(3) UNIQUE NOT NULL, -- Ex: FRA, MDG, SEN, CIV
    nom_pays VARCHAR(100) NOT NULL,
    devise_principale VARCHAR(3) NOT NULL, -- Code ISO de la devise
    taux_tva_par_defaut NUMERIC(5,2) DEFAULT 0,
    systeme_comptable VARCHAR(50) DEFAULT 'OHADA', -- Ex: OHADA, FRANCE, etc.
    date_application_tva DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.2 Table `compagnies`
```sql
CREATE TABLE compagnies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    email VARCHAR(150),
    nif VARCHAR(50), -- Numéro d'identification fiscale
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    pays_id UUID REFERENCES pays(id),
    devise_principale VARCHAR(3) DEFAULT 'MGA',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.3 Table `modules`
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);
```

#### 3.1.4 Table `permissions`
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,        -- Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description TEXT,
    module_id UUID REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.5 Table `profils`
```sql
CREATE TABLE profils (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id) ON DELETE SET NULL,  -- La compagnie qui a créé le profil
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.6 Table `profil_permissions`
```sql
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(profil_id, permission_id)
);
```

#### 3.1.7 Table `stations`
```sql
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(30),
    email VARCHAR(150),
    adresse TEXT,
    pays_id UUID REFERENCES pays(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.8 Table `utilisateurs`
```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    nom VARCHAR(150) NOT NULL,
    profil_id UUID REFERENCES profils(id) ON DELETE SET NULL,
    email VARCHAR(150),
    telephone VARCHAR(30),
    stations_user JSONB DEFAULT '[]'::jsonb,  -- Liste des UUID des stations auxquelles l'utilisateur a accès
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    last_login TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id),
    type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.9 Table `auth_tokens`
```sql
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);
```

#### 3.1.10 Table `familles_articles`
```sql
CREATE TABLE familles_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la famille d'articles appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    parent_id UUID NULL REFERENCES familles_articles(id), -- Référence à la famille parente (NULL si racine)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.11 Table `plan_comptable`
```sql
CREATE TABLE plan_comptable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero VARCHAR(20) UNIQUE NOT NULL,           -- Numéro de compte comptable (ex: 100000)
    intitule VARCHAR(255) NOT NULL,               -- Nom du compte (ex: Capital & Réserves)
    classe VARCHAR(5) NOT NULL,                   -- Classe comptable (ex: 1, 2, etc.)
    type_compte VARCHAR(100) NOT NULL,            -- Type de compte (ex: Capitaux Propres)
    sens_solde VARCHAR(10) CHECK (sens_solde IN ('D', 'C')), -- Sens de solde
    compte_parent_id UUID REFERENCES plan_comptable(id) ON DELETE SET NULL, -- Lien vers le compte parent
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    est_compte_racine BOOLEAN DEFAULT FALSE,
    est_compte_de_resultat BOOLEAN DEFAULT FALSE,
    est_compte_actif BOOLEAN DEFAULT TRUE,
    pays_id UUID REFERENCES pays(id),
    est_specifique_pays BOOLEAN DEFAULT FALSE,
    code_pays VARCHAR(3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.12 Table `type_tiers`
```sql
CREATE TABLE type_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    num_compte VARCHAR(10),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'article appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.1.13 Table `articles`
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    codebarre VARCHAR(100) UNIQUE,
    famille_id UUID REFERENCES familles_articles(id) ON DELETE SET NULL,
    unite VARCHAR(20) DEFAULT 'Litre',
    unite_principale VARCHAR(10) REFERENCES unites_mesure(code_unite),
    unite_stock VARCHAR(10) REFERENCES unites_mesure(code_unite),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'article appartient
    type_article VARCHAR(20) DEFAULT 'produit' CHECK (type_article IN ('produit', 'service')),
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    tva NUMERIC(5,2) DEFAULT 0,
    taxes_applicables JSONB DEFAULT '[]'::jsonb, -- Liste des IDs de taxes
    stock_minimal NUMERIC(18,3) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.2 Tables fonctionnelles

#### 3.2.1 Table `carburants`
```sql
CREATE TABLE carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- Ex: "Essence", "Gasoil", "Pétrole"
    compagnie_id UUID REFERENCES compagnies(id),
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    qualite NUMERIC(3,2) DEFAULT 1.00, -- Note de qualité sur 10
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.2 Table `cuves`
```sql
CREATE TABLE cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL,
    capacite NUMERIC(18,3) NOT NULL CHECK (capacite >= 0),
    carburant_id UUID REFERENCES carburants(id) ON DELETE SET NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la cuve appartient (via la station)
    temperature NUMERIC(5,2) DEFAULT 0, -- Température pour correction volumétrique
    UNIQUE (station_id, code),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.3 Table `barremage_cuves`
```sql
CREATE TABLE barremage_cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    hauteur NUMERIC(18,3) NOT NULL CHECK (hauteur >= 0),
    volume NUMERIC(18,3) NOT NULL CHECK (volume >= 0),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    compagnie_id UUID REFERENCES compagnies(id)
);
```

#### 3.2.4 Table `pompes`
```sql
CREATE TABLE pompes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL UNIQUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.5 Table `pistolets`
```sql
CREATE TABLE pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) NOT NULL,
    pompe_id UUID REFERENCES pompes(id),
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    index_initiale NUMERIC(18,3) DEFAULT 0, -- Index initial du pistolet
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le pistolet appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.6 Table `historique_index_pistolets`
```sql
CREATE TABLE historique_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID REFERENCES pistolets(id),
    index_releve NUMERIC(18,3) NOT NULL,
    date_releve DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.7 Table `reinitialisation_index_pistolets`
```sql
CREATE TABLE reinitialisation_index_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID REFERENCES pistolets(id),
    ancien_index NUMERIC(18,3) NOT NULL,
    nouvel_index NUMERIC(18,3) NOT NULL,
    utilisateur_demande_id UUID REFERENCES utilisateurs(id),
    utilisateur_autorise_id UUID REFERENCES utilisateurs(id),
    motif TEXT NOT NULL,
    date_demande TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_autorisation TIMESTAMPTZ,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Approuve', 'Rejete', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.8 Table `clients`
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    nif VARCHAR(50),
    email VARCHAR(150),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le client appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle le client est rattaché
    type_tiers_id UUID REFERENCES type_tiers(id) ON DELETE SET NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    nb_jrs_creance INTEGER DEFAULT 0,
    solde_comptable NUMERIC(18,2) DEFAULT 0, -- Solde actuel du client
    solde_confirme NUMERIC(18,2) DEFAULT 0, -- Solde confirmé lors des rapprochements
    date_dernier_rapprochement TIMESTAMPTZ, -- Dernière date de rapprochement
    devise_facturation VARCHAR(3) DEFAULT 'MGA',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.9 Table `fournisseurs`
```sql
CREATE TABLE fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(30),
    nif VARCHAR(50),
    email VARCHAR(150),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le fournisseur appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle le fournisseur est rattaché
    type_tiers_id UUID REFERENCES type_tiers(id) ON DELETE SET NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    nb_jrs_creance INTEGER DEFAULT 0,
    solde_comptable NUMERIC(18,2) DEFAULT 0, -- Solde actuel du fournisseur
    solde_confirme NUMERIC(18,2) DEFAULT 0, -- Solde confirmé lors des rapprochements
    date_dernier_rapprochement TIMESTAMPTZ, -- Dernière date de rapprochement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.10 Table `employes`
```sql
CREATE TABLE employes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(150) NOT NULL,
    prenom VARCHAR(150),
    adresse TEXT,
    telephone VARCHAR(30),
    poste VARCHAR(100), -- Poste occupé (ex: pompiste, caissier, etc.)
    salaire_base NUMERIC(18,2) DEFAULT 0,
    avances NUMERIC(18,2) DEFAULT 0, -- Avances sur salaire
    creances NUMERIC(18,2) DEFAULT 0, -- Créances sur salaire
    station_ids JSONB DEFAULT '[]'::jsonb, -- Liste des stations auxquelles l'employé est rattaché
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'employé appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.11 Table `methode_paiment`
```sql
CREATE TABLE methode_paiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_tresorerie VARCHAR(100) NOT NULL,
    mode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) NOT NULL DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3.2.12 Table `tresoreries`
```sql
CREATE TABLE tresoreries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la trésorerie appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle la trésorerie est rattachée
    solde NUMERIC(18,2) DEFAULT 0 CHECK (solde >= -1000000000),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    type_tresorerie UUID REFERENCES methode_paiment(id),
    methode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    solde_theorique NUMERIC(18,2) DEFAULT 0,  -- Solde recalculé à partir des mouvements
    solde_reel NUMERIC(18,2) DEFAULT 0,        -- Solde réel vérifié (par exemple lors des rapprochements)
    date_dernier_rapprochement TIMESTAMPTZ,    -- Dernière date de rapprochement
    utilisateur_dernier_rapprochement UUID REFERENCES utilisateurs(id),  -- Utilisateur qui a effectué le dernier rapprochement
    type_tresorerie_libelle VARCHAR(50),      -- Pour identifier la caisse boutique/principale, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.13 Table `tickets_caisse`
```sql
CREATE TABLE tickets_caisse (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_ticket VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    caissier_id UUID REFERENCES utilisateurs(id),
    date_ticket DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME,
    montant_initial NUMERIC(18,2) DEFAULT 0,
    montant_final_theorique NUMERIC(18,2) DEFAULT 0,
    montant_final_reel NUMERIC(18,2) DEFAULT 0,
    ecart NUMERIC(18,2) DEFAULT 0, -- Différence entre théorique et réel
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'Ferme', 'Reconcilie')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.14 Table `arrets_compte_caissier`
```sql
CREATE TABLE arrets_compte_caissier (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_caisse_id UUID REFERENCES tickets_caisse(id),
    utilisateur_id UUID REFERENCES utilisateurs(id), -- L'utilisateur qui fait l'arrêt de compte
    date_arret DATE NOT NULL,
    heure_arret TIME NOT NULL,
    total_vente_especes NUMERIC(18,2) DEFAULT 0,
    total_vente_cb NUMERIC(18,2) DEFAULT 0,
    total_vente_chq NUMERIC(18,2) DEFAULT 0,
    total_vente_autre NUMERIC(18,2) DEFAULT 0,
    total_vente_credit NUMERIC(18,2) DEFAULT 0,
    total_vente_total NUMERIC(18,2) GENERATED ALWAYS AS (total_vente_especes + total_vente_cb + total_vente_chq + total_vente_autre + total_vente_credit) STORED,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.15 Table `journal_entries`
```sql
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_ecriture DATE NOT NULL,
    libelle TEXT NOT NULL,
    type_operation VARCHAR(30) CHECK (type_operation IN ('Achat','Vente','Tresorerie','Stock','Autre','Ouverture','Regul')) DEFAULT 'Autre',
    reference_operation VARCHAR(100),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'écriture appartient
    pays_id UUID REFERENCES pays(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.16 Table `journal_entry_lines`
```sql
CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    compte_comptable_id UUID REFERENCES plan_comptable(id), -- Compte concerné par l'écriture
    debit NUMERIC(18,2) DEFAULT 0,
    credit NUMERIC(18,2) DEFAULT 0,
    tiers_id UUID, -- Peut être un client, un fournisseur ou un autre tiers
    libelle TEXT, -- Libellé spécifique à la ligne d'écriture
    date_prevue_reglement DATE, -- Date prévue pour le règlement
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Reconcilie')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.17 Table `historique_prix_carburants`
```sql
CREATE TABLE historique_prix_carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID NOT NULL REFERENCES carburants(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.18 Table `historique_prix_articles`
```sql
CREATE TABLE historique_prix_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.19 Table `stocks_initial`
```sql
CREATE TABLE stocks_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id), -- Pour les carburants
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4) NOT NULL,
    date_releve DATE NOT NULL,
    station_id UUID REFERENCES stations(id),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le stock initial appartient
    type_stock VARCHAR(20) DEFAULT 'carburant' CHECK (type_stock IN ('carburant', 'boutique')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.20 Table `index_pistolets_initial`
```sql
CREATE TABLE index_pistolets_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pistolet_id UUID NOT NULL REFERENCES pistolets(id),
    index_initial NUMERIC(18,3) NOT NULL,
    date_releve DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'index initial appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.21 Table `achats`
```sql
CREATE TABLE achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    date_achat DATE NOT NULL,
    montant_total_ht NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_tva NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_total_ttc NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_paye NUMERIC(18,2) NOT NULL DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Valide', 'Regle', 'Partiellement_regle', 'Annule')) NOT NULL,
    reference VARCHAR(50) UNIQUE,
    description TEXT,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_validation TIMESTAMPTZ,
    date_regle DATE,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'achat appartient
    type_achat VARCHAR(20) DEFAULT 'carburant' CHECK (type_achat IN ('carburant', 'boutique'))
);
```

#### 3.2.22 Table `achat_items`
```sql
CREATE TABLE achat_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID NOT NULL REFERENCES achats(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_ht NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire_ht) STORED,
    montant_tva NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht * taux_tva / 100) STORED,
    montant_ttc NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht + montant_tva) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.23 Table `achats_livraison`
```sql
CREATE TABLE achats_livraison (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID NOT NULL REFERENCES achats(id) ON DELETE CASCADE,
    date_livraison DATE NOT NULL,
    mesures_avant JSONB NOT NULL, -- Format : [{"cuve_id": "uuid", "hauteur": 100.5, "temperature": 25.0}, ...]
    mesures_apres JSONB NOT NULL, -- Format : [{"cuve_id": "uuid", "hauteur": 150.2, "temperature": 25.5}, ...]
    ecart_total NUMERIC(18,3) DEFAULT 0, -- Différence en litres entre mesures avant et après
    ecart_acceptable NUMERIC(5,2) DEFAULT 0.5, -- Taux d'écart acceptable (en %)
    validite_ecart BOOLEAN DEFAULT FALSE, -- Indique si l'écart est dans les limites acceptables
    observation TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la livraison appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.24 Table `achats_reglements`
```sql
CREATE TABLE achats_reglements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID NOT NULL REFERENCES achats(id) ON DELETE CASCADE,
    mode_paiement VARCHAR(50), -- Espèces, Chèque, Virement, etc.
    montant NUMERIC(18,2) NOT NULL,
    date_reglement DATE NOT NULL,
    reference_paiement VARCHAR(100), -- Numéro de chèque, référence de virement, etc.
    utilisateur_id UUID REFERENCES utilisateurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le règlement appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.25 Table `ventes`
```sql
CREATE TABLE ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    date_vente DATE NOT NULL,
    heure_vente TIME NOT NULL,
    montant_total_ht NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_tva NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_total_ttc NUMERIC(18,2) NOT NULL DEFAULT 0,
    montant_paye NUMERIC(18,2) NOT NULL DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Valide', 'Regle', 'Partiellement_regle', 'Annule', 'Ecart_pompiste')) NOT NULL,
    reference VARCHAR(50) UNIQUE,
    description TEXT,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_validation TIMESTAMPTZ,
    date_regle DATE,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la vente appartient
    type_vente VARCHAR(20) DEFAULT 'carburant' CHECK (type_vente IN ('carburant', 'boutique', 'services')),
    Pompe_id UUID REFERENCES pistolets(id), -- Pompe utilisée pour la vente de carburant
    quantite_totale NUMERIC(18,3) DEFAULT 0 -- Quantité totale vendue pour la transaction
);
```

#### 3.2.26 Table `vente_items`
```sql
CREATE TABLE vente_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID NOT NULL REFERENCES ventes(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire_ht NUMERIC(18,4) NOT NULL,
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_ht NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire_ht) STORED,
    montant_tva NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht * taux_tva / 100) STORED,
    montant_ttc NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht + montant_tva) STORED,
    index_debut NUMERIC(18,3), -- Pour les ventes de carburant
    index_fin NUMERIC(18,3), -- Pour les ventes de carburant
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.27 Table `ventes_reglements`
```sql
CREATE TABLE ventes_reglements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID NOT NULL REFERENCES ventes(id) ON DELETE CASCADE,
    mode_paiement VARCHAR(50), -- Espèces, Chèque, Virement, Carte bancaire, etc.
    montant NUMERIC(18,2) NOT NULL,
    date_reglement DATE NOT NULL,
    reference_paiement VARCHAR(100), -- Numéro de transaction, référence de virement, etc.
    utilisateur_id UUID REFERENCES utilisateurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le règlement appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.28 Table `inventaires`
```sql
CREATE TABLE inventaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date_inventaire DATE NOT NULL,
    type_inventaire VARCHAR(20) DEFAULT 'boutique' CHECK (type_inventaire IN ('carburant', 'boutique')) NOT NULL,
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Reconcilie')) NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'inventaire appartient
    observation TEXT,
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_fin TIMESTAMPTZ
);
```

#### 3.2.29 Table `inventaire_items`
```sql
CREATE TABLE inventaire_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventaire_id UUID NOT NULL REFERENCES inventaires(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id), -- Pour les inventaires carburants
    quantite_theorique NUMERIC(18,3) NOT NULL, -- Quantité selon le système
    quantite_reelle NUMERIC(18,3) NOT NULL, -- Quantité mesurée dans la réalité
    ecart NUMERIC(18,3) GENERATED ALWAYS AS (quantite_reelle - quantite_theorique) STORED,
    unite VARCHAR(20) DEFAULT 'Litre',
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'item d'inventaire appartient
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.30 Table `mouvements_stock`
```sql
CREATE TABLE mouvements_stock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('entree', 'sortie', 'ajustement', 'inventaire')),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4), -- Prix unitaire au moment du mouvement
    montant_total NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    date_mouvement DATE NOT NULL,
    reference_operation UUID, -- ID de l'opération liée (achat, vente, etc.)
    type_operation VARCHAR(20), -- Type de l'opération liée
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le mouvement appartient
    observation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.31 Table `depenses`
```sql
CREATE TABLE depenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    categorie VARCHAR(100) NOT NULL, -- Ex: entretien, salaire, loyer, etc.
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_depense DATE NOT NULL,
    mode_paiement VARCHAR(50), -- Espèces, Chèque, Virement, etc.
    statut VARCHAR(20) DEFAULT 'Non paye' CHECK (statut IN ('Paye', 'Non paye', 'En attente', 'Regle')) NOT NULL,
    reference VARCHAR(50),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la dépense appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.32 Table `paiement_salaires`
```sql
CREATE TABLE paiement_salaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employe_id UUID NOT NULL REFERENCES employes(id),
    mois_paiement INTEGER NOT NULL, -- Mois (1-12)
    annee_paiement INTEGER NOT NULL, -- Année
    salaire_base NUMERIC(18,2) NOT NULL,
    avances NUMERIC(18,2) DEFAULT 0, -- Avances déjà données
    creances NUMERIC(18,2) DEFAULT 0, -- Créances sur salaire
    autres_deductions NUMERIC(18,2) DEFAULT 0, -- Autres déductions
    net_a_payer NUMERIC(18,2) GENERATED ALWAYS AS (salaire_base - avances - creances - autres_deductions) STORED,
    date_paiement DATE,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Paye', 'Retarde', 'Annule')) NOT NULL,
    utilisateur_paie_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui effectue le paiement
    tresorerie_id UUID REFERENCES tresoreries(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le paiement de salaire appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.33 Table `immobilisations`
```sql
CREATE TABLE immobilisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(30) UNIQUE NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL, -- Ex: matériel, équipement, véhicule
    date_acquisition DATE NOT NULL,
    valeur_acquisition NUMERIC(18,2) NOT NULL,
    valeur_nette NUMERIC(18,2) NOT NULL,
    duree_vie INTEGER NOT NULL, -- Durée de vie en années
    taux_amortissement NUMERIC(5,2) NOT NULL,
    date_mise_en_service DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'En maintenance', 'Vendu', 'Hors service')) NOT NULL,
    description TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'immobilisation appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.34 Table `mouvements_tresorerie`
```sql
CREATE TABLE mouvements_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tresorerie_id UUID NOT NULL REFERENCES tresoreries(id),
    type_mouvement VARCHAR(10) NOT NULL CHECK (type_mouvement IN ('entree', 'sortie')),
    montant NUMERIC(18,2) NOT NULL,
    date_mouvement DATE NOT NULL,
    libelle TEXT NOT NULL,
    reference_operation VARCHAR(100), -- Référence de l'opération liée (achat, vente, etc.)
    utilisateur_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Annule')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le mouvement appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.35 Table `ajustement_stocks`
```sql
CREATE TABLE ajustement_stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id),
    type_ajustement VARCHAR(20) NOT NULL CHECK (type_ajustement IN ('entree', 'sortie')), -- Entrée ou Sortie
    quantite_ajustee NUMERIC(18,3) NOT NULL,
    motif TEXT NOT NULL, -- Explication de l'ajustement
    date_ajustement DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'ajustement appartient
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.36 Table `depots_garantie`
```sql
CREATE TABLE depots_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    montant_depot NUMERIC(18,2) NOT NULL,
    date_depot DATE NOT NULL,
    date_utilisation DATE, -- Date d'utilisation du dépôt
    date_remboursement DATE, -- Date de remboursement du dépôt
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Utilise', 'Rembourse', 'Partiellement_rembourse')) NOT NULL,
    motif_utilisation TEXT, -- Raison de l'utilisation
    montant_utilise NUMERIC(18,2) DEFAULT 0, -- Montant déjà utilisé
    montant_rembourse NUMERIC(18,2) DEFAULT 0, -- Montant déjà remboursé
    utilisateur_depot_id UUID REFERENCES utilisateurs(id),
    utilisateur_utilisation_id UUID REFERENCES utilisateurs(id),
    utilisateur_remboursement_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le dépôt appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.3 Tables de rapprochement et validation

#### 3.3.1 Table `rapprochements_bancaires`
```sql
CREATE TABLE rapprochements_bancaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tresorerie_id UUID NOT NULL REFERENCES tresoreries(id),
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    solde_initial NUMERIC(18,2) NOT NULL,
    solde_final_theorique NUMERIC(18,2) NOT NULL,
    solde_final_reel NUMERIC(18,2) NOT NULL,
    ecart_total NUMERIC(18,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Reconcilie')) NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le rapprochement appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.2 Table `rapprochement_items`
```sql
CREATE TABLE rapprochement_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapprochement_id UUID NOT NULL REFERENCES rapprochements_bancaires(id) ON DELETE CASCADE,
    mouvement_id UUID, -- ID du mouvement de trésorerie
    type_mouvement VARCHAR(10) CHECK (type_mouvement IN ('entree', 'sortie')),
    montant_mouvement NUMERIC(18,2) NOT NULL,
    date_mouvement DATE NOT NULL,
    reference_mouvement VARCHAR(100),
    rapproche BOOLEAN DEFAULT FALSE,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'item de rapprochement appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.3 Table `validations_hierarchiques`
```sql
CREATE TABLE validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entite_type VARCHAR(50) NOT NULL, -- Type d'entité à valider (ex: "achat", "vente", "depense")
    entite_id UUID NOT NULL, -- ID de l'entité à valider
    utilisateur_demande_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a demandé l'opération
    utilisateur_validation_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a validé
    niveau_validation INTEGER NOT NULL, -- Niveau de validation requis
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Valide', 'Rejete', 'Annule')) NOT NULL,
    motif_rejet TEXT,
    commentaire TEXT,
    date_demande TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_validation TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la validation appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.3.4 Table `journaux_operations`
```sql
CREATE TABLE journaux_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id),
    type_operation VARCHAR(50) NOT NULL, -- Ex: "login", "create_vente", "update_client", etc.
    entite_type VARCHAR(50), -- Type d'entité concernée
    entite_id UUID, -- ID de l'entité concernée
    ancienne_valeur JSONB, -- Valeur avant modification (si applicable)
    nouvelle_valeur JSONB, -- Valeur après modification (si applicable)
    ip_address VARCHAR(45), -- Adresse IP de l'utilisateur
    user_agent TEXT, -- Navigateur/agent utilisateur
    statut_operation VARCHAR(20) DEFAULT 'Reussi' CHECK (statut_operation IN ('Reussi', 'Echec', 'Erreur')) NOT NULL,
    description TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle le journal appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.4 Tables pour indicateurs de performance

#### 3.4.1 Table `indicateurs_performance`
```sql
CREATE TABLE indicateurs_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicateur_code VARCHAR(50) NOT NULL, -- Ex: "litres_vendus", "marge_brute", "rendement_pompiste"
    indicateur_libelle VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL, -- Ex: "commercial", "operational", "financier"
    unite_mesure VARCHAR(20) DEFAULT '', -- Ex: "litres", "%", "MGA"
    formule_calcul TEXT, -- Formule de calcul de l'indicateur
    periode_calcul VARCHAR(20) DEFAULT 'mensuel' CHECK (periode_calcul IN ('journalier', 'hebdomadaire', 'mensuel', 'trimestriel', 'annuel')),
    active BOOLEAN DEFAULT TRUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'indicateur appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.4.2 Table `valeurs_indicateurs`
```sql
CREATE TABLE valeurs_indicateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicateur_id UUID NOT NULL REFERENCES indicateurs_performance(id) ON DELETE CASCADE,
    valeur NUMERIC(18,4) NOT NULL,
    date_valeur DATE NOT NULL, -- Date de calcul de la valeur
    periode_debut DATE, -- Si c'est une période, date de début
    periode_fin DATE, -- Si c'est une période, date de fin
    utilisateur_calcul_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a déclenché le calcul
    statut_calcul VARCHAR(20) DEFAULT 'Calcule' CHECK (statut_calcul IN ('Calcule', 'En cours', 'Echec')),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la valeur appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.5 Tables de configuration

#### 3.5.1 Table `configurations_systeme`
```sql
CREATE TABLE configurations_systeme (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cle_config VARCHAR(100) UNIQUE NOT NULL, -- Clé de configuration (ex: "seuil_alerte_stock", "taux_ecart_acceptable")
    valeur_config TEXT NOT NULL, -- Valeur de configuration
    type_valeur VARCHAR(20) DEFAULT 'texte' CHECK (type_valeur IN ('texte', 'nombre', 'booleen', 'json')), -- Type de la valeur
    description TEXT, -- Description de la configuration
    categorie VARCHAR(50), -- Catégorie de configuration (ex: "securite", "stock", "finance")
    active BOOLEAN DEFAULT TRUE,
    date_modification TIMESTAMPTZ NOT NULL DEFAULT now(),
    utilisateur_modification_id UUID REFERENCES utilisateurs(id) -- Utilisateur qui a modifié la configuration
);
```

#### 3.5.2 Table `unites_mesure`
```sql
CREATE TABLE unites_mesure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_unite VARCHAR(10) UNIQUE NOT NULL, -- Ex: L, KG, TONNE, M3
    libelle_unite VARCHAR(50) NOT NULL, -- Ex: Litre, Kilogramme, Tonne, Mètre cube
    categorie VARCHAR(30) NOT NULL, -- Ex: volume, poids, longueur
    est_principale BOOLEAN DEFAULT FALSE, -- Indique si c'est l'unité principale de la catégorie
    taux_conversion NUMERIC(10,6) DEFAULT 1.000000, -- Taux de conversion par rapport à l'unité principale
    unite_reference VARCHAR(10), -- Référence à l'unité principale de conversion
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 4. Relations entre les tables

### 4.1 Relations de base
- `pays.id` → `compagnies.pays_id` (One-to-Many)
- `compagnies.id` → `stations.compagnie_id` (One-to-Many)
- `compagnies.id` → `utilisateurs.compagnie_id` (One-to-Many)
- `pays.id` → `journal_entries.pays_id` (One-to-Many)
- `pays.id` → `plan_comptable.pays_id` (One-to-Many)
- `compagnies.id` → `articles.compagnie_id` (One-to-Many)
- `familles_articles.id` → `articles.famille_id` (One-to-Many)
- `compagnies.id` → `familles_articles.compagnie_id` (One-to-Many)

### 4.2 Relations de sécurité et permissions
- `modules.id` → `permissions.module_id` (One-to-Many)
- `permissions.id` → `profil_permissions.permission_id` (One-to-Many)
- `profils.id` → `profil_permissions.profil_id` (One-to-Many)
- `profils.id` → `utilisateurs.profil_id` (One-to-Many)
- `utilisateurs.id` → `auth_tokens.user_id` (One-to-Many)

### 4.3 Relations fonctionnelles
- `stations.id` → `cuves.station_id` (One-to-Many)
- `carburants.id` → `cuves.carburant_id` (One-to-Many)
- `compagnies.id` → `cuves.compagnie_id` (One-to-Many)
- `cuves.id` → `barremage_cuves.cuve_id` (One-to-Many)
- `stations.id` → `barremage_cuves.station_id` (One-to-Many)
- `compagnies.id` → `barremage_cuves.compagnie_id` (One-to-Many)
- `stations.id` → `pompes.station_id` (One-to-Many)
- `compagnies.id` → `pompes.compagnie_id` (One-to-Many)
- `pompes.id` → `pistolets.pompe_id` (One-to-Many)
- `cuves.id` → `pistolets.cuve_id` (One-to-Many)
- `compagnies.id` → `pistolets.compagnie_id` (One-to-Many)
- `pistolets.id` → `historique_index_pistolets.pistolet_id` (One-to-Many)
- `utilisateurs.id` → `historique_index_pistolets.utilisateur_id` (One-to-Many)
- `pistolets.id` → `reinitialisation_index_pistolets.pistolet_id` (One-to-Many)
- `utilisateurs.id` → `reinitialisation_index_pistolets.utilisateur_demande_id` (One-to-Many)
- `utilisateurs.id` → `reinitialisation_index_pistolets.utilisateur_autorise_id` (One-to-Many)

### 4.4 Relations clients/fournisseurs/employés
- `compagnies.id` → `clients.compagnie_id` (One-to-Many)
- `type_tiers.id` → `clients.type_tiers_id` (One-to-Many)
- `compagnies.id` → `fournisseurs.compagnie_id` (One-to-Many)
- `type_tiers.id` → `fournisseurs.type_tiers_id` (One-to-Many)
- `compagnies.id` → `employes.compagnie_id` (One-to-Many)
- `compagnies.id` → `tresoreries.compagnie_id` (One-to-Many)
- `fournisseurs.id` → `tresoreries.fournisseur_id` (One-to-Many)
- `methode_paiment.id` → `tresoreries.type_tresorerie` (One-to-Many)
- `utilisateurs.id` → `tresoreries.utilisateur_dernier_rapprochement` (One-to-Many)

### 4.5 Relations des ventes/achats
- `clients.id` → `ventes.client_id` (One-to-Many)
- `utilisateurs.id` → `ventes.utilisateur_id` (One-to-Many)
- `pistolets.id` → `ventes.Pompe_id` (One-to-Many)
- `compagnies.id` → `ventes.compagnie_id` (One-to-Many)
- `ventes.id` → `vente_items.vente_id` (One-to-Many)
- `articles.id` → `vente_items.article_id` (One-to-Many)
- `ventes.id` → `ventes_reglements.vente_id` (One-to-Many)
- `utilisateurs.id` → `ventes_reglements.utilisateur_id` (One-to-Many)
- `tresoreries.id` → `ventes_reglements.tresorerie_id` (One-to-Many)
- `compagnies.id` → `ventes_reglements.compagnie_id` (One-to-Many)

### 4.6 Relations d'inventaire et de stock
- `inventaires.id` → `inventaire_items.inventaire_id` (One-to-Many)
- `articles.id` → `inventaire_items.article_id` (One-to-Many)
- `cuves.id` → `inventaire_items.cuve_id` (One-to-Many)
- `compagnies.id` → `inventaire_items.compagnie_id` (One-to-Many)
- `articles.id` → `mouvements_stock.article_id` (One-to-Many)
- `utilisateurs.id` → `mouvements_stock.utilisateur_id` (One-to-Many)
- `compagnies.id` → `mouvements_stock.compagnie_id` (One-to-Many)

### 4.7 Relations de trésorerie
- `tresoreries.id` → `mouvements_tresorerie.tresorerie_id` (One-to-Many)
- `utilisateurs.id` → `mouvements_tresorerie.utilisateur_id` (One-to-Many)
- `compagnies.id` → `mouvements_tresorerie.compagnie_id` (One-to-Many)

### 4.8 Relations de comptabilité
- `plan_comptable.id` → `journal_entry_lines.compte_comptable_id` (One-to-Many)
- `journal_entries.id` → `journal_entry_lines.journal_entry_id` (One-to-Many)
- `compagnies.id` → `journal_entries.compagnie_id` (One-to-Many)

---

## 5. Contraintes d'intégrité

### 5.1 Contraintes fonctionnelles
- Toutes les tables avec des montants doivent avoir des contraintes de validation pour s'assurer que les valeurs sont positives
- Les relations entre entités respectent les contraintes d'intégrité référentielle
- Les champs `created_at` et `updated_at` sont automatiquement gérés par des triggers

### 5.2 Contraintes de sécurité
- Toutes les tables sensibles incluent un champ `compagnie_id` pour la séparation des données
- Les accès aux données sont filtrés par la compagnie de l'utilisateur connecté
- Le **gérant de compagnie** a automatiquement accès à toutes les fonctionnalités pour sa propre compagnie, mais ne peut effectuer des opérations que sur les données appartenant à sa propre compagnie
- Le **utilisateur de compagnie** a un accès limité selon ses permissions spécifiques

### 5.3 Contraintes d'audit
- Toutes les opérations critiques sont journalisées dans la table `journaux_operations`
- Les modifications de données sensibles sont tracées avec l'utilisateur, l'heure et la nature de la modification

---

## 6. Indexes pour les performances

### 6.1 Indexes de base
- `idx_stations_compagnie`: INDEX ON stations(compagnie_id)
- `idx_utilisateurs_compagnie`: INDEX ON utilisateurs(compagnie_id)
- `idx_articles_compagnie`: INDEX ON articles(compagnie_id)
- `idx_ventes_compagnie`: INDEX ON ventes(compagnie_id)
- `idx_achats_compagnie`: INDEX ON achats(compagnie_id)
- `idx_clients_compagnie`: INDEX ON clients(compagnie_id)
- `idx_fournisseurs_compagnie`: INDEX ON fournisseurs(compagnie_id)

### 6.2 Indexes fonctionnels
- `idx_ventes_date`: INDEX ON ventes(date_vente)
- `idx_achats_date`: INDEX ON achats(date_achat)
- `idx_inventaire_date`: INDEX ON inventaires(date_inventaire)
- `idx_mouvements_date`: INDEX ON mouvements_stock(date_mouvement)
- `idx_journal_date`: INDEX ON journal_entries(date_ecriture)

### 6.3 Indexes de recherche
- `idx_articles_code`: INDEX ON articles(code)
- `idx_clients_code`: INDEX ON clients(code)
- `idx_fournisseurs_code`: INDEX ON fournisseurs(code)
- `idx_utilisateurs_login`: INDEX ON utilisateurs(login)
- `idx_stations_code`: INDEX ON stations(code)
- `idx_compagnies_code`: INDEX ON compagnies(code)

---

## 7. Triggers et procédures

### 7.1 Triggers de mise à jour
```sql
-- Trigger pour mettre à jour le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stations_updated_at
    BEFORE UPDATE ON stations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_carburants_updated_at
    BEFORE UPDATE ON carburants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_fournisseurs_updated_at
    BEFORE UPDATE ON fournisseurs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_employes_updated_at
    BEFORE UPDATE ON employes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_tresoreries_updated_at
    BEFORE UPDATE ON tresoreries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_plan_comptable_updated_at
    BEFORE UPDATE ON plan_comptable
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 7.2 Triggers de validation
```sql
-- Trigger pour valider les écritures comptables
CREATE OR REPLACE FUNCTION validate_journal_entry()
RETURNS TRIGGER AS $$
DECLARE
    total_debit NUMERIC(18,2);
    total_credit NUMERIC(18,2);
BEGIN
    -- Calcul des totaux de débit et crédit pour l'écriture
    SELECT COALESCE(SUM(debit), 0), COALESCE(SUM(credit), 0)
    INTO total_debit, total_credit
    FROM journal_entry_lines
    WHERE journal_entry_id = NEW.id;

    -- Vérification de l'équilibre de l'écriture
    IF ABS(total_debit - total_credit) > 0.01 THEN  -- Tolérance de 0.01 pour les arrondis
        RAISE EXCEPTION 'L''écriture comptable n''est pas équilibrée. Debit: %, Credit: %', total_debit, total_credit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_journal_entry
    AFTER INSERT OR UPDATE ON journal_entries
    FOR EACH ROW
    EXECUTE FUNCTION validate_journal_entry();
```

---

## 8. Sécurité et permissions

### 8.1 Gestion des permissions
- Le système de permissions RBAC (Role-Based Access Control) est implémenté pour gérer les accès
- Les utilisateurs sont classifiés en 4 types : super_administrateur, administrateur, gerant_compagnie, utilisateur_compagnie
- Chaque type d'utilisateur a des permissions spécifiques selon son rôle
- Le **gérant de compagnie** a automatiquement accès à toutes les fonctionnalités mais seulement pour les données de sa propre compagnie
- Les données sont filtrées automatiquement selon la compagnie de l'utilisateur
- Les endpoints sont séparés pour administrateurs et utilisateurs standards