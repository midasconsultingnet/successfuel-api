# Technical Specification - Module d'Internationalisation

## 1. Contexte & Objectif du Sprint

### Description métier
Le module d'internationalisation permet d'adapter le système SuccessFuel aux spécificités des différents pays africains francophones. Il gère les particularités locales telles que les législations fiscales, les systèmes comptables (OHADA, etc.), les devises multiples, les unités de mesure locales et les formats de reporting spécifiques. Le module offre une architecture modulaire pour assurer la flexibilité du système face aux spécifications locales variables.

### Problème à résoudre
Sans un module d'internationalisation, le système SuccessFuel ne pourrait pas s'adapter aux différentes législations, systèmes comptables, pratiques fiscales, unités de mesure et formats de reporting des divers pays africains francophones, ce qui limiterait sa capacité à être déployé efficacement dans différents contextes régionaux.

### Définition du périmètre
Le périmètre du sprint couvre:
- Gestion multi-pays avec configuration des spécifications locales
- Support des différentes législations fiscales et systèmes comptables
- Gestion des devises multiples et conversion automatique
- Système de taxation modulaire adaptable aux réglementations locales
- Gestion des unités de mesure locales et conversion entre unités
- Modèles de rapports spécifiques par pays
- Architecture modulaire pour l'internationalisation avec configuration dynamique

## 2. User Stories & Critères d'acceptation

### US-INT-001: En tant que gestionnaire, je veux configurer les spécifications locales par pays
**Critères d'acceptation :**
- Saisie des informations de base du pays (nom, code ISO, devise principale)
- Configuration des législations fiscales applicables
- Spécification du système comptable utilisé (OHADA, local, etc.)
- Définition des unités de mesure locales
- Configuration des formats de reporting
- Activation/désactivation des modules selon les besoins locaux
- Historique des changements de configuration

### US-INT-002: En tant que gestionnaire, je veux gérer les différentes législations fiscales
**Critères d'acceptation :**
- Configuration des taux de taxes et impôts applicables
- Gestion des différentes structures fiscales selon le pays
- Calcul automatique des taxes selon les réglementations locales
- Génération de rapports fiscaux conformes aux normes locales
- Intégration avec les systèmes de reporting fiscaux locaux
- Suivi des échéances fiscales selon la législation locale
- Historique des modifications législatives

### US-INT-003: En tant que gestionnaire, je veux que le système supporte les systèmes comptables locaux
**Critères d'acceptation :**
- Support du système OHADA et autres systèmes comptables locaux
- Configuration des plans comptables spécifiques
- Adaptation des règles de comptabilité selon les systèmes locaux
- Génération des états financiers selon les normes locales
- Intégration avec les logiciels comptables locaux
- Conformité aux normes internationales de reporting
- Documentation des spécificités comptables locales

### US-INT-004: En tant que gestionnaire, je veux gérer les devises multiples
**Critères d'acceptation :**
- Support de plusieurs devises pour les transactions internationales
- Historique des taux de change journaux
- Conversion automatique selon les taux en temps réel ou historiques
- Affichage des montants dans la devise locale
- Génération de rapports financiers dans différentes devises
- Gestion des fluctuations de change
- Synchronisation avec les sources de taux de change externes

### US-INT-005: En tant que gestionnaire, je veux que les conversions de devises soient précises
**Critères d'acceptation :**
- Calcul des conversions selon les taux exacts
- Gestion des arrondis selon les règles locales
- Historique des conversions effectuées
- Validation des taux de change avant conversion
- Gestion des erreurs de conversion
- Journalisation des opérations de conversion
- Rapports de suivi des conversions

### US-INT-006: En tant que gestionnaire, je veux que les rapports financiers soient disponibles en devise locale
**Critères d'acceptation :**
- Génération des rapports dans la devise configurée pour le pays
- Convertion des montants selon les taux appropriés
- Préservation de la précision des montants convertis
- Affichage des taux de change utilisés
- Export des rapports dans la devise locale
- Conformité aux normes locales de reporting financier
- Historique des taux utilisés pour les rapports

### US-INT-007: En tant que gestionnaire, je veux disposer d'un système de taxation modulaire
**Critères d'acceptation :**
- Configuration des taux de taxes par pays
- Gestion des différentes structures fiscales
- Calcul automatique basé sur les réglementations locales
- Adaptation des règles de taxation selon le pays
- Intégration avec les modules de ventes/achats
- Reporting fiscal conforme aux normes locales
- Mise à jour automatique selon les changements législatifs

