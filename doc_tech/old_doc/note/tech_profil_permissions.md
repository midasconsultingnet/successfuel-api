# Technical Specification - Gestion des profils et permissions RBAC

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter un système complet de gestion des profils utilisateurs et des permissions selon le modèle RBAC (Role-Based Access Control) pour le système SuccessFuel. Ce système permettra aux administrateurs de gérer les droits d'accès des utilisateurs de manière fine, avec une distinction claire entre les rôles, les permissions attachées à ces rôles, et les stations auxquelles les utilisateurs ont accès.

### Problème à résoudre
Le système SuccessFuel a besoin d'un mécanisme de gestion des autorisations qui permet :
- De créer des profils avec des permissions spécifiques
- D'assigner des utilisateurs à des profils
- De restreindre l'accès des utilisateurs à certaines stations
- De gérer des permissions par module fonctionnel
- De permettre une gestion décentralisée des profils par compagnie

### Définition du périmètre
Le périmètre inclut :
- Gestion des structures de base (pays, compagnies, stations)
- Gestion des modules fonctionnels et des permissions
- Gestion des profils et des permissions associées
- Gestion des utilisateurs et de leurs attributions
- Contrôle d'accès basé sur les profils et les stations
- Journalisation des actions liées à la gestion des accès
- Distinction des endpoints pour administrateurs et utilisateurs
- Classification des types d'utilisateurs avec contrôles d'accès distincts

## 2. User Stories & Critères d'acceptation

### US-RBAC-001: En tant qu'administrateur, je veux gérer les pays
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver un pays
  - Chaque pays a un code unique (ISO 3 caractères)
  - Pouvoir configurer les spécifications locales par pays (devise, TVA, système comptable)

### US-RBAC-002: En tant qu'administrateur, je veux gérer les compagnies
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver une compagnie
  - Chaque compagnie a un code unique
  - Pouvoir associer des stations à une compagnie
  - Pouvoir associer une compagnie à un pays

### US-RBAC-003: En tant qu'administrateur, je veux gérer les stations-service
- **Critères d'acceptation :**
  - Pouvoir créer, modifier une station
  - Chaque station est liée à une seule compagnie
  - Pouvoir activer/désactiver une station
  - Pouvoir associer une station à un pays

### US-RBAC-004: En tant qu'administrateur, je veux gérer les modules fonctionnels
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des modules
  - Chaque module a un libellé unique
  - Les modules servent de regroupement pour les permissions

### US-RBAC-005: En tant qu'administrateur, je veux gérer les permissions
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des permissions
  - Chaque permission est rattachée à un module
  - Les permissions sont de type CRUD (Create, Read, Update, Delete) ou spécifiques

### US-RBAC-006: En tant qu'administrateur, je veux créer et gérer des profils utilisateurs
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des profils
  - Chaque profil peut être affecté à une seule compagnie
  - Pouvoir assigner des permissions à un profil
  - Pouvoir supprimer des permissions d'un profil

### US-RBAC-007: En tant qu'administrateur, je veux créer et gérer des utilisateurs
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver des utilisateurs
  - Chaque utilisateur a un login unique
  - Chaque utilisateur est affecté à un profil
  - Chaque utilisateur peut être limité à certaines stations
  - Le mot de passe est haché avec bcrypt
  - Classification du type d'utilisateur (super_administrateur, administrateur, gerant_compagnie, utilisateur_compagnie)

### US-RBAC-008: En tant qu'administrateur, je veux restreindre les accès par station
- **Critères d'acceptation :**
  - Pouvoir assigner des stations spécifiques à un utilisateur
  - L'utilisateur ne peut accéder qu'aux données des stations qui lui sont assignées
  - Les stations sont stockées dans un format JSONB

### US-RBAC-009: En tant qu'administrateur, je veux distinguer les endpoints pour administrateurs et utilisateurs
- **Critères d'acceptation :**
  - Les utilisateurs de type "super_administrateur" et "administrateur" doivent utiliser l'endpoint administrateur
  - Les utilisateurs de type "gerant_compagnie" et "utilisateur_compagnie" doivent utiliser l'endpoint utilisateur
  - Bloquer automatiquement les accès interdits entre les endpoints
  - Journaliser les tentatives d'accès non autorisées aux endpoints

