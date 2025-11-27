-- succes_fuel_bdd.sql
-- Fichier de la base de données pour l'ERP SuccessFuel
-- Organisé dans l'ordre de création correct des tables pour éviter les erreurs de dépendance

-- Activer l'extension UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) Tables de base sans dépendances
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

CREATE TABLE unites_mesure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_unite VARCHAR(10) UNIQUE NOT NULL, -- 'L', 'GAL', 'KG', 'TON', etc.
    libelle_unite VARCHAR(50) NOT NULL,
    pays_id UUID REFERENCES pays(id), -- Unités spécifiques à un pays
    est_standard BOOLEAN DEFAULT FALSE, -- Unité standard internationale
    est_utilisee BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

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

CREATE TABLE type_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    num_compte VARCHAR(10),
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle l'article appartient
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) Tables dépendant des tables de base
CREATE TABLE specifications_locales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES pays(id),
    type_specification VARCHAR(50) NOT NULL, -- 'taxe', 'reglementation', 'comptabilite', etc.
    code_specification VARCHAR(50) NOT NULL, -- 'tva', 'timbre', 'cnaps', etc.
    libelle_specification VARCHAR(200) NOT NULL,
    valeur_specification VARCHAR(200), -- Valeur textuelle (ex: 18% ou "Obligatoire")
    taux_specification NUMERIC(10,4), -- Pour les taux (ex: 18.0000%)
    est_actif BOOLEAN DEFAULT TRUE,
    date_debut_validite DATE,
    date_fin_validite DATE,
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE configurations_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES pays(id),
    cle_configuration VARCHAR(100) NOT NULL, -- 'format_date', 'format_numero_facture', etc.
    valeur_configuration TEXT NOT NULL, -- Valeur de la configuration
    description TEXT,
    est_systeme BOOLEAN DEFAULT FALSE, -- TRUE si c'est une configuration système
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE methode_paiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_tresorerie VARCHAR(100) NOT NULL,
    mode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) NOT NULL DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tresoreries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la trésorerie appartient
    station_ids JSONB DEFAULT '[]'::jsonb, -- Optionnel : station à laquelle la trésorerie est rattachée
    solde NUMERIC(18,2) DEFAULT 0 CHECK (solde >= -1000000000),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL, -- ATTENTION : dépendance circulaire - sera ajustée plus tard
    type_tresorerie UUID REFERENCES methode_paiment(id),
    methode_paiement JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    solde_theorique NUMERIC(18,2) DEFAULT 0,  -- Solde recalculé à partir des mouvements
    solde_reel NUMERIC(18,2) DEFAULT 0,        -- Solde réel vérifié (par exemple lors des rapprochements)
    date_dernier_rapprochement TIMESTAMPTZ,    -- Dernière date de rapprochement
    utilisateur_dernier_rapprochement UUID REFERENCES utilisateurs(id),  -- ATTENTION : dépendance circulaire - sera ajustée plus tard
    type_tresorerie_libelle VARCHAR(50),      -- Pour identifier la caisse boutique/principale, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) Tables dépendant des tables précédentes
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

CREATE TABLE pompes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL UNIQUE,
    compagnie_id UUID REFERENCES compagnies(id), -- Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE types_taxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_taxe VARCHAR(20) UNIQUE NOT NULL,
    libelle_taxe VARCHAR(100) NOT NULL,
    description TEXT,
    pays_id UUID REFERENCES pays(id),
    taux_par_defaut NUMERIC(5,2) DEFAULT 0,
    type_calcul VARCHAR(20) NOT NULL CHECK (type_calcul IN ('fixe', 'pourcentage', 'tranche')), -- Calcul de la taxe
    compte_comptable VARCHAR(20) REFERENCES plan_comptable(numero), -- Compte de taxe
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,        -- Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description TEXT,
    module_id UUID REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE tranches_taxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_taxe_id UUID REFERENCES types_taxes(id),
    borne_inferieure NUMERIC(18,2) DEFAULT 0,
    borne_superieure NUMERIC(18,2),
    taux NUMERIC(5,2) NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4) Tables nécessitant la table 'utilisateurs' - doit être créé après 'utilisateurs'
-- (Nous créons d'abord 'utilisateurs' pour résoudre les dépendances)
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

-- Maintenant que 'utilisateurs' est créée, nous pouvons créer les tables qui en dépendent
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

CREATE TABLE conversions_unite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unite_origine_id UUID REFERENCES unites_mesure(id),
    unite_destination_id UUID REFERENCES unites_mesure(id),
    facteur_conversion NUMERIC(15,6) NOT NULL, -- Facteur pour convertir d'une unité à l'autre
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5) Tables dépendant de 'utilisateurs'
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);

CREATE TABLE tentatives_connexion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL,
    ip_connexion VARCHAR(45),
    resultat_connexion VARCHAR(10) CHECK (resultat_connexion IN ('Reussie', 'Echouee')),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evenements_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_evenement VARCHAR(50) NOT NULL, -- 'connexion_anormale', 'tentative_acces_non_autorise', etc.
    description TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    donnees_supplementaires JSONB,
    statut VARCHAR(20) DEFAULT 'NonTraite' CHECK (statut IN ('NonTraite', 'EnCours', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE modifications_sensibles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    type_operation VARCHAR(50) NOT NULL, -- 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    objet_modifie VARCHAR(50), -- 'vente', 'stock', 'achat', etc.
    objet_id UUID,
    ancienne_valeur JSONB,
    nouvelle_valeur JSONB,
    seuil_alerte BOOLEAN DEFAULT FALSE, -- TRUE si dépasse un seuil défini
    commentaire TEXT,
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    statut VARCHAR(20) DEFAULT 'Enregistre' CHECK (statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE politiques_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom_politique VARCHAR(100) NOT NULL,
    description TEXT,
    type_politique VARCHAR(50) NOT NULL, -- 'mot_de_passe', 'connexion', 'acces_donnees', etc.
    valeur_parametre VARCHAR(200),
    seuil_valeur INTEGER,
    est_actif BOOLEAN DEFAULT TRUE,
    commentaire TEXT,
    utilisateur_config_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a configuré la politique
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historique_prix_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historique_prix_carburants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID NOT NULL REFERENCES carburants(id) ON DELETE CASCADE,
    prix_achat NUMERIC(18,4) DEFAULT 0,
    prix_vente NUMERIC(18,4) DEFAULT 0,
    date_application DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    date_bilan_initial DATE NOT NULL,
    est_valide BOOLEAN DEFAULT FALSE,
    est_verifie BOOLEAN DEFAULT FALSE,
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ecarts_soldes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiers_type VARCHAR(20) CHECK (tiers_type IN ('Client', 'Fournisseur')),
    tiers_id UUID,
    solde_fiche NUMERIC(18,2),
    solde_reel NUMERIC(18,2),
    ecart NUMERIC(18,2) GENERATED ALWAYS AS (solde_fiche - solde_reel) STORED,
    statut VARCHAR(20) DEFAULT 'Identifie' CHECK (statut IN ('Identifie', 'Enquete', 'Corrige', 'Rejete')),
    utilisateur_detecte_id UUID REFERENCES utilisateurs(id),
    utilisateur_traite_id UUID REFERENCES utilisateurs(id),
    date_detection TIMESTAMPTZ DEFAULT now(),
    date_traitement TIMESTAMPTZ,
    motif TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6) Tables avec dépendances multiples
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(profil_id, permission_id)
);

CREATE TABLE taux_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devise_source VARCHAR(3) NOT NULL,
    devise_cible VARCHAR(3) NOT NULL,
    taux NUMERIC(15,6) NOT NULL, -- Précision pour les taux de change
    date_application DATE NOT NULL,
    heure_application TIME DEFAULT CURRENT_TIME,
    est_actuel BOOLEAN DEFAULT FALSE, -- Indique si c'est le taux en cours
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

CREATE TABLE achats_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(achat_id, station_id)  -- Empêche la duplication
);

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