### US-INT-008: En tant que gestionnaire, je veux gérer les différentes unités de mesure selon les pays
**Critères d'acceptation :**
- Support des unités de mesure locales (litres, gallons, etc.)
- Système de conversion entre différentes unités
- Adaptation de l'interface selon les unités locales
- Calcul des conversions avec précision
- Affichage cohérent des unités dans les rapports
- Configuration des unités par pays/station
- Historique des conversions d'unités

### US-INT-009: En tant que gestionnaire, je veux disposer de modèles de rapports spécifiques par pays
**Critères d'acceptation :**
- Modèles de rapports personnalisés par pays
- Conformité aux normes locales de reporting
- Adaptation des formats aux exigences locales
- Génération automatique selon les spécifications locales
- Export dans les formats requis localement
- Intégration avec les systèmes de reporting locaux
- Mise à jour des modèles selon les évolutions légales

### US-INT-010: En tant que développeur, je veux une architecture modulaire pour l'internationalisation
**Critères d'acceptation :**
- Système conçu avec des modules interchangeables
- Configuration dynamique sans modification du code source
- Support des spécificités locales via un système de plugins
- Interfaces standardisées avec modules spécifiques selon la localisation
- Activation/désactivation de modules selon les besoins locaux
- Paramètres configurables par pays
- Documentation claire des points d'extension

## 3. Modèle de Données

### Tables existantes utilisées (sans modification)
- `utilisateurs` - données des utilisateurs
- `stations` - données des stations
- `pays` - données de base des pays
- `devises` - données des devises
- `comptes_comptables` - données des comptes comptables
- `ecritures_comptables` - données des écritures comptables
- `ventes` - données des ventes
- `achats` - données des achats
- `stocks` - données des stocks
- `modes_paiements` - données des modes de paiement
- `tresoreries` - données des trésoreries
- `modules` - données des modules fonctionnels

### Nouvelles tables à créer

