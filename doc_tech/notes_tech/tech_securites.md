# Technical Specification - Sécurité du système

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter un ensemble de mesures de sécurité complètes pour protéger le système informatique SuccessFuel et les données sensibles des stations-service à Madagascar. La solution comprendra des mécanismes de prévention des injections SQL, un système d'authentification et d'autorisation robuste (RBAC) avec distinction des types d'utilisateurs, la protection des données sensibles, une journalisation détaillée, des contrôles d'accès granulaires, et une surveillance proactive des accès. Une attention particulière sera portée à la séparation des endpoints pour les administrateurs et les utilisateurs standards.

### Problème à résoudre
Le système SuccessFuel nécessite une couche de sécurité solide pour :
- Protéger les données sensibles des utilisateurs, clients et finances
- Empêcher les accès non autorisés aux fonctionnalités critiques
- Garantir l'intégrité des opérations et des données
- Se conformer aux meilleures pratiques de sécurité informatique
- Mettre en place une distinction claire entre les rôles administrateur et utilisateur avec des endpoints séparés

### Définition du périmètre
Le périmètre inclut :
- Implémentation des protections contre les injections SQL
- Développement du système d'authentification et d'autorisation (RBAC) avec classification des utilisateurs
- Mise en place du chiffrement des données sensibles
- Création des tables de journalisation et de surveillance
- Développement des contrôles d'accès basés sur les rôles et les stations
- Mise en place de la validation des entrées
- Sécurisation des communications et gestion des erreurs
- Séparation des endpoints administrateur et utilisateur avec blocage des accès croisés

## 2. User Stories & Critères d'acceptation

### US-SEC-001: En tant qu'administrateur, je veux pouvoir gérer les utilisateurs du système de manière sécurisée
- **Critères d'acceptation :**
  - Pouvoir créer, modifier, activer/désactiver un utilisateur
  - Le mot de passe doit être haché avec bcrypt
  - L'utilisateur peut être affecté à des stations spécifiques
  - Les informations sensibles sont masquées dans l'interface
  - Attribution d'un type d'utilisateur (super administrateur, administrateur, gérant compagnie, utilisateur compagnie)

### US-SEC-002: En tant qu'utilisateur, je veux m'authentifier de manière sécurisée pour accéder au système
- **Critères d'acceptation :**
  - Authentification par login/mot de passe
  - Génération automatique de jeton d'authentification
  - Token avec durée de vie limitée
  - Suivi des connexions dans le système
  - Accès automatique à l'endpoint approprié selon le type d'utilisateur

### US-SEC-003: En tant qu'administrateur, je veux contrôler les accès des utilisateurs aux différentes fonctionnalités
- **Critères d'acceptation :**
  - Gestion des profils utilisateurs (RBAC)
  - Attribution de permissions spécifiques
  - Contrôle des accès aux stations
  - Validation hiérarchique pour les opérations sensibles
  - Distinction des endpoints selon le type d'utilisateur

### US-SEC-004: En tant qu'administrateur, je veux être alerté des événements de sécurité
- **Critères d'acceptation :**
  - Journalisation des tentatives de connexions (réussies/échouées)
  - Suivi des événements de sécurité
  - Journalisation des modifications sensibles
  - Surveillance proactive des comportements suspects

### US-SEC-005: En tant qu'administrateur, je veux utiliser un endpoint administrateur pour accéder aux fonctionnalités étendues
- **Critères d'acceptation :**
  - Accès exclusif à l'endpoint administrateur pour les utilisateurs de type "Administrateur"
  - Blocage automatique des accès à l'endpoint administrateur pour les autres types d'utilisateurs
  - Journalisation de toutes les tentatives d'accès non autorisé