### US-RBAC-010: En tant qu'administrateur, je veux contrôler les validations hiérarchiques
- **Critères d'acceptation :**
  - Système de validation selon le montant ou le type d'opération
  - Niveau de validation basé sur le type d'utilisateur
  - Journalisation des validations effectuées

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: pays
```sql
CREATE TABLE pays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_pays VARCHAR(3) UNIQUE NOT NULL,  -- ISO 3166-1 alpha-3
    nom_pays VARCHAR(100) NOT NULL,
    devise_principale VARCHAR(3) DEFAULT 'MGA',
    taux_tva_par_defaut DECIMAL(5,2) DEFAULT 20.00,  -- Format: 20.00 pour 20%
    systeme_comptable VARCHAR(50) DEFAULT 'IFRS', -- IFRS, GAAP, etc.
    date_application_tva DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_pays_code ON pays(code_pays);
CREATE INDEX idx_pays_statut ON pays(statut);
```

#### Table: compagnies
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

-- Index pour les performances
CREATE INDEX idx_compagnies_code ON compagnies(code);
CREATE INDEX idx_compagnies_statut ON compagnies(statut);
CREATE INDEX idx_compagnies_pays ON compagnies(pays_id);
```

#### Table: stations
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

-- Index pour les performances
CREATE INDEX idx_stations_compagnie ON stations(compagnie_id);
CREATE INDEX idx_stations_code ON stations(code);
CREATE INDEX idx_stations_statut ON stations(statut);
```

#### Table: modules
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

-- Index pour les performances
CREATE INDEX idx_modules_libelle ON modules(libelle);
```

#### Table: permissions
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,        -- Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description TEXT,
    module_id UUID REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_permissions_libelle ON permissions(libelle);
CREATE INDEX idx_permissions_module ON permissions(module_id);
CREATE INDEX idx_permissions_statut ON permissions(statut);
```

#### Table: profils
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

-- Index pour les performances
CREATE INDEX idx_profils_code ON profils(code);
CREATE INDEX idx_profils_compagnie ON profils(compagnie_id);
CREATE INDEX idx_profils_statut ON profils(statut);
```

#### Table: profil_permissions
```sql
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(profil_id, permission_id)
);

-- Index pour les performances
CREATE INDEX idx_profil_permissions_profil ON profil_permissions(profil_id);
CREATE INDEX idx_profil_permissions_permission ON profil_permissions(permission_id);
```

#### Table: utilisateurs
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
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime', 'Bloque')) NOT NULL,
    last_login TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id),
    type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_utilisateurs_login ON utilisateurs(login);
CREATE INDEX idx_utilisateurs_profil ON utilisateurs(profil_id);
CREATE INDEX idx_utilisateurs_compagnie ON utilisateurs(compagnie_id);
CREATE INDEX idx_utilisateurs_statut ON utilisateurs(statut);
CREATE INDEX idx_utilisateurs_type ON utilisateurs(type_utilisateur);
```

#### Table: auth_tokens
```sql
CREATE TABLE auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL, -- Haché du jeton
    user_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    type_endpoint VARCHAR(20) DEFAULT 'utilisateur' CHECK (type_endpoint IN ('administrateur', 'utilisateur')), -- Endpoint pour lequel le jeton est valide
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la recherche par token_hash
CREATE INDEX idx_auth_tokens_hash ON auth_tokens(token_hash);

-- Index pour la recherche par utilisateur
CREATE INDEX idx_auth_tokens_user ON auth_tokens(user_id);

-- Index pour filtrer par statut et date d'expiration
CREATE INDEX idx_auth_tokens_status ON auth_tokens(is_active, expires_at);

-- Index pour filtrer par type d'endpoint
CREATE INDEX idx_auth_tokens_endpoint ON auth_tokens(type_endpoint);
```

#### Table: tentatives_acces_non_autorise
```sql
CREATE TABLE tentatives_acces_non_autorise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    endpoint_accesse VARCHAR(20) NOT NULL, -- Endpoint que l'utilisateur a tenté d'accéder
    endpoint_autorise VARCHAR(20), -- Endpoint que l'utilisateur aurait dû utiliser
    ip_connexion VARCHAR(45),
    statut VARCHAR(20) DEFAULT 'Traite' CHECK (statut IN ('EnAttente', 'Traite', 'Enquete')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les analyses de sécurité
CREATE INDEX idx_tentatives_acces_non_autorise_date ON tentatives_acces_non_autorise(created_at);
CREATE INDEX idx_tentatives_acces_non_autorise_utilisateur ON tentatives_acces_non_autorise(utilisateur_id);
CREATE INDEX idx_tentatives_acces_non_autorise_endpoint ON tentatives_acces_non_autorise(endpoint_accesse);
```

