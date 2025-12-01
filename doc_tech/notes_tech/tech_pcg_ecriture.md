# Technical Specification - Plan comptable et écritures (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer le plan comptable et les écritures comptables pour assurer la conformité fiscale et comptable de la station-service. L'objectif est de permettre une comptabilité rigoureuse et conforme aux systèmes locaux (OHADA, etc.), avec une journalisation automatique des opérations métier et la génération d'états financiers fiables.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module comptable complet permettant :
- De gérer un plan comptable selon les systèmes locaux (OHADA, etc.)
- De générer automatiquement des écritures comptables correctes
- De valider la cohérence des écritures comptables
- De produire des états financiers fiables

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des modifications comptables que sur les données appartenant à sa compagnie.

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
- Gestion des périodes comptables
- Contrôle des accès aux modifications comptables

## 2. User Stories & Critères d'acceptation

### US-PCG-001: En tant que comptable, je veux gérer le plan comptable
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des comptes
  - Maintenir la hiérarchie des comptes (classes, généraux, auxiliaires)
  - Appliquer les règles de nomenclature selon le système local
  - Associer les comptes à des catégories (actif, passif, produit, charge)
  - Vérifier l'équilibre entre débit et crédit
  - Seuls les utilisateurs avec les permissions appropriées peuvent modifier le plan comptable
  - Les gérants de compagnie peuvent consulter et utiliser tous les comptes pour leur compagnie

### US-PCG-002: En tant que comptable, je veux générer automatiquement les écritures comptables
- **Critères d'acceptation :**
  - Générer automatiquement les écritures à partir des opérations métier
  - Appliquer les règles de ventilation comptable
  - Numéroter automatiquement les pièces comptables
  - Assurer l'équilibre entre débit et crédit pour chaque écriture
  - Conserver un historique des écritures générées
  - Les gérants de compagnie peuvent consulter toutes les écritures pour leur compagnie

### US-PCG-003: En tant que comptable, je veux valider la cohérence des écritures comptables
- **Critères d'acceptation :**
  - Vérifier l'équilibre débit/crédit pour chaque écriture
  - Contrôler la validité des comptes utilisés
  - Valider la cohérence avec les règles comptables locales
  - Identifier et signaler les écritures incorrectes
  - Appliquer des validations hiérarchiques pour les écritures sensibles
  - Les gérants de compagnie peuvent valider les écritures selon les règles de validation pour leur compagnie

### US-PCG-004: En tant que comptable, je veux calculer les soldes des comptes
- **Critères d'acceptation :**
  - Calculer les soldes au jour le jour
  - Calculer les soldes pour une période donnée
  - Afficher les soldes avec sens (débiteur/créditeur)
  - Générer des fiches de comptes détaillées
  - Calculer les soldes de clôture pour les états financiers
  - Les gérants de compagnie peuvent consulter tous les soldes pour leur compagnie

### US-PCG-005: En tant que comptable, je veux générer les états financiers
- **Critères d'acceptation :**
  - Générer le bilan comptable
  - Produire le compte de résultat
  - Créer le grand livre
  - Éditer la balance
  - Produire le journal
  - Les gérants de compagnie peuvent produire tous les états financiers pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations comptables dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations comptables pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les validations hiérarchiques s'appliquent selon les seuils établis pour la modification des écritures

## 4. Dépendances avec d'autres modules

### Module des ventes
- Les ventes génèrent des écritures comptables automatiques
- Les encaissements affectent les comptes de trésorerie

### Module des achats
- Les achats génèrent des écritures comptables automatiques
- Les dettes fournisseurs sont enregistrées dans les comptes appropriés

### Module de trésorerie
- Les mouvements de trésorerie affectent les comptes bancaires et caisses
- Les paiements et encaissements sont enregistrés comptablement

## 5. Modèle de Données

### 5.1 Tables à créer/modifier

#### Table: plan_comptable
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
    compagnie_id UUID REFERENCES compagnies(id),  -- Compte spécifique à une compagnie
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_plan_comptable_numero ON plan_comptable(numero);
CREATE INDEX idx_plan_comptable_classe ON plan_comptable(classe);
CREATE INDEX idx_plan_comptable_type ON plan_comptable(type_compte);
CREATE INDEX idx_plan_comptable_parent ON plan_comptable(compte_parent_id);
CREATE INDEX idx_plan_comptable_pays ON plan_comptable(pays_id);
CREATE INDEX idx_plan_comptable_compagnie ON plan_comptable(compagnie_id);  -- Ajout de l'index pour compagnie
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
    compagnie_id UUID NOT NULL REFERENCES compagnies(id),  -- Lien vers la compagnie propriétaire
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
CREATE INDEX idx_ecritures_compagnie ON ecritures_comptables(compagnie_id);  -- Ajout de l'index pour compagnie
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

### 5.2 Relations
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

### 5.3 Triggers et règles d'intégrité
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
    WHERE ecriture_id = NEW.id;

    -- Vérifier que les totaux sont équilibrés
    IF ABS(total_debit - total_credit) > 0.01 THEN  -- Tolérance de 0.01 pour les arrondis
        RAISE EXCEPTION 'L''écriture comptable n''est pas équilibrée: débit total % != crédit total %', total_debit, total_credit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ajouter le trigger à la table ecritures_comptables
CREATE TRIGGER trig_verif_equilibre_ecriture
    AFTER INSERT OR UPDATE ON ecritures_comptables
    FOR EACH ROW EXECUTE FUNCTION verif_equilibre_ecriture();
```

### 5.4 Contrôles de Sécurité et Permissions
Afin de s'assurer que les nouvelles règles de permissions sont respectées, les tables critiques (plan_comptable, ecritures_comptables, etc.) incluent un champ `compagnie_id` pour garantir que chaque utilisateur n'accède qu'aux données de sa propre compagnie. Les requêtes devront filtrer systématiquement selon ce champ pour respecter les nouvelles règles de permissions.

- Les gérants de compagnie auront un accès complet aux données appartenant à leur propre compagnie
- Les super administrateurs auront un accès global à toutes les données
- Les administrateurs et utilisateurs auront un accès limité selon leurs permissions spécifiques

## 6. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités comptables pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que la cohérence comptable est maintenue