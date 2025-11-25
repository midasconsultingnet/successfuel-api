# Technical Specification - Module des structures de base (Phase 1)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce module constitue les fondations du système ERP SuccessFuel. Il permet de créer et gérer les structures de base nécessaires au fonctionnement du système : les compagnies (entités de regroupement), les stations-service, les modules fonctionnels, les permissions de base, et les profils d'utilisateurs. Ce module est essentiel car toutes les autres fonctionnalités (achats, ventes, inventaires, etc.) dépendent de ces structures de base.

### Problème à résoudre
Sans une base solide pour les structures fondamentales du système, il est impossible de mettre en place un système de gestion sécurisé et fonctionnel. Il est nécessaire de disposer d'un système d'administration permettant de créer les entités de base (compagnies, stations) et la structure de gestion des droits (modules, permissions, profils) avant d'implémenter les fonctionnalités métier.

### Définition du périmètre
Le périmètre du sprint couvre :
- Création des compagnies (entités de regroupement des stations et utilisateurs)
- Création des stations-service (liées à une compagnie)
- Définition des modules fonctionnels (ventes, achats, stocks, etc.)
- Définition des permissions de base (lire, créer, modifier, supprimer, annuler) par module
- Création des profils d'utilisateurs avec leurs permissions associées
- Interface pour la gestion de ces structures de base
- Validation des données saisies
- Dépendances entre les entités

## 2. User Stories & Critères d'acceptation

### US-BS-001: En tant qu'administrateur, je veux créer une compagnie
**Critères d'acceptation :**
- Saisie d'un code unique pour la compagnie
- Saisie du nom de la compagnie (obligatoire)
- Saisie optionnelle de l'adresse, téléphone, email, NIF
- Sélection d'un pays d'origine
- Sélection d'une devise principale (par défaut MGA)
- Statut actif/inactif/géré
- Historique des modifications
- Validation des données avant enregistrement

### US-BS-002: En tant qu'administrateur, je veux créer une station-service
**Critères d'acceptation :**
- Association obligatoire à une compagnie existante
- Saisie d'un code unique pour la station
- Saisie du nom de la station (obligatoire)
- Saisie optionnelle de l'adresse, téléphone, email
- Sélection d'un pays d'implantation
- Statut actif/inactif/géré
- Historique des modifications
- Validation des données avant enregistrement

### US-BS-003: En tant qu'administrateur, je veux gérer les modules fonctionnels
**Critères d'acceptation :**
- Création d'un module avec libellé unique
- Statut actif/inactif pour chaque module
- Historique des modules créés
- Possibilité de modifier les modules existants
- Contrôle de la cohérence des données

### US-BS-004: En tant qu'administrateur, je veux gérer les permissions de base
**Critères d'acceptation :**
- Création de permissions avec libellé unique
- Association obligatoire à un module fonctionnel
- Description optionnelle de la permission
- Statut actif/inactif pour chaque permission
- Historique des permissions créées
- Contrôle de la cohérence des données

### US-BS-005: En tant qu'administrateur, je veux créer des profils d'utilisateurs
**Critères d'acceptation :**
- Saisie d'un code unique pour le profil
- Saisie du libellé du profil (obligatoire)
- Association optionnelle à une compagnie
- Description optionnelle du profil
- Statut actif/inactif pour le profil
- Historique des modifications
- Association de plusieurs permissions au profil
- Validation des données avant enregistrement

### US-BS-006: En tant qu'administrateur, je veux associer des permissions à un profil
**Critères d'acceptation :**
- Sélection d'un profil existant
- Attribution de plusieurs permissions à un profil
- Suppression de permissions d'un profil
- Vérification de la cohérence des associations
- Historique des modifications d'associations
- Interface pour gérer les associations

## 3. Modèle de Données

### Tables existantes à créer

#### Table compagnies
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

#### Table stations
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

