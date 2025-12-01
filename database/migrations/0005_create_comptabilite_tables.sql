-- Migration pour créer les tables de comptabilité

-- Table plan_comptable
CREATE TABLE plan_comptable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero VARCHAR(20) UNIQUE NOT NULL,           
    intitule VARCHAR(255) NOT NULL,               
    classe VARCHAR(5) NOT NULL,                   
    type_compte VARCHAR(100) NOT NULL,            
    sens_solde VARCHAR(10) CHECK (sens_solde IN ('D', 'C')), 
    compte_parent_id UUID REFERENCES plan_comptable(id) ON DELETE SET NULL,
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    est_compte_racine BOOLEAN DEFAULT FALSE,
    est_compte_de_resultat BOOLEAN DEFAULT FALSE,
    est_compte_actif BOOLEAN DEFAULT TRUE,
    pays_id UUID REFERENCES pays(id),
    est_specifique_pays BOOLEAN DEFAULT FALSE,
    code_pays VARCHAR(3),
    compagnie_id UUID REFERENCES compagnies(id),  
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_plan_comptable_numero ON plan_comptable(numero);
CREATE INDEX idx_plan_comptable_classe ON plan_comptable(classe);
CREATE INDEX idx_plan_comptable_type ON plan_comptable(type_compte);
CREATE INDEX idx_plan_comptable_parent ON plan_comptable(compte_parent_id);
CREATE INDEX idx_plan_comptable_pays ON plan_comptable(pays_id);
CREATE INDEX idx_plan_comptable_compagnie ON plan_comptable(compagnie_id);  
CREATE INDEX idx_plan_comptable_statut ON plan_comptable(statut);

-- Table journaux
CREATE TABLE journaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,             
    libelle VARCHAR(100) NOT NULL,                
    description TEXT,
    pays_id UUID REFERENCES pays(id),             
    compagnie_id UUID REFERENCES compagnies(id),  
    type_journal VARCHAR(50) NOT NULL CHECK (type_journal IN ('achats', 'ventes', 'tresorerie', 'banque', 'caisse', 'opex', 'stock', 'autre')), 
    derniere_piece INTEGER DEFAULT 0,             
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_journaux_code ON journaux(code);
CREATE INDEX idx_journaux_type ON journaux(type_journal);
CREATE INDEX idx_journaux_pays ON journaux(pays_id);
CREATE INDEX idx_journaux_compagnie ON journaux(compagnie_id);
CREATE INDEX idx_journaux_statut ON journaux(statut);

-- Table ecritures_comptables
CREATE TABLE ecritures_comptables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_id UUID NOT NULL REFERENCES journaux(id),
    numero_piece VARCHAR(50) NOT NULL,           
    date_ecriture DATE NOT NULL,
    libelle TEXT NOT NULL,
    montant_debit NUMERIC(18,2) DEFAULT 0,
    montant_credit NUMERIC(18,2) DEFAULT 0,
    tiers_id UUID,                               
    utilisateur_id UUID REFERENCES utilisateurs(id),  
    operation_id UUID,                           
    operation_type VARCHAR(50),                  
    est_validee BOOLEAN DEFAULT FALSE,           
    est_cloturee BOOLEAN DEFAULT FALSE,          
    date_validation TIMESTAMPTZ,                 
    utilisateur_validation_id UUID REFERENCES utilisateurs(id), 
    reference_externe VARCHAR(100),              
    compagnie_id UUID NOT NULL REFERENCES compagnies(id),  
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(journal_id, numero_piece)
);

-- Index pour les performances
CREATE INDEX idx_ecritures_journal_piece ON ecritures_comptables(journal_id, numero_piece);
CREATE INDEX idx_ecritures_date ON ecritures_comptables(date_ecriture);
CREATE INDEX idx_ecritures_tiers ON ecritures_comptables(tiers_id);
CREATE INDEX idx_ecritures_utilisateur ON ecritures_comptables(utilisateur_id);
CREATE INDEX idx_ecritures_operation ON ecritures_comptables(operation_id, operation_type);
CREATE INDEX idx_ecritures_validee ON ecritures_comptables(est_validee);
CREATE INDEX idx_ecritures_cloturee ON ecritures_comptables(est_cloturee);
CREATE INDEX idx_ecritures_compagnie ON ecritures_comptables(compagnie_id);

