# Technical Specification - Internationalisation

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant l'adaptation du système SuccessFuel à différents pays africains francophones. L'objectif est de rendre le système suffisamment flexible pour s'adapter aux spécificités légales, fiscales, comptables, monétaires et culturelles de chaque pays tout en maintenant une architecture cohérente et standardisée.

### Problème à résoudre
Actuellement, le système SuccessFuel est configuré pour fonctionner dans un contexte spécifique (Madagascar). Pour permettre son déploiement dans d'autres pays africains francophones, il est nécessaire de:
- Supporter différentes législations fiscales et systèmes comptables (OHADA, etc.)
- Gérer des devises multiples avec conversion automatique
- Adapter les unités de mesure selon les pratiques locales
- Générer des rapports conformes aux normes locales
- Configurer dynamiquement les spécifications locales sans modification du code

### Définition du périmètre
Le périmètre inclut:
- Gestion multi-pays avec configuration des spécifications locales
- Support des différentes législations fiscales et systèmes comptables
- Gestion des devises multiples et historique des taux de change
- Système de taxation modulaire configurable par pays
- Gestion des unités de mesure locales et conversions
- Modèles de rapports spécifiques par pays
- Architecture modulaire pour l'adaptation internationale
- Support des spécificités locales via système de plugins/configurations

## 2. User Stories & Critères d'acceptation

### US-INT-001: En tant qu'administrateur, je veux gérer les pays pris en charge par le système
- **Critères d'acceptation :**
  - Pouvoir ajouter un nouveau pays avec ses spécifications locales
  - Pouvoir configurer la devise principale d'un pays
  - Pouvoir définir le système comptable applicable (OHADA, etc.)
  - Pouvoir activer/désactiver un pays
  - Pouvoir configurer le taux de TVA par défaut pour chaque pays

### US-INT-002: En tant que gestionnaire, je veux configurer les spécifications locales d'un pays
- **Critères d'acceptation :**
  - Pouvoir définir les spécifications fiscales (taxes, obligations)
  - Pouvoir configurer les spécifications comptables (plan de comptes local)
  - Pouvoir définir les règlements locaux applicables
  - Pouvoir configurer la validité temporelle des spécifications
  - Pouvoir associer des commentaires aux spécifications

### US-INT-003: En tant que gestionnaire, je veux gérer les taux de change pour les transactions multi-devises
- **Critères d'acceptation :**
  - Pouvoir enregistrer les taux de change historiques
  - Pouvoir définir les taux de change pour les paires de devises utilisées
  - Pouvoir spécifier la date d'application des taux
  - Le système doit conserver l'historique des taux
  - Les taux doivent être associés à un utilisateur responsable

### US-INT-004: En tant que gestionnaire, je veux que les taxes soient calculées automatiquement selon les réglementations locales
- **Critères d'acceptation :**
  - Le système doit appliquer les taux de taxe appropriés selon le pays
  - Le système doit gérer les différentes structures fiscales (tranches, pourcentage fixe, etc.)
  - Les calculs doivent être conformes aux réglementations locales
  - Les taxes doivent être affichées séparément sur les documents
  - Le système doit générer des rapports fiscaux selon les normes locales

### US-INT-005: En tant que gestionnaire, je veux gérer les unités de mesure selon les pratiques locales
- **Critères d'acceptation :**
  - Pouvoir définir les unités de mesure spécifiques à un pays
  - Pouvoir configurer les facteurs de conversion entre unités
  - Le système doit permettre l'utilisation d'unités standard internationales
  - Le système doit convertir automatiquement entre unités selon le contexte
  - Les unités doivent être visibles selon les préférences locales