#### Table modules
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) UNIQUE NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);
```

#### Table permissions
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

#### Table profils
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

#### Table profil_permissions
```sql
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(profil_id, permission_id)
);
```

### Index recommandés
```sql
-- Index pour les compagnies
CREATE INDEX idx_compagnies_code ON compagnies(code);
CREATE INDEX idx_compagnies_statut ON compagnies(statut);

-- Index pour les stations
CREATE INDEX idx_stations_code ON stations(code);
CREATE INDEX idx_stations_compagnie ON stations(compagnie_id);
CREATE INDEX idx_stations_statut ON stations(statut);

-- Index pour les modules
CREATE INDEX idx_modules_libelle ON modules(libelle);

-- Index pour les permissions
CREATE INDEX idx_permissions_libelle ON permissions(libelle);
CREATE INDEX idx_permissions_module ON permissions(module_id);

-- Index pour les profils
CREATE INDEX idx_profils_code ON profils(code);
CREATE INDEX idx_profils_compagnie ON profils(compagnie_id);
CREATE INDEX idx_profils_statut ON profils(statut);

-- Index pour les associations profil-permission
CREATE INDEX idx_profil_permissions_profil ON profil_permissions(profil_id);
CREATE INDEX idx_profil_permissions_permission ON profil_permissions(permission_id);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour la mise à jour automatique du champ updated_at dans la table compagnies
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_compagnies_updated_at 
    BEFORE UPDATE ON compagnies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

## 4. API Backend

### 4.1 Gestion des compagnies