```sql
-- Table pour les configurations pays
CREATE TABLE IF NOT EXISTS configurations_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_pays CHAR(3) NOT NULL UNIQUE, -- Code ISO 3166-1 alpha-3
    nom_pays VARCHAR(100) NOT NULL,
    devise_principale_id UUID REFERENCES devises(id),
    systeme_comptable VARCHAR(50) NOT NULL, -- 'OHADA', 'local', 'autre'
    taux_tva_default NUMERIC(5,2) DEFAULT 0,
    unite_mesure_default VARCHAR(10), -- 'litres', 'gallons', 'kg', etc.
    format_date_locale VARCHAR(20) DEFAULT 'DD/MM/YYYY', -- Format de date local
    format_nombre_locale VARCHAR(20) DEFAULT 'fr_FR', -- Localisation des nombres
    timezone VARCHAR(50) DEFAULT 'Africa/Nairobi', -- Fuseau horaire par défaut
    langue_interface VARCHAR(5) DEFAULT 'fr', -- Langue par défaut
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Test')),
    est_zone_ohada BOOLEAN DEFAULT FALSE,
    seuil_alerte_devise NUMERIC(18,2), -- Seuil pour alertes sur taux de change
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_modification_id UUID REFERENCES utilisateurs(id),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_modification TIMESTAMPTZ,
    CONSTRAINT chk_code_pays_format CHECK (code_pays ~ '^[A-Z]{3}$')
);

-- Table pour les taux de change
CREATE TABLE IF NOT EXISTS taux_change (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devise_source_id UUID REFERENCES devises(id),
    devise_destination_id UUID REFERENCES devises(id),
    taux_change NUMERIC(12,6) NOT NULL,
    date_effet DATE NOT NULL,
    date_maj_source DATE, -- Date de mise à jour des données source
    source_donnees VARCHAR(100), -- 'Banque Centrale', 'API externe', 'Saisie manuelle'
    utilisateur_maj_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    COMPARTMENT BY LIST (source_donnees), -- Partitionnement par source
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les structures fiscales par pays
CREATE TABLE IF NOT EXISTS structures_fiscales_pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES configurations_pays(id),
    type_taxe VARCHAR(50) NOT NULL, -- 'TVA', 'Accise', 'Impôt sur les sociétés', etc.
    taux_taxe NUMERIC(5,2) NOT NULL,
    code_taxe VARCHAR(20), -- Code officiel de la taxe
    libelle_taxe VARCHAR(100) NOT NULL,
    est_cumulative BOOLEAN DEFAULT FALSE, -- Si la taxe s'ajoute à d'autres taxes
    base_calcul VARCHAR(50) NOT NULL DEFAULT 'prix_ht', -- 'prix_ht', 'prix_ttc', 'quantite', etc.
    periodicite_declaration VARCHAR(20) DEFAULT 'mensuelle', -- 'mensuelle', 'trimestrielle', 'annuelle'
    date_debut_validite DATE NOT NULL,
    date_fin_validite DATE, -- NULL si permanente
    est_active BOOLEAN DEFAULT TRUE,
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les unités de mesure locales
CREATE TABLE IF NOT EXISTS unites_mesure_locales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES configurations_pays(id),
    nom_unite_locale VARCHAR(50) NOT NULL,
    symbole_unite_locale VARCHAR(10) NOT NULL,
    type_grande VARCHAR(20) NOT NULL, -- 'volume', 'masse', 'longueur', 'quantite'
    unite_reference VARCHAR(20) NOT NULL, -- 'litres', 'kilogrammes', 'mètres', 'unite'
    facteur_conversion NUMERIC(18,6) NOT NULL, -- Facteur pour conversion vers l'unité de référence
    est_unite_principale BOOLEAN DEFAULT FALSE,
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les conversions d'unités
CREATE TABLE IF NOT EXISTS conversions_unites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unite_origine_id UUID REFERENCES unites_mesure_locales(id),
    unite_destination_id UUID REFERENCES unites_mesure_locales(id),
    facteur_conversion NUMERIC(18,10) NOT NULL,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les modèles de rapports locaux
CREATE TABLE IF NOT EXISTS modeles_rapports_locaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_modele VARCHAR(50) UNIQUE NOT NULL,
    pays_id UUID REFERENCES configurations_pays(id),
    titre_modele VARCHAR(100) NOT NULL,
    description TEXT,
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'compte_resultat', 'etat_flux', 'fiscal', etc.
    format_sortie VARCHAR(20) DEFAULT 'PDF', -- 'PDF', 'Excel', 'Word', 'CSV'
    chemin_modele VARCHAR(200), -- Chemin vers le fichier modèle
    champs_requis JSONB, -- Liste des champs requis pour le modèle
    specifications_locales JSONB, -- Spécifications spécifiques au pays
    est_actif BOOLEAN DEFAULT TRUE,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_maj_id UUID REFERENCES utilisateurs(id),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT now(),
    date_mise_a_jour TIMESTAMPTZ,
    commentaire TEXT
);

-- Table pour les plans comptables locaux
CREATE TABLE IF NOT EXISTS plans_comptables_locaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES configurations_pays(id),
    systeme_comptable VARCHAR(50) NOT NULL, -- 'OHADA', 'local', 'autre'
    numero_plan VARCHAR(20) NOT NULL, -- Numéro du plan comptable
    libelle_plan VARCHAR(200) NOT NULL,
    date_effet DATE NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les associations de comptes comptables
CREATE TABLE IF NOT EXISTS associations_comptes_locaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES configurations_pays(id),
    compte_local_id UUID REFERENCES comptes_comptables(id),
    compte_standard_id UUID REFERENCES comptes_comptables(id), -- Compte standard SuccessFuel
    correspondance_parfaite BOOLEAN DEFAULT FALSE, -- Si la correspondance est exacte
    commentaire TEXT,
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les configurations modulaires
CREATE TABLE IF NOT EXISTS configurations_modules_locaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pays_id UUID REFERENCES configurations_pays(id),
    module_id UUID REFERENCES modules(id),
    est_active BOOLEAN DEFAULT TRUE,
    parametres_config JSONB, -- Paramètres de configuration spécifique pour le module
    utilisateur_createur_id UUID REFERENCES utilisateurs(id),
    utilisateur_maj_id UUID REFERENCES utilisateurs(id),
    date_activation DATE,
    date_desactivation DATE,
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les historiques de conversion de devises
CREATE TABLE IF NOT EXISTS historiques_conversions_devise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devise_source_id UUID REFERENCES devises(id),
    devise_destination_id UUID REFERENCES devises(id),
    montant_original NUMERIC(18,2) NOT NULL,
    montant_converti NUMERIC(18,2) NOT NULL,
    taux_utilise NUMERIC(12,6) NOT NULL,
    date_conversion TIMESTAMPTZ NOT NULL DEFAULT now(),
    utilisateur_convertisseur_id UUID REFERENCES utilisateurs(id),
    objet_conversion_type VARCHAR(50), -- Type de l'objet converti
    objet_conversion_id UUID, -- ID de l'objet converti
    commentaire TEXT
);

-- Table pour les historiques de conversion d'unités
CREATE TABLE IF NOT EXISTS historiques_conversions_unite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unite_origine_id UUID REFERENCES unites_mesure_locales(id),
    unite_destination_id UUID REFERENCES unites_mesure_locales(id),
    valeur_originale NUMERIC(18,6) NOT NULL,
    valeur_convertie NUMERIC(18,6) NOT NULL,
    facteur_utilise NUMERIC(18,10) NOT NULL,
    date_conversion TIMESTAMPTZ NOT NULL DEFAULT now(),
    utilisateur_convertisseur_id UUID REFERENCES utilisateurs(id),
    objet_conversion_type VARCHAR(50), -- Type de l'objet converti
    objet_conversion_id UUID, -- ID de l'objet converti
    commentaire TEXT
);
```

