# Technical Specification - Initialisation des stocks

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de configurer les stocks au démarrage du système SuccessFuel. Cela inclut l'initialisation des stocks de carburant dans les cuves avec les index des pistolets, ainsi que l'initialisation des stocks de produits dans la boutique. L'objectif est de permettre une prise en main rapide et correcte du système par les gestionnaires de station-service.

### Problème à résoudre
Actuellement, il n'existe pas de mécanisme permettant d'initialiser les stocks réels de la station-service dans le système informatique. Cela pose problème car :
- Les mouvements de stock ne peuvent pas être correctement suivis sans un point de départ
- Les rapports de gestion ne reflètent pas la réalité des stocks
- Les calculs de rentabilité sont biaisés
- L'historique des stocks n'est pas disponible

### Définition du périmètre
Le périmètre inclut :
- Initialisation des stocks de carburant par cuve
- Initialisation des index des pistolets
- Historisation automatique des stocks initiaux
- Analyse de la qualité du carburant initial
- Initialisation des stocks de produits boutique
- Valorisation initiale des stocks
- Analyse des coûts logistique initiaux

## 2. User Stories & Critères d'acceptation

### US-INIT-001: En tant que gestionnaire, je veux initialiser les stocks de carburant
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales de carburant par cuve
  - Pouvoir spécifier la date d'initialisation
  - Le système doit enregistrer l'historique automatiquement
  - Pouvoir analyser la qualité du carburant initial
  - Les quantités saisies doivent être validées

### US-INIT-002: En tant que gestionnaire, je veux initialiser les index des pistolets
- **Critères d'acceptation :**
  - Pouvoir saisir les index initiaux de chaque pistolet
  - Pouvoir spécifier la date d'initialisation
  - Le système doit conserver l'historique
  - Les valeurs d'index doivent être cohérentes avec les stocks de cuve

### US-INIT-003: En tant que gestionnaire, je veux initialiser les stocks de produits boutique
- **Critères d'acceptation :**
  - Pouvoir saisir les quantités initiales de chaque produit
  - Pouvoir spécifier les prix unitaires d'achat et de vente
  - Le système doit calculer automatiquement la valorisation initiale
  - Les données doivent être historisées

### US-INIT-004: En tant que gestionnaire, je veux avoir accès à l'analyse des coûts logistique initiaux
- **Critères d'acceptation :**
  - Le système doit permettre d'analyser les coûts liés à l'approvisionnement initial
  - Les coûts doivent être rattachés à chaque produit initial
  - Les analyses doivent être disponibles pour les carburants et les produits boutique

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: bilan_initial
```sql
CREATE TABLE bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    date_bilan_initial DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id), -- Utilisateur qui a effectué le bilan
    description TEXT,
    est_valide BOOLEAN DEFAULT FALSE, -- Indique si le bilan a été validé
    est_verifie BOOLEAN DEFAULT FALSE, -- Indique si le bilan a été vérifié
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_bilan_initial_compagnie ON bilan_initial(compagnie_id);
CREATE INDEX idx_bilan_initial_station ON bilan_initial(station_id);
CREATE INDEX idx_bilan_initial_date ON bilan_initial(date_bilan_initial);
CREATE INDEX idx_bilan_initial_utilisateur ON bilan_initial(utilisateur_id);
```

#### Table: stocks_initial_carburant
```sql
CREATE TABLE stocks_initial_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID NOT NULL REFERENCES bilan_initial(id),
    cuve_id UUID NOT NULL REFERENCES cuves(id),
    carburant_id UUID NOT NULL REFERENCES carburants(id),
    quantite NUMERIC(18,3) NOT NULL, -- Quantité en unité de mesure du carburant
    prix_unitaire NUMERIC(18,4), -- Prix unitaire d'achat à la date d'initialisation
    valeur_totale NUMERIC(18,4) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED, -- Calcul automatique
    temperature NUMERIC(5,2), -- Température au moment de la mesure
    qualite NUMERIC(3,2), -- Note de qualité sur 10
    observation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_stocks_initial_carburant_bilan ON stocks_initial_carburant(bilan_initial_id);
CREATE INDEX idx_stocks_initial_carburant_cuve ON stocks_initial_carburant(cuve_id);
CREATE INDEX idx_stocks_initial_carburant_carburant ON stocks_initial_carburant(carburant_id);
```