#### POST /api/base/compagnies
**Description:** Créer une nouvelle compagnie

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "nom": "string (max 150)",
  "adresse": "string (optional)",
  "telephone": "string (optional)",
  "email": "string (optional, format email)",
  "nif": "string (optional)",
  "pays_id": "uuid (optional)",
  "devise_principale": "string (default: MGA)"
}
```

**Response:**
```json
{
  "success": boolean,
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
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Compagnie créée
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 409: Code de compagnie déjà existant

#### GET /api/base/compagnies
**Description:** Récupérer toutes les compagnies avec pagination

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)
- statut: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "compagnies": [
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
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Compagnies récupérées
- 401: Non autorisé
- 403: Permissions insuffisantes

#### PUT /api/base/compagnies/{compagnie_id}
**Description:** Mettre à jour une compagnie

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "nom": "string (optional, max 150)",
  "adresse": "string (optional)",
  "telephone": "string (optional)",
  "email": "string (optional, format email)",
  "nif": "string (optional)",
  "pays_id": "uuid (optional)",
  "devise_principale": "string (optional)",
  "statut": "string"
}
```

**Response:**
```json
{
  "success": boolean,
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
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Compagnie mise à jour
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 404: Compagnie non trouvée

### 4.2 Gestion des stations

#### POST /api/base/stations
**Description:** Créer une nouvelle station

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "compagnie_id": "uuid",
  "code": "string (unique, max 20)",
  "nom": "string (max 100)",
  "adresse": "string (optional)",
  "telephone": "string (optional)",
  "email": "string (optional, format email)",
  "pays_id": "uuid (optional)"
}
```

**Response:**
```json
{
  "success": boolean,
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
    "created_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Station créée
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 404: Compagnie non trouvée
- 409: Code de station déjà existant

#### GET /api/base/stations
**Description:** Récupérer toutes les stations avec pagination

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)
- compagnie_id: uuid (optional)
- statut: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "stations": [
      {
        "id": "uuid",
        "compagnie_id": "uuid",
        "compagnie_nom": "string",
        "code": "string",
        "nom": "string",
        "adresse": "string",
        "telephone": "string",
        "email": "string",
        "pays_id": "uuid",
        "statut": "string",
        "created_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Stations récupérées
- 401: Non autorisé
- 403: Permissions insuffisantes

### 4.3 Gestion des modules

#### POST /api/base/modules
**Description:** Créer un nouveau module

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "libelle": "string (max 100)",
  "statut": "string"
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "id": "uuid",
    "libelle": "string",
    "statut": "string"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Module créé
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 409: Libellé de module déjà existant

#### GET /api/base/modules
**Description:** Récupérer tous les modules avec pagination

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)
- statut: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "modules": [
      {
        "id": "uuid",
        "libelle": "string",
        "statut": "string"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Modules récupérés
- 401: Non autorisé
- 403: Permissions insuffisantes

### 4.4 Gestion des permissions

#### POST /api/base/permissions
**Description:** Créer une nouvelle permission

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "libelle": "string (max 100)",
  "description": "string (optional)",
  "module_id": "uuid",
  "statut": "string"
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "id": "uuid",
    "libelle": "string",
    "description": "string",
    "module_id": "uuid",
    "module_libelle": "string",
    "statut": "string",
    "created_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Permission créée
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 404: Module non trouvé
- 409: Libellé de permission déjà existant

#### GET /api/base/permissions
**Description:** Récupérer toutes les permissions avec pagination

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)
- module_id: uuid (optional)
- statut: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "permissions": [
      {
        "id": "uuid",
        "libelle": "string",
        "description": "string",
        "module_id": "uuid",
        "module_libelle": "string",
        "statut": "string",
        "created_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Permissions récupérées
- 401: Non autorisé
- 403: Permissions insuffisantes

### 4.5 Gestion des profils

#### POST /api/base/profils
**Description:** Créer un nouveau profil

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "libelle": "string (max 100)",
  "compagnie_id": "uuid (optional)",
  "description": "string (optional)",
  "statut": "string",
  "permissions": ["uuid"] // tableau d'IDs de permissions à associer
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "id": "uuid",
    "code": "string",
    "libelle": "string",
    "compagnie_id": "uuid",
    "description": "string",
    "statut": "string",
    "permissions": [
      {
        "id": "uuid",
        "libelle": "string",
        "module_libelle": "string"
      }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Profil créé
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 409: Code de profil déjà existant

#### GET /api/base/profils
**Description:** Récupérer tous les profils avec pagination

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)
- compagnie_id: uuid (optional)
- statut: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "profils": [
      {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "compagnie_id": "uuid",
        "compagnie_nom": "string",
        "description": "string",
        "statut": "string",
        "permissions": [
          {
            "id": "uuid",
            "libelle": "string",
            "module_libelle": "string"
          }
        ],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Profils récupérés
- 401: Non autorisé
- 403: Permissions insuffisantes

#### PUT /api/base/profils/{profil_id}
**Description:** Mettre à jour un profil et ses permissions

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "libelle": "string (optional, max 100)",
  "compagnie_id": "uuid (optional)",
  "description": "string (optional)",
  "statut": "string",
  "permissions": ["uuid"] // tableau d'IDs de permissions à associer (remplace les associations actuelles)
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "id": "uuid",
    "code": "string",
    "libelle": "string",
    "compagnie_id": "uuid",
    "description": "string",
    "statut": "string",
    "permissions": [
      {
        "id": "uuid",
        "libelle": "string",
        "module_libelle": "string"
      }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Profil mis à jour
- 400: Données invalides
- 401: Non autorisé
- 403: Permissions insuffisantes
- 404: Profil non trouvé

## 5. Logique Métier

### 5.1 Gestion des compagnies
1. Vérifier l'unicité du code de la compagnie
2. Valider les formats des champs (email, téléphone)
3. Appliquer la devise par défaut (MGA) si non spécifiée
4. Créer la compagnie avec le statut "Actif" par défaut
5. Enregistrer les dates de création et de modification

### 5.2 Gestion des stations
1. Vérifier l'existence de la compagnie spécifiée
2. Vérifier l'unicité du code de la station
3. Valider les formats des champs (email, téléphone)
4. Créer la station avec le statut "Actif" par défaut
5. Enregistrer la date de création

### 5.3 Gestion des modules
1. Vérifier l'unicité du libellé du module
2. Créer le module avec le statut "Actif" par défaut
3. Enregistrer la date de création

### 5.4 Gestion des permissions
1. Vérifier l'existence du module spécifié
2. Vérifier l'unicité du libellé de la permission
3. Créer la permission avec le statut "Actif" par défaut
4. Enregistrer la date de création

### 5.5 Gestion des profils
1. Vérifier l'unicité du code du profil
2. Vérifier l'existence de la compagnie spécifiée (si fournie)
3. Créer le profil avec le statut "Actif" par défaut
4. Lier les permissions spécifiées au profil via la table d'association
5. Enregistrer les dates de création et de modification

### 5.6 Gestion des associations profil-permission
1. Vérifier l'existence du profil et de la permission
2. Créer l'association dans la table profil_permissions
3. Empêcher les doublons grâce à la contrainte UNIQUE
4. Supprimer toutes les associations existantes lors d'une mise à jour

### 5.7 Validations
- Les codes doivent être uniques pour chaque entité
- Les champs obligatoires doivent être renseignés
- Les formats des champs doivent être valides (email, téléphone)
- Les liaisons entre entités (FK) doivent exister
- Les statuts doivent être valides (Actif, Inactif, Supprime)

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
compagnies ||--o{ stations : "possède"
compagnies ||--o{ profils : "possède"

modules ||--o{ permissions : "contient"
profils ||--o{ profil_permissions : "a des"
permissions ||--o{ profil_permissions : "appartient à"
```

### 6.2 Diagramme de séquence - Création d'un profil avec permissions
```
Administrateur -> Serveur: POST /api/base/profils
Serveur -> Validation: Vérifie les données
Validation -> Serveur: Données valides
Serveur -> DB: Insère le profil
DB -> Serveur: Profil créé
Serveur -> DB: Insère les associations profil-permission
DB -> Serveur: Associations créées
Serveur -> Administrateur: Retourne le profil avec permissions
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Validation des données d'entrée pour chaque entité
- Création, lecture, mise à jour et suppression (CRUD) pour chaque entité
- Vérification des contraintes d'unicité
- Vérification des relations entre entités
- Gestion des erreurs et exceptions

### 7.2 Tests d'intégration
- Flux complet de création des structures de base
- Dépendances entre les entités (FK)
- Mise à jour des profils avec modifications de permissions
- Pagination des listes d'entités
- Filtres de recherche et de statut

### 7.3 Tests de charge/performance
- Création massive d'entités
- Récupération de grandes quantités de données
- Performance des requêtes avec filtres
- Performance des opérations de mise à jour

### 7.4 Jeux de données de test
```sql
-- Données de test pour les structures de base
INSERT INTO compagnies (code, nom, telephone, adresse, devise_principale) 
VALUES 
('CIE001', 'Compagnie de Test', '0341234567', 'Adresse de test', 'MGA'),
('CIE002', 'Seconde Compagnie', '0329876543', 'Deuxième adresse', 'USD');

INSERT INTO stations (compagnie_id, code, nom, telephone) 
SELECT 
    id,
    'STN001', 
    'Station de Test',
    '0331234567'
FROM compagnies 
WHERE code = 'CIE001'
ON CONFLICT DO NOTHING;

INSERT INTO stations (compagnie_id, code, nom, telephone) 
SELECT 
    id,
    'STN002', 
    'Seconde Station',
    '0339876543'
FROM compagnies 
WHERE code = 'CIE002'
ON CONFLICT DO NOTHING;

INSERT INTO modules (libelle, statut) VALUES
('ventes', 'Actif'),
('achats', 'Actif'),
('stocks', 'Actif'),
('utilisateurs', 'Actif')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id, statut)
SELECT 
    'lire_ventes', 
    'Lire les détails des ventes', 
    id, 
    'Actif'
FROM modules
WHERE libelle = 'ventes';

INSERT INTO permissions (libelle, description, module_id, statut)
SELECT 
    'creer_vente', 
    'Créer une nouvelle vente', 
    id, 
    'Actif'
FROM modules
WHERE libelle = 'ventes';

INSERT INTO permissions (libelle, description, module_id, statut)
SELECT 
    'modifier_stock', 
    'Modifier manuellement les stocks', 
    id, 
    'Actif'
FROM modules
WHERE libelle = 'stocks';

INSERT INTO profils (code, libelle, description, statut, compagnie_id)
VALUES 
('ADMIN', 'Administrateur', 'Profil avec toutes les permissions', 'Actif', 
    (SELECT id FROM compagnies WHERE code = 'CIE001')),
('MANAGER', 'Gestionnaire', 'Profil gestionnaire avec permissions limitées', 'Actif', 
    (SELECT id FROM compagnies WHERE code = 'CIE001'));
```

## 8. Checklist Développeur

### Tâches techniques détaillées

**Phase 1 - Modèle de données**
- [ ] Créer les tables dans la base de données
- [ ] Mettre en place les contraintes d'intégrité
- [ ] Créer les indexes nécessaires
- [ ] Mettre en place les triggers si nécessaires
- [ ] Tester l'intégrité des données

**Phase 2 - Services backend**
- [ ] Créer les services pour la gestion des compagnies
- [ ] Créer les services pour la gestion des stations
- [ ] Créer les services pour la gestion des modules
- [ ] Créer les services pour la gestion des permissions
- [ ] Créer les services pour la gestion des profils
- [ ] Mettre en place la logique d'association profil-permission

**Phase 3 - API endpoints**
- [ ] Créer les endpoints POST pour chaque entité
- [ ] Créer les endpoints GET pour chaque entité
- [ ] Créer les endpoints PUT pour chaque entité
- [ ] Mettre en place la pagination
- [ ] Mettre en place les filtres de recherche
- [ ] Mettre en place les validations d'entrée

**Phase 4 - Sécurité et validation**
- [ ] Mettre en place l'authentification
- [ ] Mettre en place l'autorisation (RBAC)
- [ ] Mettre en place la validation des données
- [ ] Gérer les erreurs et exceptions
- [ ] Mettre en place la journalisation

**Phase 5 - Tests**
- [ ] Écrire les tests unitaires
- [ ] Écrire les tests d'intégration
- [ ] Écrire les tests de validation
- [ ] Exécuter les tests et corriger les erreurs
- [ ] Mettre en place un jeu de données de test

### Ordre recommandé
1. Commencer par la modélisation des données
2. Puis implémenter les services backend
3. Ensuite les endpoints API
4. Puis la sécurité et les validations
5. Enfin les tests

### Livrables attendus
- [ ] Modèle de données complet
- [ ] Services backend fonctionnels
- [ ] API complète pour la gestion des structures de base
- [ ] Documentation API
- [ ] Jeux de données de test
- [ ] Tests unitaires et d'intégration

## 9. Risques & Points de vigilance

### Points sensibles
- Gestion des contraintes d'intégrité référentielle
- Gestion des codes uniques pour chaque entité
- Validation des données d'entrée
- Gestion des associations profil-permission
- Performance des requêtes avec de grandes quantités de données

### Risques techniques
- Problèmes de performance avec la pagination
- Erreurs dans la gestion des associations profil-permission
- Problèmes de sécurité liés à l'accès aux données
- Problèmes de cohérence des données
- Erreurs dans les validations d'entrée

### Dette technique potentielle
- Nécessité de mettre en place un système de cache pour les structures de base
- Éventuelle nécessité de partitionner certaines tables avec beaucoup de données
- Possibilité de devoir optimiser les requêtes pour de grandes bases
- Nécessité de mettre en place des procédures de sauvegarde pour les structures de base