### US-SEC-006: En tant qu'utilisateur standard, je veux utiliser un endpoint utilisateur pour accéder aux fonctionnalités limitées
- **Critères d'acceptation :**
  - Accès exclusif à l'endpoint utilisateur pour les utilisateurs de type "Utilisateur"
  - Blocage automatique des accès à l'endpoint utilisateur pour les types "Super administrateur" et "Administrateur"
  - Journalisation de toutes les tentatives d'accès non autorisé

### US-SEC-007: En tant qu'administrateur du système, je veux bloquer l'accès aux endpoints non autorisés
- **Critères d'acceptation :**
  - Mise en place de contrôles d'accès pour empêcher les accès croisés entre endpoints
  - Journalisation des tentatives d'accès interdites
  - Notification des événements de sécurité liés aux accès non autorisés

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: utilisateurs
```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL UNIQUE,
    mot_de_passe TEXT NOT NULL, -- Haché avec bcrypt
    nom VARCHAR(150) NOT NULL,
    profil_id UUID REFERENCES profils(id) ON DELETE SET NULL,
    email VARCHAR(150),
    telephone VARCHAR(30),
    stations_user JSONB DEFAULT '[]'::jsonb, -- Tableau JSON des stations accessibles
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime', 'Bloque')),
    last_login TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id),
    type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index sur le login pour des performances optimales
CREATE INDEX idx_utilisateurs_login ON utilisateurs(login);

-- Index sur le profil_id pour les jointures rapides
CREATE INDEX idx_utilisateurs_profil ON utilisateurs(profil_id);

-- Index sur la compagnie pour les requêtes multi-compagnie
CREATE INDEX idx_utilisateurs_compagnie ON utilisateurs(compagnie_id);

-- Index sur le type d'utilisateur pour les requêtes d'accès
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

#### Table: profils
```sql
CREATE TABLE profils (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    libelle VARCHAR(100) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id) ON DELETE SET NULL,  -- La compagnie qui a créé le profil
    description TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprime')) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index unique sur le code du profil
CREATE UNIQUE INDEX idx_profils_code ON profils(code);
```

#### Table: modules
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    statut VARCHAR(20) DEFAULT 'ACTIF' CHECK (statut IN ('ACTIF', 'INACTIF')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index unique sur le libellé
CREATE UNIQUE INDEX idx_modules_libelle ON modules(libelle);
```

#### Table: permissions
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL, -- Ex: 'ventes.lire', 'achats.creer', 'stocks.modifier'
    description TEXT,
    module_id UUID NOT NULL REFERENCES modules(id),
    statut VARCHAR(20) DEFAULT 'ACTIF' CHECK (statut IN ('ACTIF', 'INACTIF')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index unique sur le libellé
CREATE UNIQUE INDEX idx_permissions_libelle ON permissions(libelle);
```

#### Table: profil_permissions
```sql
CREATE TABLE profil_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profil_id UUID NOT NULL REFERENCES profils(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profil_id, permission_id)
);

-- Index pour les requêtes rapides
CREATE INDEX idx_profil_permissions_profil ON profil_permissions(profil_id);
CREATE INDEX idx_profil_permissions_permission ON profil_permissions(permission_id);
```

#### Table: tentatives_connexion
```sql
CREATE TABLE tentatives_connexion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL,
    ip_connexion VARCHAR(45),
    resultat_connexion VARCHAR(10) CHECK (resultat_connexion IN ('Reussie', 'Echouee')),
    utilisateur_id UUID REFERENCES utilisateurs(id), -- NULL si échec
    type_endpoint VARCHAR(20) DEFAULT 'utilisateur' CHECK (type_endpoint IN ('administrateur', 'utilisateur')), -- Endpoint utilisé pour la connexion
    type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie')), -- Type de l'utilisateur
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les analyses de sécurité
CREATE INDEX idx_tentatives_connexion_date ON tentatives_connexion(created_at);
CREATE INDEX idx_tentatives_connexion_login ON tentatives_connexion(login);
CREATE INDEX idx_tentatives_connexion_ip ON tentatives_connexion(ip_connexion);
-- Index pour filtrer par type d'endpoint
CREATE INDEX idx_tentatives_connexion_endpoint ON tentatives_connexion(type_endpoint);
-- Index pour filtrer par type d'utilisateur
CREATE INDEX idx_tentatives_connexion_type ON tentatives_connexion(type_utilisateur);
```

#### Table: evenements_securite
```sql
CREATE TABLE evenements_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_evenement VARCHAR(50) NOT NULL, -- Ex: 'connexion_anormale', 'tentative_acces_non_autorise', etc.
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

