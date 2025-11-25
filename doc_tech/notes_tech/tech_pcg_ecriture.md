# Technical Specification - Plan comptable et écritures

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer le plan comptable et les écritures comptables pour assurer la conformité fiscale et comptable de la station-service. L'objectif est de permettre une comptabilité rigoureuse et conforme aux systèmes locaux (OHADA, etc.), avec une journalisation automatique des opérations métier et la génération d'états financiers fiables.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module comptable complet permettant :
- De gérer un plan comptable selon les systèmes locaux (OHADA, etc.)
- De générer automatiquement des écritures comptables correctes
- De valider la cohérence des écritures comptables
- De produire des états financiers fiables

### Définition du périmètre
Le périmètre inclut :
- Gestion du plan comptable avec hiérarchie et types appropriés
- Génération automatique des écritures comptables
- Validation des écritures selon les règles comptables
- Journalisation des opérations comptables
- Numérotation automatique des pièces comptables
- Contrôle de la cohérence des écritures
- Calcul des soldes des comptes
- Génération des états financiers
- Validation de l'équilibre comptable

## 2. User Stories & Critères d'acceptation

### US-PCG-001: En tant que comptable, je veux gérer le plan comptable
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des comptes
  - Chaque compte a un numéro unique, intitulé, classe, type
  - Pouvoir définir une hiérarchie entre comptes (parent/enfant)
  - Pouvoir affecter un compte à un pays spécifique
  - Pouvoir distinguer les comptes de bilan et de résultat

### US-PCG-002: En tant que comptable, je veux que les écritures soient générées automatiquement
- **Critères d'acceptation :**
  - Chaque opération métier génère des écritures comptables correspondantes
  - Les écritures respectent les règles comptables
  - Les écritures sont affectées aux bons comptes
  - Le montant total des débits égale le montant total des crédits

### US-PCG-003: En tant que comptable, je veux valider les écritures comptables
- **Critères d'acceptation :**
  - Pouvoir valider les écritures avant leur comptabilisation
  - Pouvoir corriger les écritures invalides
  - Les écritures doivent avoir un journal et une date correcte
  - Les écritures doivent respecter les règles de base (équilibre)

### US-PCG-004: En tant que comptable, je veux gérer les journaux comptables
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des journaux
  - Chaque journal a un code unique et une description
  - Pouvoir associer des journaux aux types d'opérations (achats, ventes, trésorerie)
  - Les journaux permettent une classification des écritures

### US-PCG-005: En tant que comptable, je veux avoir une numérotation automatique des pièces
- **Critères d'acceptation :**
  - Chaque écriture est affectée à un numéro de pièce comptable
  - Le système génère automatiquement les numéros
  - Les numéros respectent une séquence logique
  - Les numéros sont uniques par journal

### US-PCG-006: En tant que gestionnaire, je veux visualiser les soldes des comptes
- **Critères d'acceptation :**
  - Pouvoir consulter les soldes de tous les comptes
  - Pouvoir filtrer par période
  - Pouvoir consulter les mouvements détaillés
  - Les soldes sont calculés en temps réel

### US-PCG-007: En tant que gestionnaire, je veux accéder aux états financiers
- **Critères d'acceptation :**
  - Pouvoir générer le bilan
  - Pouvoir générer le compte de résultat
  - Les états financiers sont correctement équilibrés
  - Les états peuvent être filtrés par période

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: plan_comptable (existant dans le schéma)
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

