# Technical Specification - Module d'initialisation des stocks

## 1. Contexte & Objectif du Sprint

### Description métier
Le module d'initialisation des stocks permet de configurer les stocks au démarrage du système SuccessFuel. Cette opération est essentielle pour établir les bases des inventaires physiques et permettre le suivi des mouvements à partir d'une situation connue et validée. Le module couvre à la fois les stocks de carburant (cuves) et les stocks de produits de boutique.

### Problème à résoudre
À l'installation du système, les stations-service ont déjà des stocks physiques existants. Sans initialisation correcte de ces stocks, le système ne refléterait pas la réalité physique, rendant impossible le suivi précis des mouvements et des écarts. Il est nécessaire de capturer avec précision les quantités initiales pour chaque type de carburant et chaque produit de la boutique.

### Définition du périmètre
Le périmètre du sprint couvre :
- L'initialisation des stocks de carburant par cuve
- L'initialisation des index des pistolets
- L'initialisation des stocks de produits de boutique
- L'analyse de la qualité du carburant initial
- L'analyse des coûts logistiques initiaux
- La valorisation initiale des stocks
- La génération automatique des écritures comptables d'ouverture
- L'historisation automatique des mouvements initiaux

## 2. User Stories & Critères d'acceptation

### US-INIT-001: En tant que gestionnaire, je veux initialiser les stocks de carburant
**Critères d'acceptation :**
- Saisie des quantités initiales pour chaque cuve
- Lien avec les données de carburant (type, prix, qualité)
- Historique automatique dans les mouvements de stock
- Analyse de la qualité du carburant (densité, indice, soufre, etc.)
- Génération des écritures comptables d'ouverture
- Calcul de la valeur totale du stock initial
- Validation de la quantité par rapport à la capacité de la cuve

### US-INIT-002: En tant que gestionnaire, je veux initialiser les index des pistolets
**Critères d'acceptation :**
- Saisie de l'index initial pour chaque pistolet
- Lien avec la cuve correspondante
- Historique de l'index dans la table appropriée
- Vérification de la cohérence avec le stock de la cuve
- Traçabilité de l'opération (qui, quand, pourquoi)
- Génération d'un mouvement initial dans les stocks

### US-INIT-003: En tant que gestionnaire, je veux initialiser les stocks de produits de boutique
**Critères d'acceptation :**
- Saisie des quantités initiales pour chaque produit
- Valorisation initiale basée sur le prix d'achat
- Calcul de la valeur totale des stocks de boutique
- Analyse des coûts logistiques initiaux
- Historique automatique des mouvements
- Génération des écritures comptables d'ouverture
- Lien avec les familles de produits et les informations de base

### US-INIT-004: En tant que gestionnaire, je veux disposer d'un bilan initial global
**Critères d'acceptation :**
- Vue agrégée de tous les stocks initiaux (carburant et boutique)
- Répartition par station, type de produit ou cuve
- Calcul de la valeur totale des stocks
- Historique des validations
- Traçabilité complète des données saisies
- Export possible pour les rapports comptables

## 3. Modèle de Données