#### Table: stocks_initial_produit
```sql
CREATE TABLE stocks_initial_produit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID NOT NULL REFERENCES bilan_initial(id),
    article_id UUID NOT NULL REFERENCES articles(id),
    quantite NUMERIC(18,3) NOT NULL, -- Quantité en unité de stock
    prix_unitaire_achat NUMERIC(18,4), -- Prix unitaire d'achat à la date d'initialisation
    prix_unitaire_vente NUMERIC(18,4), -- Prix unitaire de vente à la date d'initialisation
    valeur_totale_achat NUMERIC(18,4) GENERATED ALWAYS AS (quantite * prix_unitaire_achat) STORED, -- Calcul automatique
    valeur_totale_vente NUMERIC(18,4) GENERATED ALWAYS AS (quantite * prix_unitaire_vente) STORED, -- Calcul automatique
    tva_applicable NUMERIC(5,2), -- Taux de TVA applicable
    observation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_stocks_initial_produit_bilan ON stocks_initial_produit(bilan_initial_id);
CREATE INDEX idx_stocks_initial_produit_article ON stocks_initial_produit(article_id);
```

#### Table: index_initial_pistolets
```sql
CREATE TABLE index_initial_pistolets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID NOT NULL REFERENCES bilan_initial(id),
    pistolet_id UUID NOT NULL REFERENCES pistolets(id),
    index_initial NUMERIC(18,3) NOT NULL,
    date_releve DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_index_initial_pistolets_bilan ON index_initial_pistolets(bilan_initial_id);
CREATE INDEX idx_index_initial_pistolets_pistolet ON index_initial_pistolets(pistolet_id);
CREATE INDEX idx_index_initial_pistolets_date ON index_initial_pistolets(date_releve);
```

### 3.2 Relations
- `bilan_initial.station_id` → `stations.id` (One-to-Many)
- `bilan_initial.utilisateur_id` → `utilisateurs.id` (One-to-Many)
- `bilan_initial.compagnie_id` → `compagnies.id` (One-to-Many)
- `stocks_initial_carburant.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `stocks_initial_carburant.cuve_id` → `cuves.id` (One-to-Many)
- `stocks_initial_carburant.carburant_id` → `carburants.id` (One-to-Many)
- `stocks_initial_produit.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `stocks_initial_produit.article_id` → `articles.id` (One-to-Many)
- `index_initial_pistolets.bilan_initial_id` → `bilan_initial.id` (One-to-Many)
- `index_initial_pistolets.pistolet_id` → `pistolets.id` (One-to-Many)
- `index_initial_pistolets.utilisateur_id` → `utilisateurs.id` (One-to-Many)

### 3.3 Triggers et règles d'intégrité
```sql
-- Trigger pour empêcher la modification des données d'initialisation après validation
CREATE OR REPLACE FUNCTION verif_bilan_initial_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Si le bilan est déjà validé, ne pas permettre les modifications
    IF (SELECT est_valide FROM bilan_initial WHERE id = NEW.bilan_initial_id) = TRUE THEN
        RAISE EXCEPTION 'Impossible de modifier les données d''un bilan initial validé';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_verif_bilan_initial_stocks_carb
    BEFORE INSERT OR UPDATE ON stocks_initial_carburant
    FOR EACH ROW
    EXECUTE FUNCTION verif_bilan_initial_modification();

CREATE TRIGGER trig_verif_bilan_initial_stocks_prod
    BEFORE INSERT OR UPDATE ON stocks_initial_produit
    FOR EACH ROW
    EXECUTE FUNCTION verif_bilan_initial_modification();

CREATE TRIGGER trig_verif_bilan_initial_index_pist
    BEFORE INSERT OR UPDATE ON index_initial_pistolets
    FOR EACH ROW
    EXECUTE FUNCTION verif_bilan_initial_modification();

-- Trigger pour mettre à jour le champ updated_at sur le bilan initial
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_bilan_initial_updated_at
    BEFORE UPDATE ON bilan_initial
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Contrainte pour s'assurer que l'opération de création de bilan initial ne soit effectuée qu'une seule fois par station par date
ALTER TABLE bilan_initial ADD CONSTRAINT unique_bilan_initial_par_date
    UNIQUE (station_id, date_bilan_initial);
```