### Index recommandés
```sql
-- Index pour les configurations pays
CREATE INDEX IF NOT EXISTS idx_configurations_pays_code ON configurations_pays(code_pays);
CREATE INDEX IF NOT EXISTS idx_configurations_pays_devise ON configurations_pays(devise_principale_id);
CREATE INDEX IF NOT EXISTS idx_configurations_pays_statut ON configurations_pays(statut);

-- Index pour les taux de change
CREATE INDEX IF NOT EXISTS idx_taux_change_source_dest ON taux_change(devise_source_id, devise_destination_id);
CREATE INDEX IF NOT EXISTS idx_taux_change_date ON taux_change(date_effet);
CREATE INDEX IF NOT EXISTS idx_taux_change_source_donnees ON taux_change(source_donnees);

-- Index pour les structures fiscales
CREATE INDEX IF NOT EXISTS idx_structures_fiscales_pays ON structures_fiscales_pays(pays_id);
CREATE INDEX IF NOT EXISTS idx_structures_fiscales_type ON structures_fiscales_pays(type_taxe);
CREATE INDEX IF NOT EXISTS idx_structures_fiscales_active ON structures_fiscales_pays(est_active);

-- Index pour les unités de mesure locales
CREATE INDEX IF NOT EXISTS idx_unites_locales_pays ON unites_mesure_locales(pays_id);
CREATE INDEX IF NOT EXISTS idx_unites_locales_type ON unites_mesure_locales(type_grande);
CREATE INDEX IF NOT EXISTS idx_unites_locales_principale ON unites_mesure_locales(est_unite_principale);

-- Index pour les conversions d'unités
CREATE INDEX IF NOT EXISTS idx_conversions_unites_orig_dest ON conversions_unites(unite_origine_id, unite_destination_id);

-- Index pour les modèles de rapports locaux
CREATE INDEX IF NOT EXISTS idx_modeles_rapports_pays ON modeles_rapports_locaux(pays_id);
CREATE INDEX IF NOT EXISTS idx_modeles_rapports_code ON modeles_rapports_locaux(code_modele);
CREATE INDEX IF NOT EXISTS idx_modeles_rapports_actif ON modeles_rapports_locaux(est_actif);

-- Index pour les plans comptables locaux
CREATE INDEX IF NOT EXISTS idx_plans_comptables_pays ON plans_comptables_locaux(pays_id);
CREATE INDEX IF NOT EXISTS idx_plans_comptables_actif ON plans_comptables_locaux(est_actif);

-- Index pour les associations de comptes
CREATE INDEX IF NOT EXISTS idx_associations_comptes_pays ON associations_comptes_locaux(pays_id);
CREATE INDEX IF NOT EXISTS idx_associations_comptes_local ON associations_comptes_locaux(compte_local_id);

-- Index pour les configurations modulaires
CREATE INDEX IF NOT EXISTS idx_configurations_modules_pays ON configurations_modules_locaux(pays_id);
CREATE INDEX IF NOT EXISTS idx_configurations_modules_module ON configurations_modules_locaux(module_id);
CREATE INDEX IF NOT EXISTS idx_configurations_modules_active ON configurations_modules_locaux(est_active);

-- Index pour les historiques
CREATE INDEX IF NOT EXISTS idx_historiques_conv_devise ON historiques_conversions_devise(date_conversion);
CREATE INDEX IF NOT EXISTS idx_historiques_conv_unite ON historiques_conversions_unite(date_conversion);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour s'assurer qu'un seul système de comptabilité est actif par pays
CREATE OR REPLACE FUNCTION validate_unique_active_plan()
RETURNS TRIGGER AS $$
DECLARE
    active_count INTEGER;
BEGIN
    -- Vérifier qu'il n'y ait qu'un seul plan comptable actif par pays et système
    SELECT COUNT(*) INTO active_count
    FROM plans_comptables_locaux
    WHERE pays_id = NEW.pays_id 
      AND systeme_comptable = NEW.systeme_comptable
      AND est_actif = TRUE
      AND id != NEW.id; -- Exclure l'élément en cours de modification
    
    IF NEW.est_actif AND active_count > 0 THEN
        RAISE EXCEPTION 'Un seul plan comptable peut être actif par pays et système';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_unique_active_plan
    BEFORE INSERT OR UPDATE ON plans_comptables_locaux
    FOR EACH ROW EXECUTE FUNCTION validate_unique_active_plan();

-- Trigger pour s'assurer qu'une seule unité principale existe par type et pays
CREATE OR REPLACE FUNCTION validate_unique_main_unit()
RETURNS TRIGGER AS $$
DECLARE
    main_count INTEGER;
BEGIN
    -- Vérifier qu'il n'y ait qu'une seule unité principale par type et pays
    SELECT COUNT(*) INTO main_count
    FROM unites_mesure_locales
    WHERE pays_id = NEW.pays_id 
      AND type_grande = NEW.type_grande
      AND est_unite_principale = TRUE
      AND id != NEW.id; -- Exclure l'élément en cours de modification
    
    IF NEW.est_unite_principale AND main_count > 0 THEN
        RAISE EXCEPTION 'Une seule unité principale peut être définie par type et pays';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_unique_main_unit
    BEFORE INSERT OR UPDATE ON unites_mesure_locales
    FOR EACH ROW EXECUTE FUNCTION validate_unique_main_unit();

-- Trigger pour vérifier que les taux de change ne sont pas dupliqués pour la même paire et date
CREATE OR REPLACE FUNCTION validate_unique_taux_change()
RETURNS TRIGGER AS $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    -- Vérifier qu'il n'existe pas déjà un taux pour la même paire de devises à la même date
    SELECT COUNT(*) INTO duplicate_count
    FROM taux_change
    WHERE devise_source_id = NEW.devise_source_id 
      AND devise_destination_id = NEW.devise_destination_id
      AND date_effet = NEW.date_effet
      AND id != NEW.id; -- Exclure l'élément en cours de modification
    
    IF duplicate_count > 0 THEN
        RAISE EXCEPTION 'Un taux de change existe déjà pour cette paire de devises à cette date';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_unique_taux_change
    BEFORE INSERT OR UPDATE ON taux_change
    FOR EACH ROW EXECUTE FUNCTION validate_unique_taux_change();

-- Fonction pour mettre à jour la date de modification dans les configurations pays
CREATE OR REPLACE FUNCTION update_config_pays_modification_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification := now();
    NEW.utilisateur_modification_id := NEW.utilisateur_createur_id; -- Devrait être mis à jour avec l'utilisateur réel
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_config_pays_modification_date
    BEFORE UPDATE ON configurations_pays
    FOR EACH ROW EXECUTE FUNCTION update_config_pays_modification_date();
```