### 3.2 Relations
- `pays.id` → `compagnies.pays_id` (One-to-Many)
- `pays.id` → `stations.pays_id` (One-to-Many)
- `compagnies.id` → `stations.compagnie_id` (One-to-Many)
- `compagnies.id` → `profils.compagnie_id` (One-to-Many)
- `compagnies.id` → `utilisateurs.compagnie_id` (One-to-Many)
- `modules.id` → `permissions.module_id` (One-to-Many)
- `profils.id` → `profil_permissions.profil_id` (One-to-Many)
- `permissions.id` → `profil_permissions.permission_id` (One-to-Many)
- `profils.id` → `utilisateurs.profil_id` (One-to-Many)
- `utilisateurs.id` → `auth_tokens.user_id` (One-to-Many)
- `utilisateurs.id` → `tentatives_acces_non_autorise.utilisateur_id` (One-to-Many)

### 3.3 Triggers et règles d'intégrité
```sql
-- Trigger pour hasher le mot de passe avant insertion/modification
CREATE OR REPLACE FUNCTION hash_mot_de_passe()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR NEW.mot_de_passe <> OLD.mot_de_passe THEN
        NEW.mot_de_passe := crypt(NEW.mot_de_passe, gen_salt('bf'));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_hash_mot_de_passe
    BEFORE INSERT OR UPDATE ON utilisateurs
    FOR EACH ROW
    EXECUTE FUNCTION hash_mot_de_passe();

-- Trigger pour mettre à jour le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_utilisateurs_updated_at
    BEFORE UPDATE ON utilisateurs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_profils_updated_at
    BEFORE UPDATE ON profils
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_pays_updated_at
    BEFORE UPDATE ON pays
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_compagnies_updated_at
    BEFORE UPDATE ON compagnies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 4. API Backend

### 4.1 Gestion des pays

#### POST /api/v1/pays
- **Description**: Créer un nouveau pays
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code_pays": "string (3 chars)",
    "nom_pays": "string (100 chars max)",
    "devise_principale": "string (3 chars max)",
    "taux_tva_par_defaut": "number",
    "systeme_comptable": "string (50 chars max)",
    "date_application_tva": "string (format YYYY-MM-DD)",
    "statut": "string ('Actif', 'Inactif')"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code_pays": "string",
        "nom_pays": "string",
        "devise_principale": "string",
        "taux_tva_par_defaut": "number",
        "systeme_comptable": "string",
        "date_application_tva": "string",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Code pays déjà existant

#### GET /api/v1/pays
- **Description**: Lister tous les pays
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - statut: "string" ('Actif', 'Inactif')
  - limit: "integer"
  - offset: "integer"
  - search: "string"
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "code_pays": "string",
            "nom_pays": "string",
            "devise_principale": "string",
            "taux_tva_par_defaut": "number",
            "systeme_comptable": "string",
            "date_application_tva": "string",
            "statut": "string",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ],
    "pagination": {
        "page": "integer",
        "limit": "integer",
        "total": "integer",
        "pages": "integer"
    }
}
```

#### PUT /api/v1/pays/{pays_id}
- **Description**: Mettre à jour un pays
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code_pays": "string (3 chars)",
    "nom_pays": "string (100 chars max)",
    "devise_principale": "string (3 chars max)",
    "taux_tva_par_defaut": "number",
    "systeme_comptable": "string (50 chars max)",
    "date_application_tva": "string (format YYYY-MM-DD)",
    "statut": "string ('Actif', 'Inactif')"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code_pays": "string",
        "nom_pays": "string",
        "devise_principale": "string",
        "taux_tva_par_defaut": "number",
        "systeme_comptable": "string",
        "date_application_tva": "string",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.2 Gestion des compagnies

