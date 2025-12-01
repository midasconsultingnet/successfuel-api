# Technical Specification - Module de Gestion des Opérations Hors Achats/Ventes

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de gestion des opérations hors achats/ventes permet de gérer toutes les autres opérations financières et opérationnelles d'une station-service. Il couvre les dépenses courantes, les salaires des employés, les immobilisations, les investissements, les opérations de recouvrement de créances et les règlements de dettes fournisseurs. Ce module complète la gestion financière du système SuccessFuel en permettant un suivi complet des flux financiers de la station.

### Problème à résoudre
Sans un module dédié aux opérations hors achats/ventes, les stations-service ne pourraient pas suivre efficacement leurs autres opérations financières, ce qui entraînerait:
- Des difficultés à contrôler les charges opérationnelles
- Des problèmes de gestion de la paie des employés
- Des lacunes dans le suivi des investissements et immobilisations
- Des difficultés à analyser la performance du recouvrement des créances
- Des problèmes de gestion des dettes fournisseurs
- Une vision incomplète de la situation financière globale

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion des dépenses courantes (catégorisation, paiement, analyse)
- Gestion des salaires (fiches de paie, suivi de productivité)
- Gestion des immobilisations et investissements (achat, suivi des coûts)
- Gestion du recouvrement des créances (analyse de performance)
- Gestion des règlements des dettes fournisseurs (analyse des délais)

## 2. User Stories & Critères d'acceptation

### US-OP-001: En tant que gestionnaire, je veux gérer les dépenses courantes
**Critères d'acceptation :**
- Saisie des dépenses avec montant, date, fournisseur
- Catégorisation des charges (entretien, électricité, etc.)
- Association avec une trésorerie pour le paiement
- Génération automatique d'une écriture comptable
- Historique des dépenses
- Recherche et filtrage des dépenses

### US-OP-002: En tant que gestionnaire, je veux catégoriser les charges
**Critères d'acceptation :**
- Création de catégories de charges personnalisées
- Association de chaque dépense à une catégorie
- Hiérarchie des catégories possible
- Analyse des charges par catégorie
- Visualisation des tendances de charges
- Export pour les rapports comptables

### US-OP-003: En tant que gestionnaire, je veux gérer les paiements des charges
**Critères d'acceptation :**
- Paiement immédiat, partiel ou différé
- Association avec un mode de paiement
- Génération d'une écriture comptable de paiement
- Mise à jour automatique de la trésorerie
- Historique des paiements
- Génération d'écritures comptables de dette si applicable

### US-OP-004: En tant que gestionnaire, je veux analyser les tendances de charges
**Critères d'acceptation :**
- Analyse des charges sur différentes périodes
- Comparaison entre périodes
- Identification des écarts significatifs
- Représentation graphique des tendances
- Calcul des moyennes mobiles
- Génération de rapports d'analyse

### US-OP-005: En tant que gestionnaire, je veux générer les fiches de paie mensuelles
**Critères d'acceptation :**
- Calcul automatique des salaires en fonction des données de base
- Prise en compte des heures supplémentaires
- Application des charges sociales et fiscales
- Génération des écritures comptables de paie
- Historique des paies
- Export des fiches de paie

### US-OP-006: En tant que gestionnaire, je veux gérer les salaires
**Critères d'acceptation :**
- Saisie des données de base des employés (salaire, poste, etc.)
- Gestion des avances et créances
- Mise à jour automatique des soldes d'employés
- Historique des modifications de salaires
- Génération des écritures comptables
- Intégration avec les données de productivité

### US-OP-007: En tant que gestionnaire, je veux suivre la productivité des employés
**Critères d'acceptation :**
- Calcul des indicateurs de productivité
- Analyse comparative entre employés
- Suivi de la productivité dans le temps
- Identification des écarts de performance
- Génération de rapports individuels
- Intégration avec les données de paie

### US-OP-008: En tant que gestionnaire, je veux gérer les immobilisations
**Critères d'acceptation :**
- Enregistrement de l'achat des immobilisations
- Affectation à une station
- Calcul de l'amortissement
- Suivi de la valeur résiduelle
- Historique des mouvements
- Génération des écritures comptables

### US-OP-009: En tant que gestionnaire, je veux suivre les coûts et l'efficacité des investissements
**Critères d'acceptation :**
- Suivi des coûts des investissements
- Calcul de la rentabilité
- Analyse du retour sur investissement (ROI)
- Comparaison entre investissements
- Représentation graphique des performances
- Génération de rapports d'analyse

### US-OP-010: En tant que gestionnaire, je veux gérer le recouvrement des créances
**Critères d'acceptation :**
- Suivi des créances clients
- Enregistrement des paiements reçus
- Gestion des échéances
- Historique des relances
- Calcul des ratios de recouvrement
- Génération d'écritures comptables