## 4. API Backend

### 4.1 Gestion des configurations pays

#### POST /api/internationalisation/configurations-pays
**Description:** Créer une nouvelle configuration pays

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "code_pays": "string (ISO 3166-1 alpha-3, format XXX)",
  "nom_pays": "string (max 100)",
  "devise_principale_id": "uuid",
  "systeme_comptable": "OHADA|local|autre",
  "taux_tva_default": "decimal (max 5,2)",
  "unite_mesure_default": "string (max 10)",
  "format_date_locale": "string (default: DD/MM/YYYY)",
  "format_nombre_locale": "string (default: fr_FR)",
  "timezone": "string (default: Africa/Nairobi)",
  "langue_interface": "string (default: fr)",
  "est_zone_ohada": "boolean",
  "seuil_alerte_devise": "decimal (max 18,2) (optionnel)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code_pays": "string",
    "nom_pays": "string",
    "devise_principale_id": "uuid",
    "systeme_comptable": "string",
    "taux_tva_default": "decimal",
    "unite_mesure_default": "string",
    "format_date_locale": "string",
    "format_nombre_locale": "string",
    "timezone": "string",
    "langue_interface": "string",
    "statut": "string",
    "est_zone_ohada": "boolean",
    "seuil_alerte_devise": "decimal",
    "commentaire": "string",
    "utilisateur_createur_id": "uuid",
    "date_creation": "datetime"
  },
  "message": "Configuration pays créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Configuration créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Devise non trouvée
- 409: Code pays déjà existant
- 500: Erreur interne du serveur