## 4. API Backend

### 4.1 Gestion du bilan initial

#### POST /api/v1/stock-initial/balance
- **Description**: Créer un nouveau bilan initial pour une station
- **Headers**: Authorization: Bearer {token}
- **Payload**:
```json
{
    "station_id": "uuid",
    "date_bilan_initial": "date",
    "description": "string",
    "stocks_carburant": [
        {
            "cuve_id": "uuid",
            "carburant_id": "uuid",
            "quantite": "number",
            "prix_unitaire": "number",
            "temperature": "number",
            "qualite": "number",
            "observation": "string"
        }
    ],
    "stocks_produit": [
        {
            "article_id": "uuid",
            "quantite": "number",
            "prix_unitaire_achat": "number",
            "prix_unitaire_vente": "number",
            "tva_applicable": "number",
            "observation": "string"
        }
    ],
    "index_pistolets": [
        {
            "pistolet_id": "uuid",
            "index_initial": "number",
            "observation": "string"
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
        "compagnie_id": "uuid",
        "station_id": "uuid",
        "date_bilan_initial": "date",
        "utilisateur_id": "uuid",
        "description": "string",
        "est_valide": "boolean",
        "est_verifie": "boolean",
        "commentaire": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```
- **Codes d'erreur**:
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès interdit
  - 409: Bilan initial déjà existant pour cette date et cette station

#### GET /api/v1/stock-initial/balance/{balance_id}
- **Description**: Récupérer les détails d'un bilan initial
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "compagnie_id": "uuid",
        "station_id": "uuid",
        "date_bilan_initial": "date",
        "utilisateur_id": "uuid",
        "description": "string",
        "est_valide": "boolean",
        "est_verifie": "boolean",
        "commentaire": "string",
        "stocks_carburant": [
            {
                "id": "uuid",
                "cuve_id": "uuid",
                "carburant_id": "uuid",
                "quantite": "number",
                "prix_unitaire": "number",
                "valeur_totale": "number",
                "temperature": "number",
                "qualite": "number",
                "observation": "string"
            }
        ],
        "stocks_produit": [
            {
                "id": "uuid",
                "article_id": "uuid",
                "quantite": "number",
                "prix_unitaire_achat": "number",
                "prix_unitaire_vente": "number",
                "valeur_totale_achat": "number",
                "valeur_totale_vente": "number",
                "tva_applicable": "number",
                "observation": "string"
            }
        ],
        "index_pistolets": [
            {
                "id": "uuid",
                "pistolet_id": "uuid",
                "index_initial": "number",
                "date_releve": "date",
                "observation": "string"
            }
        ],
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

#### PUT /api/v1/stock-initial/balance/{balance_id}/validate
- **Description**: Valider un bilan initial
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "est_valide": "boolean",
        "updated_at": "timestamp"
    }
}
```

### 4.2 Gestion des stocks initiaux

#### GET /api/v1/stock-initial/fuel/{balance_id}
- **Description**: Récupérer les stocks initiaux de carburant pour un bilan
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "cuve_id": "uuid",
            "carburant_id": "uuid",
            "quantite": "number",
            "prix_unitaire": "number",
            "valeur_totale": "number",
            "temperature": "number",
            "qualite": "number",
            "observation": "string",
            "created_at": "timestamp"
        }
    ]
}
```