-- Table lignes_ecritures
CREATE TABLE lignes_ecritures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ecriture_id UUID NOT NULL REFERENCES ecritures_comptables(id) ON DELETE CASCADE,
    compte_id UUID NOT NULL REFERENCES plan_comptable(id),
    montant_debit NUMERIC(18,2) DEFAULT 0,
    montant_credit NUMERIC(18,2) DEFAULT 0,
    libelle TEXT,                                
    tiers_id UUID,                               
    projet_id UUID,                              
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_lignes_ecriture ON lignes_ecritures(ecriture_id);
CREATE INDEX idx_lignes_compte ON lignes_ecritures(compte_id);
CREATE INDEX idx_lignes_tiers ON lignes_ecritures(tiers_id);
CREATE INDEX idx_lignes_projet ON lignes_ecritures(projet_id);

-- Contrainte pour s'assurer qu'une ligne n'a que du débit ou que du crédit, jamais les deux
ALTER TABLE lignes_ecritures
ADD CONSTRAINT check_montant_uniquement_debit_ou_credit
CHECK (
    (montant_debit > 0 AND montant_credit = 0) OR
    (montant_credit > 0 AND montant_debit = 0) OR
    (montant_debit = 0 AND montant_credit = 0)
);

-- Table soldes_comptes
CREATE TABLE soldes_comptes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compte_id UUID NOT NULL REFERENCES plan_comptable(id),
    date_solde DATE NOT NULL,
    solde_debit NUMERIC(18,2) DEFAULT 0,
    solde_credit NUMERIC(18,2) DEFAULT 0,
    solde_net NUMERIC(18,2) GENERATED ALWAYS AS (solde_debit - solde_credit) STORED, 
    type_solde VARCHAR(20) NOT NULL CHECK (type_solde IN ('ouverture', 'cloture', 'intermediaire')),
    compagnie_id UUID NOT NULL REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(compte_id, date_solde, compagnie_id)
);

-- Index pour les performances
CREATE INDEX idx_soldes_compte ON soldes_comptes(compte_id);
CREATE INDEX idx_soldes_date ON soldes_comptes(date_solde);
CREATE INDEX idx_soldes_compagnie ON soldes_comptes(compagnie_id);
CREATE INDEX idx_soldes_type ON soldes_comptes(type_solde);

-- Table bilan_initial
CREATE TABLE bilan_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compagnie_id uuid,
    date_bilan_initial date NOT NULL,
    est_valide boolean DEFAULT false,
    est_verifie boolean DEFAULT false,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    utilisateur_id uuid,
    description text
);

-- Ajout des contraintes
ALTER TABLE bilan_initial ADD CONSTRAINT bilan_initial_pkey PRIMARY KEY (id);
ALTER TABLE bilan_initial ADD CONSTRAINT fk_bilan_initial_compagnie FOREIGN KEY (compagnie_id) REFERENCES compagnies(id);
ALTER TABLE bilan_initial ADD CONSTRAINT fk_bilan_initial_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id);

-- Index pour les performances
CREATE INDEX idx_bilan_initial_compagnie ON bilan_initial(compagnie_id);
CREATE INDEX idx_bilan_initial_date ON bilan_initial(date_bilan_initial);
CREATE INDEX idx_bilan_initial_utilisateur ON bilan_initial(utilisateur_id);
CREATE INDEX idx_bilan_initial_validation ON bilan_initial(est_valide, est_verifie);