-- Index pour les performances
CREATE INDEX idx_plan_comptable_numero ON plan_comptable(numero);
CREATE INDEX idx_plan_comptable_classe ON plan_comptable(classe);
CREATE INDEX idx_plan_comptable_type ON plan_comptable(type_compte);
CREATE INDEX idx_plan_comptable_parent ON plan_comptable(compte_parent_id);
CREATE INDEX idx_plan_comptable_pays ON plan_comptable(pays_id);
CREATE INDEX idx_plan_comptable_statut ON plan_comptable(statut);
```

#### Table: journaux
```sql
CREATE TABLE journaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,             -- Code du journal (ex: ACH, VTE, BQ, CAI)
    libelle VARCHAR(100) NOT NULL,                -- Libellé du journal (ex: Journal des achats)
    description TEXT,
    pays_id UUID REFERENCES pays(id),             -- Journal spécifique à un pays
    compagnie_id UUID REFERENCES compagnies(id),  -- Journal spécifique à une compagnie
    type_journal VARCHAR(50) NOT NULL CHECK (type_journal IN ('achats', 'ventes', 'tresorerie', 'banque', 'caisse', 'opex', 'stock', 'autre')), -- Type d'opérations
    derniere_piece INTEGER DEFAULT 0,             -- Dernier numéro de pièce affecté
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
```

#### Table: ecritures_comptables
```sql
CREATE TABLE ecritures_comptables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_id UUID NOT NULL REFERENCES journaux(id),
    numero_piece VARCHAR(50) NOT NULL,           -- Numéro de pièce comptable (ex: ACH-202501-001)
    date_ecriture DATE NOT NULL,
    libelle TEXT NOT NULL,
    montant_debit NUMERIC(18,2) DEFAULT 0,
    montant_credit NUMERIC(18,2) DEFAULT 0,
    tiers_id UUID,                               -- Référence au tiers (client/fournisseur) si applicable
    utilisateur_id UUID REFERENCES utilisateurs(id),  -- Utilisateur qui a créé l'écriture
    operation_id UUID,                           -- Référence à l'opération métier (achat, vente, etc.)
    operation_type VARCHAR(50),                  -- Type d'opération métier
    est_validee BOOLEAN DEFAULT FALSE,           -- Indique si l'écriture est validée
    est_cloturee BOOLEAN DEFAULT FALSE,          -- Indique si l'écriture fait partie d'une clôture
    date_validation TIMESTAMPTZ,                 -- Date de validation si applicable
    utilisateur_validation_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a validé
    reference_externe VARCHAR(100),              -- Référence externe (numéro de facture, etc.)
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
```

#### Table: lignes_ecritures
```sql
CREATE TABLE lignes_ecritures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ecriture_id UUID NOT NULL REFERENCES ecritures_comptables(id) ON DELETE CASCADE,
    compte_id UUID NOT NULL REFERENCES plan_comptable(id),
    montant_debit NUMERIC(18,2) DEFAULT 0,
    montant_credit NUMERIC(18,2) DEFAULT 0,
    libelle TEXT,                                -- Libellé spécifique de la ligne
    tiers_id UUID,                               -- Référence au tiers spécifique pour cette ligne
    projet_id UUID,                              -- Référence au projet si applicable
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
```

#### Table: soldes_comptes
```sql
CREATE TABLE soldes_comptes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compte_id UUID NOT NULL REFERENCES plan_comptable(id),
    date_solde DATE NOT NULL,
    solde_debit NUMERIC(18,2) DEFAULT 0,
    solde_credit NUMERIC(18,2) DEFAULT 0,
    solde_net NUMERIC(18,2) GENERATED ALWAYS AS (solde_debit - solde_credit) STORED, -- Calcul automatique
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
```

### 3.2 Relations
- `journaux.pays_id` → `pays.id` (One-to-Many)
- `journaux.compagnie_id` → `compagnies.id` (One-to-Many)
- `ecritures_comptables.journal_id` → `journaux.id` (One-to-Many)
- `ecritures_comptables.tiers_id` → `fournisseurs.id` ou `clients.id` (One-to-Many)
- `ecritures_comptables.utilisateur_id` → `utilisateurs.id` (One-to-Many)
- `ecritures_comptables.utilisateur_validation_id` → `utilisateurs.id` (One-to-Many)
- `lignes_ecritures.ecriture_id` → `ecritures_comptables.id` (One-to-Many)
- `lignes_ecritures.compte_id` → `plan_comptable.id` (One-to-Many)
- `lignes_ecritures.tiers_id` → `fournisseurs.id` ou `clients.id` (One-to-Many)
- `soldes_comptes.compte_id` → `plan_comptable.id` (One-to-Many)
- `soldes_comptes.compagnie_id` → `compagnies.id` (One-to-Many)

### 3.3 Triggers et règles d'intégrité
```sql
-- Trigger pour valider l'équilibre des écritures comptables
CREATE OR REPLACE FUNCTION verif_equilibre_ecriture()
RETURNS TRIGGER AS $$
DECLARE
    total_debit NUMERIC(18,2);
    total_credit NUMERIC(18,2);