### US-INT-006: En tant que gestionnaire, je veux que les rapports soient générés selon les normes locales
- **Critères d'acceptation :**
  - Pouvoir sélectionner des modèles de rapports spécifiques au pays
  - Les rapports doivent respecter les formats locaux requis
  - Les rapports doivent être disponibles dans la devise locale
  - Les rapports fiscaux doivent être conformes aux exigences locales
  - Les formats d'exportation doivent respecter les normes locales

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: pays (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS pays (
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

#### Table: specifications_locales (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS specifications_locales (
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
```

#### Table: configurations_pays (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS configurations_pays (
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
```

#### Table: types_taxes (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS types_taxes (
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
```

#### Table: tranches_taxes (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS tranches_taxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_taxe_id UUID REFERENCES types_taxes(id),
    borne_inferieure NUMERIC(18,2) DEFAULT 0,
    borne_superieure NUMERIC(18,2),
    taux NUMERIC(5,2) NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: unites_mesure (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS unites_mesure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_unite VARCHAR(10) UNIQUE NOT NULL, -- 'L', 'GAL', 'KG', 'TON', etc.
    libelle_unite VARCHAR(50) NOT NULL,
    pays_id UUID REFERENCES pays(id), -- Unités spécifiques à un pays
    est_standard BOOLEAN DEFAULT FALSE, -- Unité standard internationale
    est_utilisee BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: conversions_unite (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS conversions_unite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unite_origine_id UUID REFERENCES unites_mesure(id),
    unite_destination_id UUID REFERENCES unites_mesure(id),
    facteur_conversion NUMERIC(15,6) NOT NULL, -- Facteur pour convertir d'une unité à l'autre
    est_actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Table: taux_changes (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS taux_changes (
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
```

#### Table: modeles_rapports (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS modeles_rapports (
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
```

#### Table: plan_comptable_pays (existante, à compléter)
```sql
CREATE TABLE IF NOT EXISTS plan_comptable_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_comptable_id UUID REFERENCES plan_comptable(id),
    pays_id UUID REFERENCES pays(id),
    numero_compte_local VARCHAR(20), -- Numéro de compte spécifique au pays
    intitule_local VARCHAR(255), -- Dénomination locale du compte
    est_compte_obligatoire BOOLEAN DEFAULT FALSE, -- Si le compte est obligatoire dans ce pays
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 3.2 Relations
- Les tables existantes sont liées à la table `pays` pour la gestion multisite
- Les spécifications locales sont liées au pays et au type pour permettre la configuration spécifique
- Les taux de change sont indépendants mais utilisables selon le contexte pays
- Les unités de mesure peuvent être spécifiques à un pays ou standard internationales
- Les modèles de rapports sont spécifiques à chaque pays

### 3.3 Index recommandés
```sql
-- Index pour les pays
CREATE INDEX IF NOT EXISTS idx_pays_code ON pays(code_pays);
CREATE INDEX IF NOT EXISTS idx_pays_systeme_comptable ON pays(systeme_comptable);

-- Index pour les spécifications locales
CREATE INDEX IF NOT EXISTS idx_specifications_locales_pays ON specifications_locales(pays_id);
CREATE INDEX IF NOT EXISTS idx_specifications_locales_type ON specifications_locales(type_specification);
CREATE INDEX IF NOT EXISTS idx_specifications_locales_code ON specifications_locales(code_specification);
CREATE INDEX IF NOT EXISTS idx_specifications_locales_dates ON specifications_locales(date_debut_validite, date_fin_validite);

-- Index pour les configurations pays
CREATE INDEX IF NOT EXISTS idx_configurations_pays_pays ON configurations_pays(pays_id);
CREATE INDEX IF NOT EXISTS idx_configurations_pays_cle ON configurations_pays(cle_configuration);

-- Index pour les types de taxes
CREATE INDEX IF NOT EXISTS idx_types_taxes_pays ON types_taxes(pays_id);
CREATE INDEX IF NOT EXISTS idx_types_taxes_code ON types_taxes(code_taxe);

-- Index pour les tranches de taxes
CREATE INDEX IF NOT EXISTS idx_tranches_taxes_type ON tranches_taxes(type_taxe_id);

-- Index pour les unités de mesure
CREATE INDEX IF NOT EXISTS idx_unites_mesure_pays ON unites_mesure(pays_id);
CREATE INDEX IF NOT EXISTS idx_unites_mesure_code ON unites_mesure(code_unite);

-- Index pour les conversions d'unités
CREATE INDEX IF NOT EXISTS idx_conversions_unite_origine ON conversions_unite(unite_origine_id);
CREATE INDEX IF NOT EXISTS idx_conversions_unite_destination ON conversions_unite(unite_destination_id);

-- Index pour les taux de change
CREATE INDEX IF NOT EXISTS idx_taux_changes_devise ON taux_changes(devise_source, devise_cible);
CREATE INDEX IF NOT EXISTS idx_taux_changes_date ON taux_changes(date_application);
CREATE INDEX IF NOT EXISTS idx_taux_changes_actuel ON taux_changes(est_actuel);

-- Index pour les modèles de rapports
CREATE INDEX IF NOT EXISTS idx_modeles_rapports_pays ON modeles_rapports(pays_id);
CREATE INDEX IF NOT EXISTS idx_modeles_rapports_type ON modeles_rapports(type_rapport);

-- Index pour les plans comptables par pays
CREATE INDEX IF NOT EXISTS idx_plan_comptable_pays_pays ON plan_comptable_pays(pays_id);
CREATE INDEX IF NOT EXISTS idx_plan_comptable_pays_compte ON plan_comptable_pays(plan_comptable_id);
```

## 4. API Backend

### 4.1 Endpoints pour la gestion des pays

#### GET /api/v1/pays
- **Description**: Récupérer la liste des pays configurés
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_pays'
- **Paramètres**:
  - `statut` (string, optionnel): 'Actif', 'Inactif'
- **Réponse (200 OK)**:
```json
{
  "pays": [
    {
      "id": "uuid_pays",
      "code_pays": "MDG",
      "nom_pays": "Madagascar",
      "devise_principale": "MGA",
      "taux_tva_par_defaut": 18.00,
      "systeme_comptable": "OHADA",
      "date_application_tva": "2023-01-01",
      "statut": "Actif"
    }
  ]
}
```

#### GET /api/v1/pays/{pays_id}
- **Description**: Récupérer les détails d'un pays spécifique
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_pays'
- **Réponse (200 OK)**:
```json
{
  "id": "uuid_pays",
  "code_pays": "MDG",
  "nom_pays": "Madagascar",
  "devise_principale": "MGA",
  "taux_tva_par_defaut": 18.00,
  "systeme_comptable": "OHADA",
  "date_application_tva": "2023-01-01",
  "statut": "Actif",
  "specifications_locales": [
    {
      "id": "uuid_spec",
      "type_specification": "taxe",
      "code_specification": "tva",
      "libelle_specification": "Taxe sur la Valeur Ajoutée",
      "taux_specification": 18.0000,
      "est_actif": true,
      "date_debut_validite": "2023-01-01",
      "date_fin_validite": null
    }
  ]
}
```

#### POST /api/v1/pays
- **Description**: Créer un nouveau pays
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_pays'
- **Payload**:
```json
{
  "code_pays": "SEN",
  "nom_pays": "Sénégal",
  "devise_principale": "XOF",
  "taux_tva_par_defaut": 18.00,
  "systeme_comptable": "OHADA",
  "date_application_tva": "2023-01-01"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Pays créé avec succès",
  "pays_id": "uuid_du_pays"
}
```

#### PUT /api/v1/pays/{pays_id}
- **Description**: Mettre à jour un pays existant
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'modifier_pays'
- **Payload**:
```json
{
  "nom_pays": "Sénégal",
  "devise_principale": "XOF",
  "taux_tva_par_defaut": 18.00,
  "systeme_comptable": "OHADA",
  "statut": "Actif"
}
```
- **Réponse (200 OK)**:
```json
{
  "success": true,
  "message": "Pays mis à jour avec succès"
}
```

### 4.2 Endpoints pour la gestion des spécifications locales

#### GET /api/v1/specifications-locales
- **Description**: Récupérer les spécifications locales pour un pays
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_specifications_locales'
- **Paramètres**:
  - `pays_id` (UUID, requis): ID du pays
  - `type_specification` (string, optionnel): type de spécification
  - `est_actif` (boolean, optionnel): état de la spécification
- **Réponse (200 OK)**:
```json
{
  "specifications_locales": [
    {
      "id": "uuid_spec",
      "pays_id": "uuid_pays",
      "type_specification": "taxe",
      "code_specification": "tva",
      "libelle_specification": "Taxe sur la Valeur Ajoutée",
      "valeur_specification": "18%",
      "taux_specification": 18.0000,
      "est_actif": true,
      "date_debut_validite": "2023-01-01",
      "date_fin_validite": null,
      "commentaire": "TVA standard applicable à la plupart des biens et services"
    }
  ]
}
```

#### POST /api/v1/specifications-locales
- **Description**: Créer une spécification locale
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_specifications_locales'
- **Payload**:
```json
{
  "pays_id": "uuid_pays",
  "type_specification": "taxe",
  "code_specification": "taxe_speciale",
  "libelle_specification": "Taxe spéciale sur les produits pétroliers",
  "valeur_specification": "500 MGA par litre",
  "taux_specification": 500.0000,
  "date_debut_validite": "2025-01-01",
  "commentaire": "Appliquée aux produits pétroliers"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Spécification locale créée avec succès",
  "specification_id": "uuid_specification"
}
```

### 4.3 Endpoints pour la gestion des taux de change

#### GET /api/v1/taux-changes
- **Description**: Récupérer les taux de change
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_taux_changes'
- **Paramètres**:
  - `devise_source` (string, optionnel): devise source
  - `devise_cible` (string, optionnel): devise cible
  - `date_application` (date, optionnel): date spécifique
  - `est_actuel` (boolean, optionnel): uniquement les taux en cours
- **Réponse (200 OK)**:
```json
{
  "taux_changes": [
    {
      "id": "uuid_taux",
      "devise_source": "EUR",
      "devise_cible": "MGA",
      "taux": 4500.000000,
      "date_application": "2025-11-25",
      "heure_application": "10:30:00",
      "est_actuel": true,
      "utilisateur": {
        "id": "uuid_utilisateur",
        "nom": "Nom de l'utilisateur"
      },
      "commentaire": "Taux mis à jour automatiquement"
    }
  ]
}
```

#### POST /api/v1/taux-changes
- **Description**: Créer un taux de change
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_taux_changes'
- **Payload**:
```json
{
  "devise_source": "USD",
  "devise_cible": "MGA",
  "taux": 3850.000000,
  "date_application": "2025-11-26",
  "heure_application": "09:00:00",
  "commentaire": "Taux du marché du jour"
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Taux de change créé avec succès",
  "taux_id": "uuid_taux"
}
```

### 4.4 Endpoints pour la gestion des taxes

#### GET /api/v1/types-taxes
- **Description**: Récupérer les types de taxes configurés
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_types_taxes'
- **Paramètres**:
  - `pays_id` (UUID, optionnel): filtre par pays
  - `est_actif` (boolean, optionnel): état de la taxe
- **Réponse (200 OK)**:
```json
{
  "types_taxes": [
    {
      "id": "uuid_type_taxe",
      "code_taxe": "tva-standard",
      "libelle_taxe": "TVA standard",
      "description": "Taxe sur la valeur ajoutée à taux standard",
      "pays_id": "uuid_pays",
      "taux_par_defaut": 18.00,
      "type_calcul": "pourcentage",
      "compte_comptable": "445710",
      "est_actif": true
    }
  ]
}
```

#### POST /api/v1/types-taxes
- **Description**: Créer un type de taxe
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_types_taxes'
- **Payload**:
```json
{
  "code_taxe": "taxe-speciale",
  "libelle_taxe": "Taxe spéciale sur les carburants",
  "description": "Taxe spéciale applicable aux produits pétroliers",
  "pays_id": "uuid_pays",
  "taux_par_defaut": 500.00,
  "type_calcul": "fixe",
  "compte_comptable": "445780",
  "est_actif": true
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Type de taxe créé avec succès",
  "type_taxe_id": "uuid_type_taxe"
}
```

### 4.5 Endpoints pour la gestion des unités de mesure

#### GET /api/v1/unites-mesure
- **Description**: Récupérer les unités de mesure configurées
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_unites_mesure'
- **Paramètres**:
  - `pays_id` (UUID, optionnel): filtre par pays
  - `est_utilisee` (boolean, optionnel): unités actuellement utilisées
- **Réponse (200 OK)**:
```json
{
  "unites_mesure": [
    {
      "id": "uuid_unite",
      "code_unite": "L",
      "libelle_unite": "Litre",
      "pays_id": null,
      "est_standard": true,
      "est_utilisee": true
    }
  ]
}
```

#### POST /api/v1/conversions-unite
- **Description**: Créer une conversion entre unités
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'creer_conversions_unite'
- **Payload**:
```json
{
  "unite_origine_id": "uuid_unite_origine",
  "unite_destination_id": "uuid_unite_destination",
  "facteur_conversion": 3.78541
}
```
- **Réponse (201 Created)**:
```json
{
  "success": true,
  "message": "Conversion d'unité créée avec succès",
  "conversion_id": "uuid_conversion"
}
```

### 4.6 Endpoints pour la gestion des rapports locaux

#### GET /api/v1/modeles-rapports
- **Description**: Récupérer les modèles de rapports configurés
- **Authentification**: Requiert jeton JWT valide
- **Permissions**: besoin de la permission 'lire_modeles_rapports'
- **Paramètres**:
  - `pays_id` (UUID, optionnel): filtre par pays
  - `type_rapport` (string, optionnel): type de rapport
  - `est_actif` (boolean, optionnel): modèle actif
- **Réponse (200 OK)**:
```json
{
  "modeles_rapports": [
    {
      "id": "uuid_modele",
      "code_modele": "bilan_ohada",
      "libelle_modele": "Modèle de bilan OHADA",
      "pays_id": "uuid_pays",
      "type_rapport": "bilan",
      "format_sortie": "PDF",
      "est_actif": true
    }
  ]
}
```

## 5. Logique Métier

### 5.1 Règles de gestion multi-pays

#### Règles pour la gestion des pays
- Chaque entité du système peut être liée à un pays spécifique
- Les spécifications locales sont applicables selon le pays de l'entité
- Les validations et contrôles dépendent du pays concerné
- Les rapports sont générés selon les modèles spécifiques au pays

#### Règles pour les spécifications locales
- Les spécifications sont valides entre deux dates précises
- Seules les spécifications activées peuvent être utilisées
- Les spécifications sont prioritairement appliquées par date de validité
- Les erreurs ou incohérences doivent être signalées lors de la configuration

#### Règles pour les taxes
- Les taux de taxe sont appliqués selon le pays des opérations
- Les calculs fiscaux se font selon les réglementations en vigueur
- Les tranches fiscales sont prises en compte pour les calculs progressifs
- Les reportings fiscaux doivent respecter les formats locaux

### 5.2 Règles de gestion des devises

#### Règles pour la conversion des devises
- La conversion se fait selon les taux en vigueur à la date de l'opération
- Les taux historiques sont conservés pour la traçabilité
- Le système peut utiliser le dernier taux connu si pas de taux disponible
- Les arrondis doivent respecter les règles locales

#### Règles pour les transactions multi-devises
- Les opérations sont enregistrées dans la devise d'origine
- Les conversions sont effectuées pour les besoins de reporting
- Les différences de change sont enregistrées selon les normes locales
- Les taux de change sont actualisés périodiquement

### 5.3 Règles pour les unités de mesure

#### Règles pour les conversions d'unités
- Les conversions se font selon les facteurs configurés
- Le système vérifie la validité des conversions avant utilisation
- Les erreurs de conversion doivent être signalées
- Les unités peuvent être spécifiques à un pays ou standard internationales

### 5.4 Règles pour les rapports locaux

#### Règles pour la génération des rapports
- Les rapports utilisent les modèles spécifiques au pays concerné
- Les données sont filtrées selon les entités du pays
- Les formats respectent les obligations locales
- Les rapports peuvent être générés dans la devise locale

### 5.5 Contraintes d'intégration

#### Contraintes avec les autres modules
- Les modules existants doivent être adaptés pour supporter le pays
- Les opérations transfrontalières doivent être gérées correctement
- Les configurations doivent être cohérentes entre modules
- Les performances doivent être maintenues malgré la complexité accrue

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
Pays 1----* Compagnie
Pays 1----* SpécificationLocale
Pays 1----* TypeTaxe
Pays 1----* UniteMesure
Pays 1----* ModeleRapport
Pays 1----* PlanComptablePays

SpécificationLocale *----* ConfigurationPays
TypeTaxe *----* TrancheTaxe
UniteMesure *----* ConversionUnite
TauxChange 1----* Vente
TauxChange 1----* Achat
```

### 6.2 Diagramme de séquence (textuel) pour la gestion d'une vente multi-pays
```
Client -> API: POST /api/v1/ventes (dans le contexte d'un pays spécifique)
API -> Pays: Vérifier les spécifications fiscales du pays
Pays -> API: Retourner les taux de taxe applicables
API -> TauxChanges: Obtenir le taux de change pour la devise
TauxChanges -> API: Fournir le taux de change applicable
API -> Vente: Calculer les taxes selon les spécifications locales
API -> Vente: Convertir les montants selon le taux de change
API -> Vente: Enregistrer la vente dans la devise locale
Vente -> API: Confirmer l'enregistrement
API -> Client: Retourner les détails de la vente avec taxes et conversion
```

## 7. Tests Requis

### 7.1 Tests unitaires

#### Tests pour les spécifications locales
- Test de validation des dates de validité des spécifications
- Test de la cohérence des données d'une spécification
- Test de la recherche des spécifications actives pour un pays
- Test de la gestion des spécifications avec chevauchement de dates

#### Tests pour les taxes
- Test du calcul des taxes selon différents types (fixe, pourcentage, tranche)
- Test de l'application des tranches fiscales
- Test de la conversion des taux de taxe
- Test de la validation des taux de taxe

#### Tests pour les unités de mesure
- Test des conversions d'unités selon les facteurs configurés
- Test de la validation des conversions
- Test des conversions multiples (A -> B -> C)
- Test des cas d'erreurs dans les conversions

### 7.2 Tests d'intégration

#### Tests pour la gestion multi-pays
- Test de création d'une entité dans un contexte pays spécifique
- Test de l'application des spécifications locales à une opération
- Test de la conversion des devises dans une opération
- Test de la génération de rapports selon les modèles locaux

#### Tests pour les workflows transfrontaliers
- Test d'une opération impliquant plusieurs pays
- Test de la cohérence des échanges entre pays
- Test de la gestion des différences de réglementation
- Test de la conversion des montants dans les rapports consolidés

### 7.3 Tests de charge/performance
- Test de performance avec une grande quantité de spécifications locales
- Test de performance avec une grande quantité de taux de change
- Test de performance avec des conversions fréquentes d'unités
- Test de performance pour la génération de rapports multi-pays

### 7.4 Jeux de données de test
- Données de test pour plusieurs pays (Madagascar, Sénégal, Côte d'Ivoire)
- Taux de change historiques pour les paires de devises utilisées
- Différentes structures fiscales selon les pays
- Unités de mesure spécifiques à certains pays
- Modèles de rapports pour chaque pays configuré

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées

#### Phase 1: Modèle de données
- [ ] Vérifier les tables existantes pour l'ajout des champs liés au pays
- [ ] Créer les indexes nécessaires pour les requêtes multi-pays
- [ ] Mettre à jour les contraintes d'intégrité existantes si nécessaire
- [ ] S'assurer de la cohérence des relations entre tables

#### Phase 2: Logique métier
- [ ] Implémenter la logique de sélection des spécifications locales selon le pays
- [ ] Développer les algorithmes de conversion de devises
- [ ] Mettre en place la logique de calcul des taxes selon les spécifications locales
- [ ] Développer les algorithmes de conversion d'unités de mesure
- [ ] Mettre en place la sélection des modèles de rapports selon le pays

#### Phase 3: API Backend
- [ ] Créer les endpoints pour la gestion des pays
- [ ] Développer les endpoints pour les spécifications locales
- [ ] Mettre en place les endpoints pour les taux de change
- [ ] Créer les endpoints pour la gestion des taxes
- [ ] Développer les endpoints pour les unités de mesure
- [ ] Mettre en place les endpoints pour les modèles de rapports

#### Phase 4: Intégration avec les modules existants
- [ ] Adapter les modules existants pour supporter le contexte pays
- [ ] Mettre à jour les opérations pour appliquer les spécifications locales
- [ ] Adapter les calculs fiscaux selon le contexte pays
- [ ] Mettre à jour les conversions monétaires selon les pays

#### Phase 5: Tests
- [ ] Écrire les tests unitaires pour chaque nouvelle fonctionnalité
- [ ] Créer les tests d'intégration pour la gestion multi-pays
- [ ] Mettre en place les tests de performance
- [ ] Préparer les jeux de données de test internationaux

### 8.2 Ordre recommandé
1. Commencer par la configuration des pays et des spécifications locales
2. Développer la gestion des taux de change
3. Implémenter les fonctionnalités de gestion des taxes
4. Mettre en place la gestion des unités de mesure
5. Intégrer les modèles de rapports locaux
6. Adapter les modules existants pour supporter le multi-pays
7. Effectuer les tests complets
8. Optimiser les performances si nécessaire

### 8.3 Livrables attendus
- Ensemble complet de tables pour la gestion internationale
- API RESTful pour l'accès aux fonctionnalités multi-pays
- Documentation des nouveaux endpoints API
- Jeux de tests unitaires et d'intégration
- Scripts de migration de base de données pour l'internationalisation
- Guide d'utilisation pour la configuration par pays
- Documentation des modèles de rapports spécifiques à chaque pays

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La complexité accrue du système avec la gestion multi-pays
- La gestion cohérente des spécifications locales qui peuvent changer
- La conversion des devises avec les taux historiques
- La cohérence des calculs fiscaux selon les réglementations locales
- La performance du système avec les requêtes multi-dimensionnelles

### 9.2 Risques techniques
- Risque de performance avec l'augmentation de la complexité des requêtes
- Risque de cohérence des données si les spécifications ne sont pas correctement gérées
- Risque de calculs fiscaux incorrects si les spécifications locales ne sont pas appliquées
- Risque de conversion inappropriée des devises/unités
- Risque de non-conformité des rapports aux normes locales

### 9.3 Dette technique potentielle
- Complexité accrue du système avec la gestion internationale
- Nécessité de mises à jour fréquentes des spécifications locales
- Maintenance des différents modèles de rapports
- Adaptation continue aux changements réglementaires
- Gestion des spécificités locales qui pourraient devenir spécifiques à des régions