### US-OP-011: En tant que gestionnaire, je veux analyser la performance du recouvrement
**Critères d'acceptation :**
- Calcul des indicateurs de performance
- Analyse des délais de recouvrement
- Identification des clients à risque
- Représentation graphique des performances
- Génération de rapports de performance
- Comparaison entre périodes

### US-OP-012: En tant que gestionnaire, je veux gérer le règlement des dettes fournisseurs
**Critères d'acceptation :**
- Suivi des dettes fournisseurs
- Enregistrement des paiements effectués
- Gestion des échéances
- Historique des paiements
- Calcul des ratios de paiement
- Génération d'écritures comptables

### US-OP-013: En tant que gestionnaire, je veux analyser les délais de paiement
**Critères d'acceptation :**
- Calcul des délais moyens de paiement
- Analyse comparative entre fournisseurs
- Identification des écarts de comportement
- Représentation graphique des tendances
- Génération de rapports d'analyse
- Suivi des améliorations potentielles

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs effectuant les opérations
- `employes` - données des employés pour la gestion des salaires
- `fournisseurs` - données des fournisseurs pour les dettes
- `clients` - données des clients pour les créances
- `tresoreries` - données des trésoreries pour les paiements
- `mode_paiements` - données des modes de paiement
- `comptes_comptables` - données des comptes comptables
- `ecritures_comptables` - données des écritures comptables
- `stations` - données des stations
- `categories_charges` - catégories de charges

### Nouvelles tables à créer