#### PUT /api/internationalisation/configurations-pays/{id}
**Description:** Mettre à jour une configuration pays

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "systeme_comptable": "OHADA|local|autre",
  "taux_tva_default": "decimal (max 5,2)",
  "unite_mesure_default": "string (max 10)",
  "format_date_locale": "string",
  "format_nombre_locale": "string",
  "timezone": "string",
  "langue_interface": "string",
  "est_zone_ohada": "boolean",
  "seuil_alerte_devise": "decimal (max 18,2) (optionnel)",
  "commentaire": "text (optionnel)",
  "statut": "Actif|Inactif|Test"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code_pays": "string",
    "nom_pays": "string",
    "devise_principale_id": "uuid",
    "systeme_comptable": "string",
    "taux_tva_default": "decimal",
    "unite_mesure_default": "string",
    "format_date_locale": "string",
    "format_nombre_locale": "string",
    "timezone": "string",
    "langue_interface": "string",
    "statut": "string",
    "est_zone_ohada": "boolean",
    "seuil_alerte_devise": "decimal",
    "commentaire": "string",
    "utilisateur_modification_id": "uuid",
    "date_modification": "datetime"
  },
  "message": "Configuration pays mise à jour avec succès"
}
```

**HTTP Status Codes:**
- 200: Configuration mise à jour avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Configuration pays non trouvée
- 409: Conflit de configuration
- 500: Erreur interne du serveur

### 4.2 Gestion des taux de change

#### POST /api/internationalisation/taux-change
**Description:** Créer ou mettre à jour un taux de change

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "devise_source_id": "uuid",
  "devise_destination_id": "uuid",
  "taux_change": "decimal (max 12,6)",
  "date_effet": "date (format YYYY-MM-DD)",
  "date_maj_source": "date (format YYYY-MM-DD) (optionnel)",
  "source_donnees": "string (max 100)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "devise_source_id": "uuid",
    "devise_destination_id": "uuid",
    "taux_change": "decimal",
    "date_effet": "date",
    "date_maj_source": "date",
    "source_donnees": "string",
    "commentaire": "string",
    "utilisateur_maj_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Taux de change enregistré avec succès"
}
```

**HTTP Status Codes:**
- 201: Taux de change créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Devise non trouvée
- 409: Taux existant pour la même paire et date
- 500: Erreur interne du serveur

#### GET /api/internationalisation/taux-change
**Description:** Obtenir les taux de change pour une période

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- devise_source_id: uuid (obligatoire)
- devise_destination_id: uuid (obligatoire)
- date_debut: date (format YYYY-MM-DD) (optionnel)
- date_fin: date (format YYYY-MM-DD) (optionnel)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "taux": [
      {
        "id": "uuid",
        "devise_source_id": "uuid",
        "devise_destination_id": "uuid",
        "taux_change": "decimal",
        "date_effet": "date",
        "date_maj_source": "date",
        "source_donnees": "string",
        "commentaire": "string"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "Taux de change récupérés avec succès"
}
```

**HTTP Status Codes:**
- 200: Données récupérées avec succès
- 400: Paramètres invalides
- 401: Non autorisé
- 403: Accès refusé
- 500: Erreur interne du serveur

### 4.3 Gestion des structures fiscales

#### POST /api/internationalisation/structures-fiscales
**Description:** Créer une nouvelle structure fiscale pour un pays

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "pays_id": "uuid",
  "type_taxe": "string (max 50)",
  "taux_taxe": "decimal (max 5,2)",
  "code_taxe": "string (max 20) (optionnel)",
  "libelle_taxe": "string (max 100)",
  "est_cumulative": "boolean (default: false)",
  "base_calcul": "prix_ht|prix_ttc|quantite (default: prix_ht)",
  "periodicite_declaration": "mensuelle|trimestrielle|annuelle (default: mensuelle)",
  "date_debut_validite": "date (format YYYY-MM-DD)",
  "date_fin_validite": "date (format YYYY-MM-DD) (optionnel)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "pays_id": "uuid",
    "type_taxe": "string",
    "taux_taxe": "decimal",
    "code_taxe": "string",
    "libelle_taxe": "string",
    "est_cumulative": "boolean",
    "base_calcul": "string",
    "periodicite_declaration": "string",
    "date_debut_validite": "date",
    "date_fin_validite": "date",
    "est_active": "boolean",
    "commentaire": "string",
    "utilisateur_createur_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Structure fiscale créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Structure fiscale créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Pays non trouvé
- 500: Erreur interne du serveur

### 4.4 Gestion des unités de mesure

#### POST /api/internationalisation/unites-mesure
**Description:** Créer une nouvelle unité de mesure locale

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "pays_id": "uuid",
  "nom_unite_locale": "string (max 50)",
  "symbole_unite_locale": "string (max 10)",
  "type_grande": "volume|masse|longueur|quantite",
  "unite_reference": "litres|kilogrammes|metres|unite",
  "facteur_conversion": "decimal (max 18,6)",
  "est_unite_principale": "boolean (default: false)",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "pays_id": "uuid",
    "nom_unite_locale": "string",
    "symbole_unite_locale": "string",
    "type_grande": "string",
    "unite_reference": "string",
    "facteur_conversion": "decimal",
    "est_unite_principale": "boolean",
    "commentaire": "string",
    "utilisateur_createur_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Unité de mesure locale créée avec succès"
}
```

**HTTP Status Codes:**
- 201: Unité de mesure créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Pays non trouvé
- 409: Unité principale existe déjà pour ce type et pays
- 500: Erreur interne du serveur

### 4.5 Gestion des modèles de rapports

#### POST /api/internationalisation/modeles-rapports
**Description:** Créer un nouveau modèle de rapport local

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "code_modele": "string (unique, max 50)",
  "pays_id": "uuid",
  "titre_modele": "string (max 100)",
  "description": "text (optionnel)",
  "type_rapport": "bilan|compte_resultat|etat_flux|fiscal|autre",
  "format_sortie": "PDF|Excel|Word|CSV (default: PDF)",
  "chemin_modele": "string (max 200) (optionnel)",
  "champs_requis": "json",
  "specifications_locales": "json",
  "commentaire": "text (optionnel)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code_modele": "string",
    "pays_id": "uuid",
    "titre_modele": "string",
    "description": "text",
    "type_rapport": "string",
    "format_sortie": "string",
    "chemin_modele": "string",
    "champs_requis": "json",
    "specifications_locales": "json",
    "est_actif": "boolean",
    "commentaire": "text",
    "utilisateur_createur_id": "uuid",
    "date_creation": "datetime"
  },
  "message": "Modèle de rapport local créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Modèle de rapport créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Pays non trouvé