-- Table bilan_initial_lignes
CREATE TABLE bilan_initial_lignes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    compte_numero VARCHAR(20) NOT NULL,
    compte_id UUID REFERENCES plan_comptable(id),
    montant_initial NUMERIC(18,2) NOT NULL,
    type_solde VARCHAR(10) CHECK (type_solde IN ('debit', 'credit')),
    poste_bilan VARCHAR(20) NOT NULL CHECK (poste_bilan IN ('actif', 'passif', 'capitaux_propres')), 
    categorie_detaillee VARCHAR(50), 
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_bilan_initial_lignes_bilan ON bilan_initial_lignes(bilan_initial_id);
CREATE INDEX idx_bilan_initial_lignes_compte ON bilan_initial_lignes(compte_numero);
CREATE INDEX idx_bilan_initial_lignes_poste ON bilan_initial_lignes(poste_bilan);
CREATE INDEX idx_bilan_initial_lignes_montant ON bilan_initial_lignes(montant_initial);

-- Table immobilisations_bilan_initial
CREATE TABLE immobilisations_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    categorie VARCHAR(100) NOT NULL, 
    date_achat DATE NOT NULL,
    valeur_acquisition NUMERIC(18,2) NOT NULL,
    valeur_nette_comptable NUMERIC(18,2) NOT NULL,
    amortissement_cumule NUMERIC(18,2) NOT NULL, 
    duree_amortissement INTEGER DEFAULT 0, 
    date_fin_amortissement DATE,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    utilisateur_achat_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Cede', 'Hors service', 'Vendu')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_immob_bilan_initial_bilan ON immobilisations_bilan_initial(bilan_initial_id);
CREATE INDEX idx_immob_bilan_initial_code ON immobilisations_bilan_initial(code);

-- Table stocks_bilan_initial
CREATE TABLE stocks_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_stock VARCHAR(20) NOT NULL CHECK (type_stock IN ('carburant', 'produit_boutique')), 
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL, 
    carburant_id UUID REFERENCES carburants(id) ON DELETE SET NULL, 
    cuve_id UUID REFERENCES cuves(id) ON DELETE SET NULL, 
    quantite NUMERIC(18,3) NOT NULL, 
    prix_unitaire NUMERIC(18,4) NOT NULL, 
    valeur_totale NUMERIC(18,4) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED, 
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_stocks_bilan_initial_bilan ON stocks_bilan_initial(bilan_initial_id);
CREATE INDEX idx_stocks_bilan_initial_article ON stocks_bilan_initial(article_id);
CREATE INDEX idx_stocks_bilan_initial_carburant ON stocks_bilan_initial(carburant_id);
CREATE INDEX idx_stocks_bilan_initial_type ON stocks_bilan_initial(type_stock);
CREATE INDEX idx_stocks_bilan_initial_valeur ON stocks_bilan_initial(valeur_totale);

-- Table creances_dettes_bilan_initial
CREATE TABLE creances_dettes_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_tiers VARCHAR(20) NOT NULL CHECK (type_tiers IN ('client', 'fournisseur')), 
    tiers_id UUID NOT NULL, 
    montant_initial NUMERIC(18,2) NOT NULL,
    devise VARCHAR(3) DEFAULT 'MGA',
    date_echeance DATE, 
    reference_piece VARCHAR(100), 
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_creances_dettes_bilan_initial_bilan ON creances_dettes_bilan_initial(bilan_initial_id);
CREATE INDEX idx_creances_dettes_bilan_initial_tiers ON creances_dettes_bilan_initial(tiers_id);
CREATE INDEX idx_creances_dettes_bilan_initial_type ON creances_dettes_bilan_initial(type_tiers);
CREATE INDEX idx_creances_dettes_bilan_initial_montant ON creances_dettes_bilan_initial(montant_initial);