```sql
-- Table pour les dépenses courantes
CREATE TABLE IF NOT EXISTS depenses_courantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_depense VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    categorie_charge_id UUID REFERENCES categories_charges(id),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    type_depense VARCHAR(50) NOT NULL, -- 'fixe', 'variable', 'exceptionnelle'
    date_depense DATE NOT NULL,
    montant_ht NUMERIC(18,2) NOT NULL,
    montant_tva NUMERIC(18,2) NOT NULL,
    montant_ttc NUMERIC(18,2) NOT NULL,
    montant_paye NUMERIC(18,2) DEFAULT 0,
    dette_restante NUMERIC(18,2) GENERATED ALWAYS AS (montant_ttc - montant_paye) STORED,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'Valide', 'Paye', 'PartiellementPaye', 'Annule')),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_paiement_id UUID REFERENCES tresoreries(id),
    reference_paiement VARCHAR(100), -- Numéro de facture, chèque, etc.
    description TEXT,
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_modification TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les catégories de charges
CREATE TABLE IF NOT EXISTS categories_charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_categorie VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    categorie_parente_id UUID REFERENCES categories_charges(id), -- Pour hiérarchie
    est_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les fiches de paie
CREATE TABLE IF NOT EXISTS fiches_paie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employe_id UUID REFERENCES employes(id),
    periode_paie_debut DATE NOT NULL, -- Première date du mois
    periode_paie_fin DATE NOT NULL,   -- Dernière date du mois
    mois_paie INTEGER NOT NULL,       -- Numéro du mois (1-12)
    annee_paie INTEGER NOT NULL,      -- Année
    salaire_base NUMERIC(18,2) NOT NULL,
    heures_normales INTEGER DEFAULT 0,
    heures_supplementaires INTEGER DEFAULT 0,
    taux_horaire_normales NUMERIC(10,2) DEFAULT 0,
    taux_horaire_supplementaires NUMERIC(10,2) DEFAULT 0,
    indemnite_transport NUMERIC(10,2) DEFAULT 0,
    indemnite_repas NUMERIC(10,2) DEFAULT 0,
    autres_indemnites NUMERIC(10,2) DEFAULT 0,
    avances NUMERIC(10,2) DEFAULT 0,
    total_brut NUMERIC(18,2) GENERATED ALWAYS AS (
        salaire_base + 
        (heures_normales * taux_horaire_normales) + 
        (heures_supplementaires * taux_horaire_supplementaires) + 
        indemnite_transport + indemnite_repas + autres_indemnites
    ) STORED,
    taux_cotisations_sociales NUMERIC(5,2) DEFAULT 0, -- En pourcentage
    montant_cotisations_sociales NUMERIC(10,2) GENERATED ALWAYS AS (
        (total_brut * taux_cotisations_sociales) / 100
    ) STORED,
    autres_retenu NUMERIC(10,2) DEFAULT 0,
    total_retenu NUMERIC(18,2) GENERATED ALWAYS AS (
        montant_cotisations_sociales + autres_retenu
    ) STORED,
    net_a_payer NUMERIC(18,2) GENERATED ALWAYS AS (
        total_brut - total_retenu - avances
    ) STORED,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'Valide', 'Paye')),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    utilisateur_paiement_id UUID REFERENCES utilisateurs(id),
    date_paiement DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les immobilisations et investissements
CREATE TABLE IF NOT EXISTS immobilisations_investissements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_immobilisation VARCHAR(50) UNIQUE NOT NULL,
    station_id UUID REFERENCES stations(id),
    type_objet VARCHAR(20) NOT NULL CHECK (type_objet IN ('immobilisation', 'investissement')),
    categorie_objet VARCHAR(50) NOT NULL, -- 'materiel', 'logiciel', 'vehicule', 'amenagement', etc.
    libelle VARCHAR(200) NOT NULL,
    description TEXT,
    date_acquisition DATE NOT NULL,
    date_mise_en_service DATE,
    fournisseur_id UUID REFERENCES fournisseurs(id),
    montant_ht_acquisition NUMERIC(18,2) NOT NULL,
    montant_tva_acquisition NUMERIC(18,2) NOT NULL,
    montant_ttc_acquisition NUMERIC(18,2) NOT NULL,
    duree_amortissement INTEGER DEFAULT 0, -- En années
    taux_amortissement NUMERIC(5,2) DEFAULT 0, -- En pourcentage
    valeur_nette_comptable NUMERIC(18,2) NOT NULL, -- Valeur à l'acquisition
    valeur_residuelle NUMERIC(18,2) DEFAULT 0, -- Valeur résiduelle estimée
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Cession', 'HorsService', 'Achete', 'Vendu')),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des amortissements
CREATE TABLE IF NOT EXISTS suivis_amortissements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    immobilisation_id UUID REFERENCES immobilisations_investissements(id),
    annee_amortissement INTEGER NOT NULL,
    mois_amortissement INTEGER NOT NULL,
    montant_amortissement NUMERIC(18,2) NOT NULL,
    valeur_nette_comptable_fin NUMERIC(18,2) NOT NULL,
    utilisateur_calcul_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les créances clients
CREATE TABLE IF NOT EXISTS creances_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_creance VARCHAR(50) NOT NULL, -- 'facture', 'avoir', 'avance', etc.
    numero_creance VARCHAR(50) NOT NULL, -- Numéro de facture ou autre
    date_creation DATE NOT NULL,
    date_echeance DATE NOT NULL,
    montant_initial NUMERIC(18,2) NOT NULL,
    montant_restant NUMERIC(18,2) NOT NULL,
    montant_paye NUMERIC(18,2) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Paye', 'Partiel', 'Echu', 'Douteux', 'Perdu')),
    nb_relances INTEGER DEFAULT 0,
    derniere_relance DATE,
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les règlements des créances
CREATE TABLE IF NOT EXISTS reglements_creances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creance_id UUID REFERENCES creances_clients(id),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_paiement_id UUID REFERENCES tresoreries(id),
    montant_reglement NUMERIC(18,2) NOT NULL,
    date_reglement DATE NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    reference_reglement VARCHAR(100),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les dettes fournisseurs
CREATE TABLE IF NOT EXISTS dettes_fournisseurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    type_dette VARCHAR(50) NOT NULL, -- 'facture', 'achat', 'avance', etc.
    numero_dette VARCHAR(50) NOT NULL, -- Numéro de facture ou autre
    date_creation DATE NOT NULL,
    date_echeance DATE NOT NULL,
    montant_initial NUMERIC(18,2) NOT NULL,
    montant_restant NUMERIC(18,2) NOT NULL,
    montant_paye NUMERIC(18,2) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'EnCours' CHECK (statut IN ('EnCours', 'Paye', 'Partiel', 'Echu', 'Contestee')),
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les règlements des dettes
CREATE TABLE IF NOT EXISTS reglements_dettes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dette_id UUID REFERENCES dettes_fournisseurs(id),
    mode_paiement_id UUID REFERENCES mode_paiements(id),
    tresorerie_paiement_id UUID REFERENCES tresoreries(id),
    montant_reglement NUMERIC(18,2) NOT NULL,
    date_reglement DATE NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    reference_reglement VARCHAR(100),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse des performances
CREATE TABLE IF NOT EXISTS analyses_performances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_analyse VARCHAR(50) NOT NULL, -- 'charges', 'recouvrement', 'paiement', 'productivite'
    periode_analyse_debut DATE NOT NULL,
    periode_analyse_fin DATE NOT NULL,
    donnees_analyse JSONB, -- Données brutes de l'analyse
    resultats_analyse JSONB, -- Résultats de l'analyse (chiffres clés, tendances)
    interpretations TEXT, -- Interprétations des résultats
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    station_id UUID REFERENCES stations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les dépenses courantes
CREATE INDEX IF NOT EXISTS idx_depenses_courantes_station ON depenses_courantes(station_id);
CREATE INDEX IF NOT EXISTS idx_depenses_courantes_fournisseur ON depenses_courantes(fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_depenses_courantes_categorie ON depenses_courantes(categorie_charge_id);
CREATE INDEX IF NOT EXISTS idx_depenses_courantes_date ON depenses_courantes(date_depense);
CREATE INDEX IF NOT EXISTS idx_depenses_courantes_statut ON depenses_courantes(statut);

-- Index pour les catégories de charges
CREATE INDEX IF NOT EXISTS idx_categories_charges_parente ON categories_charges(categorie_parente_id);

-- Index pour les fiches de paie
CREATE INDEX IF NOT EXISTS idx_fiches_paie_employe ON fiches_paie(employe_id);
CREATE INDEX IF NOT EXISTS idx_fiches_paie_periode ON fiches_paie(periode_paie_debut, periode_paie_fin);
CREATE INDEX IF NOT EXISTS idx_fiches_paie_mois_annee ON fiches_paie(mois_paie, annee_paie);

-- Index pour les immobilisations
CREATE INDEX IF NOT EXISTS idx_immobilisations_station ON immobilisations_investissements(station_id);
CREATE INDEX IF NOT EXISTS idx_immobilisations_fournisseur ON immobilisations_investissements(fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_immobilisations_type ON immobilisations_investissements(type_objet);
CREATE INDEX IF NOT EXISTS idx_immobilisations_statut ON immobilisations_investissements(statut);

-- Index pour le suivi des amortissements
CREATE INDEX IF NOT EXISTS idx_suivis_amortissements_immobilisation ON suivis_amortissements(immobilisation_id);
CREATE INDEX IF NOT EXISTS idx_suivis_amortissements_periode ON suivis_amortissements(annee_amortissement, mois_amortissement);

-- Index pour les créances clients
CREATE INDEX IF NOT EXISTS idx_creances_clients_client ON creances_clients(client_id);
CREATE INDEX IF NOT EXISTS idx_creances_clients_date ON creances_clients(date_creation);
CREATE INDEX IF NOT EXISTS idx_creances_clients_echeance ON creances_clients(date_echeance);
CREATE INDEX IF NOT EXISTS idx_creances_clients_statut ON creances_clients(statut);

-- Index pour les règlements des créances
CREATE INDEX IF NOT EXISTS idx_reglements_creances_creance ON reglements_creances(creance_id);
CREATE INDEX IF NOT EXISTS idx_reglements_creances_date ON reglements_creances(date_reglement);

-- Index pour les dettes fournisseurs
CREATE INDEX IF NOT EXISTS idx_dettes_fournisseurs_fournisseur ON dettes_fournisseurs(fournisseur_id);
CREATE INDEX IF NOT EXISTS idx_dettes_fournisseurs_date ON dettes_fournisseurs(date_creation);
CREATE INDEX IF NOT EXISTS idx_dettes_fournisseurs_echeance ON dettes_fournisseurs(date_echeance);
CREATE INDEX IF NOT EXISTS idx_dettes_fournisseurs_statut ON dettes_fournisseurs(statut);

-- Index pour les règlements des dettes
CREATE INDEX IF NOT EXISTS idx_reglements_dettes_dette ON reglements_dettes(dette_id);
CREATE INDEX IF NOT EXISTS idx_reglements_dettes_date ON reglements_dettes(date_reglement);

-- Index pour les analyses de performances
CREATE INDEX IF NOT EXISTS idx_analyses_performances_type ON analyses_performances(type_analyse);
CREATE INDEX IF NOT EXISTS idx_analyses_performances_periode ON analyses_performances(periode_analyse_debut, periode_analyse_fin);
CREATE INDEX IF NOT EXISTS idx_analyses_performances_station ON analyses_performances(station_id);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour générer automatiquement le numéro de dépense
CREATE OR REPLACE FUNCTION generate_numero_depense()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : DEP-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_depense, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_depense FROM 5 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM depenses_courantes
    WHERE SUBSTRING(numero_depense FROM 5 FOR 8) = date_str;
    
    numero := 'DEP-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    NEW.numero_depense := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_depense
    BEFORE INSERT ON depenses_courantes
    FOR EACH ROW EXECUTE FUNCTION generate_numero_depense();

-- Trigger pour générer automatiquement le numéro d'immobilisation/investissement
CREATE OR REPLACE FUNCTION generate_numero_immobilisation()
RETURNS TRIGGER AS $$
DECLARE
    date_str VARCHAR(8);
    sequence_num INTEGER;
    numero VARCHAR(50);
BEGIN
    -- Format : IMMO-AAAAMMJJ-XXX ou INV-AAAAMMJJ-XXX
    date_str := TO_CHAR(NEW.date_acquisition, 'YYYYMMDD');
    
    -- Trouver le prochain numéro de séquence pour cette date
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_immobilisation FROM 6 FOR 8) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM immobilisations_investissements
    WHERE SUBSTRING(numero_immobilisation FROM 6 FOR 8) = date_str;
    
    IF NEW.type_objet = 'immobilisation' THEN
        numero := 'IMMO-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    ELSE
        numero := 'INV-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    END IF;
    
    NEW.numero_immobilisation := numero;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_generate_numero_immobilisation
    BEFORE INSERT ON immobilisations_investissements
    FOR EACH ROW EXECUTE FUNCTION generate_numero_immobilisation();

-- Trigger pour empêcher la modification d'une dépense validée
CREATE OR REPLACE FUNCTION prevent_depense_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'une dépense validée, payée ou annulée
    IF OLD.statut = 'Valide' OR OLD.statut = 'Paye' OR OLD.statut = 'Annule' THEN
        RAISE EXCEPTION 'Impossible de modifier une dépense déjà validée, payée ou annulée';
    END IF;

    NEW.updated_at := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Devrait être mis à jour avec l'utilisateur réel

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_depense_modification
    BEFORE UPDATE ON depenses_courantes
    FOR EACH ROW EXECUTE FUNCTION prevent_depense_modification();

-- Trigger pour empêcher la modification d'une fiche de paie validée
CREATE OR REPLACE FUNCTION prevent_fiche_paie_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'une fiche de paie validée ou payée
    IF OLD.statut = 'Valide' OR OLD.statut = 'Paye' THEN
        RAISE EXCEPTION 'Impossible de modifier une fiche de paie déjà validée ou payée';
    END IF;

    NEW.updated_at := now();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_fiche_paie_modification
    BEFORE UPDATE ON fiches_paie
    FOR EACH ROW EXECUTE FUNCTION prevent_fiche_paie_modification();

-- Trigger pour mettre à jour la trésorerie après un paiement de dépense
CREATE OR REPLACE FUNCTION update_tresorerie_depense()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour le solde de la trésorerie concernée
    IF NEW.statut = 'Paye' OR NEW.statut = 'PartiellementPaye' THEN
        UPDATE tresoreries
        SET 
            solde_theorique = solde_theorique - NEW.montant_paye,
            solde_reel = solde_reel - NEW.montant_paye
        WHERE id = NEW.tresorerie_paiement_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tresorerie_depense
    AFTER UPDATE ON depenses_courantes
    FOR EACH ROW EXECUTE FUNCTION update_tresorerie_depense();

-- Trigger pour calculer automatiquement le montant payé et la dette restante
CREATE OR REPLACE FUNCTION update_dette_depense()
RETURNS TRIGGER AS $$
DECLARE
    total_paiements NUMERIC(18,2);
BEGIN
    -- Calculer le total des paiements pour cette dépense
    SELECT COALESCE(SUM(montant_reglement), 0)
    INTO total_paiements
    FROM reglements_creances
    WHERE creance_id = NEW.id;

    -- Mettre à jour le montant payé et la dette restante dans la table des dépenses
    UPDATE depenses_courantes
    SET 
        montant_paye = total_paiements,
        dette_restante = montant_ttc - total_paiements
    WHERE id = NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_dette_depense
    AFTER INSERT OR UPDATE OR DELETE ON reglements_creances
    FOR EACH ROW EXECUTE FUNCTION update_dette_depense();
```