### Tables existantes utilisées (avec éventuelles modifications)
```sql
-- Table pour les stocks (amélioration pour l'initialisation)
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS est_initial BOOLEAN DEFAULT FALSE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS date_initialisation DATE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS utilisateur_initialisation UUID REFERENCES utilisateurs(id);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS observation_initialisation TEXT;

-- Table pour les mouvements de stock (déjà existante mais optimisée)
-- Ajout de champs pour lier aux opérations d'initialisation
ALTER TABLE stocks_mouvements ADD COLUMN IF NOT EXISTS est_initial BOOLEAN DEFAULT FALSE;
ALTER TABLE stocks_mouvements ADD COLUMN IF NOT EXISTS operation_initialisation_id UUID;

-- Table pour l'analyse de la qualité du carburant initial
CREATE TABLE IF NOT EXISTS qualite_carburant_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuve_id UUID REFERENCES cuves(id),
    carburant_id UUID REFERENCES carburants(id),
    date_analyse DATE NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    densite NUMERIC(8,4), -- Ex: 0.8350 kg/L
    indice_octane INTEGER, -- Ex: 95 pour SP95
    soufre_ppm NUMERIC(10,2), -- Partie par million
    type_additif VARCHAR(100), -- Type d'additif utilisé
    commentaire_qualite TEXT,
    resultat_qualite VARCHAR(20) CHECK (resultat_qualite IN ('Conforme', 'Non conforme', 'En attente')),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour l'analyse des coûts logistiques initiaux
CREATE TABLE IF NOT EXISTS couts_logistique_stocks_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    article_id UUID REFERENCES articles(id),
    cuve_id UUID REFERENCES cuves(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES utilisateurs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour le bilan initial global
CREATE TABLE IF NOT EXISTS bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
    date_bilan DATE NOT NULL,
    commentaire TEXT,
    valeur_totale_stocks NUMERIC(18,2) DEFAULT 0,
    nombre_elements INTEGER DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'Brouillon' CHECK (statut IN ('Brouillon', 'En cours', 'Termine', 'Validé')),
    utilisateur_validation_id UUID REFERENCES utilisateurs(id),
    date_validation DATE,
    est_valide BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table pour les lignes du bilan initial
CREATE TABLE IF NOT EXISTS bilan_initial_lignes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bilan_initial_id UUID REFERENCES bilan_initial(id) ON DELETE CASCADE,
    type_element VARCHAR(20) NOT NULL CHECK (type_element IN ('carburant', 'article_boutique', 'autre')),
    element_id UUID NOT NULL,  -- ID de la cuve ou de l'article
    description_element TEXT,
    quantite NUMERIC(18,3) NOT NULL,
    unite_mesure VARCHAR(10),
    prix_unitaire NUMERIC(18,4) NOT NULL,
    valeur_totale NUMERIC(18,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    taux_tva NUMERIC(5,2) DEFAULT 0,
    montant_tva NUMERIC(18,2),
    montant_ht NUMERIC(18,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Index recommandés
```sql
-- Index pour les stocks initiaux
CREATE INDEX IF NOT EXISTS idx_stocks_est_initial ON stocks(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_date_initialisation ON stocks(date_initialisation);

-- Index pour les mouvements de stock initiaux
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_est_initial ON stocks_mouvements(est_initial);
CREATE INDEX IF NOT EXISTS idx_stocks_mouvements_operation ON stocks_mouvements(operation_initialisation_id);

-- Index pour la qualité du carburant initial
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_cuve ON qualite_carburant_initial(cuve_id);
CREATE INDEX IF NOT EXISTS idx_qualite_carburant_initial_date ON qualite_carburant_initial(date_analyse);

-- Index pour les coûts logistiques initiaux
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_article ON couts_logistique_stocks_initial(article_id);
CREATE INDEX IF NOT EXISTS idx_couts_logistique_initial_date ON couts_logistique_stocks_initial(date_cout);

-- Index pour le bilan initial
CREATE INDEX IF NOT EXISTS idx_bilan_initial_compagnie ON bilan_initial(compagnie_id);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_date ON bilan_initial(date_bilan);
CREATE INDEX IF NOT EXISTS idx_bilan_initial_statut ON bilan_initial(statut);
```

### Triggers et règles d'intégrité
```sql
-- Trigger pour empêcher la modification d'un stock initialisé
CREATE OR REPLACE FUNCTION prevent_initial_stock_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Ne pas permettre la modification d'un stock marqué comme initial
    IF OLD.est_initial = TRUE THEN
        RAISE EXCEPTION 'Impossible de modifier un stock initialisé';
    END IF;
    
    -- Si le stock devient initial, effectuer des validations
    IF NEW.est_initial = TRUE AND OLD.est_initial IS DISTINCT FROM TRUE THEN
        -- Validation de la quantité par rapport à la capacité
        IF NEW.cuve_id IS NOT NULL THEN
            DECLARE
                capacite_cuve NUMERIC(18,3);
            BEGIN
                SELECT capacite INTO capacite_cuve
                FROM cuves
                WHERE id = NEW.cuve_id;
                
                IF NEW.stock_theorique > capacite_cuve THEN
                    RAISE EXCEPTION 'La quantité initiale dépasse la capacité de la cuve (% litres)', capacite_cuve;
                END IF;
            END;
        END IF;
        
        -- Historisation automatique du mouvement initial
        INSERT INTO stocks_mouvements (
            stock_id, article_id, cuve_id, station_id, type_mouvement, 
            quantite, prix_unitaire, date_mouvement, reference_operation, 
            utilisateur_id, commentaire, compagnie_id, est_initial
        )
        VALUES (
            NEW.id, NEW.article_id, NEW.cuve_id, NEW.station_id, 'Initial',
            NEW.stock_theorique, NEW.prix_unitaire, NEW.date_initialisation, 'INIT-' || NEW.id,
            NEW.utilisateur_initialisation, 'Initialisation du stock', NEW.compagnie_id, TRUE
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_initial_stock_modification
    BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION prevent_initial_stock_modification();

-- Trigger pour calculer automatiquement les totaux du bilan initial
CREATE OR REPLACE FUNCTION update_bilan_initial_totals()
RETURNS TRIGGER AS $$
DECLARE
    total_valeur NUMERIC(18,2);
    count_elements INTEGER;
BEGIN
    CASE TG_OP
        WHEN 'INSERT', 'UPDATE' THEN
            -- Calculer le total et le nombre d'éléments
            SELECT 
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM bilan_initial_lignes
            WHERE bilan_initial_id = NEW.bilan_initial_id;
            
        WHEN 'DELETE' THEN
            -- Récalculer après suppression
            SELECT 
                COALESCE(SUM(valeur_totale), 0),
                COUNT(*)
            INTO total_valeur, count_elements
            FROM bilan_initial_lignes
            WHERE bilan_initial_id = OLD.bilan_initial_id;
    END CASE;
    
    -- Mettre à jour le bilan principal
    UPDATE bilan_initial
    SET 
        valeur_totale_stocks = total_valeur,
        nombre_elements = count_elements
    WHERE id = (
        CASE WHEN TG_OP = 'DELETE' THEN OLD.bilan_initial_id ELSE NEW.bilan_initial_id END
    );
    
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_bilan_initial_totals
    AFTER INSERT OR UPDATE OR DELETE ON bilan_initial_lignes
    FOR EACH ROW EXECUTE FUNCTION update_bilan_initial_totals();
```

## 4. API Backend

### 4.1 Initialisation des stocks de carburant

#### POST /api/initialisation/stocks-carburant
**Description:** Initialiser les stocks de carburant pour une cuve

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "cuve_id": "uuid",
  "quantite_initiale": "decimal (max 18,3)",
  "date_initialisation": "date (format YYYY-MM-DD)",
  "observation": "string (max 255)",
  "analyse_qualite": {
    "densite": "decimal (max 8,4)",
    "indice_octane": "integer",
    "soufre_ppm": "decimal (max 10,2)",
    "type_additif": "string (max 100)",
    "commentaire_qualite": "string",
    "resultat_qualite": "Conforme|Non conforme|En attente"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "cuve_id": "uuid",
    "carburant_id": "uuid",
    "quantite_initiale": "decimal",
    "date_initialisation": "date",
    "observation": "string",
    "analyse_qualite": {
      "densite": "decimal",
      "indice_octane": "integer",
      "soufre_ppm": "decimal",
      "type_additif": "string",
      "commentaire_qualite": "string",
      "resultat_qualite": "string"
    },
    "compagnie_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Stock de carburant initialisé avec succès"
}
```

**HTTP Status Codes:**
- 201: Initialisation créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Cuve non trouvée
- 409: Stock initial déjà existant pour cette cuve

#### POST /api/initialisation/index-pistolets
**Description:** Initialiser les index des pistolets

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "pistolet_id": "uuid",
  "valeur_index": "decimal (max 18,3)",
  "date_initialisation": "date (format YYYY-MM-DD)",
  "observation": "string (max 255)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "pistolet_id": "uuid",
    "valeur_index": "decimal",
    "date_initialisation": "date",
    "observation": "string",
    "compagnie_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Index du pistolet initialisé avec succès"
}
```

**HTTP Status Codes:**
- 201: Initialisation créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Pistolet non trouvé
- 409: Index initial déjà existant pour ce pistolet

#### POST /api/initialisation/stocks-boutique
**Description:** Initialiser les stocks de produits de boutique

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "article_id": "uuid",
  "station_id": "uuid",
  "quantite_initiale": "decimal (max 18,3)",
  "prix_unitaire": "decimal (max 18,4)",
  "date_initialisation": "date (format YYYY-MM-DD)",
  "observation": "string (max 255)",
  "cout_logistique": {
    "transport": "decimal (max 18,2)",
    "stockage": "decimal (max 18,2)",
    "assurance": "decimal (max 18,2)",
    "autres": "decimal (max 18,2)"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "article_id": "uuid",
    "station_id": "uuid",
    "quantite_initiale": "decimal",
    "prix_unitaire": "decimal",
    "montant_initial": "decimal",
    "date_initialisation": "date",
    "observation": "string",
    "cout_logistique": {
      "transport": "decimal",
      "stockage": "decimal",
      "assurance": "decimal",
      "autres": "decimal",
      "total": "decimal"
    },
    "compagnie_id": "uuid",
    "created_at": "datetime"
  },
  "message": "Stock de boutique initialisé avec succès"
}
```

**HTTP Status Codes:**
- 201: Initialisation créée avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 404: Article ou station non trouvé
- 409: Stock initial déjà existant pour cet article

#### POST /api/initialisation/bilan-initial
**Description:** Créer un bilan initial global

**Headers:**
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body:**
```json
{
  "date_bilan": "date (format YYYY-MM-DD)",
  "commentaire": "string (max 255)",
  "elements_initialisation": [
    {
      "type_element": "carburant|article_boutique",
      "element_id": "uuid",
      "quantite": "decimal (max 18,3)",
      "prix_unitaire": "decimal (max 18,4)",
      "taux_tva": "decimal (max 5,2)",
      "description": "string"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "compagnie_id": "uuid",
    "date_bilan": "date",
    "commentaire": "string",
    "valeur_totale_stocks": "decimal",
    "nombre_elements": 0,
    "statut": "string",
    "elements": [
      {
        "id": "uuid",
        "type_element": "string",
        "element_id": "uuid",
        "description_element": "string",
        "quantite": "decimal",
        "unite_mesure": "string",
        "prix_unitaire": "decimal",
        "valeur_totale": "decimal",
        "taux_tva": "decimal",
        "montant_tva": "decimal",
        "montant_ht": "decimal"
      }
    ],
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "message": "Bilan initial créé avec succès"
}
```

**HTTP Status Codes:**
- 201: Bilan initial créé avec succès
- 400: Données invalides
- 401: Non autorisé
- 403: Accès refusé
- 409: Bilan initial déjà existant pour cette date

## 5. Logique Métier

### 5.1 Validation des données

**Processus de validation :**
1. Vérification de l'existence des entités référencées (cuve, article, station)
2. Vérification que la quantité n'est pas négative
3. Vérification que le prix unitaire n'est pas négatif
4. Vérification que la date d'initialisation n'est pas dans le futur
5. Vérification que l'utilisateur appartient à la même compagnie que les objets manipulés
6. Vérification qu'il n'existe pas déjà un stock initial pour cet élément
7. Pour les cuves, vérification que la quantité n'excède pas la capacité maximale
8. Validation des analyses de qualité selon les normes applicables

### 5.2 Calculs automatiques

**Calculs effectués automatiquement :**
1. Valeur totale du stock initial (quantité × prix unitaire)
2. Total des coûts logistiques
3. Montant TVA pour le bilan initial
4. Montant HT pour le bilan initial
5. Historique automatique des mouvements
6. Génération automatique des écritures comptables

### 5.3 Génération d'écritures comptables

**Processus :**
1. Après l'initialisation d'un stock, génération automatique d'écritures comptables
2. Lier aux comptes appropriés dans le plan comptable
3. Création d'une entrée dans `journal_entries` avec le type "Ouverture"
4. Création des lignes correspondantes dans `journal_lines`
5. Liaison avec le bilan initial via `bilan_initial_id`

### 5.4 Contraintes d'intégrité

**Contraintes à respecter :**
- Un stock initial ne peut être modifié une fois validé
- La quantité initiale ne doit pas dépasser la capacité de la cuve
- Les indices de qualité doivent être dans les plages acceptables
- L'utilisateur doit avoir les permissions appropriées
- Les données doivent être cohérentes entre elles

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)