- 409: Code modèle déjà existant
- 500: Erreur interne du serveur

## 5. Logique Métier

### Règles de gestion multi-pays
1. Chaque pays dispose d'une configuration unique avec ses spécifications locales
2. Les législations fiscales sont appliquées selon le pays de la station
3. Les systèmes comptables varient selon les pays (OHADA, locaux, etc.)
4. Les formats de reporting sont adaptés aux exigences locales
5. Les unités de mesure sont locales au pays concerné
6. Les devises sont gérées selon les besoins locaux

### Règles de gestion des devises
1. Les taux de change sont valides à partir d'une date précise
2. Les conversions utilisent les taux en vigueur à la date des transactions
3. Les rapports financiers peuvent être générés dans différentes devises
4. Les fluctuations de change sont enregistrées et suivies
5. Les taux de change proviennent de sources fiables (banques centrales, API externes)
6. Les seuils d'alerte peuvent être configurés pour les variations importantes

### Règles de gestion fiscale
1. Les taux de taxe sont spécifiques à chaque pays
2. Les structures fiscales peuvent être cumulatives ou exclusives
3. Les déclarations fiscales suivent les périodicités locales
4. Les calculs fiscaux sont effectués selon les bases locales
5. Les modifications législatives sont prises en compte avec dates de validité
6. Les rapports fiscaux sont conformes aux normes locales

### Règles de gestion des unités de mesure
1. Les unités sont spécifiques à chaque pays
2. Les conversions entre unités sont précises et inversibles
3. L'unité principale est unique par type et par pays
4. Les interfaces s'adaptent aux unités locales
5. Les rapports affichent les unités appropriées
6. Les conversions sont historisées pour traçabilité

### Règles de gestion des rapports
1. Les modèles sont spécifiques à chaque pays
2. Les formats de sortie sont adaptables aux besoins locaux
3. Les données sont présentées selon les normes locales
4. Les exports respectent les formats requis localement
5. Les rapports sont disponibles dans la langue locale
6. Les spécifications peuvent être mises à jour indépendamment

### Règles d'architecture modulaire
1. Les modules peuvent être activés/désactivés selon les pays
2. Les paramètres sont configurables dynamiquement
3. Les spécificités locales sont intégrées via des plugins
4. Les interfaces sont standardisées avec spécialisations locales
5. L'extensibilité est garantie via des points d'extension clairs
6. La maintenance des spécificités locales est facilitée

### Impacts sur d'autres modules
1. Les modules de vente/achat intègrent la gestion des taxes locales
2. Les modules comptables s'adaptent aux systèmes locaux
3. Les modules de reporting utilisent les modèles locaux
4. Les modules de trésorerie gèrent les devises locales
5. Les modules de stock gèrent les unités de mesure locales
6. Les modules d'interface s'adaptent aux spécificités pays

## 6. Diagrammes / Séquences

### Schéma ERD (simplifié)
```
utilisateurs ||--o{ configurations_pays
utilisateurs ||--o{ taux_change
utilisateurs ||--o{ structures_fiscales_pays
utilisateurs ||--o{ unites_mesure_locales
pays ||--o{ configurations_pays
devises ||--o{ configurations_pays (devise_principale)
devises ||--o{ taux_change (source)
devises ||--o{ taux_change (destination)
configurations_pays ||--o{ structures_fiscales_pays
configurations_pays ||--o{ unites_mesure_locales
configurations_pays ||--o{ modeles_rapports_locaux
configurations_pays ||--o{ plans_comptables_locaux
modules ||--o{ configurations_modules_locaux
comptes_comptables ||--o{ associations_comptes_locaux
unites_mesure_locales ||--o{ conversions_unites (origine)
unites_mesure_locales ||--o{ conversions_unites (destination)
```