## 4. API Backend

### 4.1 Gestion des dépenses courantes

#### POST /api/operations/depenses-courantes
**Description:** Créer une nouvelle dépense courante

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "fournisseur_id": "uuid",
  "categorie_charge_id": "uuid",
  "type_depense": "fixe|variable|exceptionnelle",
  "date_depense": "date (format YYYY-MM-DD)",
  "montant_ht": "decimal (max 18,2)",
  "montant_tva": "decimal (max 18,2)",
  "description": "string (optionnel)",
  "mode_paiement_id": "uuid (optionnel)",
  "tresorerie_paiement_id": "uuid (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_depense": "string",
    "station_id": "uuid",
    "fournisseur_id": "uuid",
    "categorie_charge_id": "uuid",
    "type_depense": "string",
    "date_depense": "date",
    "montant_ht": "decimal",
    "montant_tva": "decimal",
    "montant_ttc": "decimal",
    "montant_paye": "decimal",
    "dette_restante": "decimal",
    "statut": "string",
    "description": "string",
    "created_at": "datetime"
  },
  "message": "Dépense courante créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Dépense créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/fournisseur/catégorie non trouvé
- 500: Erreur interne du serveur

#### POST /api/operations/depenses-courantes/{id}/valider
**Description:** Valider une dépense courante

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:** Empty

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_depense": "string",
    "statut": "Valide",
    "utilisateur_validation_id": "uuid",
    "date_validation": "date"
  },
  "message": "Dépense courante validée avec succès"
}
```

**HTTP Status Codes:**
- 200: Dépense validée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépense non trouvée
- 409: Dépense déjà validée ou annulée
- 500: Erreur interne du serveur

#### POST /api/operations/depenses-courantes/{id}/paiement
**Description:** Enregistrer un paiement pour une dépense

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "mode_paiement_id": "uuid",
  "tresorerie_paiement_id": "uuid",
  "montant_paiement": "decimal (max 18,2)",
  "date_paiement": "date (format YYYY-MM-DD)",
  "reference_paiement": "string (optionnel)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "depense_id": "uuid",
    "mode_paiement_id": "uuid",
    "tresorerie_paiement_id": "uuid",
    "montant_paiement": "decimal",
    "date_paiement": "date",
    "reference_paiement": "string",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Paiement enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Paiement enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Dépense/mode_paiement/tresorerie non trouvé
- 409: Montant de paiement supérieur à la dette restante
- 500: Erreur interne du serveur

### 4.2 Gestion des salaires et paies

#### POST /api/operations/fiches-paie
**Description:** Créer une nouvelle fiche de paie

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "employe_id": "uuid",
  "periode_paie_debut": "date (format YYYY-MM-DD)",
  "periode_paie_fin": "date (format YYYY-MM-DD)",
  "salaire_base": "decimal (max 18,2)",
  "heures_normales": "integer",
  "heures_supplementaires": "integer",
  "taux_horaire_normales": "decimal (max 10,2)",
  "taux_horaire_supplementaires": "decimal (max 10,2)",
  "indemnite_transport": "decimal (max 10,2) (optionnel)",
  "indemnite_repas": "decimal (max 10,2) (optionnel)",
  "autres_indemnites": "decimal (max 10,2) (optionnel)",
  "avances": "decimal (max 10,2) (optionnel)",
  "taux_cotisations_sociales": "decimal (max 5,2)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employe_id": "uuid",
    "periode_paie_debut": "date",
    "periode_paie_fin": "date",
    "mois_paie": "integer",
    "annee_paie": "integer",
    "salaire_base": "decimal",
    "heures_normales": "integer",
    "heures_supplementaires": "integer",
    "taux_horaire_normales": "decimal",
    "taux_horaire_supplementaires": "decimal",
    "indemnite_transport": "decimal",
    "indemnite_repas": "decimal",
    "autres_indemnites": "decimal",
    "avances": "decimal",
    "total_brut": "decimal",
    "taux_cotisations_sociales": "decimal",
    "montant_cotisations_sociales": "decimal",
    "autres_retenu": "decimal",
    "total_retenu": "decimal",
    "net_a_payer": "decimal",
    "statut": "Brouillon",
    "created_at": "datetime"
  },
  "message": "Fiche de paie créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Fiche de paie créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Employé non trouvé
- 500: Erreur interne du serveur

### 4.3 Gestion des immobilisations et investissements

#### POST /api/operations/immobilisations
**Description:** Créer une nouvelle immobilisation ou investissement

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "station_id": "uuid",
  "type_objet": "immobilisation|investissement",
  "categorie_objet": "materiel|logiciel|vehicule|amenagement|etc.",
  "libelle": "string (max 200)",
  "description": "text (optionnel)",
  "date_acquisition": "date (format YYYY-MM-DD)",
  "date_mise_en_service": "date (format YYYY-MM-DD) (optionnel)",
  "fournisseur_id": "uuid (optionnel)",
  "montant_ht_acquisition": "decimal (max 18,2)",
  "montant_tva_acquisition": "decimal (max 18,2)",
  "duree_amortissement": "integer (optionnel)",
  "taux_amortissement": "decimal (max 5,2) (optionnel)",
  "valeur_nette_comptable": "decimal (max 18,2)",
  "valeur_residuelle": "decimal (max 18,2) (optionnel)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "numero_immobilisation": "string",
    "station_id": "uuid",
    "type_objet": "string",
    "categorie_objet": "string",
    "libelle": "string",
    "description": "text",
    "date_acquisition": "date",
    "date_mise_en_service": "date",
    "fournisseur_id": "uuid",
    "montant_ht_acquisition": "decimal",
    "montant_tva_acquisition": "decimal",
    "montant_ttc_acquisition": "decimal",
    "duree_amortissement": "integer",
    "taux_amortissement": "decimal",
    "valeur_nette_comptable": "decimal",
    "valeur_residuelle": "decimal",
    "statut": "string",
    "commentaire": "text",
    "created_at": "datetime"
  },
  "message": "Immobilisation/investissement créé(e) avec succès"
}
```