BEGIN
    -- Calculer les totaux débit et crédit des lignes pour cette écriture
    SELECT 
        COALESCE(SUM(montant_debit), 0), 
        COALESCE(SUM(montant_credit), 0)
    INTO total_debit, total_credit
    FROM lignes_ecritures 
    WHERE ecriture_id = NEW.id OR ecriture_id = OLD.id;
    
    -- Vérifier l'équilibre
    IF total_debit != total_credit THEN
        RAISE EXCEPTION 'L''écriture comptable n''est pas équilibrée: débits (%) != crédits (%)', total_debit, total_credit;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ce trigger sera appliqué après les opérations de modification des lignes
-- pour vérifier l'équilibre de l'écriture globale

-- Trigger pour générer automatiquement le numéro de pièce
CREATE OR REPLACE FUNCTION generate_numero_piece()
RETURNS TRIGGER AS $$
DECLARE
    date_str TEXT;
    sequence_num INTEGER;
BEGIN
    -- Extraire la date au format AAAAMM
    date_str := TO_CHAR(NEW.date_ecriture, 'YYYYMM');
    
    -- Incrémenter la séquence dans la table journal
    UPDATE journaux 
    SET derniere_piece = derniere_piece + 1 
    WHERE id = NEW.journal_id
    RETURNING derniere_piece INTO sequence_num;
    
    -- Générer le numéro de pièce
    NEW.numero_piece := NEW.journal_id || '-' || date_str || '-' || LPAD(sequence_num::TEXT, 3, '0');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Application du trigger pour la génération automatique du numéro de pièce
CREATE TRIGGER trig_generate_numero_piece
    BEFORE INSERT ON ecritures_comptables
    FOR EACH ROW
    EXECUTE FUNCTION generate_numero_piece();

-- Trigger pour calculer les montants totaux dans l'écriture depuis les lignes
CREATE OR REPLACE FUNCTION update_montants_ecriture()
RETURNS TRIGGER AS $$
DECLARE
    total_debit NUMERIC(18,2);
    total_credit NUMERIC(18,2);
BEGIN
    -- Calculer les totaux débit et crédit des lignes pour cette écriture
    SELECT 
        COALESCE(SUM(montant_debit), 0), 
        COALESCE(SUM(montant_credit), 0)
    INTO total_debit, total_credit
    FROM lignes_ecritures 
    WHERE ecriture_id = NEW.ecriture_id;
    
    -- Mettre à jour les montants dans la table d'écriture
    UPDATE ecritures_comptables
    SET 
        montant_debit = total_debit,
        montant_credit = total_credit
    WHERE id = NEW.ecriture_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Application du trigger sur les insertions et mises à jour des lignes d'écriture
CREATE TRIGGER trig_update_montants_ecriture
    AFTER INSERT OR UPDATE OR DELETE ON lignes_ecritures
    FOR EACH ROW
    EXECUTE FUNCTION update_montants_ecriture();

-- Trigger pour empêcher la modification d'écritures validées
CREATE OR REPLACE FUNCTION verif_modif_ecriture_validee()
RETURNS TRIGGER AS $$
BEGIN
    -- Vérifier si l'écriture est déjà validée
    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        IF (SELECT est_validee FROM ecritures_comptables WHERE id = OLD.ecriture_id) = TRUE THEN
            RAISE EXCEPTION 'Impossible de modifier une écriture comptable déjà validée';
        END IF;
    ELSIF TG_OP = 'INSERT' THEN
        -- Vérifier si on ajoute à une écriture déjà validée
        IF (SELECT est_validee FROM ecritures_comptables WHERE id = NEW.ecriture_id) = TRUE THEN
            RAISE EXCEPTION 'Impossible de modifier une écriture comptable déjà validée';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_verif_modif_ecriture_validee_lignes
    BEFORE INSERT OR UPDATE OR DELETE ON lignes_ecritures
    FOR EACH ROW
    EXECUTE FUNCTION verif_modif_ecriture_validee();

CREATE TRIGGER trig_verif_modif_ecriture_validee_ecritures
    BEFORE UPDATE ON ecritures_comptables
    FOR EACH ROW
    EXECUTE FUNCTION verif_modif_ecriture_validee();
