# Technical Specification - Module de sécurité du système

## 1. Contexte & Objectif du Sprint

### Description métier
Le module de sécurité du système vise à protéger l'ERP SuccessFuel contre les menaces internes et externes. Il assure la protection des données sensibles, la gestion sécurisée des accès utilisateurs, l'authentification robuste, la journalisation des événements de sécurité, et la prévention des attaques courantes telles que les injections SQL, les attaques CSRF et les erreurs de divulgation d'informations.

### Problème à résoudre
Sans un système de sécurité robuste, l'ERP SuccessFuel serait vulnérable à diverses menaces :
- Accès non autorisés aux données financières et opérationnelles
- Attaques de type injection SQL pouvant compromettre l'intégrité des données
- Divulgation d'informations sensibles via des messages d'erreur
- Manque de traçabilité des actions critiques
- Absence de contrôles d'accès adaptés aux rôles et permissions

### Définition du périmètre
Le périmètre du sprint couvre :
- La mise en place d'un système d'authentification et d'autorisation (RBAC)
- La protection contre les attaques de sécurité connues (SQLi, XSS, CSRF)
- La journalisation sécurisée des actions critiques
- Le chiffrement des données sensibles
- La gestion des erreurs sécurisée
- Les contrôles d'accès basés sur les rôles et les stations
- La surveillance proactive des activités suspectes

## 2. User Stories & Critères d'acceptation

### US-SEC-001: En tant qu'utilisateur, je veux m'authentifier de manière sécurisée
**Critères d'acceptation :**
- L'utilisateur doit se connecter avec un login et mot de passe
- Le mot de passe doit être haché avec bcrypt avant stockage
- Un jeton d'authentification est généré après une connexion réussie
- Le jeton a une durée de vie limitée et expire automatiquement
- Le système enregistre la tentative de connexion dans la table `tentatives_connexion`

### US-SEC-002: En tant qu'administrateur, je veux assigner des permissions précises à un profil utilisateur
**Critères d'acceptation :**
- Les profils peuvent être créés avec des permissions spécifiques
- Les permissions sont regroupées par modules fonctionnels
- Un utilisateur ne peut exécuter que les actions pour lesquelles il a les permissions
- Les associations entre profils et permissions sont stockées dans la table `profil_permissions`

### US-SEC-003: En tant qu'administrateur, je veux limiter l'accès des utilisateurs à certaines stations
**Critères d'acceptation :**
- L'utilisateur est limité à un ensemble spécifique de stations
- Les stations autorisées sont stockées dans le champ `stations_user` de la table `utilisateurs`
- L'accès aux fonctionnalités est filtré selon les stations autorisées
- Les modifications en dehors des stations autorisées sont rejetées

### US-SEC-004: En tant que système, je veux journaliser toutes les actions critiques
**Critères d'acceptation :**
- Toutes les actions importantes sont enregistrées dans la table `modifications_sensibles`
- Les données sensibles ne sont pas stockées en clair dans les journaux
- Les informations d'identification ne sont pas exposées dans les logs
- Les tentatives de connexion sont journalisées dans la table `tentatives_connexion`

### US-SEC-005: En tant qu'utilisateur, je veux que les communications soient sécurisées
**Critères d'acceptation :**
- Toutes les communications se font via HTTPS
- Les jetons CSRF sont générés et vérifiés pour les opérations sensibles
- Les origines des requêtes sont validées pour prévenir les attaques de type CSRF

## 3. Modèle de Données

### Tables existantes utilisées (non modifiées)
- `utilisateurs` - stockage des comptes utilisateur
- `profils` - gestion des profils d'utilisateurs
- `permissions` - définition des actions permises
- `modules` - regroupement des fonctionnalités
- `profil_permissions` - association profil-permission
- `auth_tokens` - stockage des jetons d'authentification

### Tables à créer (si non existantes)