#### GET /api/v1/stock-initial/product/{balance_id}
- **Description**: Récupérer les stocks initiaux de produits pour un bilan
- **Headers**: Authorization: Bearer {token}
- **Réponse**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "article_id": "uuid",
            "quantite": "number",
            "prix_unitaire_achat": "number",
            "prix_unitaire_vente": "number",
            "valeur_totale_achat": "number",
            "valeur_totale_vente": "number",
            "tva_applicable": "number",
            "observation": "string",
            "created_at": "timestamp"
        }
    ]
}
```

## 5. Logique Métier

### 5.1 Règles d'initialisation des stocks de carburant
- Chaque cuve peut contenir un seul type de carburant à la date d'initialisation
- La quantité initiale dans une cuve ne doit pas dépasser la capacité maximale de la cuve
- Le prix unitaire d'achat doit être supérieur ou égal à 0
- La température est nécessaire pour les corrections volumétriques
- La qualité du carburant est notée sur 10

### 5.2 Règles d'initialisation des stocks de produits
- Chaque produit doit appartenir à une famille de produits existante
- La quantité initiale doit être positive
- Le prix unitaire d'achat et de vente doivent être supérieurs ou égaux à 0
- La valeur totale est calculée automatiquement (quantité × prix unitaire)
- Les taxes applicables doivent être correctement affectées

### 5.3 Règles d'initialisation des index des pistolets
- Chaque index initial doit être affecté à un pistolet spécifique
- La date de relevé doit être égale ou antérieure à la date du bilan initial
- L'index initial doit être inférieur ou égal aux volumes distribuables (cohérence avec stocks de cuve)

### 5.4 Validation du bilan initial
- Un bilan initial ne peut être modifié une fois validé
- Un bilan initial ne peut être créé qu'une seule fois par station et par date
- La validation nécessite une autorisation spécifique (profil administrateur ou gestionnaire)
- Le bilan initial sert de point de départ pour tous les calculs de mouvements de stock

### 5.5 Impacts sur d'autres modules
- Les stocks initiaux servent de base pour le module de gestion des achats
- Les index initiaux servent de base pour le module de gestion des ventes
- Les coûts logistiques initiaux influencent les calculs de rentabilité

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
[compagnies] 1 -- * [bilan_initial]
[stations] 1 -- * [bilan_initial]
[utilisateurs] 1 -- * [bilan_initial]

[bilan_initial] 1 -- * [stocks_initial_carburant]
[cuves] 1 -- * [stocks_initial_carburant]
[carburants] 1 -- * [stocks_initial_carburant]

[bilan_initial] 1 -- * [stocks_initial_produit]
[articles] 1 -- * [stocks_initial_produit]

[bilan_initial] 1 -- * [index_initial_pistolets]
[pistolets] 1 -- * [index_initial_pistolets]
[utilisateurs] 1 -- * [index_initial_pistolets]
```

### 6.2 Diagramme de séquence (initialisation des stocks)
```
Gestionnaire -> API: POST /api/v1/stock-initial/balance (station_id, date_bilan_initial, stocks_carburant, stocks_produit, index_pistolets)
API -> Database: Vérifier que la station appartient à la compagnie de l'utilisateur
Database -> API: Station trouvée
API -> Database: Vérifier qu'il n'y a pas de bilan initial existant pour cette date et cette station
Database -> API: Aucun conflit trouvé
API -> Database: Créer le bilan initial
Database -> API: Bilan initial créé
API -> Database: Créer les stocks initiaux de carburant
API -> Database: Créer les stocks initiaux de produits
API -> Database: Créer les index initiaux des pistolets
API -> Gestionnaire: {success: true, data: {...}}
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test des validations de données pour chaque modèle
- Test des contraintes de base de données
- Test de la logique de calcul automatique des valeurs totales
- Test des triggers de protection des données validées

### 7.2 Tests d'intégration
- Test de la création complète d'un bilan initial avec tous les composants
- Test de la protection contre les modifications des bilans validés
- Test de la cohérence entre index des pistolets et stocks de cuve
- Test de la validation du bilan initial

### 7.3 Tests de charge/performance
- Test de la performance lors de la création de bilans initiaux avec de nombreuses références
- Test de la performance lors de la récupération des données de bilan

### 7.4 Jeux de données de test
```sql
-- Données de test pour l'initialisation des stocks

