# Technical Specification - Bilan initial (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant d'établir le bilan initial d'une station-service avant l'utilisation du système SuccessFuel. Ce bilan initial constitue le point de départ comptable et opérationnel du système, permettant de capturer l'état exact des actifs, passifs, capitaux propres et stocks au moment de l'activation du système informatique. L'objectif est de permettre une continuité des opérations et un suivi fiable des indicateurs financiers et opérationnels.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un mécanisme permettant d'enregistrer l'état initial des postes comptables et opérationnels avant l'utilisation du système. Cela pose problème car :
- Les comptes comptables n'ont pas de solde initial
- Les stocks de départ ne sont pas enregistrés
- Les immobilisations ne sont pas prises en compte
- Les créances clients et dettes fournisseurs ne sont pas initialisées
- L'analyse comparative entre l'état initial et l'état actuel est impossible
- Les états financiers ne reflètent pas la réalité initiale

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra effectuer des initialisations que sur les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Initialisation des postes de bilan (actifs et passifs)
- Enregistrement des immobilisations existantes
- Initialisation des stocks de carburant et de produits boutique
- Prise en compte des créances clients et dettes fournisseurs
- Saisie des capitaux propres et emprunts existants
- Création d'un point de départ pour la comptabilité
- Analyse comparative entre l'état initial et l'état actuel
- Historique des modifications du bilan initial

## 2. User Stories & Critères d'acceptation

### US-BI-001: En tant que gestionnaire, je veux initialiser les postes d'actif du bilan
- **Critères d'acceptation :**
  - Pouvoir saisir les soldes initiaux pour chaque poste d'actif
  - Associer les valeurs aux bons comptes du plan comptable
  - Vérifier l'équilibre comptable (actif = passif + capitaux propres)
  - Sauvegarder les données saisies dans le système
  - Générer un état du bilan initial
  - Seuls les utilisateurs avec les permissions appropriées peuvent effectuer l'initialisation
  - Les gérants de compagnie peuvent initialiser l'ensemble des postes pour leur compagnie

### US-BI-002: En tant que gestionnaire, je veux initialiser les postes de passif du bilan
- **Critères d'acceptation :**
  - Pouvoir saisir les soldes initiaux pour chaque poste de passif
  - Intégrer les capitaux propres existants
  - Enregistrer les emprunts en cours
  - Assurer la cohérence avec les postes d'actif
  - Les gérants de compagnie peuvent initialiser tous les postes de passif pour leur compagnie

### US-BI-003: En tant que gestionnaire, je veux initialiser les stocks de carburant et de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités et valeurs des stocks existants
  - Associer les stocks aux cuves et aux références produits
  - Vérifier la correspondance entre les quantités physiques et les stocks enregistrés
  - Intégrer les données dans le module de gestion des stocks
  - Les gérants de compagnie peuvent initialiser les stocks pour toutes les stations de leur compagnie

### US-BI-004: En tant que gestionnaire, je veux enregistrer les créances clients et dettes fournisseurs existantes
- **Critères d'acceptation :**
  - Pouvoir saisir les montants des créances clients existantes
  - Enregistrer les dettes fournisseurs actuelles
  - Associer les montants aux tiers concernés
  - Intégrer les données dans les modules clients et fournisseurs
  - Les gérants de compagnie peuvent enregistrer toutes les créances et dettes pour leur compagnie

### US-BI-005: En tant que gestionnaire, je veux effectuer une analyse comparative entre l'état initial et l'état actuel
- **Critères d'acceptation :**
  - Pouvoir consulter le bilan initial à tout moment
  - Comparer les valeurs initiales avec les valeurs actuelles
  - Générer des rapports d'évolution
  - Analyser les variations de chaque poste
  - Les gérants de compagnie peuvent accéder à toutes les analyses pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de bilan initial dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de bilan initial pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Toutes les opérations sont filtrées selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent voir et modifier que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation

## 4. Modèle de Données

### 4.1 Tables à créer/modifier