-- Index pour les recherches rapides
CREATE INDEX idx_evenements_date ON evenements_securite(created_at);
CREATE INDEX idx_evenements_type ON evenements_securite(type_evenement);
CREATE INDEX idx_evenements_utilisateur ON evenements_securite(utilisateur_id);
```

#### Table: modifications_sensibles
```sql
CREATE TABLE modifications_sensibles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    type_operation VARCHAR(50) NOT NULL, -- Ex: 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    objet_modifie VARCHAR(50), -- Ex: 'vente', 'stock', 'achat', etc.
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

-- Index pour les analyses
CREATE INDEX idx_modifications_date ON modifications_sensibles(created_at);
CREATE INDEX idx_modifications_objet ON modifications_sensibles(objet_modifie, objet_id);
CREATE INDEX idx_modifications_utilisateur ON modifications_sensibles(utilisateur_id);
```

#### Table: permissions_tresorerie
```sql
CREATE TABLE permissions_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id),
    tresorerie_id UUID NOT NULL REFERENCES tresoreries(id),
    droits VARCHAR(50) NOT NULL, -- Ex: 'LECTURE', 'ECRITURE', 'VALIDATION', 'ADMIN'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(utilisateur_id, tresorerie_id)
);

-- Index pour les requêtes rapides
CREATE INDEX idx_permissions_tresorerie_utilisateur ON permissions_tresorerie(utilisateur_id);
CREATE INDEX idx_permissions_tresorerie_tresorerie ON permissions_tresorerie(tresorerie_id);
```

#### Table: politiques_securite
```sql
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
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les recherches rapides
CREATE INDEX idx_politiques_securite_type ON politiques_securite(type_politique);
CREATE INDEX idx_politiques_securite_actif ON politiques_securite(est_actif);
```

### 3.2 Relations
- `utilisateurs.profil_id` → `profils.id` (One-to-Many inverse)
- `profils.id` → `profil_permissions.profil_id` (One-to-Many)
- `permissions.id` → `profil_permissions.permission_id` (One-to-Many)
- `modules.id` → `permissions.module_id` (One-to-Many)
- `utilisateurs.id` → `auth_tokens.user_id` (One-to-Many)
- `utilisateurs.id` → `tentatives_connexion.utilisateur_id` (One-to-Many)
- `utilisateurs.id` → `evenements_securite.utilisateur_id` (One-to-Many)
- `utilisateurs.id` → `modifications_sensibles.utilisateur_id` (One-to-Many)
- `utilisateurs.id` → `politiques_securite.utilisateur_config_id` (One-to-Many)
- `compagnies.id` → `politiques_securite.compagnie_id` (One-to-Many)

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

-- Trigger pour journaliser les modifications sensibles
CREATE OR REPLACE FUNCTION journaliser_modification_sensible()
RETURNS TRIGGER AS $$
DECLARE
    seuil_alerte BOOLEAN;
BEGIN
    -- Déterminer si une alerte est nécessaire
    -- Cela dépendra de la configuration et des seuils spécifiques
    seuil_alerte := FALSE; -- Doit être défini selon la logique métier

    INSERT INTO modifications_sensibles(
        utilisateur_id,
        type_operation,
        objet_modifie,
        objet_id,
        ancienne_valeur,
        nouvelle_valeur,
        seuil_alerte,
        commentaire,
        ip_utilisateur,
        poste_utilisateur,
        compagnie_id
    ) VALUES (
        current_setting('app.current_user_id', true)::UUID, -- Doit être défini dans le contexte de la requête
        TG_OP,
        TG_TABLE_NAME,
        CASE
            WHEN TG_OP = 'DELETE' THEN OLD.id
            ELSE NEW.id
        END,
        CASE
            WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN to_jsonb(OLD)
            ELSE NULL
        END,
        CASE
            WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN to_jsonb(NEW)
            ELSE NULL
        END,
        seuil_alerte,
        'Modification automatiquement journalisée',
        current_setting('app.client_ip', true),
        current_setting('app.client_host', true),
        current_setting('app.current_company_id', true)::UUID -- Doit être défini dans le contexte de la requête
    );

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$ LANGUAGE plpgsql;
```