#### POST /api/v1/companies
- **Description**: Créer une nouvelle compagnie
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "nom": "string (150 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "email": "string (150 chars max)",
    "nif": "string (50 chars max)",
    "pays_id": "uuid",
    "devise_principale": "string (3 chars max)"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "nif": "string",
        "statut": "string",
        "pays_id": "uuid",
        "devise_principale": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Code déjà existant

#### GET /api/v1/companies
- **Description**: Lister toutes les compagnies
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - statut: "string" ('Actif', 'Inactif', 'Supprime')
  - pays_id: "uuid"
  - limit: "integer"
  - offset: "integer"
- **Réponse**:
```json
{
    "success": true,
    "pagination": {
        "total": "integer",
        "limit": "integer",
        "offset": "integer"
    },
    "data": [
        {
            "id": "uuid",
            "code": "string",
            "nom": "string",
            "adresse": "string",
            "telephone": "string",
            "email": "string",
            "nif": "string",
            "statut": "string",
            "pays_id": "uuid",
            "devise_principale": "string",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ]
}
```

#### PUT /api/v1/companies/{company_id}
- **Description**: Mettre à jour une compagnie
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "nom": "string (150 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "email": "string (150 chars max)",
    "nif": "string (50 chars max)",
    "pays_id": "uuid",
    "devise_principale": "string (3 chars max)",
    "statut": "string ('Actif', 'Inactif', 'Supprime')"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "nif": "string",
        "statut": "string",
        "pays_id": "uuid",
        "devise_principale": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### 4.3 Gestion des stations

#### POST /api/v1/stations
- **Description**: Créer une nouvelle station
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "compagnie_id": "uuid",
    "code": "string (20 chars max)",
    "nom": "string (100 chars max)",
    "adresse": "string",
    "telephone": "string (30 chars max)",
    "email": "string (150 chars max)",
    "pays_id": "uuid"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "compagnie_id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "pays_id": "uuid",
        "statut": "string",
        "created_at": "timestamp"
    }
}
```

#### GET /api/v1/stations/{station_id}
- **Description**: Récupérer les détails d'une station
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "compagnie_id": "uuid",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "pays_id": "uuid",
        "statut": "string",
        "created_at": "timestamp"
    }
}
```

### 4.4 Gestion des modules et permissions

#### POST /api/v1/modules
- **Description**: Créer un nouveau module
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "libelle": "string (100 chars max)"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "libelle": "string",
        "statut": "string"
    }
}
```

#### GET /api/v1/modules
- **Description**: Lister tous les modules
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "libelle": "string",
            "statut": "string"
        }
    ]
}
```

#### POST /api/v1/permissions
- **Description**: Créer une nouvelle permission
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "libelle": "string (100 chars max)",
    "description": "string",
    "module_id": "uuid"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "libelle": "string",
        "description": "string",
        "module_id": "uuid",
        "statut": "string",
        "created_at": "timestamp"
    }
}
```

### 4.5 Gestion des profils

#### POST /api/v1/profiles
- **Description**: Créer un nouveau profil
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string (20 chars max)",
    "libelle": "string (100 chars max)",
    "description": "string",
    "compagnie_id": "uuid",
    "permissions": ["uuid", ...]
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
        "compagnie_id": "uuid",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "permissions": [
            {
                "id": "uuid",
                "libelle": "string",
                "module_id": "uuid"
            }
        ]
    }
}
```

#### PUT /api/v1/profiles/{profile_id}
- **Description**: Mettre à jour un profil
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "libelle": "string (100 chars max)",
    "description": "string",
    "statut": "string",
    "permissions": ["uuid", ...]
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
        "compagnie_id": "uuid",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "permissions": [
            {
                "id": "uuid",
                "libelle": "string",
                "module_id": "uuid"
            }
        ]
    }
}
```

#### GET /api/v1/profiles/{profile_id}
- **Description**: Récupérer les détails d'un profil avec ses permissions
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "description": "string",
        "compagnie_id": "uuid",
        "statut": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "permissions": [
            {
                "id": "uuid",
                "libelle": "string",
                "module_id": "uuid"
            }
        ]
    }
}
```

#### GET /api/v1/profiles
- **Description**: Lister les profils d'une compagnie
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - compagnie_id: "uuid"
  - statut: "string" ('Actif', 'Inactif', 'Supprime')
  - limit: "integer"
  - offset: "integer"