#### Table: bilan_initial
```sql
CREATE TABLE public.bilan_initial (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    compagnie_id uuid,
    date_bilan_initial date NOT NULL,
    est_valide boolean DEFAULT false,
    est_verifie boolean DEFAULT false,
    commentaire text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Ajout du champ utilisateur_id et description
ALTER TABLE public.bilan_initial ADD COLUMN utilisateur_id uuid;
ALTER TABLE public.bilan_initial ADD COLUMN description text;

-- Ajout des contraintes
ALTER TABLE public.bilan_initial ADD CONSTRAINT bilan_initial_pkey PRIMARY KEY (id);
ALTER TABLE public.bilan_initial ADD CONSTRAINT fk_bilan_initial_compagnie FOREIGN KEY (compagnie_id) REFERENCES public.compagnies(id);
ALTER TABLE public.bilan_initial ADD CONSTRAINT fk_bilan_initial_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES public.utilisateurs(id);

-- Index pour les performances
CREATE INDEX idx_bilan_initial_compagnie ON public.bilan_initial(compagnie_id);
CREATE INDEX idx_bilan_initial_date ON public.bilan_initial(date_bilan_initial);
CREATE INDEX idx_bilan_initial_utilisateur ON public.bilan_initial(utilisateur_id);
CREATE INDEX idx_bilan_initial_validation ON public.bilan_initial(est_valide, est_verifie);
```

#### Table: bilan_initial_lignes
```sql
CREATE TABLE bilan_initial_lignes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    compte_numero VARCHAR(20) NOT NULL,
    compte_id UUID REFERENCES plan_comptable(id),
    montant_initial NUMERIC(18,2) NOT NULL,
    type_solde VARCHAR(10) CHECK (type_solde IN ('debit', 'credit')),
    poste_bilan VARCHAR(20) NOT NULL CHECK (poste_bilan IN ('actif', 'passif', 'capitaux_propres')), -- Poste du bilan
    categorie_detaillee VARCHAR(50), -- Ex: 'immobilisations', 'stocks', 'creances', 'dettes', 'capital', 'reserves'
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_bilan_initial_lignes_bilan ON bilan_initial_lignes(bilan_initial_id);
CREATE INDEX idx_bilan_initial_lignes_compte ON bilan_initial_lignes(compte_numero);
CREATE INDEX idx_bilan_initial_lignes_poste ON bilan_initial_lignes(poste_bilan);
CREATE INDEX idx_bilan_initial_lignes_montant ON bilan_initial_lignes(montant_initial);
```

#### Table: immobilisations_bilan_initial
```sql
CREATE TABLE immobilisations_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    categorie VARCHAR(100) NOT NULL, -- Ex: véhicule, matériel, etc.
    date_achat DATE NOT NULL,
    valeur_acquisition NUMERIC(18,2) NOT NULL,
    valeur_nette_comptable NUMERIC(18,2) NOT NULL,
    amortissement_cumule NUMERIC(18,2) NOT NULL, -- Amortissement déjà pratiqué
    duree_amortissement INTEGER DEFAULT 0, -- En années
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
```

#### Table: stocks_bilan_initial
```sql
CREATE TABLE stocks_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_stock VARCHAR(20) NOT NULL CHECK (type_stock IN ('carburant', 'produit_boutique')), -- Type de stock
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL, -- Pour les produits boutique
    carburant_id UUID REFERENCES carburants(id) ON DELETE SET NULL, -- Pour le carburant
    cuve_id UUID REFERENCES cuves(id) ON DELETE SET NULL, -- Pour les carburants
    quantite NUMERIC(18,3) NOT NULL, -- Quantité en unité de stock
    prix_unitaire NUMERIC(18,4) NOT NULL, -- Prix unitaire d'achat à la date d'initialisation
    valeur_totale NUMERIC(18,4) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED, -- Calcul automatique
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_stocks_bilan_initial_bilan ON stocks_bilan_initial(bilan_initial_id);
CREATE INDEX idx_stocks_bilan_initial_article ON stocks_bilan_initial(article_id);
CREATE INDEX idx_stocks_bilan_initial_carburant ON stocks_bilan_initial(carburant_id);
CREATE INDEX idx_stocks_bilan_initial_type ON stocks_bilan_initial(type_stock);
CREATE INDEX idx_stocks_bilan_initial_valeur ON stocks_bilan_initial(valeur_totale);
```