```
compagnies ||--o{ stocks : "possède"
cuves ||--o{ stocks : "contient"
articles ||--o{ stocks : "affecté à"
stations ||--o{ stocks : "localisé à"

stocks ||--o{ stocks_mouvements : "génère"
fournisseurs ||--o{ couts_logistique_stocks_initial : "associe"
articles ||--o{ couts_logistique_stocks_initial : "affecté à"
cuves ||--o{ qualite_carburant_initial : "concerne"
bilan_initial ||--o{ bilan_initial_lignes : "composé de"
utilisateurs ||--o{ qualite_carburant_initial : "analyse"
```

### 6.2 Diagramme de séquence - Initialisation d'un stock de carburant

```
Gestionnaire -> Serveur: POST /api/initialisation/stocks-carburant
Serveur -> Serveur: Valider les permissions
Serveur -> DB: Charger les informations de la cuve
DB -> Serveur: Retourner les détails de la cuve
Serveur -> Serveur: Valider la quantité par rapport à la capacité
Serveur -> Serveur: Calculer la valeur totale
Serveur -> DB: Créer l'entrée dans stocks avec est_initial = TRUE
DB -> Serveur: Retourner l'entrée créée
Serveur -> DB: Créer une écriture comptable dans journal_entries
Serveur -> DB: Créer une ligne dans journal_lines
Serveur -> DB: Enregistrer dans l'historique des mouvements
Serveur -> DB: Enregistrer l'analyse de qualité si fournie
Serveur -> Gestionnaire: Retourner le stock initialisé
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Validation des données d'entrée pour chaque type d'initialisation
- Méthodes de calcul des totaux et valeurs
- Méthodes de vérification d'unicité
- Méthodes de génération des écritures comptables
- Méthodes de traitement des analyses de qualité

### 7.2 Tests d'intégration
- Cycle complet d'initialisation de stocks
- Génération automatique des écritures comptables
- Cohérence entre les différentes tables de stock
- Contraintes d'intégrité
- Contrôles d'accès selon la compagnie

### 7.3 Tests de charge/performance
- Performance des requêtes d'initialisation avec de grandes quantités
- Impact des écritures comptables automatiques
- Performance des recherches d'initialisation
- Tests de synchronisation si plusieurs utilisateurs initialisent en même temps

### 7.4 Jeux de données de test
```sql
-- Données de test pour l'initialisation des stocks