- **Réponse**:
```json
{
    "success": true,
    "pagination": {
        "total": "integer",
        "limit": "integer",
        "offset": "integer"
    },
    "data": [
        {
            "id": "uuid",
            "code": "string",
            "libelle": "string",
            "description": "string",
            "compagnie_id": "uuid",
            "statut": "string",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ]
}
```

### 4.6 Gestion des utilisateurs

#### POST /api/v1/users
- **Description**: Créer un nouvel utilisateur
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "login": "string (50 chars max)",
    "password": "string (8 chars min)",
    "nom": "string (150 chars max)",
    "profil_id": "uuid",
    "email": "string (150 chars max)",
    "telephone": "string (30 chars max)",
    "stations_user": ["uuid", ...],
    "compagnie_id": "uuid",
    "type_utilisateur": "string ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "login": "string",
        "nom": "string",
        "profil_id": "uuid",
        "email": "string",
        "telephone": "string",
        "stations_user": ["uuid", ...],
        "statut": "string",
        "compagnie_id": "uuid",
        "type_utilisateur": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### PUT /api/v1/users/{user_id}
- **Description**: Mettre à jour un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "profil_id": "uuid",
    "email": "string",
    "telephone": "string",
    "stations_user": ["uuid", ...],
    "statut": "string",
    "type_utilisateur": "string ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "login": "string",
        "nom": "string",
        "profil_id": "uuid",
        "email": "string",
        "telephone": "string",
        "stations_user": ["uuid", ...],
        "statut": "string",
        "compagnie_id": "uuid",
        "type_utilisateur": "string",
        "updated_at": "timestamp"
    }
}
```

#### GET /api/v1/users/{user_id}
- **Description**: Récupérer les détails d'un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "login": "string",
        "nom": "string",
        "profil_id": "uuid",
        "email": "string",
        "telephone": "string",
        "stations_user": ["uuid", ...],
        "statut": "string",
        "compagnie_id": "uuid",
        "type_utilisateur": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### GET /api/v1/users
- **Description**: Lister les utilisateurs d'une compagnie
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - compagnie_id: "uuid"
  - statut: "string" ('Actif', 'Inactif', 'Supprime', 'Bloque')
  - type_utilisateur: "string"
  - limit: "integer"
  - offset: "integer"
- **Réponse**:
```json
{
    "success": true,
    "pagination": {
        "total": "integer",
        "limit": "integer",
        "offset": "integer"
    },
    "data": [
        {
            "id": "uuid",
            "login": "string",
            "nom": "string",
            "profil_id": "uuid",
            "email": "string",
            "telephone": "string",
            "stations_user": ["uuid", ...],
            "statut": "string",
            "compagnie_id": "uuid",
            "type_utilisateur": "string",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    ]
}
```

### 4.7 Contrôles d'accès et endpoints

#### GET /api/v1/access-control/user-permissions/{user_id}
- **Description**: Récupérer les permissions d'un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "user_id": "uuid",
        "profil": {
            "id": "uuid",
            "code": "string",
            "libelle": "string"
        },
        "permissions": [
            {
                "id": "uuid",
                "libelle": "string",
                "module": "string"
            }
        ]
    }
}
```

#### POST /api/v1/access-control/check-permission
- **Description**: Vérifier si un utilisateur a une permission spécifique
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "user_id": "uuid",
    "permission": "string"  // Ex: "ventes.lire", "achats.creer"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "has_permission": "boolean"
    }
}
```

#### GET /api/v1/access-control/user-stations/{user_id}
- **Description**: Récupérer les stations accessibles par un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "code": "string",
            "nom": "string"
        }
    ]
}
```

## 5. Logique Métier

### 5.1 Règles de gestion des profils
- Chaque profil est rattaché à une seule compagnie
- Les utilisateurs d'une compagnie ne peuvent voir que les profils de leur propre compagnie
- Un profil peut avoir plusieurs permissions
- Une permission ne peut être attribuée qu'une seule fois à un profil
- Les profils peuvent être restreints à une compagnie spécifique

### 5.2 Règles de gestion des permissions
- Les permissions sont rattachées à des modules fonctionnels
- Une permission peut être attribuée à plusieurs profils
- Les permissions sont de type CRUD (Create, Read, Update, Delete) ou spécifiques
- Le système distingue les permissions de lecture, d'écriture, de modification et de suppression