#### Table: creances_dettes_bilan_initial
```sql
CREATE TABLE creances_dettes_bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_tiers VARCHAR(20) NOT NULL CHECK (type_tiers IN ('client', 'fournisseur')), -- Type de tiers
    tiers_id UUID NOT NULL, -- ID du client ou fournisseur
    montant_initial NUMERIC(18,2) NOT NULL,
    devise VARCHAR(3) DEFAULT 'MGA',
    date_echeance DATE, -- Pour les opérations à crédit
    reference_piece VARCHAR(100), -- Référence de la facture/dette
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_creances_dettes_bilan_initial_bilan ON creances_dettes_bilan_initial(bilan_initial_id);
CREATE INDEX idx_creances_dettes_bilan_initial_tiers ON creances_dettes_bilan_initial(tiers_id);
CREATE INDEX idx_creances_dettes_bilan_initial_type ON creances_dettes_bilan_initial(type_tiers);
CREATE INDEX idx_creances_dettes_bilan_initial_montant ON creances_dettes_bilan_initial(montant_initial);
```

### 4.2 Relations
- `bilan_initial.compagnie_id` → `compagnies.id` (One-to-Many)
- `bilan_initial.utilisateur_id` → `utilisateurs.id` (One-to-Many)
- `bilan_initial_lignes.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `bilan_initial_lignes.compte_id` → `plan_comptable.id` (One-to-Many)
- `immobilisations_bilan_initial.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `immobilisations_bilan_initial.fournisseur_id` → `fournisseurs.id` (One-to-Many)
- `immobilisations_bilan_initial.utilisateur_achat_id` → `utilisateurs.id` (One-to-Many)
- `stocks_bilan_initial.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `stocks_bilan_initial.article_id` → `articles.id` (One-to-Many)
- `stocks_bilan_initial.carburant_id` → `carburants.id` (One-to-Many)
- `stocks_bilan_initial.cuve_id` → `cuves.id` (One-to-Many)
- `creances_dettes_bilan_initial.bilan_initial_id` → `bilan_initial.id` (One-to-Many)

### 4.3 Triggers et règles d'intégrité
```sql
-- Trigger pour vérifier la cohérence du bilan initial (actifs = passifs + capitaux propres)
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
        RAISE EXCEPTION 'Le bilan initial n''est pas équilibré: Actifs (% MGA) != Passifs + Capitaux Propres (% MGA)', total_actifs, total_passifs_capitaux;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger
CREATE TRIGGER trigger_verifier_coherence_bilan_initial
    AFTER INSERT OR UPDATE ON bilan_initial_lignes
    FOR EACH ROW
    EXECUTE FUNCTION verifier_coherence_bilan_initial();
```

### 4.4 Contrôles de Sécurité et Permissions
Afin de s'assurer que les nouvelles règles de permissions sont respectées, la table principale (bilan_initial) inclut un champ `compagnie_id` pour garantir que chaque utilisateur n'accède qu'aux données de sa propre compagnie. Les requêtes devront filtrer systématiquement selon ce champ pour respecter les nouvelles règles de permissions.

- Les gérants de compagnie auront un accès complet aux données appartenant à leur propre compagnie
- Les super administrateurs auront un accès global à toutes les données
- Les administrateurs et utilisateurs auront un accès limité selon leurs permissions spécifiques

## 5. Dépendances avec d'autres modules

### Module comptable
- Le bilan initial est intégré au plan comptable existant
- Les soldes initiaux sont enregistrés comme des écritures comptables spécifiques
- Les états financiers utilisent les données du bilan initial

### Module des structures
- Les données sont associées aux stations de la compagnie
- Les comptes sont liés au plan comptable de la compagnie

### Module des stocks
- Les stocks initiaux sont enregistrés dans le module de gestion des stocks
- Les données sont utilisées pour les calculs de valeur des stocks

## 6. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de bilan initial pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les validations fonctionnent correctement selon les permissions

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que la cohérence comptable est maintenue après les initialisations