-- Créer une cuve de test
INSERT INTO cuves (
    id, station_id, code, capacite, carburant_id, compagnie_id, statut
)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM stations WHERE compagnie_id = (SELECT id FROM compagnies LIMIT 1) LIMIT 1),
    'CUV001',
    10000.000,
    (SELECT id FROM carburants LIMIT 1),
    (SELECT id FROM compagnies LIMIT 1),
    'Actif'
LIMIT 1;

-- Créer un article de test
INSERT INTO articles (
    id, code, libelle, famille_id, compagnie_id, type_article, prix_achat, prix_vente
)
SELECT 
    gen_random_uuid(),
    'ART001',
    'Huile moteur 10W40',
    (SELECT id FROM familles_articles LIMIT 1),
    (SELECT id FROM compagnies LIMIT 1),
    'produit',
    5000.0000,
    6500.0000
LIMIT 1;

-- Données pour test d'initialisation de stock de carburant
INSERT INTO stocks (
    id, cuve_id, station_id, stock_theorique, stock_reel, prix_unitaire, compagnie_id, est_initial
)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM cuves WHERE code = 'CUV001' LIMIT 1),
    (SELECT station_id FROM cuves WHERE code = 'CUV001' LIMIT 1),
    8000.000,
    8000.000,
    3500.0000,
    (SELECT id FROM compagnies LIMIT 1),
    true