**HTTP Status Codes:**
- 201: Immobilisation/investissement créé(e) avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Station/fournisseur non trouvé
- 500: Erreur interne du serveur

### 4.4 Gestion du recouvrement des créances

#### POST /api/operations/creances
**Description:** Créer une nouvelle créance client

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "client_id": "uuid",
  "type_creance": "facture|avoir|avance|etc.",
  "numero_creance": "string (max 50)",
  "date_creation": "date (format YYYY-MM-DD)",
  "date_echeance": "date (format YYYY-MM-DD)",
  "montant_initial": "decimal (max 18,2)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "client_id": "uuid",
    "type_creance": "string",
    "numero_creance": "string",
    "date_creation": "date",
    "date_echeance": "date",
    "montant_initial": "decimal",
    "montant_restant": "decimal",
    "montant_paye": "decimal",
    "statut": "EnCours",
    "nb_relances": 0,
    "commentaire": "text",
    "created_at": "datetime"
  },
  "message": "Créance client créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Créance créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Client non trouvé
- 500: Erreur interne du serveur

#### POST /api/operations/creances/{id}/reglement
**Description:** Enregistrer un règlement pour une créance

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "mode_paiement_id": "uuid",
  "tresorerie_paiement_id": "uuid",
  "montant_reglement": "decimal (max 18,2)",
  "date_reglement": "date (format YYYY-MM-DD)",
  "reference_reglement": "string (optionnel)",
  "commentaire": "string (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "creance_id": "uuid",
    "mode_paiement_id": "uuid",
    "tresorerie_paiement_id": "uuid",
    "montant_reglement": "decimal",
    "date_reglement": "date",
    "reference_reglement": "string",
    "commentaire": "string",
    "created_at": "datetime"
  },
  "message": "Règlement de créance enregistré avec succès"
}
```

**HTTP Status Codes:**
- 200: Règlement enregistré avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Créance/mode_paiement/tresorerie non trouvé
- 409: Montant de règlement supérieur au montant restant
- 500: Erreur interne du serveur

### 4.5 Gestion des dettes fournisseurs

#### POST /api/operations/dettes
**Description:** Créer une nouvelle dette fournisseur

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "fournisseur_id": "uuid",
  "type_dette": "facture|achat|avance|etc.",
  "numero_dette": "string (max 50)",
  "date_creation": "date (format YYYY-MM-DD)",
  "date_echeance": "date (format YYYY-MM-DD)",
  "montant_initial": "decimal (max 18,2)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "fournisseur_id": "uuid",
    "type_dette": "string",
    "numero_dette": "string",
    "date_creation": "date",
    "date_echeance": "date",
    "montant_initial": "decimal",
    "montant_restant": "decimal",
    "montant_paye": "decimal",
    "statut": "EnCours",
    "commentaire": "text",
    "created_at": "datetime"
  },
  "message": "Dette fournisseur créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Dette créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Fournisseur non trouvé
- 500: Erreur interne du serveur

### 4.6 Analyses de performance

#### GET /api/operations/analyses-performances
**Description:** Obtenir les analyses de performance

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- type_analyse: charges|recouvrement|paiement|productivite (optionnel)
- periode_debut: date (format YYYY-MM-DD) (optionnel)
- periode_fin: date (format YYYY-MM-DD) (optionnel)
- station_id: uuid (optionnel)

**Response:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": "uuid",
        "type_analyse": "string",
        "periode_analyse_debut": "date",
        "periode_analyse_fin": "date",
        "donnees_analyse": "jsonb",
        "resultats_analyse": "jsonb",
        "interpretations": "string",
        "utilisateur_createur_id": "uuid"
      }
    ]
  },
  "message": "Analyses de performance récupérées avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de gestion des dépenses courantes
1. Les dépenses doivent être catégorisées selon des catégories prédéfinies
2. Les paiements peuvent être immédiats, partiels ou différés
3. Les écritures comptables sont générées automatiquement
4. Les seuils d'approbation peuvent être requis pour certaines catégories ou montants
5. L'historique des modifications est maintenu

### Règles de gestion des salaires
1. Les calculs de paie suivent les règles fiscales et sociales en vigueur
2. Les heures supplémentaires sont majorées selon les conventions en vigueur
3. Les charges sociales sont calculées automatiquement
4. Les fiches de paie sont historisées pour référence
5. Les avances sont déduites du net à payer

### Règles de gestion des immobilisations
1. L'amortissement est calculé selon les règles comptables
2. La valeur résiduelle est estimée à l'acquisition
3. Les mouvements d'immobilisations sont tracés
4. Les écritures comptables de réévaluation peuvent être générées
5. Le statut des immobilisations est mis à jour selon leur état (actif, cédé, hors service)

### Règles de gestion des créances
1. Les échéances sont gérées selon les conditions de paiement
2. Les relances sont programmées automatiquement
3. Les créances douteuses sont identifiées
4. Les provisions pour créances douteuses peuvent être calculées
5. Les règlements sont enregistrés et affectés aux créances appropriées

### Règles de gestion des dettes
1. Les délais de paiement sont suivis
2. Les fournisseurs sont classés selon leur performance
3. Les échéances sont gérées pour optimiser la trésorerie
4. Les règlements sont enregistrés et affectés aux dettes appropriées
5. Les retards de paiement sont signalés

### Règles de validation des données
1. Les montants doivent être positifs
2. Les dates doivent être valides
3. Les associations avec d'autres entités doivent exister
4. Les montants de paiement ne peuvent pas dépasser les montants dus
5. Les statuts sont gérés selon des workflows prédéfinis

### Impacts sur d'autres modules
1. Le module d'opérations affecte les modules de trésorerie (mouvements)
2. Le module d'opérations affecte le module comptable (écritures)
3. Le module d'opérations affecte les modules de reporting (analyses)
4. Le module d'opérations affecte le module de gestion des employés
5. Le module d'opérations fournit des données aux modules de gestion des stocks

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ depenses_courantes
utilisateurs ||--o{ fiches_paie
utilisateurs ||--o{ immobilisations_investissements
fournisseurs ||--o{ depenses_courantes
fournisseurs ||--o{ immobilisations_investissements
fournisseurs ||--o{ dettes_fournisseurs
clients ||--o{ creances_clients
employes ||--o{ fiches_paie
stations ||--o{ depenses_courantes
stations ||--o{ immobilisations_investissements
tresoreries ||--o{ depenses_courantes
tresoreries ||--o{ reglements_creances
mode_paiements ||--o{ depenses_courantes
comptes_comptables ||--o{ ecritures_comptables
categories_charges ||--o{ depenses_courantes
depenses_courantes ||--o{ reglements_creances
creances_clients ||--o{ reglements_creances
dettes_fournisseurs ||--o{ reglements_dettes
analyses_performances }o--o{ stations
```