### 5.3 Règles de gestion des stations
- Un utilisateur peut être limité à l'accès à certaines stations spécifiques
- Le champ `stations_user` est un tableau JSONB contenant les UUID des stations autorisées
- Les données d'autres stations sont masquées pour un utilisateur non autorisé

### 5.4 Contrôles d'accès
- Les utilisateurs n'ont accès qu'aux fonctionnalités autorisées par leur profil
- Les validations hiérarchiques sont requises pour certaines opérations sensibles
- Les opérations critiques nécessitent des permissions spécifiques
- Les endpoints sont distincts pour administrateurs et utilisateurs standards

### 5.5 Validation des endpoints
- Les utilisateurs de type "super_administrateur" et "administrateur" doivent utiliser l'endpoint administrateur
- Les utilisateurs de type "gerant_compagnie" et "utilisateur_compagnie" doivent utiliser l'endpoint utilisateur
- Les tentatives d'accès à un endpoint non autorisé sont bloquées et journalisées
- Les jetons d'authentification contiennent l'information sur le type d'endpoint autorisé

### 5.6 Validations hiérarchiques
- Les validations sont basées sur le montant ou le type d'opération
- Le niveau de validation dépend du type d'utilisateur
- Pour les opérations critiques (annulation de ventes > X MGA, modification de stocks importants, etc.), une validation hiérarchique est requise
- Les validations hiérarchiques sont enregistrées dans le système pour traçabilité

### 5.7 Sécurité des données
- Les mots de passe sont hachés avec bcrypt avec un coût minimum de 12
- Les jetons d'authentification ont une durée de vie limitée
- Les tentatives de connexion infructueuses sont limitées
- Les accès non autorisés aux endpoints sont journalisés

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
[pays] 1 -- * [compagnies]
[pays] 1 -- * [stations]

[compagnies] 1 -- * [stations]
[compagnies] 1 -- * [profils]
[compagnies] 1 -- * [utilisateurs]

[modules] 1 -- * [permissions]
[profils] 1 -- * [profil_permissions]
[permissions] 1 -- * [profil_permissions]
[profils] 1 -- * [utilisateurs]
[utilisateurs] 1 -- * [auth_tokens]
[utilisateurs] 1 -- * [tentatives_acces_non_autorise]
```

### 6.2 Diagramme de séquence (attribution des permissions à un profil)
```
Administrateur -> API: POST /api/v1/profiles (code, libelle, compagnie_id, permissions)
API -> Database: Vérifier que la compagnie existe
Database -> API: Compagnie trouvée
API -> Database: Créer le profil
Database -> API: Profil créé
API -> Database: Associer les permissions au profil
Database -> API: Permissions associées
API -> Administrateur: {success: true, profil: {...}}
```

### 6.3 Diagramme de séquence (validation des endpoints)
```
Client -> API: GET /api/v1/admin/... (with token)
API -> Database: Vérifier le type d'utilisateur et endpoint
Database -> API: type_utilisateur = 'utilisateur_compagnie', token.type_endpoint = 'administrateur'
API -> Database: INSERT INTO tentatives_acces_non_autorise (...)
API -> Client: {error: "Accès non autorisé", code: 403}
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de la fonction de hachage des mots de passe
- Test des validations de données pour chaque modèle
- Test des triggers de mise à jour des timestamps
- Test de la logique d'attribution des permissions
- Test de la validation des endpoints
- Test de la classification des types d'utilisateurs

### 7.2 Tests d'intégration
- Test de la création complète d'une compagnie avec ses stations
- Test de la création d'un profil avec ses permissions
- Test de la création d'un utilisateur avec ses stations autorisées
- Test des contrôles d'accès aux différentes fonctionnalités
- Test de la distinction des endpoints administrateur/utilisateur
- Test des validations hiérarchiques

### 7.3 Tests de charge/performance
- Test de la performance lors de la gestion de nombreuses permissions
- Test de la performance lors de la vérification des permissions d'utilisateur
- Test de la performance lors de la validation des endpoints
- Test de la performance lors de l'accès aux données par station