-- Table rapports_financiers
CREATE TABLE rapports_financiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, 
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB, 
    format_sortie VARCHAR(20) DEFAULT 'PDF', 
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Erreur', 'Archive')),
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    fichier_joint TEXT, 
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_financiers_type ON rapports_financiers(type_rapport);
CREATE INDEX idx_rapports_financiers_periode ON rapports_financiers(periode_debut, periode_fin);
CREATE INDEX idx_rapports_financiers_utilisateur ON rapports_financiers(utilisateur_generateur_id);
CREATE INDEX idx_rapports_financiers_compagnie ON rapports_financiers(compagnie_id);
CREATE INDEX idx_rapports_financiers_station ON rapports_financiers(station_id);
CREATE INDEX idx_rapports_financiers_date ON rapports_financiers(created_at);
CREATE INDEX idx_rapports_financiers_statut ON rapports_financiers(statut);

-- Table historique_rapports
CREATE TABLE historique_rapports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom_rapport VARCHAR(100) NOT NULL, 
    type_rapport VARCHAR(50) NOT NULL, 
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    utilisateur_demandeur_id UUID REFERENCES utilisateurs(id),
    utilisateur_generation_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Demande' CHECK (statut IN ('Demande', 'En cours', 'Termine', 'Erreur', 'Archive')),
    parametres JSONB, 
    resultat_generation TEXT, 
    date_demande TIMESTAMPTZ DEFAULT now(),
    date_generation TIMESTAMPTZ,
    date_consultation TIMESTAMPTZ,
    est_a_jour BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_rapports_type ON historique_rapports(type_rapport);
CREATE INDEX idx_historique_rapports_periode ON historique_rapports(periode_debut, periode_fin);
CREATE INDEX idx_historique_rapports_demandeur ON historique_rapports(utilisateur_demandeur_id);
CREATE INDEX idx_historique_rapports_generation ON historique_rapports(utilisateur_generation_id);
CREATE INDEX idx_historique_rapports_date ON historique_rapports(created_at);
CREATE INDEX idx_historique_rapports_a_jour ON historique_rapports(est_a_jour);

-- Trigger pour vérifier la cohérence du bilan initial
CREATE OR REPLACE FUNCTION verifier_coherence_bilan_initial()
RETURNS TRIGGER AS $$
DECLARE
    total_actifs NUMERIC(18,2);
    total_passifs_capitaux NUMERIC(18,2);
BEGIN
    -- Calcul du total des actifs
    SELECT COALESCE(SUM(montant_initial), 0) INTO total_actifs
    FROM bilan_initial_lignes
    WHERE bilan_initial_id = NEW.bilan_initial_id AND poste_bilan = 'actif';

    -- Calcul du total des passifs et capitaux propres
    SELECT COALESCE(SUM(montant_initial), 0) INTO total_passifs_capitaux
    FROM bilan_initial_lignes
    WHERE bilan_initial_id = NEW.bilan_initial_id AND poste_bilan IN ('passif', 'capitaux_propres');

    -- Vérification de l'égalité
    IF ABS(total_actifs - total_passifs_capitaux) > 0.01 THEN -- Tolérance de 0.01 pour les arrondis
        RAISE EXCEPTION 'Le bilan initial n''est pas équilibré (actifs %s != passifs + capitaux propres %s)', total_actifs, total_passifs_capitaux;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verifier_coherence_bilan_initial
    AFTER INSERT OR UPDATE ON bilan_initial_lignes
    FOR EACH ROW
    EXECUTE FUNCTION verifier_coherence_bilan_initial();

-- Trigger pour vérifier que la période de fin est postérieure à la période de début
CREATE OR REPLACE FUNCTION verifier_periode_rapport()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.periode_fin < NEW.periode_debut THEN
        RAISE EXCEPTION 'La période de fin (%s) doit être postérieure à la période de début (%s)', NEW.periode_fin, NEW.periode_debut;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger pour la table rapports_financiers
CREATE TRIGGER trigger_verifier_periode_rapport
    BEFORE INSERT OR UPDATE ON rapports_financiers
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();

-- Création du trigger pour la table historique_rapports
CREATE TRIGGER trigger_verifier_periode_historique
    BEFORE INSERT OR UPDATE ON historique_rapports
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();