### Diagramme de séquence pour une dépense courante
```
Gestionnaire -> API: POST /api/operations/depenses-courantes
API -> Base de données: Créer la dépense (statut: Brouillon)
API -> Gestionnaire: Retourner la dépense créée

Gestionnaire -> API: POST /api/operations/depenses-courantes/{id}/valider
API -> Base de données: Valider la dépense
API -> API: Générer l'écriture comptable
API -> Gestionnaire: Retourner confirmation de validation

Gestionnaire -> API: POST /api/operations/depenses-courantes/{id}/paiement
API -> Base de données: Enregistrer le paiement
API -> Base de données: Mettre à jour la dette restante
API -> Base de données: Mettre à jour la trésorerie
API -> API: Générer l'écriture comptable de paiement
API -> Gestionnaire: Retourner confirmation de paiement
```

## 7. Tests Requises

### Tests unitaires
1. Test de la fonction de génération automatique de numéro de dépense
2. Test des validations de données pour les différents endpoints
3. Test des calculs de paie (brut, net, cotisations)
4. Test des calculs d'amortissement
5. Test des validations de montants et dates
6. Test des fonctions de mise à jour de trésorerie

### Tests d'intégration
1. Test complet du processus de dépense courante
2. Test complet du processus de paie
3. Test complet du processus d'immobilisation
4. Test complet du processus de recouvrement des créances
5. Test complet du processus de règlement des dettes
6. Test de l'analyse des performances