## 4. API Backend

### 4.1 Gestion des utilisateurs

#### POST /api/v1/auth/register
- **Description**: Créer un nouvel utilisateur
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
    "compagnie_id": "uuid"
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
        "created_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 409: Login déjà existant

#### POST /api/v1/auth/login
- **Description**: Authentifier un utilisateur
- **Payload**:
```json
{
    "login": "string",
    "password": "string"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "token": "string",
        "user": {
            "id": "uuid",
            "login": "string",
            "profil_id": "uuid",
            "stations_user": ["uuid", ...]
        }
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Identifiants incorrects
  - 403: Compte bloqué

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
        "last_login": "timestamp",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 401: Non autorisé
  - 403: Accès non autorisé
  - 404: Utilisateur non trouvé

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
    "statut": "string"
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
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès non autorisé
  - 404: Utilisateur non trouvé

#### DELETE /api/v1/users/{user_id}
- **Description**: Supprimer un utilisateur (logique)
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Utilisateur supprimé avec succès"
}
```
- **Codes d'erreur**:
  - 401: Non autorisé
  - 403: Accès non autorisé
  - 404: Utilisateur non trouvé

#### PUT /api/v1/users/{user_id}/activate
- **Description**: Activer un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Utilisateur activé avec succès"
}
```
- **Codes d'erreur**:
  - 401: Non autorisé
  - 403: Accès non autorisé
  - 404: Utilisateur non trouvé

#### PUT /api/v1/users/{user_id}/deactivate
- **Description**: Désactiver un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Utilisateur désactivé avec succès"
}
```
- **Codes d'erreur**:
  - 401: Non autorisé
  - 403: Accès non autorisé
  - 404: Utilisateur non trouvé

#### POST /api/v1/auth/refresh-token
- **Description**: Rafraîchir un token d'authentification
- **Payload**:
```json
{
    "refresh_token": "string"
}
```
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "token": "string",
        "refresh_token": "string"
    }
}
```
- **Codes d'erreur**:
  - 400: Token invalide
  - 401: Token expiré ou non autorisé

#### POST /api/v1/auth/logout
- **Description**: Déconnexion d'un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Déconnexion réussie"
}
```
- **Codes d'erreur**:
  - 401: Non autorisé

#### POST /api/v1/auth/logout-all
- **Description**: Déconnexion de toutes les sessions d'un utilisateur
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Toutes les sessions ont été terminées"
}
```
- **Codes d'erreur**:
  - 401: Non autorisé

### 4.2 Gestion des permissions et profils

#### GET /api/v1/profils
- **Description**: Lister tous les profils
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "code": "string",
            "libelle": "string",
            "description": "string",
            "statut": "string"
        }
    ]
}
```

#### POST /api/v1/profils
- **Description**: Créer un nouveau profil
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "code": "string",
    "libelle": "string",
    "description": "string",
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
        "statut": "string"
    }
}
```

#### PUT /api/v1/profils/{profil_id}
- **Description**: Mettre à jour un profil
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "libelle": "string",
    "description": "string",
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
        "statut": "string"
    }
}
```