LIMIT 1;

-- Données pour test d'initialisation de stock de boutique
INSERT INTO stocks (
    id, article_id, station_id, stock_theorique, stock_reel, prix_unitaire, compagnie_id, est_initial
)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM articles WHERE code = 'ART001' LIMIT 1),
    (SELECT station_id FROM cuves LIMIT 1),
    100.000,
    100.000,
    5000.0000,
    (SELECT id FROM compagnies LIMIT 1),
    true
LIMIT 1;
```

## 8. Checklist Développeur

### Tâches techniques détaillées

**Phase 1 - Initialisation des stocks de carburant (jours 1-2)**
- [ ] Créer les services de gestion des stocks initiaux de carburant
- [ ] Implémenter les validations de quantité par rapport à la capacité
- [ ] Créer les endpoints API pour les stocks initiaux de carburant
- [ ] Implémenter l'analyse de qualité du carburant
- [ ] Générer les écritures comptables automatiques
- [ ] Tester la cohérence des données
- [ ] Créer les tests unitaires

**Phase 2 - Initialisation des index de pistolets (jour 3)**
- [ ] Créer les services de gestion des index initiaux de pistolets
- [ ] Créer les endpoints API pour les index initiaux
- [ ] Assurer la cohérence avec les cuves et stocks
- [ ] Tester les validations des index
- [ ] Créer les tests unitaires

**Phase 3 - Initialisation des stocks de boutique (jours 4-5)**
- [ ] Créer les services de gestion des stocks initiaux de boutique
- [ ] Implémenter le calcul de valorisation
- [ ] Créer les endpoints API pour les stocks initiaux de boutique
- [ ] Implémenter l'analyse des coûts logistiques
- [ ] Générer les écritures comptables automatiques
- [ ] Tester la gestion des différentes unités de mesure
- [ ] Créer les tests unitaires

**Phase 4 - Bilan initial et intégration (jours 6-7)**
- [ ] Créer le service de bilan initial global
- [ ] Implémenter l'agrégation des différents types de stocks
- [ ] Créer les endpoints API pour le bilan initial
- [ ] Intégrer la génération automatique des écritures comptables
- [ ] Tester l'intégration complète
- [ ] Documenter les API
- [ ] Créer les tests d'intégration

**Phase 5 - Tests et validation (jour 8)**
- [ ] Exécuter les tests unitaires
- [ ] Exécuter les tests d'intégration
- [ ] Tester les scénarios d'erreur
- [ ] Valider la sécurité des données
- [ ] Valider les contrôles d'accès
- [ ] Finaliser la documentation

### Ordre recommandé
1. Commencer par les stocks de carburant (fonctionnalité la plus critique)
2. Puis les index de pistolets (liés aux carburants)
3. Ensuite les stocks de boutique
4. Enfin l'assemblage dans un bilan initial global

### Livrables attendus
- [ ] Services d'initialisation des stocks
- [ ] Endpoints API complets
- [ ] Validation des données
- [ ] Génération automatique des écritures comptables
- [ ] Contrôles d'accès
- [ ] Tests unitaires et d'intégration
- [ ] Documentation API
- [ ] Jeux de données de test

## 9. Risques & Points de vigilance

### Points sensibles
- Validité des quantités par rapport aux capacités physiques
- Génération correcte des écritures comptables
- Cohérence des dates d'initialisation
- Gestion des unités de mesure
- Sécurité des données d'initialisation

### Risques techniques
- Risque d'incohérence entre stocks et comptabilité
- Risque de performance avec de grandes quantités
- Risque d'erreurs dans la génération des écritures comptables
- Risque de contournement des contrôles d'accès
- Risque de perte de données sans sauvegarde adéquate

### Dette technique potentielle
- Mise en place d'un système de workflow pour la validation des stocks initiaux
- Centralisation de la gestion des validations dans un framework dédié
- Mise en place d'un système d'audit plus détaillé
- Intégration avec des systèmes de contrôle physique
- Automatisation des contrôles de cohérence