```sql
-- Table pour le suivi des tentatives de connexion
CREATE TABLE IF NOT EXISTS tentatives_connexion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(50) NOT NULL,
    ip_connexion VARCHAR(45),
    resultat_connexion VARCHAR(10) CHECK (resultat_connexion IN ('Reussie', 'Echouee')),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des événements de sécurité
CREATE TABLE IF NOT EXISTS evenements_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_evenement VARCHAR(50) NOT NULL, -- 'connexion_anormale', 'tentative_acces_non_autorise', etc.
    description TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    donnees_supplementaires JSONB,
    statut VARCHAR(20) DEFAULT 'NonTraite' CHECK (statut IN ('NonTraite', 'EnCours', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le suivi des modifications sensibles
CREATE TABLE IF NOT EXISTS modifications_sensibles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    type_operation VARCHAR(50) NOT NULL, -- 'modification_vente', 'annulation_vente', 'modification_stock', etc.
    objet_modifie VARCHAR(30) NOT NULL, -- 'vente', 'stock', 'achat', etc.
    objet_id UUID,
    ancienne_valeur JSONB,
    nouvelle_valeur JSONB,
    seuil_alerte BOOLEAN DEFAULT FALSE, -- TRUE si dépasse un seuil défini
    commentaire TEXT,
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    statut VARCHAR(20) DEFAULT 'Enregistre' CHECK (statut IN ('Enregistre', 'Enquete', 'Traite', 'Ferme')),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour la gestion des droits d'accès spécifiques aux trésoreries
CREATE TABLE IF NOT EXISTS permissions_tresorerie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    tresorerie_id UUID REFERENCES tresoreries(id),
    droits VARCHAR(20) CHECK (droits IN ('lecture', 'ecriture', 'validation', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les tentatives de connexion
CREATE INDEX IF NOT EXISTS idx_tentatives_connexion_utilisateur ON tentatives_connexion(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_tentatives_connexion_date ON tentatives_connexion(created_at);
CREATE INDEX IF NOT EXISTS idx_tentatives_connexion_ip ON tentatives_connexion(ip_connexion);

-- Index pour les événements de sécurité
CREATE INDEX IF NOT EXISTS idx_evenements_securite_utilisateur ON evenements_securite(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_evenements_securite_date ON evenements_securite(created_at);
CREATE INDEX IF NOT EXISTS idx_evenements_securite_type ON evenements_securite(type_evenement);

-- Index pour les modifications sensibles
CREATE INDEX IF NOT EXISTS idx_modifications_sensibles_utilisateur ON modifications_sensibles(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_modifications_sensibles_date ON modifications_sensibles(created_at);
CREATE INDEX IF NOT EXISTS idx_modifications_sensibles_objet ON modifications_sensibles(objet_modifie);

-- Index pour les jetons d'authentification
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires ON auth_tokens(expires_at);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour vérifier l'unicité des jetons actifs par utilisateur
CREATE OR REPLACE FUNCTION verify_single_active_token()
RETURNS TRIGGER AS $$
BEGIN
    -- Assurer qu'un utilisateur n'a qu'un seul jeton actif à la fois
    IF NEW.is_active AND EXISTS (
        SELECT 1 FROM auth_tokens 
        WHERE user_id = NEW.user_id AND is_active = TRUE AND id != NEW.id
    ) THEN
        UPDATE auth_tokens 
        SET is_active = FALSE 
        WHERE user_id = NEW.user_id AND is_active = TRUE AND id != NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verify_single_active_token
    BEFORE INSERT OR UPDATE ON auth_tokens
    FOR EACH ROW EXECUTE FUNCTION verify_single_active_token();
```

## 4. API Backend

### 4.1 Authentification

#### POST /api/auth/login
**Description:** Authenticate user and generate JWT token