#### DELETE /api/v1/profils/{profil_id}
- **Description**: Supprimer un profil
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "message": "Profil supprimé avec succès"
}
```

#### GET /api/v1/permissions
- **Description**: Lister toutes les permissions
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "libelle": "string",
            "description": "string",
            "module_id": "uuid",
            "statut": "string"
        }
    ]
}
```

### 4.3 Journalisation et surveillance

#### GET /api/v1/security/login-attempts
- **Description**: Récupérer les tentatives de connexion
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - date_debut: "date"
  - date_fin: "date"
  - resultat: "string" (REUSSIE|ECHEC)
  - utilisateur_id: "uuid"
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
            "ip_connexion": "string",
            "resultat_connexion": "string",
            "utilisateur_id": "uuid",
            "created_at": "timestamp"
        }
    ]
}
```

#### GET /api/v1/security/security-events
- **Description**: Récupérer les événements de sécurité
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - date_debut: "date"
  - date_fin: "date"
  - type_evenement: "string"
  - utilisateur_id: "uuid"
  - statut: "string"
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
            "type_evenement": "string",
            "description": "string",
            "utilisateur_id": "uuid",
            "ip_utilisateur": "string",
            "poste_utilisateur": "string",
            "donnees_supplementaires": {},
            "statut": "string",
            "created_at": "timestamp"
        }
    ]
}
```

#### GET /api/v1/security/sensitive-modifications
- **Description**: Récupérer les modifications sensibles
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - date_debut: "date"
  - date_fin: "date"
  - objet_modifie: "string"
  - utilisateur_id: "uuid"
  - seuil_alerte: "boolean"
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
            "type_operation": "string",
            "objet_modifie": "string",
            "objet_id": "uuid",
            "ancienne_valeur": {},
            "nouvelle_valeur": {},
            "seuil_alerte": "boolean",
            "commentaire": "string",
            "ip_utilisateur": "string",
            "poste_utilisateur": "string",
            "statut": "string",
            "created_at": "timestamp"
        }
    ]
}
```

#### GET /api/v1/security/unauthorized-access
- **Description**: Récupérer les tentatives d'accès non autorisées aux endpoints
- **Headers**: Authorization: Bearer {token}
- **Paramètres**:
  - date_debut: "date"
  - date_fin: "date"
  - utilisateur_id: "uuid"
  - endpoint_accesse: "string"
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
            "utilisateur_id": "uuid",
            "endpoint_accesse": "string",
            "endpoint_autorise": "string",
            "ip_connexion": "string",
            "statut": "string",
            "created_at": "timestamp"
        }
    ]
}
```

### 4.4 Contrôles d'accès

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

### 5.1 Règles d'authentification
- Les mots de passe doivent être hachés avec bcrypt avec un coût minimum de 12
- Les tokens d'authentification ont une durée de vie de 24 heures par défaut
- Les tokens peuvent être rafraîchis dans les 7 jours suivant leur expiration
- Les tentatives de connexion infructueuses sont limitées à 5 par heure par IP
- Les comptes sont bloqués automatiquement après 10 tentatives infructueuses
- La validation des endpoints se fait en fonction du type d'utilisateur
  - Les utilisateurs de type "super_administrateur" et "administrateur" doivent utiliser l'endpoint administrateur
  - Les utilisateurs de type "gerant_compagnie" et "utilisateur_compagnie" doivent utiliser l'endpoint utilisateur
- Les jetons sont invalidés lors de la déconnexion ou en cas d'accès non autorisé à un endpoint

### 5.2 Règles d'autorisation (RBAC)
- Les utilisateurs sont affectés à un seul profil
- Les profils peuvent avoir plusieurs permissions
- Les permissions sont organisées par modules (ventes, achats, stocks, etc.)
- Les permissions sont de type CRUD (Create, Read, Update, Delete) ou spécifiques
- Les validations hiérarchiques sont requises pour certaines opérations sensibles (ex: annulation de ventes > 1M MGA)
- Les permissions sont vérifiées à chaque accès à une ressource
- Les profils peuvent être restreints à une compagnie spécifique