### Tests de charge/performance
1. Test de performance pour des centaines de dépenses simultanées
2. Test de performance pour des calculs de paie complexes
3. Test de performance pour des analyses de tendances
4. Test de performance pour des règlements multiples
5. Test de la génération d'écritures comptables pour de grands volumes

### Jeux de données de test
1. Données de dépenses valides avec différentes configurations
2. Données d'employés avec différents profils de paie
3. Données d'immobilisations avec différents types et durées
4. Données de clients/fournisseurs avec différents statuts
5. Données de trésoreries et de modes de paiement
6. Données historiques pour les tests d'analyse

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour chaque fonctionnalité
5. [ ] Créer les services de gestion (dépenses, paie, immobilisations, etc.)
6. [ ] Implémenter la logique de validation des données
7. [ ] Créer les utilitaires de génération d'écritures comptables
8. [ ] Implémenter la gestion de la trésorerie
9. [ ] Créer les algorithmes de calcul (paie, amortissement, etc.)
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion des opérations (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec les modules de reporting pour les analyses
15. [ ] Intégrer avec le module comptable pour les écritures

### Ordre recommandé
1. Commencer par la création des tables et modèles
2. Implémenter les endpoints de base pour les dépenses courantes
3. Développer les fonctionnalités de paie
4. Implémenter la gestion des immobilisations
5. Créer les fonctionnalités de gestion des créances et dettes
6. Développer les analyses de performance
7. Intégrer avec les modules de trésorerie et comptable
8. Créer les tests
9. Optimiser les performances
10. Documenter la solution

### Livrables attendus
1. Code source complet avec commentaires
2. Scripts de migration de base de données
3. Documentation API
4. Jeux de tests et résultats
5. Documentation technique détaillée
6. Guide d'installation et de déploiement

## 9. Risques & Points de vigilance

### Points sensibles
1. La précision des calculs de paie selon les règles fiscales et sociales
2. La gestion des amortissements selon les règles comptables
3. La sécurité des données financières sensibles
4. La performance des calculs pour de grands volumes de données
5. La cohérence des écritures comptables générées automatiquement

### Risques techniques
1. Risque d'erreurs dans les calculs de paie ou d'amortissement
2. Risque de non-conformité aux règles fiscales et sociales
3. Risque de problèmes de performances avec de grands volumes
4. Risque de perte de données en cas de panne pendant les processus
5. Risque de manipulation des données par des utilisateurs non autorisés
6. Risque d'incohérence entre les modules si les intégrations ne sont pas correctes

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples règles de gestion
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les règles de paie et fiscales
4. Risque de dépendance excessive à des bibliothèques tierces pour les calculs complexes
5. Besoin d'ajustements fréquents des paramètres selon les évolutions réglementaires