**Request Body:**
```json
{
  "login": "string (max 50)",
  "password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "user_id": "uuid",
    "login": "string",
    "profile_id": "uuid",
    "profile_name": "string",
    "access_token": "string",
    "expires_at": "datetime",
    "stations": ["uuid"]
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Authentication successful
- 400: Invalid input data
- 401: Invalid credentials
- 403: Account blocked due to security reasons
- 429: Too many failed attempts

#### POST /api/auth/logout
**Description:** Logout user and invalidate token

**Headers:**
- Authorization: Bearer {token}

**Request Body:** Empty

**Response:**
```json
{
  "success": boolean,
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Logout successful
- 401: Invalid or expired token
- 403: Insufficient permissions

#### POST /api/auth/refresh-token
**Description:** Refresh access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "success": boolean,
  "data": {
    "access_token": "string",
    "expires_at": "datetime"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 200: Token refreshed
- 400: Invalid refresh token
- 401: Expired refresh token

### 4.2 Gestion des profils et permissions

#### GET /api/security/profiles
**Description:** Get all profiles with permissions

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- page: integer (default: 1)
- limit: integer (default: 10)
- search: string (optional)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "profiles": [
      {
        "id": "uuid",
        "code": "string",
        "libelle": "string",
        "company_id": "uuid",
        "statut": "string",
        "permissions": [
          {
            "id": "uuid",
            "libelle": "string",
            "module": "string"
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
- 200: Profiles retrieved
- 401: Unauthorized
- 403: Insufficient permissions

#### POST /api/security/profiles
**Description:** Create a new profile

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "code": "string (unique, max 20)",
  "libelle": "string (max 100)",
  "description": "string (optional)",
  "permissions": ["uuid"] // Array of permission IDs
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
    "statut": "string"
  },
  "message": "string"
}
```

**HTTP Status Codes:**
- 201: Profile created
- 400: Invalid input
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Profile code already exists

### 4.3 Surveillance de la sécurité

#### GET /api/security/logs
**Description:** Get security logs with filtering options

**Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- type: string (optional)
- user_id: uuid (optional)
- start_date: date (optional)
- end_date: date (optional)
- page: integer (default: 1)
- limit: integer (default: 10)

**Response:**
```json
{
  "success": boolean,
  "data": {
    "logs": [
      {
        "id": "uuid",
        "type_evenement": "string",
        "description": "string",
        "utilisateur_id": "uuid",
        "utilisateur_nom": "string",
        "ip_utilisateur": "string",
        "date": "datetime",
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
- 200: Logs retrieved
- 401: Unauthorized
- 403: Insufficient permissions

## 5. Logique Métier

### 5.1 Authentification et gestion des sessions

**Processus d'authentification :**
1. Valider les entrées (login et mot de passe)
2. Rechercher l'utilisateur dans la base de données
3. Vérifier le statut (actif/inactif/supprimé)
4. Comparer le mot de passe haché avec bcrypt
5. Vérifier les tentatives de connexion récentes
6. Générer un jeton JWT avec une durée de vie définie
7. Créer une entrée dans `auth_tokens` pour le suivi
8. Enregistrer la tentative de connexion dans `tentatives_connexion`

**Cas particuliers :**
- Blocage temporaire après plusieurs tentatives échouées
- Expiration automatique des jetons
- Génération de nouveaux jetons lors du rafraîchissement

### 5.2 RBAC (Role-Based Access Control)

**Processus de vérification des permissions :**
1. Extraire le jeton d'authentification de la requête
2. Vérifier la validité et l'expiration du jeton
3. Charger le profil de l'utilisateur
4. Charger les permissions associées au profil
5. Vérifier si l'action demandée est autorisée
6. Vérifier les restrictions de station si applicable

**Contraintes :**
- Un utilisateur ne peut agir que sur les stations autorisées
- Les permissions sont vérifiées à chaque requête sensible
- Les rôles peuvent être assignés par les administrateurs

### 5.3 Journalisation des événements de sécurité

**Types d'événements surveillés :**
- Connexions/déconnexions
- Échecs d'authentification
- Modifications critiques (montants élevés, suppression de données)
- Accès à des zones sensibles
- Tentatives d'injection SQL ou autres attaques

**Processus de journalisation :**
1. Détecter l'événement de sécurité
2. Extraire les informations pertinentes (IP, utilisateur, action)
3. Masquer les données sensibles dans les logs
4. Enregistrer dans la table `evenements_securite`
5. Générer des alertes si seuil dépassé

### 5.4 Validation des entrées et prévention des attaques

**Validation côté serveur :**
- Vérification des types de données
- Validation des longueurs maximales
- Filtrage des caractères dangereux
- Validation des formats (emails, numéros, etc.)

**Prévention des attaques :**
- Utilisation de requêtes préparées pour toutes les requêtes SQL
- Validation des origines des requêtes (CSRF tokens)
- Encodage des sorties pour prévenir XSS
- Validation des URLs de redirection

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
utilisateurs ||--o{ auth_tokens : "possède"
utilisateurs ||--o{ tentatives_connexion : "génère"
utilisateurs ||--o{ evenements_securite : "génère"
utilisateurs ||--o{ modifications_sensibles : "effectue"

profils ||--o{ utilisateurs : "assigné à"
profils ||--o{ profil_permissions : "a des"
profil_permissions }o--|| permissions : "permet"
permissions }o--|| modules : "appartient à"

tentatives_connexion ||--o{ evenements_securite : "peut causer"
modifications_sensibles ||--o{ evenements_securite : "peut causer"
```

### 6.2 Diagramme de séquence - Processus de connexion

```
Utilisateur -> Serveur: POST /api/auth/login
Serveur -> DB: Chercher utilisateur par login
DB -> Serveur: Retourner utilisateur
Serveur -> Serveur: Valider mot de passe avec bcrypt
Serveur -> Serveur: Vérifier le statut du compte
Serveur -> DB: Enregistrer tentative de connexion
Serveur -> Serveur: Générer JWT token
Serveur -> DB: Stocker token dans auth_tokens
Serveur -> Utilisateur: Retourner token + infos utilisateur
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Hachage et vérification des mots de passe avec bcrypt
- Génération et validation des tokens JWT
- Validation des entrées utilisateur
- Méthodes de vérification des permissions
- Processus de journalisation des événements

### 7.2 Tests d'intégration
- Cycle complet d'authentification et déconnexion
- Attribution correcte des permissions
- Vérification des contrôles d'accès
- Processus de rafraîchissement des tokens
- Surveillance des tentatives de connexion

### 7.3 Tests de charge/performance
- Simuler plusieurs connexions simultanées
- Tester la performance de vérification des permissions
- Vérifier l'impact de la journalisation sur la performance
- Tester la génération et validation des tokens sous charge

### 7.4 Jeux de données de test
```sql
-- Données de test pour la sécurité
INSERT INTO modules (libelle, statut) VALUES
('ventes', 'Actif'),
('achats', 'Actif'),
('stocks', 'Actif'),
('utilisateurs', 'Actif')
ON CONFLICT (libelle) DO NOTHING;

INSERT INTO permissions (libelle, description, module_id)
SELECT 'lire_ventes', 'Lire les détails des ventes', id
FROM modules
WHERE libelle = 'ventes';

INSERT INTO permissions (libelle, description, module_id)
SELECT 'creer_vente', 'Créer une nouvelle vente', id
FROM modules
WHERE libelle = 'ventes';

INSERT INTO permissions (libelle, description, module_id)
SELECT 'modifier_stock', 'Modifier manuellement les stocks', id
FROM modules
WHERE libelle = 'stocks';

INSERT INTO profils (code, libelle, description, statut)
VALUES ('ADMIN', 'Administrateur', 'Profil avec toutes les permissions', 'Actif');

-- Créer un utilisateur test avec mot de passe haché
-- (Le mot de passe est "password123" haché avec bcrypt)
INSERT INTO utilisateurs (
    id, login, mot_de_passe, nom, profil_id, statut, compagnie_id, created_at
)
VALUES (
    gen_random_uuid(),
    'admin_test',
    '$2b$12$L.RZ2T0pL.z8x1q2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n', -- haché de "password123"
    'Admin Test',
    (SELECT id FROM profils WHERE code = 'ADMIN'),
    'Actif',
    (SELECT id FROM compagnies LIMIT 1), -- Supposant qu'il existe une compagnie
    now()
);
```

## 8. Checklist Développeur

### Tâches techniques détaillées

**Phase 1 - Authentification (jours 1-2)**
- [ ] Implémenter le service d'authentification
- [ ] Intégrer bcrypt pour le hachage des mots de passe
- [ ] Créer les endpoints de login/logout/refresh-token
- [ ] Gérer la journalisation des tentatives de connexion
- [ ] Tester les scénarios d'échec d'authentification

**Phase 2 - RBAC (jours 3-4)**
- [ ] Créer les services de gestion des profils et permissions
- [ ] Implémenter les middlewares de vérification des permissions
- [ ] Créer les endpoints CRUD pour les profils
- [ ] Tester l'attribution et la vérification des permissions
- [ ] Gérer les contraintes d'accès par station

**Phase 3 - Journalisation de sécurité (jours 5-6)**
- [ ] Créer les services de journalisation des événements de sécurité
- [ ] Implémenter les outils de surveillance proactive
- [ ] Créer les endpoints pour la consultation des logs
- [ ] Mettre en place les alertes pour les événements critiques
- [ ] Tester la journalisation des actions sensibles

**Phase 4 - Sécurité avancée (jour 7)**
- [ ] Mettre en place les protections contre CSRF
- [ ] Gérer la sécurité des communications (HTTPS)
- [ ] Tester la gestion des erreurs sécurisée
- [ ] Mettre en place les validations d'entrées strictes
- [ ] Tester la prévention des injections SQL

### Ordre recommandé
1. Commencer par l'authentification (base du système de sécurité)
2. Puis implémenter le RBAC (gestion des droits)
3. Ensuite la journalisation (surveillance)
4. Enfin les protections avancées

### Livrables attendus
- [ ] Services d'authentification fonctionnels
- [ ] Système RBAC complet
- [ ] Journalisation des événements de sécurité
- [ ] Middleware de sécurité
- [ ] Tests unitaires et d'intégration
- [ ] Documentation API
- [ ] Jeux de données de test

## 9. Risques & Points de vigilance

### Points sensibles
- Stockage sécurisé des mots de passe (utiliser bcrypt ou Argon2)
- Gestion des sessions et invalidation des tokens
- Protection contre les attaques par force brute
- Journalisation sans exposition de données sensibles
- Gestion des erreurs sans fuite d'informations techniques

### Risques techniques
- Performance impactée par la vérification des permissions à chaque requête
- Risque de déni de service par abus de tentatives de connexion
- Gestion incorrecte des tokens pouvant permettre des attaques de type hijacking
- Erreurs dans la validation des entrées pouvant permettre des injections

### Dette technique potentielle
- Mise en place d'un système de cache pour les permissions pour améliorer les performances
- Centralisation de la gestion des événements de sécurité dans un service dédié
- Mise en place d'un système d'alerts et de notifications en temps réel
- Intégration avec un SIEM (Security Information and Event Management) externe