-- Création d'un bilan initial de test
INSERT INTO bilan_initial (id, compagnie_id, station_id, date_bilan_initial, utilisateur_id, description, created_at, updated_at)
VALUES ('BILAN001-UUID', 'COMP1-UUID', 'STATION001-UUID', '2025-01-01', 'USER001-UUID', 'Bilan initial de la station', now(), now());

-- Création de stocks initiaux de carburant de test
INSERT INTO stocks_initial_carburant (id, bilan_initial_id, cuve_id, carburant_id, quantite, prix_unitaire, temperature, qualite, created_at)
VALUES 
('STOCKCARB001-UUID', 'BILAN001-UUID', 'CUVE001-UUID', 'FUEL001-UUID', 10000.000, 4200.0000, 25.5, 8.5, now()),
('STOCKCARB002-UUID', 'BILAN001-UUID', 'CUVE002-UUID', 'FUEL002-UUID', 8000.500, 3800.0000, 26.0, 9.0, now());

-- Création de stocks initiaux de produits de test
INSERT INTO stocks_initial_produit (id, bilan_initial_id, article_id, quantite, prix_unitaire_achat, prix_unitaire_vente, tva_applicable, created_at)
VALUES 
('STOCKPROD001-UUID', 'BILAN001-UUID', 'ART001-UUID', 500.000, 1200.0000, 1500.0000, 20.00, now()),
('STOCKPROD002-UUID', 'BILAN001-UUID', 'ART002-UUID', 200.000, 800.0000, 1000.0000, 20.00, now());
```

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Création des modèles SQLAlchemy pour les tables : bilan_initial, stocks_initial_carburant, stocks_initial_produit, index_initial_pistolets
- [ ] Mise en place des relations entre les modèles
- [ ] Développement des services pour la gestion des bilans initiaux
- [ ] Développement des services pour la gestion des stocks initiaux de carburant
- [ ] Développement des services pour la gestion des stocks initiaux de produits
- [ ] Développement des services pour la gestion des index initiaux des pistolets
- [ ] Développement des endpoints API pour la création et la consultation des bilans initiaux
- [ ] Mise en place des validations de données
- [ ] Mise en place des triggers pour protéger les données validées
- [ ] Mise en place des contraintes d'unicité
- [ ] Calcul automatique des valeurs totales
- [ ] Tests unitaires et d'intégration
- [ ] Documentation des API

### 8.2 Ordre recommandé
1. Création des modèles et migrations des tables
2. Développement des services pour la gestion des bilans initiaux
3. Développement des services pour chaque type de données d'initialisation
4. Développement des endpoints API
5. Mise en place des validations et contraintes
6. Tests et documentation

### 8.3 Livrables attendus
- Modèles SQLAlchemy pour les tables d'initialisation des stocks
- Services backend pour la gestion des bilans initiaux
- Endpoints API complets pour la gestion de l'initialisation
- Système de validation des données
- Système de protection des données validées
- Documentation API
- Jeux de tests unitaires et d'intégration

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La protection des données validées pour éviter les modifications accidentelles
- La cohérence entre les différents types de stocks initiaux
- La validation des quantités et des prix saisis
- La gestion des droits d'accès à l'initialisation des stocks

### 9.2 Risques techniques
- Risque de performance lié à la gestion de nombreux articles lors de l'initialisation
- Risque d'incohérence si les données d'initialisation ne sont pas complètes
- Risque de conflits si plusieurs utilisateurs essaient d'initialiser en même temps
- Risque de perte de données si le processus d'initialisation n'est pas terminé correctement

### 9.3 Dette technique potentielle
- Mise en place d'un système d'audit plus complet des modifications de stocks
- Mise en place d'outils d'analyse comparative entre stocks réels et stocks théoriques
- Mise en place d'une interface d'administration plus avancée pour la gestion des stocks
- Mise en place d'automatismes pour la validation des données d'initialisation