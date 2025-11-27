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
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_by UUID REFERENCES utilisateurs(id),
    est_valide BOOLEAN DEFAULT FALSE,
    valide_par UUID REFERENCES utilisateurs(id),
    date_validation TIMESTAMPTZ,
    type_document_origine VARCHAR(50),
    document_origine_id UUID,
    est_ouverture BOOLEAN DEFAULT FALSE,
    bilan_initial_id UUID REFERENCES bilan_initial(id)
);
```

#### 3.2.16 Table `journal_lines`
```sql
CREATE TABLE journal_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    compte_num VARCHAR(20),
    compte_id UUID REFERENCES plan_comptable(id),
    debit NUMERIC(18,2) DEFAULT 0 CHECK (debit >= 0),
    credit NUMERIC(18,2) DEFAULT 0 CHECK (credit >= 0),
    sens CHAR(1) CHECK (sens IN ('D','C')) GENERATED ALWAYS AS (
        CASE WHEN debit > credit THEN 'D' WHEN credit > debit THEN 'C' ELSE 'D' END
    ) STORED
);
```

#### 3.2.17 Table `achats`
```sql
CREATE TABLE achats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    date_achat DATE NOT NULL,
    total NUMERIC(18,2) NOT NULL CHECK (total >= 0),
    reference_facture VARCHAR(100),
    observation TEXT,
    type_achat VARCHAR(20) DEFAULT 'Produits' CHECK (type_achat IN ('Produits', 'Carburants')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'achat appartient
    pays_id UUID REFERENCES pays(id),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    journal_entry_id UUID,
    statut VARCHAR(40) DEFAULT 'En attente de livraison' CHECK (statut IN ('En attente de livraison', 'Livré','Annulé')) NOT NULL,
    date_livraison DATE, -- Nouveau champ pour la date de livraison
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.18 Table `bons_commande`
```sql
CREATE TABLE bons_commande (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_bon VARCHAR(50) UNIQUE NOT NULL,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    date_bon DATE NOT NULL,
    total NUMERIC(18,2) NOT NULL CHECK (total >= 0),
    observation TEXT,
    type_bon VARCHAR(20) DEFAULT 'Produits' CHECK (type_bon IN ('Produits', 'Carburants')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id),
    statut VARCHAR(40) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Livre', 'Facture', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### 3.2.19 Table `achats_stations`
```sql
CREATE TABLE achats_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(achat_id, station_id)  -- Empêche la duplication
);
```

#### 3.2.20 Table `achats_details`
```sql
CREATE TABLE achats_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    article_id UUID NOT NULL,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE, -- Ajout de la station
    cuve_id UUID REFERENCES cuves(id) ON DELETE SET NULL,     -- Ajout de la cuve pour les carburants
    quantite NUMERIC(18,3) NOT NULL CHECK (quantite >= 0),
    prix_unitaire NUMERIC(18,4) NOT NULL CHECK (prix_unitaire >= 0),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    montant NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED
);
```

#### 3.2.21 Table `dette_fournisseurs`
```sql
CREATE TABLE dettes_fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID NOT NULL REFERENCES fournisseurs(id),
    achat_id UUID NOT NULL REFERENCES achats(id),
    montant_achat NUMERIC(18,2) NOT NULL, -- Montant total (peut être négatif pour une créance)
    montant_paye NUMERIC(18,2) NOT NULL DEFAULT 0 CHECK (montant_paye >= 0), -- Montant déjà payé
    solde NUMERIC(18,2) NOT NULL, -- Solde restant (peut être négatif pour une créance)
    date_creation DATE NOT NULL DEFAULT CURRENT_DATE,
    reference_facture VARCHAR(100) NOT NULL,
    compagnie_id UUID NOT NULL REFERENCES compagnies(id),
    nb_jrs_creance INTEGER DEFAULT 0,
    date_prevu_paiement DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Paye', 'EnRetard', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. Gestion des Permissions et Types d'Utilisateurs

### 4.1 Types d'Utilisateurs
Le système distingue 4 types d'utilisateurs avec des droits d'accès spécifiques :

#### 4.1.1 Super Administrateur
- Accès complet à toutes les fonctionnalités du système
- Gestion globale du système
- Création et gestion des autres administrateurs
- Gestion des gérants de compagnie
- Surveillance complète des opérations
- Endpoint : administrateur

#### 4.1.2 Administrateur
- Accès selon les permissions définies par le super administrateur
- Gestion des aspects opérationnels selon ses permissions
- Supervision des stations selon ses droits
- Endpoint : administrateur

#### 4.1.3 Gérant de Compagnie
- Accès à toutes les opérations de sa propre compagnie (achats, ventes, stocks, trésorerie, comptabilité, etc.)
- Supervision de toutes les stations de sa compagnie
- Gestion des utilisateurs de sa compagnie
- Accès limité aux données de sa propre compagnie
- Endpoint : utilisateur

#### 4.1.4 Utilisateur de Compagnie
- Accès limité selon ses permissions spécifiques
- Opérations quotidiennes selon ses droits
- Responsabilité limitée à ses tâches assignées
- Endpoint : utilisateur

### 4.2 Gestion des Permissions
- Le système utilise un modèle RBAC (Role-Based Access Control)
- Pour les gérants de compagnie : attribution automatique de toutes les permissions fonctionnelles
- Pour les autres utilisateurs : permissions basées sur les profils et les associations profil-permission
- Filtrage des données selon la compagnie de l'utilisateur (champ `compagnie_id`)
- Le champ `stations_user` permet un filtrage plus fin au niveau des stations

### 4.3 Contrôles de Sécurité
- Validation hiérarchique selon le montant ou le type d'opération
- Journalisation des tentatives d'accès non autorisés
- Contrôle d'accès basé sur les rôles (RBAC)
- Séparation des endpoints administrateur et utilisateur
- Filtrage automatique des données selon la compagnie de l'utilisateur