### 7.4 Jeux de données de test
```sql
-- Création des modules de base
INSERT INTO modules (libelle, statut) VALUES
('Ventes', 'Actif'),
('Achats', 'Actif'),
('Stocks', 'Actif'),
('Trésorerie', 'Actif'),
('Comptabilité', 'Actif');

-- Création des permissions de base
INSERT INTO permissions (libelle, description, module_id, statut, created_at) VALUES
('ventes.lire', 'Lire les ventes', (SELECT id FROM modules WHERE libelle = 'Ventes'), 'Actif', now()),
('ventes.creer', 'Créer des ventes', (SELECT id FROM modules WHERE libelle = 'Ventes'), 'Actif', now()),
('ventes.modifier', 'Modifier les ventes', (SELECT id FROM modules WHERE libelle = 'Ventes'), 'Actif', now()),
('achats.lire', 'Lire les achats', (SELECT id FROM modules WHERE libelle = 'Achats'), 'Actif', now()),
('stocks.lire', 'Lire les stocks', (SELECT id FROM modules WHERE libelle = 'Stocks'), 'Actif', now()),
('tresorerie.lire', 'Lire les opérations de trésorerie', (SELECT id FROM modules WHERE libelle = 'Trésorerie'), 'Actif', now());
```

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Création des modèles SQLAlchemy pour les tables : pays, compagnies, stations, modules, permissions, profils, profil_permissions, utilisateurs, auth_tokens, tentatives_acces_non_autorise
- [ ] Mise en place des relations entre les modèles
- [ ] Développement des services pour la gestion des pays
- [ ] Développement des services pour la gestion des compagnies
- [ ] Développement des services pour la gestion des stations
- [ ] Développement des services pour la gestion des modules
- [ ] Développement des services pour la gestion des permissions
- [ ] Développement des services pour la gestion des profils
- [ ] Développement des services pour la gestion des associations profil-permission
- [ ] Développement des services pour la gestion des utilisateurs
- [ ] Développement des services pour la gestion des validations d'endpoint
- [ ] Développement des endpoints API pour chaque service
- [ ] Mise en place des validations de données
- [ ] Mise en place du hachage des mots de passe
- [ ] Mise en place des contrôles d'accès basés sur les profils
- [ ] Mise en place de la distinction des endpoints administrateur/utilisateur
- [ ] Mise en place des validations hiérarchiques
- [ ] Tests unitaires et d'intégration
- [ ] Documentation des API

### 8.2 Ordre recommandé
1. Création des modèles et migrations des tables
2. Développement des services de base (pays, compagnies, stations)
3. Développement des services pour la gestion des modules et permissions
4. Développement du système RBAC (profils et associations)
5. Développement du système de gestion des utilisateurs avec classification
6. Mise en place des contrôles d'accès et des validations d'endpoint
7. Mise en place des validations hiérarchiques
8. Tests et documentation

### 8.3 Livrables attendus
- Modèles SQLAlchemy pour toutes les tables du système RBAC
- Services backend pour la gestion des différentes entités
- Endpoints API complets pour la gestion des profils et permissions
- Système de validation des données
- Système de hachage des mots de passe
- Système de distinction des endpoints administrateur/utilisateur
- Système de validations hiérarchiques
- Documentation API
- Jeux de tests unitaires et d'intégration

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La sécurité du système de hachage des mots de passe
- La gestion correcte des associations profil-permission
- La restriction des accès par station pour les utilisateurs
- La performance du système lors de la vérification des permissions
- La validation correcte des endpoints selon le type d'utilisateur
- La gestion sécurisée des jetons d'authentification

### 9.2 Risques techniques
- Risque de performance lié à la vérification des permissions à chaque requête
- Risque de complexité dans la gestion des permissions multiples
- Risque de conflits si plusieurs utilisateurs modifient les mêmes profils simultanément
- Risque d'erreurs dans la gestion des stations pour les utilisateurs
- Risque de contournement des validations d'endpoint si mal implémentées
- Risque de confusion entre les endpoints administrateur et utilisateur

### 9.3 Dette technique potentielle
- Mise en place d'un système d'audit plus complet des modifications de profils et permissions
- Mise en place de rôles par défaut pour les types d'utilisateur courants
- Mise en place d'outils d'analyse et de reporting des permissions
- Mise en place d'une interface d'administration plus avancée
- Mise en place de politiques de rotation des jetons d'authentification
- Mise en place d'alertes automatiques pour les tentatives d'accès non autorisés