### 5.3 Contrôles d'accès
- Les utilisateurs n'ont accès qu'aux stations spécifiées dans leur profil
- Les opérations de trésorerie sont soumises à des permissions spécifiques
- Les données des autres stations sont masquées pour un utilisateur non autorisé
- La modification des données sensibles nécessite une validation supplémentaire
- Les endpoints sont bloqués en fonction du type d'utilisateur (admin vs utilisateur)

### 5.4 Journalisation
- Toutes les connexions sont enregistrées (réussies ou échouées)
- Les modifications des données sensibles sont journalisées avec valeurs avant/après
- Les accès aux fonctionnalités sensibles sont surveillés
- Des alertes sont déclenchées pour les comportements suspects (multiples échecs de connexion, etc.)
- Les tentatives d'accès aux endpoints non autorisés sont journalisées

### 5.5 Validation des entrées
- Toutes les données utilisateur sont validées avant traitement
- Les requêtes SQL utilisent des paramètres positionnels pour prévenir les injections
- Les types de données sont strictement vérifiés
- Les longueurs de champs sont limitées pour prévenir les dépassements
- Les validations sont effectuées à plusieurs niveaux : API, service, base de données
- Le format des données est vérifié selon des règles spécifiques (email, téléphone, etc.)

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
[utilisateurs] 1 -- * [auth_tokens]
[utilisateurs] 1 -- * [tentatives_connexion]
[utilisateurs] 1 -- * [evenements_securite]
[utilisateurs] 1 -- * [modifications_sensibles]
[utilisateurs] 1 -- * [permissions_tresorerie]

[profils] 1 -- * [utilisateurs]
[profils] 1 -- * [profil_permissions]
[modules] 1 -- * [permissions]
[permissions] 1 -- * [profil_permissions]
[stations] 1 -- * [permissions_tresorerie]
```

### 6.2 Diagramme de séquence (authentification)
```
Client -> API: POST /api/v1/auth/login (login, password)
API -> Database: SELECT * FROM utilisateurs WHERE login = ?
Database -> API: utilisateur (mot_de_passe_haché)
API -> API: Comparer mot de passe haché
API -> Database: INSERT INTO tentatives_connexion (login, ip, resultat)
API -> API: Générer token JWT
API -> Database: INSERT INTO auth_tokens (token_hash, user_id, expires_at)
API -> Client: {success: true, token: "..."}
```

### 6.3 Diagramme de séquence (accès non autorisé à endpoint)
```
Client -> API: GET /api/v1/admin/... (with token)
API -> Database: Vérifier le type d'utilisateur et endpoint
Database -> API: type_utilisateur = 'utilisateur_compagnie', token.type_endpoint = 'administrateur'
API -> Database: INSERT INTO tentatives_acces_non_autorise (...)
API -> Database: INSERT INTO evenements_securite (...)
API -> Client: {error: "Accès non autorisé", code: 403}
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de hachage des mots de passe avec bcrypt
- Test de génération et validation des tokens
- Test des validations d'entrée
- Test des fonctions de vérification des permissions
- Test des fonctions de journalisation

### 7.2 Tests d'intégration
- Test complet du flux d'authentification (login, vérification, token)
- Test des contrôles d'autorisation sur les API
- Test de la journalisation des connexions
- Test de la journalisation des modifications sensibles
- Test des contrôles d'accès aux stations
- Test des contrôles de validation des endpoints

### 7.3 Tests de charge/performance
- Test de performance pour la vérification des permissions
- Test de la génération de tokens sous charge
- Test de la journalisation sous charge
- Test de la validation des entrées sous charge