```

## 4. API Backend

### 4.1 Gestion du plan comptable

#### POST /api/v1/accounting/chart-of-accounts
- **Description**: Créer un nouveau compte dans le plan comptable
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "numero": "string (20 chars max)",
    "intitule": "string (255 chars max)",
    "classe": "string (5 chars max)",
    "type_compte": "string (100 chars max)",
    "sens_solde": "string (1 char, D or C)",
    "compte_parent_id": "uuid",
    "description": "string",
    "pays_id": "uuid",
    "est_specifique_pays": "boolean",
    "code_pays": "string (3 chars max)"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "numero": "string",
        "intitule": "string",
        "classe": "string",
        "type_compte": "string",
        "sens_solde": "string",
        "compte_parent_id": "uuid",
        "description": "string",
        "statut": "string",
        "est_compte_racine": "boolean",
        "est_compte_de_resultat": "boolean",
        "est_compte_actif": "boolean",
        "pays_id": "uuid",
        "est_specifique_pays": "boolean",
        "code_pays": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Numéro de compte déjà existant

#### GET /api/v1/accounting/chart-of-accounts/{account_id}
- **Description**: Récupérer les détails d'un compte du plan comptable
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "numero": "string",
        "intitule": "string",
        "classe": "string",
        "type_compte": "string",
        "sens_solde": "string",
        "compte_parent": {
            "id": "uuid",
            "numero": "string",
            "intitule": "string"
        },
        "description": "string",
        "statut": "string",
        "est_compte_racine": "boolean",
        "est_compte_de_resultat": "boolean",
        "est_compte_actif": "boolean",
        "pays_id": "uuid",
        "est_specifique_pays": "boolean",
        "code_pays": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### PUT /api/v1/accounting/chart-of-accounts/{account_id}
- **Description**: Mettre à jour un compte du plan comptable
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "intitule": "string (255 chars max)",
    "type_compte": "string (100 chars max)",
    "description": "string",
    "statut": "string"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "numero": "string",
        "intitule": "string",
        "classe": "string",
        "type_compte": "string",
        "sens_solde": "string",
        "compte_parent_id": "uuid",
        "description": "string",
        "statut": "string",
        "updated_at": "timestamp"
    }
}
```

### 4.2 Gestion des journaux

#### POST /api/v1/accounting/journals
- **Description**: Créer un nouveau journal
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "libelle": "string (100 chars max)",
    "description": "string",
    "pays_id": "uuid",
    "compagnie_id": "uuid",
    "type_journal": "string (50 chars max)"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "description": "string",
        "pays_id": "uuid",
        "compagnie_id": "uuid",
        "type_journal": "string",
        "derniere_piece": "integer",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.3 Gestion des écritures comptables

#### POST /api/v1/accounting/entries
- **Description**: Créer une nouvelle écriture comptable
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "journal_id": "uuid",
    "date_ecriture": "date",
    "libelle": "string",
    "est_validee": "boolean",
    "reference_externe": "string (100 chars max)",
    "lignes": [
        {
            "compte_id": "uuid",
            "montant_debit": "number",
            "montant_credit": "number",
            "libelle": "string",
            "tiers_id": "uuid",
            "projet_id": "uuid"
        }
    ]
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "journal_id": "uuid",
        "numero_piece": "string",
        "date_ecriture": "date",
        "libelle": "string",
        "montant_debit": "number",
        "montant_credit": "number",
        "tiers_id": "uuid",
        "utilisateur_id": "uuid",
        "operation_id": "uuid",
        "operation_type": "string",
        "est_validee": "boolean",
        "est_cloturee": "boolean",
        "reference_externe": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "lignes": [
            {
                "id": "uuid",
                "compte_id": "uuid",
                "montant_debit": "number",
                "montant_credit": "number",
                "libelle": "string",
                "tiers_id": "uuid",
                "projet_id": "uuid"
            }
        ]
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides ou écriture non équilibrée
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Numéro de pièce déjà existant

#### PUT /api/v1/accounting/entries/{entry_id}/validate
- **Description**: Valider une écriture comptable
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "est_validee": "boolean",
        "date_validation": "timestamp",
        "utilisateur_validation_id": "uuid"
    }
}
```

### 4.4 Gestion des soldes

#### GET /api/v1/accounting/balances/{account_id}
- **Description**: Récupérer le solde d'un compte
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - date_debut: "date"
  - date_fin: "date"
  - compagnie_id: "uuid"
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "compte": {
            "id": "uuid",
            "numero": "string",
            "intitule": "string"
        },
        "soldes": [
            {
                "date_solde": "date",
                "solde_debit": "number",
                "solde_credit": "number",
                "solde_net": "number",
                "type_solde": "string"
            }
        ],
        "solde_actuel": {
            "solde_debit": "number",
            "solde_credit": "number",
            "solde_net": "number"
        }
    }
}
```