CREATE TABLE achats_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    tresorerie_id UUID REFERENCES tresoreries(id) ON DELETE SET NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    note_paiement JSONB DEFAULT '{}',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE mesures_livraison (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    achat_id UUID REFERENCES achats(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    mesure_avant_livraison NUMERIC(18,3) NOT NULL,
    mesure_apres_livraison NUMERIC(18,3) NOT NULL,
    ecart_livraison NUMERIC(18,3) GENERATED ALWAYS AS (mesure_apres_livraison - mesure_avant_livraison) STORED,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE, -- Pour les carburants
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    stock_theorique NUMERIC(18,3) DEFAULT 0 CHECK (stock_theorique >= 0),
    stock_reel NUMERIC(18,3) DEFAULT 0 CHECK (stock_reel >= 0),
    ecart_stock NUMERIC(18,3) GENERATED ALWAYS AS (stock_reel - stock_theorique) STORED,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    est_initial BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE stocks_mouvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Entree', 'Sortie', 'Ajustement', 'Inventaire', 'Initial')),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4) DEFAULT 0, -- Pour calcul CUMP
    cout_total NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    date_mouvement DATE NOT NULL,
    reference_operation VARCHAR(100), -- Référence à l'opération d'origine
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    valeur_stock_avant NUMERIC(18,2) DEFAULT 0,  -- Valeur du stock avant le mouvement
    valeur_stock_apres NUMERIC(18,2) DEFAULT 0,  -- Valeur du stock après le mouvement
    cout_unitaire_moyen_apres NUMERIC(18,4) DEFAULT 0, -- CUMP après le mouvement
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE mouvements_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tresorerie_id UUID REFERENCES tresoreries(id),
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Entree', 'Sortie', 'Annulation', 'Correction')),
    sous_type_mouvement VARCHAR(30) NOT NULL, -- 'Vente_carburant', 'Vente_boutique', 'Achat', 'Depense', etc.
    montant NUMERIC(18,2) NOT NULL,
    reference_operation VARCHAR(100), -- ID de l'opération source
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    date_mouvement DATE NOT NULL,
    date_enregistrement TIMESTAMPTZ NOT NULL DEFAULT now(),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Annule', 'Corrige', 'EnAttente')),
    mouvement_origine_id UUID REFERENCES mouvements_tresorerie(id), -- Pour les annulations
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    CHECK ((type_mouvement = 'Annulation' AND mouvement_origine_id IS NOT NULL) OR (type_mouvement != 'Annulation'))
);

CREATE TABLE ventes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    date_vente DATE NOT NULL,
    total_ht NUMERIC(18,2) NOT NULL CHECK (total_ht >= 0),
    total_ttc NUMERIC(18,2) NOT NULL CHECK (total_ttc >= 0),
    total_tva NUMERIC(18,2) NOT NULL CHECK (total_tva >= 0),
    reference_facture VARCHAR(100),
    observation TEXT,
    type_vente VARCHAR(20) DEFAULT 'Boutique' CHECK (type_vente IN ('Carburant', 'Boutique', 'Service')) NOT NULL,
    type_transaction VARCHAR(20) DEFAULT 'General' CHECK (type_transaction IN ('General', 'Boutique', 'Station', 'Carburant')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    pays_id UUID REFERENCES pays(id),
    devise_code VARCHAR(3) DEFAULT 'MGA',
    taux_change NUMERIC(15,6) DEFAULT 1.000000,
    journal_entry_id UUID,
    statut VARCHAR(20) DEFAULT 'Valide' CHECK (statut IN ('Valide', 'Retour', 'Annule')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ventes_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL,
    pistolet_id UUID REFERENCES pistolets(id) ON DELETE SET NULL, -- Pour les ventes de carburant
    index_debut NUMERIC(18,3), -- Index de début pour le carburant
    index_fin NUMERIC(18,3),   -- Index de fin pour le carburant
    quantite NUMERIC(18,3) NOT NULL CHECK (quantite >= 0),
    prix_unitaire_ht NUMERIC(18,4) NOT NULL CHECK (prix_unitaire_ht >= 0),
    prix_unitaire_ttc NUMERIC(18,4) NOT NULL CHECK (prix_unitaire_ttc >= 0),
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_ht NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire_ht) STORED,
    montant_tva NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht * (taux_tva / 100)) STORED,
    montant_ttc NUMERIC(18,2) GENERATED ALWAYS AS (montant_ht + montant_tva) STORED,
    taxes_detaillees JSONB DEFAULT '{}', -- Détail des taxes par ligne
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ventes_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vente_id UUID REFERENCES ventes(id) ON DELETE CASCADE,
    tresorerie_id UUID REFERENCES tresoreries(id) ON DELETE SET NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    note_paiement JSONB DEFAULT '{}',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE permissions_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    droits VARCHAR(20) CHECK (droits IN ('lecture', 'ecriture', 'validation', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

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

-- Table pour les bons de commande
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

-- Table pour les tickets de caisse
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
    compagnie_id UUID REFERENCES compagnies(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'Ferme', 'Reconcilie')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les arrêts de compte caissier
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
    compagnie_id UUID REFERENCES compagnies(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour historique des paiements clients
CREATE TABLE historique_paiements_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    montant_paye NUMERIC(18,2) NOT NULL,
    date_paiement DATE NOT NULL,
    mode_paiement VARCHAR(50),
    reference_paiement VARCHAR(100),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour inventaires
CREATE TABLE inventaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_inventaire VARCHAR(20) NOT NULL CHECK (type_inventaire IN ('Carburant', 'Boutique', 'Complet')) DEFAULT 'Complet',
    date_inventaire DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Cloture')) NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mesures d'inventaire des cuves
CREATE TABLE mesures_inventaire_cuves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventaire_id UUID REFERENCES inventaires(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id),
    hauteur_reelle NUMERIC(18,3) NOT NULL, -- Hauteur mesurée réellement
    volume_reel NUMERIC(18,3) NOT NULL,   -- Volume calculé à partir de la hauteur et du barème
    stock_reel NUMERIC(18,3) NOT NULL,    -- Stock calculé à partir du volume
    stock_theorique NUMERIC(18,3) NOT NULL, -- Stock théorique dans la base
    ecart NUMERIC(18,3) GENERATED ALWAYS AS (stock_reel - stock_theorique) STORED,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mesures d'inventaire des articles
CREATE TABLE mesures_inventaire_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventaire_id UUID REFERENCES inventaires(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id),
    stock_reel NUMERIC(18,3) NOT NULL,    -- Quantité réellement comptée
    stock_theorique NUMERIC(18,3) NOT NULL, -- Stock théorique dans la base
    ecart NUMERIC(18,3) GENERATED ALWAYS AS (stock_reel - stock_theorique) STORED,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les dépenses
CREATE TABLE depenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    categorie VARCHAR(100) NOT NULL,
    libelle TEXT NOT NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    date_depense DATE NOT NULL,
    mode_paiement VARCHAR(50),
    tresorerie_id UUID REFERENCES tresoreries(id),
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    projet TEXT,
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Payee', 'Annulee')) NOT NULL,
    reference_piece VARCHAR(100),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les fiches de paie
CREATE TABLE fiches_paie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employe_id UUID REFERENCES employes(id),
    mois_paie INTEGER NOT NULL, -- Numéro du mois (1-12)
    annee_paie INTEGER NOT NULL, -- Année
    date_paie DATE NOT NULL,
    salaire_base NUMERIC(18,2) NOT NULL,
    avances NUMERIC(18,2) DEFAULT 0,
    autres_deductions NUMERIC(18,2) DEFAULT 0,
    cotisations_sociales NUMERIC(18,2) DEFAULT 0,
    autres_retenues NUMERIC(18,2) DEFAULT 0,
    salaire_net NUMERIC(18,2) GENERATED ALWAYS AS (salaire_base - avances - autres_deductions - cotisations_sociales - autres_retenues) STORED,
    commentaire TEXT,
    utilisateur_calcul_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a effectué le calcul
    utilisateur_paye_id UUID REFERENCES utilisateurs(id),   -- Utilisateur qui a effectué le paiement
    statut VARCHAR(20) DEFAULT 'Calculee' CHECK (statut IN ('Calculee', 'Payee', 'Annulee')) NOT NULL,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les immobilisations
CREATE TABLE immobilisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    categorie VARCHAR(100) NOT NULL, -- Ex: véhicule, matériel, etc.
    date_achat DATE NOT NULL,
    valeur_acquisition NUMERIC(18,2) NOT NULL,
    valeur_nette_comptable NUMERIC(18,2) NOT NULL,
    amortissement_annuel NUMERIC(18,2) DEFAULT 0,
    duree_amortissement INTEGER DEFAULT 0, -- En années
    date_fin_amortissement DATE,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    tresorerie_id UUID REFERENCES tresoreries(id), -- Pour le paiement
    utilisateur_achat_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Cede', 'Hors service', 'Vendu')) NOT NULL,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les mouvements d'immobilisations
CREATE TABLE mouvements_immobilisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    immobilisation_id UUID REFERENCES immobilisations(id) ON DELETE CASCADE,
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Achat', 'Amortissement', 'Cession', 'Hors service', 'Vente')),
    date_mouvement DATE NOT NULL,
    valeur_mouvement NUMERIC(18,2) NOT NULL,
    commentaire TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les ajustements de stock
CREATE TABLE ajustements_stock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE, -- Pour les carburants
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_ajustement VARCHAR(20) NOT NULL CHECK (type_ajustement IN ('Entree', 'Sortie', 'Perte', 'Casse', 'Peremption')),
    quantite NUMERIC(18,3) NOT NULL, -- Positive pour entrée, négative pour sortie
    motif TEXT NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    date_ajustement DATE NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les dépôts de garantie
CREATE TABLE depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    montant NUMERIC(18,2) NOT NULL,
    date_enregistrement DATE NOT NULL,
    mode_paiement VARCHAR(50),
    reference_paiement VARCHAR(100),
    utilisateur_enregistre_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Utilise', 'Rembourse', 'Transfere')) NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'historique des utilisations du dépôt de garantie
CREATE TABLE utilisation_depot_garantie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    depot_garantie_id UUID REFERENCES depot_garantie(id),
    type_utilisation VARCHAR(20) NOT NULL CHECK (type_utilisation IN ('Dette', 'Vente', 'Ecart', 'Autre')),
    montant_utilise NUMERIC(18,2) NOT NULL,
    reference_operation VARCHAR(100), -- Référence à la facture, vente, etc.
    utilisateur_utilise_id UUID REFERENCES utilisateurs(id),
    date_utilisation DATE NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les lignes du bilan initial
CREATE TABLE bilan_initial_lignes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    compte_numero VARCHAR(20) NOT NULL,
    compte_id UUID REFERENCES plan_comptable(id),
    montant_initial NUMERIC(18,2) NOT NULL,
    type_solde VARCHAR(10) CHECK (type_solde IN ('debit', 'credit')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les périodes comptables
CREATE TABLE periodes_comptables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL CHECK (mois BETWEEN 1 AND 12),
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    est_cloture BOOLEAN DEFAULT FALSE,
    est_exercice BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les soldes comptables
CREATE TABLE soldes_comptables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compte_numero VARCHAR(20) NOT NULL,
    date_solde DATE NOT NULL,
    solde_debit NUMERIC(18,2) DEFAULT 0,
    solde_credit NUMERIC(18,2) DEFAULT 0,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    periode_id UUID REFERENCES periodes_comptables(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les rapports financiers
CREATE TABLE rapports_financiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'compte_resultat', 'grand_livre'
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les modèles de rapports par pays
CREATE TABLE modeles_rapports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_modele VARCHAR(50) NOT NULL,
    libelle_modele VARCHAR(200) NOT NULL,
    pays_id UUID REFERENCES pays(id),
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'tva', 'fiscal', etc.
    format_sortie VARCHAR(20) DEFAULT 'PDF', -- PDF, Excel, CSV, etc.
    contenu_modele TEXT, -- Modèle de rapport (format spécifique)
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les KPIs opérationnels
CREATE TABLE kpi_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    periode DATE NOT NULL,
    type_carburant UUID REFERENCES carburants(id), -- NULL pour ensemble
    litres_vendus NUMERIC(18,3) DEFAULT 0,
    marge_brute NUMERIC(18,2) DEFAULT 0,
    nombre_clients_servis INTEGER DEFAULT 0,
    volume_moyen_transaction NUMERIC(18,3) DEFAULT 0,
    rendement_pompiste UUID REFERENCES utilisateurs(id), -- NULL pour ensemble
    productivite_horaires NUMERIC(18,3) DEFAULT 0, -- litres par heure
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les déclarations fiscales
CREATE TABLE declarations_fiscales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_declaration VARCHAR(50) NOT NULL, -- TVA, autres taxes
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    montant_total NUMERIC(18,2) NOT NULL,
    montant_declare NUMERIC(18,2) NOT NULL,
    ecart NUMERIC(18,2) GENERATED ALWAYS AS (montant_declare - montant_total) STORED,
    date_depot DATE,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Soumis', 'Traite', 'Retour')),
    fichier_joint TEXT, -- Lien ou nom du fichier de déclaration
    utilisateur_depose_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi de conformité
CREATE TABLE suivi_conformite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_norme VARCHAR(50) NOT NULL, -- sécurité, qualité, fiscalité
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_prevue DATE NOT NULL,
    date_realisee DATE,
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme', 'En attente', 'Non applicable')),
    responsable_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les incidents de sécurité
CREATE TABLE incidents_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_incident VARCHAR(50) NOT NULL CHECK (type_incident IN ('Fuite', 'Accident', 'Vol', 'Intrusion', 'Autre')),
    date_incident TIMESTAMPTZ NOT NULL,
    description TEXT NOT NULL,
    gravite INTEGER CHECK (gravite BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'En cours', 'Résolu', 'Fermé')),
    utilisateur_declare_id UUID REFERENCES utilisateurs(id),
    utilisateur_traite_id UUID REFERENCES utilisateurs(id),
    action_corrective TEXT,
    date_resolution TIMESTAMPTZ,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les assurances
CREATE TABLE assurances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_assurance VARCHAR(50) NOT NULL, -- responsabilité civile, incendie, vol, etc.
    compagnie_assurance VARCHAR(100) NOT NULL,
    numero_police VARCHAR(50) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    montant_couverture NUMERIC(18,2) NOT NULL,
    prime_annuelle NUMERIC(18,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    fichier_joint TEXT, -- Lien ou nom du fichier de police
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse commerciale
CREATE TABLE analyse_commerciale (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_analyse VARCHAR(50) NOT NULL, -- tendance_vente, comportement_client, etc.
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    resultat JSONB, -- Données d'analyse au format JSON
    commentaire TEXT,
    utilisateur_analyse_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour la prévision de la demande
CREATE TABLE prevision_demande (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    date_prevision DATE NOT NULL,
    quantite_prevue NUMERIC(18,3) NOT NULL, -- En litres
    methode_prevision VARCHAR(50) NOT NULL, -- historique, saisonnalité, etc.
    confiance_prevision NUMERIC(5,2) CHECK (confiance_prevision BETWEEN 0 AND 100),
    commentaire TEXT,
    utilisateur_prevision_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les services annexes
CREATE TABLE services_annexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_service VARCHAR(50) NOT NULL, -- lavage, atelier, restaurant
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    prix_unitaire NUMERIC(18,2) NOT NULL,
    unite_mesure VARCHAR(20) DEFAULT 'Unité',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprimé')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les contrats de maintenance
CREATE TABLE contrats_maintenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    type_contrat VARCHAR(50) NOT NULL, -- pompe, cuve, caisse, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    cout_mensuel NUMERIC(18,2) NOT NULL,
    frequence INT, -- En mois
    prochaine_intervention DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le contrôle interne
CREATE TABLE controle_interne (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_controle VARCHAR(50) NOT NULL, -- controle_caisse, controle_stock, etc.
    element_controle VARCHAR(100), -- Numéro de caisse, cuve, etc.
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Anomalie', 'Non applicable')),
    montant_ecart NUMERIC(18,2) DEFAULT 0, -- Ecart constaté
    commentaire TEXT,
    statut VARCHAR(20) DEFAULT 'Terminé' CHECK (statut IN ('Planifié', 'En cours', 'Terminé', 'En attente')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les programmes de fidélisation
CREATE TABLE programme_fidelite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    type_programme VARCHAR(50) NOT NULL, -- points, réduction, etc.
    seuil_activation NUMERIC(18,2) DEFAULT 0, -- Montant/quantité requis
    benefice TEXT, -- Description du bénéfice
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Expiré')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les cartes de carburant
CREATE TABLE cartes_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    numero_carte VARCHAR(50) UNIQUE NOT NULL,
    date_activation DATE NOT NULL,
    date_expiration DATE,
    solde_carte NUMERIC(18,2) DEFAULT 0,
    plafond_mensuel NUMERIC(18,2), -- NULL pour illimité
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Inactive', 'Bloquee', 'Perdue', 'Remplacee')),
    utilisateur_creation_id UUID REFERENCES utilisateurs(id),
    utilisateur_blocage_id UUID REFERENCES utilisateurs(id), -- Qui a bloqué la carte
    motif_blocage TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les contrats clients
CREATE TABLE contrats_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_contrat VARCHAR(50) NOT NULL, -- ravitaillement, stationnement, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    volume_garanti NUMERIC(18,3), -- En litres
    prix_contractuel NUMERIC(18,4), -- Prix convenu
    frequence_livraison INTEGER, -- En jours
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé', 'Suspendu')),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour la qualité du carburant
CREATE TABLE qualite_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    cuve_id UUID REFERENCES cuves(id),
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    type_controle VARCHAR(50) NOT NULL, -- densité, octane, etc.
    valeur_relevee VARCHAR(50), -- Valeur mesurée
    valeur_standard VARCHAR(50), -- Valeur attendue
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme')),
    observation TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les coûts logistique
CREATE TABLE couts_logistique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- transport, stockage, assurance, etc.
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour gérer les validations hiérarchiques
CREATE TABLE validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL,  -- Ex: 'annulation_vente', 'modification_stock'
    seuil_montant NUMERIC(18,2),         -- Montant à partir duquel validation est requise
    niveau_validation INTEGER DEFAULT 1, -- Niveau hiérarchique requis pour validation
    profil_autorise_id UUID REFERENCES profils(id), -- Profil autorisé à valider
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

-- Table pour l'historique des actions utilisateur
CREATE TABLE historique_actions_utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    action VARCHAR(100) NOT NULL,       -- Ex: 'creation_vente', 'modification_stock'
    module VARCHAR(50) NOT NULL,        -- Ex: 'ventes', 'stocks'
    sous_module VARCHAR(50),            -- Ex: 'carburant', 'boutique'
    objet_id UUID,                      -- ID de l'objet affecté
    donnees_avant JSONB,                -- Données avant modification
    donnees_apres JSONB,                -- Données après modification
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    statut_action VARCHAR(20) DEFAULT 'Reussie' CHECK (statut_action IN ('Reussie', 'Echouee', 'Bloquee')),
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les associations plan comptable spécifique
CREATE TABLE plan_comptable_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_comptable_id UUID REFERENCES plan_comptable(id),
    pays_id UUID REFERENCES pays(id),
    numero_compte_local VARCHAR(20), -- Numéro de compte spécifique au pays
    intitule_local VARCHAR(255), -- Dénomination locale du compte
    est_compte_obligatoire BOOLEAN DEFAULT FALSE, -- Si le compte est obligatoire dans ce pays
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les cuve stocks (spécifique au carburant)
CREATE TABLE cuve_stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    stock_theorique NUMERIC(18,3) DEFAULT 0 CHECK (stock_theorique >= 0),
    stock_reel NUMERIC(18,3) DEFAULT 0 CHECK (stock_reel >= 0),
    ecart_stock NUMERIC(18,3) GENERATED ALWAYS AS (stock_reel - stock_theorique) STORED,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour historique des mouvements de cuve
CREATE TABLE cuve_stocks_mouvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_stock_id UUID REFERENCES cuve_stocks(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Entree', 'Sortie', 'Ajustement', 'Initial')),
    quantite NUMERIC(18,3) NOT NULL,
    prix_unitaire NUMERIC(18,4) DEFAULT 0, -- Pour calcul CUMP
    cout_total NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    date_mouvement DATE NOT NULL,
    reference_operation VARCHAR(100), -- Référence à l'opération d'origine
    utilisateur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    compagnie_id UUID REFERENCES utilisateurs(id), -- ATTENTION : devrait être REFERENCES compagnies(id)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Correction de certaines tables qui avaient des références incorrectes
-- Mise à jour de la table tresoreries pour corriger la dépendance circulaire
ALTER TABLE tresoreries DROP CONSTRAINT IF EXISTS tresoreries_fournisseur_id_fkey;
ALTER TABLE tresoreries ADD CONSTRAINT tresoreries_fournisseur_id_fkey FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id) ON DELETE SET NULL;

ALTER TABLE tresoreries DROP CONSTRAINT IF EXISTS tresoreries_utilisateur_dernier_rapprochement_fkey;
ALTER TABLE tresoreries ADD CONSTRAINT tresoreries_utilisateur_dernier_rapprochement_fkey FOREIGN KEY (utilisateur_dernier_rapprochement) REFERENCES utilisateurs(id);

-- Mise à jour de la table politiques_securite pour corriger la référence incorrecte
ALTER TABLE politiques_securite DROP CONSTRAINT IF EXISTS politiques_securite_compagnie_id_fkey;
ALTER TABLE politiques_securite ADD CONSTRAINT politiques_securite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table bilan_initial pour corriger la référence incorrecte
ALTER TABLE bilan_initial DROP CONSTRAINT IF EXISTS bilan_initial_compagnie_id_fkey;
ALTER TABLE bilan_initial ADD CONSTRAINT bilan_initial_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table stocks pour corriger la référence incorrecte
ALTER TABLE stocks DROP CONSTRAINT IF EXISTS stocks_compagnie_id_fkey;
ALTER TABLE stocks ADD CONSTRAINT stocks_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table stocks_mouvements pour corriger la référence incorrecte
ALTER TABLE stocks_mouvements DROP CONSTRAINT IF EXISTS stocks_mouvements_compagnie_id_fkey;
ALTER TABLE stocks_mouvements ADD CONSTRAINT stocks_mouvements_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table mouvements_tresorerie pour corriger la référence incorrecte
ALTER TABLE mouvements_tresorerie DROP CONSTRAINT IF EXISTS mouvements_tresorerie_compagnie_id_fkey;
ALTER TABLE mouvements_tresorerie ADD CONSTRAINT mouvements_tresorerie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table ventes pour corriger la référence incorrecte
ALTER TABLE ventes DROP CONSTRAINT IF EXISTS ventes_compagnie_id_fkey;
ALTER TABLE ventes ADD CONSTRAINT ventes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table tickets_caisse pour corriger la référence incorrecte
ALTER TABLE tickets_caisse DROP CONSTRAINT IF EXISTS tickets_caisse_compagnie_id_fkey;
ALTER TABLE tickets_caisse ADD CONSTRAINT tickets_caisse_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table arrets_compte_caissier pour corriger la référence incorrecte
ALTER TABLE arrets_compte_caissier DROP CONSTRAINT IF EXISTS arrets_compte_caissier_compagnie_id_fkey;
ALTER TABLE arrets_compte_caissier ADD CONSTRAINT arrets_compte_caissier_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table inventaires pour corriger la référence incorrecte
ALTER TABLE inventaires DROP CONSTRAINT IF EXISTS inventaires_compagnie_id_fkey;
ALTER TABLE inventaires ADD CONSTRAINT inventaires_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table depenses pour corriger la référence incorrecte
ALTER TABLE depenses DROP CONSTRAINT IF EXISTS depenses_compagnie_id_fkey;
ALTER TABLE depenses ADD CONSTRAINT depenses_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table fiches_paie pour corriger la référence incorrecte
ALTER TABLE fiches_paie DROP CONSTRAINT IF EXISTS fiches_paie_compagnie_id_fkey;
ALTER TABLE fiches_paie ADD CONSTRAINT fiches_paie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table immobilisations pour corriger la référence incorrecte
ALTER TABLE immobilisations DROP CONSTRAINT IF EXISTS immobilisations_compagnie_id_fkey;
ALTER TABLE immobilisations ADD CONSTRAINT immobilisations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table mouvements_immobilisations pour corriger la référence incorrecte
ALTER TABLE mouvements_immobilisations DROP CONSTRAINT IF EXISTS mouvements_immobilisations_compagnie_id_fkey;
ALTER TABLE mouvements_immobilisations ADD CONSTRAINT mouvements_immobilisations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table ajustements_stock pour corriger la référence incorrecte
ALTER TABLE ajustements_stock DROP CONSTRAINT IF EXISTS ajustements_stock_compagnie_id_fkey;
ALTER TABLE ajustements_stock ADD CONSTRAINT ajustements_stock_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table depot_garantie pour corriger la référence incorrecte
ALTER TABLE depot_garantie DROP CONSTRAINT IF EXISTS depot_garantie_compagnie_id_fkey;
ALTER TABLE depot_garantie ADD CONSTRAINT depot_garantie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table utilisation_depot_garantie pour corriger la référence incorrecte
ALTER TABLE utilisation_depot_garantie DROP CONSTRAINT IF EXISTS utilisation_depot_garantie_compagnie_id_fkey;
ALTER TABLE utilisation_depot_garantie ADD CONSTRAINT utilisation_depot_garantie_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table periodes_comptables pour corriger la référence incorrecte
ALTER TABLE periodes_comptables DROP CONSTRAINT IF EXISTS periodes_comptables_compagnie_id_fkey;
ALTER TABLE periodes_comptables ADD CONSTRAINT periodes_comptables_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table soldes_comptables pour corriger la référence incorrecte
ALTER TABLE soldes_comptables DROP CONSTRAINT IF EXISTS soldes_comptables_compagnie_id_fkey;
ALTER TABLE soldes_comptables ADD CONSTRAINT soldes_comptables_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table rapports_financiers pour corriger la référence incorrecte
ALTER TABLE rapports_financiers DROP CONSTRAINT IF EXISTS rapports_financiers_compagnie_id_fkey;
ALTER TABLE rapports_financiers ADD CONSTRAINT rapports_financiers_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table kpi_operations pour corriger la référence incorrecte
ALTER TABLE kpi_operations DROP CONSTRAINT IF EXISTS kpi_operations_compagnie_id_fkey;
ALTER TABLE kpi_operations ADD CONSTRAINT kpi_operations_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table declarations_fiscales pour corriger la référence incorrecte
ALTER TABLE declarations_fiscales DROP CONSTRAINT IF EXISTS declarations_fiscales_compagnie_id_fkey;
ALTER TABLE declarations_fiscales ADD CONSTRAINT declarations_fiscales_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table suivi_conformite pour corriger la référence incorrecte
ALTER TABLE suivi_conformite DROP CONSTRAINT IF EXISTS suivi_conformite_compagnie_id_fkey;
ALTER TABLE suivi_conformite ADD CONSTRAINT suivi_conformite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table incidents_securite pour corriger la référence incorrecte
ALTER TABLE incidents_securite DROP CONSTRAINT IF EXISTS incidents_securite_compagnie_id_fkey;
ALTER TABLE incidents_securite ADD CONSTRAINT incidents_securite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table assurances pour corriger la référence incorrecte
ALTER TABLE assurances DROP CONSTRAINT IF EXISTS assurances_compagnie_id_fkey;
ALTER TABLE assurances ADD CONSTRAINT assurances_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table analyse_commerciale pour corriger la référence incorrecte
ALTER TABLE analyse_commerciale DROP CONSTRAINT IF EXISTS analyse_commerciale_compagnie_id_fkey;
ALTER TABLE analyse_commerciale ADD CONSTRAINT analyse_commerciale_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table prevision_demande pour corriger la référence incorrecte
ALTER TABLE prevision_demande DROP CONSTRAINT IF EXISTS prevision_demande_compagnie_id_fkey;
ALTER TABLE prevision_demande ADD CONSTRAINT prevision_demande_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table services_annexes pour corriger la référence incorrecte
ALTER TABLE services_annexes DROP CONSTRAINT IF EXISTS services_annexes_compagnie_id_fkey;
ALTER TABLE services_annexes ADD CONSTRAINT services_annexes_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table contrats_maintenance pour corriger la référence incorrecte
ALTER TABLE contrats_maintenance DROP CONSTRAINT IF EXISTS contrats_maintenance_compagnie_id_fkey;
ALTER TABLE contrats_maintenance ADD CONSTRAINT contrats_maintenance_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table controle_interne pour corriger la référence incorrecte
ALTER TABLE controle_interne DROP CONSTRAINT IF EXISTS controle_interne_compagnie_id_fkey;
ALTER TABLE controle_interne ADD CONSTRAINT controle_interne_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table programme_fidelite pour corriger la référence incorrecte
ALTER TABLE programme_fidelite DROP CONSTRAINT IF EXISTS programme_fidelite_compagnie_id_fkey;
ALTER TABLE programme_fidelite ADD CONSTRAINT programme_fidelite_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table cartes_carburant pour corriger la référence incorrecte
ALTER TABLE cartes_carburant DROP CONSTRAINT IF EXISTS cartes_carburant_compagnie_id_fkey;
ALTER TABLE cartes_carburant ADD CONSTRAINT cartes_carburant_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table contrats_clients pour corriger la référence incorrecte
ALTER TABLE contrats_clients DROP CONSTRAINT IF EXISTS contrats_clients_compagnie_id_fkey;
ALTER TABLE contrats_clients ADD CONSTRAINT contrats_clients_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table qualite_carburant pour corriger la référence incorrecte
ALTER TABLE qualite_carburant DROP CONSTRAINT IF EXISTS qualite_carburant_compagnie_id_fkey;
ALTER TABLE qualite_carburant ADD CONSTRAINT qualite_carburant_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table couts_logistique pour corriger la référence incorrecte
ALTER TABLE couts_logistique DROP CONSTRAINT IF EXISTS couts_logistique_compagnie_id_fkey;
ALTER TABLE couts_logistique ADD CONSTRAINT couts_logistique_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table historique_actions_utilisateurs pour corriger la référence incorrecte
ALTER TABLE historique_actions_utilisateurs DROP CONSTRAINT IF EXISTS historique_actions_utilisateurs_compagnie_id_fkey;
ALTER TABLE historique_actions_utilisateurs ADD CONSTRAINT historique_actions_utilisateurs_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table cuve_stocks pour corriger la référence incorrecte
ALTER TABLE cuve_stocks DROP CONSTRAINT IF EXISTS cuve_stocks_compagnie_id_fkey;
ALTER TABLE cuve_stocks ADD CONSTRAINT cuve_stocks_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Mise à jour de la table cuve_stocks_mouvements pour corriger la référence incorrecte
ALTER TABLE cuve_stocks_mouvements DROP CONSTRAINT IF EXISTS cuve_stocks_mouvements_compagnie_id_fkey;
ALTER TABLE cuve_stocks_mouvements ADD CONSTRAINT cuve_stocks_mouvements_compagnie_id_fkey FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);

-- Vue pour vérifier les permissions d'un utilisateur
CREATE VIEW vue_permissions_utilisateur AS
SELECT
    u.id as utilisateur_id,
    u.nom as utilisateur_nom,
    p.id as profil_id,
    p.libelle as profil_libelle,
    perm.id as permission_id,
    perm.libelle as permission_libelle,
    m.libelle as module_libelle
FROM utilisateurs u
JOIN profils p ON u.profil_id = p.id
JOIN profil_permissions pp ON p.id = pp.profil_id
JOIN permissions perm ON pp.permission_id = perm.id
JOIN modules m ON perm.module_id = m.id
WHERE u.statut = 'Actif' AND p.statut = 'Actif' AND perm.statut = 'Actif';

-- Vues pour les rapports comptables

-- Vue du grand livre
CREATE VIEW vue_grand_livre AS
SELECT
    jl.compte_num,
    pc.intitule as compte_intitule,
    je.date_ecriture,
    je.libelle,
    je.type_operation,
    jl.debit,
    jl.credit,
    je.reference_operation
FROM journal_lines jl
JOIN journal_entries je ON jl.entry_id = je.id
LEFT JOIN plan_comptable pc ON jl.compte_num = pc.numero AND jl.compte_id = pc.id
ORDER BY jl.compte_num, je.date_ecriture, je.id;

-- Vue de la balance de vérification
CREATE VIEW vue_balance_verif AS
SELECT
    jl.compte_num,
    pc.intitule,
    SUM(jl.debit) as total_debit,
    SUM(jl.credit) as total_credit,
    SUM(jl.debit - jl.credit) as solde
FROM journal_lines jl
JOIN plan_comptable pc ON jl.compte_num = pc.numero AND jl.compte_id = pc.id
JOIN journal_entries je ON jl.entry_id = je.id
WHERE je.date_ecriture >= CURRENT_DATE - INTERVAL '1 year'  -- Paramétrable selon besoin
GROUP BY jl.compte_num, pc.intitule;

-- Vue de synthèse des soldes de compte
CREATE VIEW vue_soldes_comptes AS
SELECT
    jl.compte_num,
    pc.intitule,
    pc.classe,
    SUM(jl.debit) as total_debit,
    SUM(jl.credit) as total_credit,
    SUM(jl.debit - jl.credit) as solde_net
FROM journal_lines jl
JOIN plan_comptable pc ON jl.compte_num = pc.numero AND jl.compte_id = pc.id
GROUP BY jl.compte_num, pc.intitule, pc.classe;

-- Vue pour le suivi des rendements des pompistes
CREATE VIEW vue_rendement_pompistes AS
SELECT
    u.id as pompiste_id,
    u.nom as pompiste_nom,
    s.id as station_id,
    s.nom as station_nom,
    st.pays_id,
    COUNT(v.id) as nombre_ventes,
    SUM(vd.montant_ttc) as montant_total_ventes,
    SUM(vd.quantite) as quantite_totale_vente
FROM utilisateurs u
JOIN ventes v ON u.id = v.created_by
JOIN ventes_details vd ON v.id = vd.vente_id
JOIN stations s ON v.station_id = s.id
JOIN stations st ON s.id = st.id
WHERE v.type_vente = 'Carburant'
GROUP BY u.id, u.nom, s.id, s.nom, st.pays_id;

-- Vue pour détecter les écarts entre les soldes de la fiche et le grand livre
CREATE OR REPLACE VIEW ecarts_soldes_tiers AS
SELECT
    'Client' as tiers_type,
    c.id as tiers_id,
    c.nom as tiers_nom,
    c.solde_comptable as solde_fiche,
    COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable_reel,
    c.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
FROM clients c
LEFT JOIN journal_lines jl ON jl.compte_num IN (
    SELECT numero FROM plan_comptable
    WHERE type_compte = 'Client' AND classe = '4'
)
LEFT JOIN journal_entries je ON jl.entry_id = je.id AND je.compagnie_id = c.compagnie_id
WHERE c.statut = 'Actif'
GROUP BY c.id, c.nom, c.solde_comptable
HAVING c.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0)

UNION ALL

SELECT
    'Fournisseur' as tiers_type,
    f.id as tiers_id,
    f.nom as tiers_nom,
    f.solde_comptable as solde_fiche,
    COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable_reel,
    f.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
FROM fournisseurs f
LEFT JOIN journal_lines jl ON jl.compte_num IN (
    SELECT numero FROM plan_comptable
    WHERE type_compte = 'Fournisseur' AND classe = '4'
)
LEFT JOIN journal_entries je ON jl.entry_id = je.id AND je.compagnie_id = f.compagnie_id
WHERE f.statut = 'Actif'
GROUP BY f.id, f.nom, f.solde_comptable
HAVING f.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0);

-- Fonction pour calculer le solde disponible client
CREATE OR REPLACE FUNCTION solde_client_disponible(client_id UUID)
RETURNS NUMERIC(18,2) AS $$
DECLARE
    solde_de_base NUMERIC(18,2);
    montant_depot NUMERIC(18,2);
BEGIN
    -- Solde de base du client
    SELECT solde_comptable INTO solde_de_base
    FROM clients
    WHERE id = client_id;

    -- Montant des dépôts de garantie actifs
    SELECT COALESCE(SUM(montant), 0) INTO montant_depot
    FROM depot_garantie
    WHERE client_id = client_id AND statut = 'Actif';

    RETURN solde_de_base + montant_depot;
END;
$$ LANGUAGE plpgsql;

-- Procédure de rapprochement mensuel des soldes de tiers
CREATE OR REPLACE FUNCTION rapprochement_mensuel_tiers()
RETURNS TABLE (
    tiers_type VARCHAR(20),
    tiers_id UUID,
    tiers_nom VARCHAR(150),
    solde_fiche NUMERIC(18,2),
    solde_comptable NUMERIC(18,2),
    ecart NUMERIC(18,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        'Client'::VARCHAR as tiers_type,
        c.id as tiers_id,
        c.nom as tiers_nom,
        c.solde_comptable as solde_fiche,
        COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable,
        c.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
    FROM clients c
    LEFT JOIN journal_lines jl ON jl.compte_num IN (SELECT numero FROM plan_comptable WHERE type_compte = 'Client')
        AND jl.entry_id IN (SELECT id FROM journal_entries WHERE compagnie_id = c.compagnie_id)
    WHERE c.statut = 'Actif'
    GROUP BY c.id, c.nom, c.solde_comptable
    HAVING c.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0)

    UNION ALL

    SELECT
        'Fournisseur'::VARCHAR as tiers_type,
        f.id as tiers_id,
        f.nom as tiers_nom,
        f.solde_comptable as solde_fiche,
        COALESCE(SUM(jl.debit - jl.credit), 0) as solde_comptable,
        f.solde_comptable - COALESCE(SUM(jl.debit - jl.credit), 0) as ecart
    FROM fournisseurs f
    LEFT JOIN journal_lines jl ON jl.compte_num IN (SELECT numero FROM plan_comptable WHERE type_compte = 'Fournisseur')
        AND jl.entry_id IN (SELECT id FROM journal_entries WHERE compagnie_id = f.compagnie_id)
    WHERE f.statut = 'Actif'
    GROUP BY f.id, f.nom, f.solde_comptable
    HAVING f.solde_comptable != COALESCE(SUM(jl.debit - jl.credit), 0);
END;
$$ LANGUAGE plpgsql;

-- Trigger pour les dettes fournisseurs
CREATE OR REPLACE FUNCTION update_fournisseur_solde()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE fournisseurs
        SET solde_comptable = solde_comptable + (NEW.montant_achat - NEW.montant_paye)
        WHERE id = NEW.fournisseur_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE fournisseurs
        SET solde_comptable = solde_comptable - (OLD.montant_achat - OLD.montant_paye)
        WHERE id = OLD.fournisseur_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_fournisseur_solde
    AFTER INSERT OR UPDATE OR DELETE ON dettes_fournisseurs
    FOR EACH ROW EXECUTE FUNCTION update_fournisseur_solde();

-- Fonction pour calculer le solde actuel d'une trésorerie
CREATE OR REPLACE FUNCTION calculer_solde_tresorerie(tresorerie_uuid UUID)
RETURNS NUMERIC(18,2) AS $$
DECLARE
    solde_calcule NUMERIC(18,2);
BEGIN
    SELECT COALESCE(SUM(
        CASE
            WHEN type_mouvement = 'Entree' THEN montant
            WHEN type_mouvement = 'Sortie' THEN -montant
            WHEN type_mouvement = 'Correction' THEN montant  -- Peut être positif ou négatif
            WHEN type_mouvement = 'Annulation' THEN -montant -- Annulation d'un mouvement précédent
            ELSE 0
        END
    ), 0)
    INTO solde_calcule
    FROM mouvements_tresorerie
    WHERE tresorerie_id = tresorerie_uuid
      AND statut IN ('Actif', 'Corrige') -- Exclure les mouvements annulés
      AND date_mouvement <= CURRENT_DATE; -- Pour les mouvements jusqu'à aujourd'hui

    RETURN solde_calcule;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour modifier un mouvement de trésorerie
CREATE OR REPLACE FUNCTION modifier_mouvement_tresorerie(
    mouvement_id UUID,
    nouveau_montant NUMERIC(18,2),
    utilisateur_action_id UUID,
    motif_modification TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    mouvement_original RECORD;
    difference_montant NUMERIC(18,2);
    mouvement_correction_id UUID;
BEGIN
    -- Récupérer le mouvement original
    SELECT * INTO mouvement_original
    FROM mouvements_tresorerie
    WHERE id = mouvement_id AND statut = 'Actif';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Mouvement non trouvé ou déjà annulé: %', mouvement_id;
    END IF;

    -- Calculer la différence
    difference_montant := nouveau_montant - mouvement_original.montant;

    -- Si pas de différence, pas besoin de correction
    IF difference_montant = 0 THEN
        RETURN TRUE;
    END IF;

    -- Créer un mouvement de correction
    INSERT INTO mouvements_tresorerie (
        tresorerie_id,
        type_mouvement,
        sous_type_mouvement,
        montant,
        reference_operation,
        utilisateur_id,
        commentaire,
        date_mouvement,
        mouvement_origine_id,  -- Référence au mouvement original
        statut,
        compagnie_id
    )
    VALUES (
        mouvement_original.tresorerie_id,
        'Correction',
        'Correction_' || mouvement_original.sous_type_mouvement,
        ABS(difference_montant),  -- Valeur absolue
        'CORR_' || mouvement_original.reference_operation,
        utilisateur_action_id,
        'Correction: ' || motif_modification || ' (Diff: ' || difference_montant || ')',
        CURRENT_DATE,
        mouvement_original.id,
        'Actif',
        (SELECT compagnie_id FROM utilisateurs WHERE id = utilisateur_action_id)
    )
    RETURNING id INTO mouvement_correction_id;

    -- Mettre à jour le statut du mouvement original pour indiquer qu'il a été corrigé
    UPDATE mouvements_tresorerie
    SET statut = CASE
        WHEN statut = 'Actif' THEN 'Corrige'
        ELSE statut
    END
    WHERE id = mouvement_original.id;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de la modification du mouvement: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour annuler une opération de trésorerie
CREATE OR REPLACE FUNCTION annuler_operation_trésorerie(
    reference_operation VARCHAR(100),
    utilisateur_action_id UUID,
    motif_annulation TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    mouvement_origine RECORD;
    mouvement_annulation_id UUID;
BEGIN
    -- Trouver le mouvement original
    SELECT * INTO mouvement_origine
    FROM mouvements_tresorerie
    WHERE reference_operation = reference_operation AND statut = 'Actif';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Aucun mouvement actif trouvé pour la référence: %', reference_operation;
    END IF;

    -- Créer un mouvement d'annulation
    INSERT INTO mouvements_tresorerie (
        tresorerie_id,
        type_mouvement,
        sous_type_mouvement,
        montant,
        reference_operation,
        utilisateur_id,
        commentaire,
        date_mouvement,
        mouvement_origine_id,
        statut,
        compagnie_id
    )
    VALUES (
        mouvement_origine.tresorerie_id,
        'Annulation',
        'Annulation_' || mouvement_origine.sous_type_mouvement,
        mouvement_origine.montant,
        'ANNULE_' || reference_operation,
        utilisateur_action_id,
        'Annulation: ' || motif_annulation,
        CURRENT_DATE,
        mouvement_origine.id,
        'Actif',
        (SELECT compagnie_id FROM utilisateurs WHERE id = utilisateur_action_id)
    )
    RETURNING id INTO mouvement_annulation_id;

    -- Mettre à jour le statut du mouvement original
    UPDATE mouvements_tresorerie
    SET statut = 'Annule'
    WHERE id = mouvement_origine.id;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de l''annulation de l''opération: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour le solde après chaque mouvement de trésorerie
CREATE OR REPLACE FUNCTION update_solde_tresorerie()
RETURNS TRIGGER AS $$
DECLARE
    nouveau_solde NUMERIC(18,2);
BEGIN
    -- Calculer le nouveau solde
    IF TG_OP = 'INSERT' THEN
        nouveau_solde := calculer_solde_tresorerie(NEW.tresorerie_id);
    ELSIF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        nouveau_solde := calculer_solde_tresorerie(OLD.tresorerie_id);
    END IF;

    -- Mettre à jour le solde dans la table tresoreries
    UPDATE tresoreries
    SET solde = nouveau_solde
    WHERE id = (CASE
        WHEN TG_OP = 'INSERT' THEN NEW.tresorerie_id
        ELSE OLD.tresorerie_id
    END);

    RETURN CASE
        WHEN TG_OP = 'INSERT' THEN NEW
        WHEN TG_OP = 'UPDATE' THEN NEW
        ELSE OLD
    END;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_solde_tresorerie
    AFTER INSERT OR UPDATE OR DELETE ON mouvements_tresorerie
    FOR EACH ROW EXECUTE FUNCTION update_solde_tresorerie();

-- Insertion des modules par défaut
INSERT INTO modules (libelle, statut) VALUES
('ventes', 'Actif'),
('achats', 'Actif'),
('stocks', 'Actif'),
('rapports', 'Actif'),
('comptabilite', 'Actif'),
('tresorerie', 'Actif'),
('utilisateurs', 'Actif'),
('configurations', 'Actif')
ON CONFLICT (libelle) DO NOTHING;

-- Insertion des permissions par défaut pour le module des ventes
INSERT INTO permissions (libelle, description, module_id)
SELECT 'lire_ventes', 'Lire les détails des ventes', id
FROM modules
WHERE libelle = 'ventes'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'creer_vente', 'Créer une nouvelle vente', id
FROM modules
WHERE libelle = 'ventes'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'modifier_vente', 'Modifier une vente existante', id
FROM modules
WHERE libelle = 'ventes'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'supprimer_vente', 'Supprimer une vente', id
FROM modules
WHERE libelle = 'ventes'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'annuler_vente', 'Annuler une vente', id
FROM modules
WHERE libelle = 'ventes'
ON CONFLICT (libelle) DO NOTHING;

-- Insertion des permissions par défaut pour le module des stocks
INSERT INTO permissions (libelle, description, module_id)
SELECT 'lire_stocks', 'Lire les informations de stock', id
FROM modules
WHERE libelle = 'stocks'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'modifier_stock', 'Modifier manuellement les stocks', id
FROM modules
WHERE libelle = 'stocks'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'inventaire_stock', 'Effectuer un inventaire de stock', id
FROM modules
WHERE libelle = 'stocks'
ON CONFLICT (libelle) DO NOTHING;

-- Insertion des permissions par défaut pour le module des achats
INSERT INTO permissions (libelle, description, module_id)
SELECT 'lire_achats', 'Lire les détails des achats', id
FROM modules
WHERE libelle = 'achats'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'creer_achat', 'Créer un nouvel achat', id
FROM modules
WHERE libelle = 'achats'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'modifier_achat', 'Modifier un achat existant', id
FROM modules
WHERE libelle = 'achats'
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'supprimer_achat', 'Supprimer un achat', id
FROM modules
WHERE libelle = 'achats'
ON CONFLICT (libelle) DO NOTHING;

-- Index pour la performance
CREATE INDEX idx_journal_entries_date_compagnie ON journal_entries(date_ecriture, compagnie_id);
CREATE INDEX idx_journal_entries_type_compagnie ON journal_entries(type_operation, compagnie_id);
CREATE INDEX idx_journal_lines_compte_date ON journal_lines(compte_num, entry_id);
CREATE INDEX idx_journal_entries_dates ON journal_entries(date_ecriture);
CREATE INDEX idx_stocks_article_station ON stocks(article_id, station_id);
CREATE INDEX idx_ventes_date_client ON ventes(date_vente, client_id);
CREATE INDEX idx_achats_date_fournisseur ON achats(date_achat, fournisseur_id);