### 7.4 Jeux de données de test
```sql
-- Jeux de données de test pour la sécurité
INSERT INTO modules (libelle, statut) VALUES
('Ventes', 'ACTIF'),
('Achats', 'ACTIF'),
('Stocks', 'ACTIF'),
('Trésorerie', 'ACTIF');

INSERT INTO permissions (libelle, description, module_id, statut) VALUES
('ventes.lire', 'Lire les ventes', (SELECT id FROM modules WHERE libelle = 'Ventes'), 'ACTIF'),
('ventes.creer', 'Créer des ventes', (SELECT id FROM modules WHERE libelle = 'Ventes'), 'ACTIF'),
('achats.modifier', 'Modifier les achats', (SELECT id FROM modules WHERE libelle = 'Achats'), 'ACTIF');

INSERT INTO profils (code, libelle, description, statut) VALUES
('ADMIN', 'Administrateur', 'Accès complet au système', 'ACTIF'),
('MANAGER', 'Manager', 'Accès aux fonctionnalités de gestion', 'ACTIF'),
('CAISSIER', 'Caisier', 'Accès aux caisses et ventes', 'ACTIF');
```

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Implémentation des modèles pour toutes les tables de sécurité
- [ ] Mise en place du hachage des mots de passe avec bcrypt
- [ ] Développement du système d'authentification avec JWT
- [ ] Mise en place du système RBAC (profils, permissions)
- [ ] Développement des endpoints API pour la gestion des utilisateurs
- [ ] Mise en place des contrôles d'accès aux stations
- [ ] Développement du système de journalisation des connexions
- [ ] Mise en place de la journalisation des événements de sécurité
- [ ] Développement des validations d'entrée
- [ ] Ajout de la journalisation des modifications sensibles
- [ ] Tests unitaires pour toutes les fonctionnalités
- [ ] Tests d'intégration pour les flux complets
- [ ] Documentation des API
- [ ] Revue de sécurité du code
- [ ] Mise en place de la distinction des endpoints administrateur/utilisateur
- [ ] Mise en place des contrôles de validation des endpoints

### 8.2 Ordre recommandé
1. Création des modèles et tables de base
2. Mise en place du hachage et de l'authentification
3. Développement du système RBAC
4. Implémentation des API de gestion des utilisateurs
5. Mise en place des contrôles d'accès
6. Développement de la journalisation
7. Mise en place de la distinction des endpoints
8. Tests et validation
9. Documentation

### 8.3 Livrables attendus
- Modèles SQLAlchemy pour toutes les tables de sécurité
- Services d'authentification et d'autorisation
- Endpoints API complets pour la gestion de la sécurité
- Système de journalisation fonctionnel
- Tests unitaires et d'intégration
- Documentation API
- Contrôles de validation des endpoints administrateur/utilisateur

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- Le hachage des mots de passe doit être correctement implémenté avec bcrypt
- La gestion des tokens doit être sécurisée pour éviter les attaques de type token theft
- Les contrôles d'accès doivent être strictement appliqués à chaque requête
- La journalisation ne doit pas contenir de données sensibles en clair
- La validation des entrées doit être effectuée à tous les niveaux
- La distinction des endpoints doit être rigoureusement appliquée
- Les contrôles de validation des endpoints doivent être incontournables

### 9.2 Risques techniques
- Risque de performance liée à la vérification des permissions à chaque requête
- Risque de saturation des tables de journalisation sans politique de rotation
- Risque de contournement des contrôles d'accès si mal implémentés
- Risque de fuite d'informations sensibles dans les messages d'erreur
- Risque de contournement des validations d'endpoint si mal implémentées
- Risque de confusion entre les endpoints administrateur et utilisateur

### 9.3 Dette technique potentielle
- Mise en place de politiques de rotation des tokens
- Mise en place d'une politique de purge des journaux après N jours
- Mise en place d'alertes automatiques pour les événements de sécurité
- Mise en place d'une interface d'administration pour la gestion de la sécurité
- Mise en place de mécanismes de notification en cas de tentatives d'accès non autorisées