## 5. Logique Métier

### 5.1 Règles de gestion du plan comptable
- Chaque compte doit avoir un numéro unique dans le plan comptable
- La hiérarchie des comptes permet une structure arborescente (comptes principaux, sous-comptes)
- Les comptes peuvent être spécifiques à un pays ou partagés entre pays
- Le système doit respecter la structure comptable OHADA ou autre système local
- Les comptes de bilan sont distingés des comptes de résultat

### 5.2 Règles de validation des écritures
- Chaque écriture comptable doit être équilibrée (total des débits = total des crédits)
- Une écriture ne peut être modifiée une fois validée
- Chaque ligne d'écriture ne peut avoir que du débit ou du crédit, jamais les deux
- Les écritures doivent être affectées à un journal approprié selon leur nature
- Les dates des écritures ne peuvent pas être antérieures à la date de clôture

### 5.3 Règles de numérotation automatique
- Le système génère automatiquement les numéros de pièces selon un format standardisé
- Le format est : {code_journal}-{année mois}-{numéro séquentiel}
- Chaque journal a sa propre séquence de numérotation
- Les numéros sont uniques par journal et par période

### 5.4 Règles de calcul des soldes
- Les soldes sont calculés en fonction des mouvements d'écritures validées
- Les soldes peuvent être calculés pour différentes périodes
- Le solde net est automatiquement calculé (débit - crédit)
- Les soldes d'ouverture sont établis à partir du bilan d'initialisation

### 5.5 Impacts sur d'autres modules
- Le module de ventes génère des écritures de vente et de TVA
- Le module d'achats génère des écritures d'achat, de TVA et de règlement
- Le module de trésorerie génère des écritures de caisse/banque
- Le module de stock génère des écritures de variation de stock

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
[pays] 1 -- * [plan_comptable]
[compagnies] 1 -- * [plan_comptable]
[plan_comptable] 1 -- * [plan_comptable] (compte parent)

[pays] 1 -- * [journaux]
[compagnies] 1 -- * [journaux]

[journaux] 1 -- * [ecritures_comptables]
[fournisseurs] 1 -- * [ecritures_comptables] (tiers)
[clients] 1 -- * [ecritures_comptables] (tiers)
[utilisateurs] 1 -- * [ecritures_comptables] (créateur)
[utilisateurs] 1 -- * [ecritures_comptables] (validateur)

[ecritures_comptables] 1 -- * [lignes_ecritures]
[plan_comptable] 1 -- * [lignes_ecritures]
[fournisseurs] 1 -- * [lignes_ecritures] (tiers)
[clients] 1 -- * [lignes_ecritures] (tiers)

[plan_comptable] 1 -- * [soldes_comptes]
[compagnies] 1 -- * [soldes_comptes]
```

### 6.2 Diagramme de séquence (génération d'une écriture comptable)
```
Système métier -> API: Déclencheur d'opération (achat, vente, etc.)
API -> Service Comptabilité: Récupérer les comptes liés à l'opération
Service Comptabilité -> Database: Rechercher les comptes appropriés
Database -> Service Comptabilité: Comptes trouvés
Service Comptabilité -> API: Informations pour écritures
API -> Database: Créer l'écriture comptable et ses lignes
Database -> API: Vérifier l'équilibre via trigger
API -> Database: Écriture validée
Database -> API: Écriture créée
API -> Système métier: Confirmation de la création
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test des validations de données pour chaque modèle
- Test des triggers de vérification d'équilibre
- Test des triggers de génération de numéros de pièce
- Test des fonctions de calcul des soldes

### 7.2 Tests d'intégration
- Test de la création complète d'une écriture comptable avec ses lignes
- Test de la validation des écritures
- Test de la génération automatique des numéros de pièce
- Test des contrôles d'équilibre des écritures
- Test de la mise à jour des soldes