### Diagramme de séquence pour une conversion de devise
```
Utilisateur -> API: POST /api/internationalisation/conversion-devise
API -> ConfigurationsPays: Récupérer pays de la station
ConfigurationsPays -> API: Retourner devise locale
API -> TauxChange: Chercher taux applicable à la date
TauxChange -> API: Retourner taux trouvé ou erreur
API -> ServiceConversionDevise: Convertir le montant
ServiceConversionDevise -> Historiques: Enregistrer opération de conversion
ServiceConversionDevise -> API: Retourner montant converti
API -> Utilisateur: Retourner résultat de conversion
```

## 7. Tests Requises

### Tests unitaires
1. Test des fonctions de conversion de devises selon différents scénarios
2. Test des validations de données pour les différentes entités
3. Test des calculs fiscaux selon différentes structures locales
4. Test des conversions d'unités avec précision
5. Test des règles d'intégrité pour les configurations pays
6. Test des fonctions d'activation/désactivation des modules

### Tests d'intégration
1. Test complet du processus de configuration d'un nouveau pays
2. Test de la conversion de devises à travers les modules
3. Test de l'application des taxes selon la localisation
4. Test de la génération de rapports selon les modèles locaux
5. Test de l'adaptation des unités de mesure dans l'interface
6. Test de l'activation des modules selon les spécificités locales

### Tests de charge/performance
1. Test de performance pour des conversions de devises massives
2. Test de performance pour des calculs fiscaux complexes
3. Test de performance pour la génération de rapports dans différentes devises
4. Test de la synchronisation des taux de change pour plusieurs pays
5. Test de la gestion concurrentielle des configurations par plusieurs utilisateurs

### Jeux de données de test
1. Données de configuration pour plusieurs pays africains francophones
2. Données de taux de change historiques et en temps réel
3. Données de structures fiscales pour différents systèmes
4. Données d'unités de mesure locales et de conversion
5. Modèles de rapports pour différentes exigences locales
6. Données de plans comptables pour les systèmes OHADA et locaux

## 8. Checklist Développeur

### Tâches techniques détaillées
1. [ ] Créer les nouvelles tables dans la base de données
2. [ ] Implémenter les triggers et contrôles d'intégrité
3. [ ] Créer les modèles SQLAlchemy pour les nouvelles tables
4. [ ] Implémenter les endpoints API pour la gestion internationale
5. [ ] Créer les services de conversion de devises
6. [ ] Implémenter la logique de gestion fiscale modulaire
7. [ ] Créer les services de conversion d'unités
8. [ ] Implémenter la gestion des modèles de rapports locaux
9. [ ] Créer le système de configuration dynamique des modules
10. [ ] Créer les tests unitaires et d'intégration
11. [ ] Implémenter la gestion des erreurs et logs
12. [ ] Créer les vues frontend pour la gestion internationale (si applicable)
13. [ ] Documenter les endpoints API
14. [ ] Intégrer avec les modules existants pour la prise en compte des spécificités locales
15. [ ] Créer un système de mise à jour automatisée des taux de change

### Ordre recommandé
1. Commencer par la création des tables de base (configurations pays, devises)
2. Implémenter les services de conversion de devises
3. Développer la gestion fiscale modulaire
4. Créer les fonctions de conversion d'unités
5. Implémenter la gestion des modèles de rapports
6. Développer l'architecture modulaire pour les spécificités locales
7. Intégrer avec les modules existants
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
7. Documentation sur la configuration pour de nouveaux pays

## 9. Risques & Points de vigilance

### Points sensibles
1. La complexité de la gestion des spécificités légales de chaque pays
2. La précision des conversions de devises et d'unités
3. La sécurité des données financières sensibles dans les conversions
4. La performance des calculs pour de grands volumes de transactions internationales
5. La conformité aux législations locales en constante évolution

### Risques techniques
1. Risque d'erreurs dans les calculs fiscaux selon les réglementations locales
2. Risque de non-conformité aux normes comptables locales
3. Risque de problèmes de performances avec de multiples conversions
4. Risque de perte de précision dans les conversions de devise/unité
5. Risque de manipulation des données par des utilisateurs non autorisés
6. Risque d'obsolescence des taux de change ou données fiscales

### Dette technique potentielle
1. Complexité accrue du système avec l'ajout de multiples spécificités locales
2. Risque d'augmentation de la dette technique si le code n'est pas bien architecturé
3. Besoin de maintenance continue pour les taux de change et structures fiscales
4. Risque de dépendance excessive à des sources externes de données
5. Risque de complexité dans la configuration des spécificités pays