### 7.3 Tests de charge/performance
- Test de la performance lors de la création de nombreuses écritures
- Test de la performance lors de la consultation des soldes pour une période

### 7.4 Jeux de données de test
```sql
-- Données de test pour le plan comptable
INSERT INTO plan_comptable (id, numero, intitule, classe, type_compte, sens_solde, description, statut, created_at, updated_at)
VALUES 
('COMPTE100-UUID', '100000', 'Capital', '1', 'Capitaux Propres', 'C', 'Capital social', 'Actif', now(), now()),
('COMPTE411-UUID', '411000', 'Clients', '4', 'Tiers', 'D', 'Compte clients', 'Actif', now(), now()),
('COMPTE401-UUID', '401000', 'Fournisseurs', '4', 'Tiers', 'C', 'Compte fournisseurs', 'Actif', now(), now()),
('COMPTE707-UUID', '707000', 'Ventes de marchandises', '7', 'Chiffre d''affaires', 'C', 'Ventes produits', 'Actif', now(), now()),
('COMPTE607-UUID', '607000', 'Achats de marchandises', '6', 'Achats', 'D', 'Achats produits', 'Actif', now(), now());

-- Données de test pour les journaux
INSERT INTO journaux (id, code, libelle, type_journal, statut, created_at, updated_at)
VALUES 
('JOURNALACH-UUID', 'ACH', 'Journal des achats', 'achats', 'Actif', now(), now()),
('JOURNALVTE-UUID', 'VTE', 'Journal des ventes', 'ventes', 'Actif', now(), now()),
('JOURNALCAI-UUID', 'CAI', 'Journal de caisse', 'caisse', 'Actif', now(), now());

-- Données de test pour une écriture comptable type
INSERT INTO ecritures_comptables (id, journal_id, date_ecriture, libelle, tiers_id, utilisateur_id, created_at, updated_at)
VALUES ('ECRITURE001-UUID', 'JOURNALVTE-UUID', '2025-01-15', 'Vente client', 'CLIENT001-UUID', 'USER001-UUID', now(), now());
```

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Création des modèles SQLAlchemy pour les tables : journaux, ecritures_comptables, lignes_ecritures, soldes_comptes
- [ ] Mise en place des relations entre les modèles
- [ ] Développement des services pour la gestion du plan comptable
- [ ] Développement des services pour la gestion des journaux
- [ ] Développement des services pour la création d'écritures comptables
- [ ] Développement des services pour la validation des écritures
- [ ] Développement des services pour la gestion des soldes
- [ ] Développement des triggers pour l'équilibre des écritures
- [ ] Développement des triggers pour la génération automatique des numéros de pièce
- [ ] Développement des triggers pour la mise à jour des montants
- [ ] Développement des endpoints API pour chaque service
- [ ] Mise en place des validations de données
- [ ] Calcul automatique des soldes
- [ ] Tests unitaires et d'intégration
- [ ] Documentation des API

### 8.2 Ordre recommandé
1. Création des modèles et migrations des tables
2. Développement des services pour la gestion du plan comptable
3. Développement des services pour la gestion des journaux
4. Développement des services pour la création des écritures
5. Mise en place des validations et contraintes
6. Développement des services pour la gestion des soldes
7. Tests et documentation

### 8.3 Livrables attendus
- Modèles SQLAlchemy pour les tables comptables
- Services backend pour la gestion comptable
- Endpoints API complets pour la gestion comptable
- Système de validation des écritures
- Système de numérotation automatique
- Documentation API
- Jeux de tests unitaires et d'intégration

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La vérification de l'équilibre des écritures comptables
- La génération automatique des numéros de pièce sans doublons
- La protection des écritures validées contre les modifications
- La performance du système avec un grand nombre d'écritures

### 9.2 Risques techniques
- Risque d'incohérence si les écritures ne sont pas équilibrées
- Risque de duplications dans les numéros de pièce
- Risque de performance lié à la mise à jour fréquente des soldes
- Risque d'erreurs si la hiérarchie des comptes n'est pas correctement respectée

### 9.3 Dette technique potentielle
- Mise en place d'automatismes pour la validation des écritures
- Mise en place de rôles spécifiques pour la validation comptable
- Mise en place d'une interface d'analyse des écarts comptables
- Mise en place de contrôles plus avancés de la cohérence comptable