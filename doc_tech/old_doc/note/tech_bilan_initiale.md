# Technical Specification - Bilan initial

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
  - Pouvoir saisir les montants pour chaque poste d'actif
  - Pouvoir affecter les montants aux comptes comptables correspondants
  - Pouvoir justifier et commenter chaque poste
  - Le système doit conserver l'historique des saisies
  - Les montants saisis doivent respecter les règles de cohérence comptable

### US-BI-002: En tant que gestionnaire, je veux initialiser les postes de passif du bilan
- **Critères d'acceptation :**
  - Pouvoir saisir les montants pour chaque poste de passif
  - Pouvoir affecter les montants aux comptes comptables correspondants
  - Pouvoir distinguer les capitaux propres des dettes
  - Pouvoir spécifier les échéances pour les emprunts
  - Le système doit contrôler la cohérence avec les actifs

### US-BI-003: En tant que gestionnaire, je veux initialiser les stocks de départ
- **Critères d'acceptation :**
  - Pouvoir saisir les stocks de carburant par cuve
  - Pouvoir saisir les stocks de produits boutique
  - Pouvoir spécifier les prix unitaires d'achat
  - Le système doit rattacher les stocks aux articles/carburants existants
  - Pouvoir inclure les stocks initiaux dans la comptabilité

### US-BI-004: En tant que gestionnaire, je veux enregistrer les immobilisations existantes
- **Critères d'acceptation :**
  - Pouvoir saisir les informations sur les immobilisations existantes
  - Pouvoir spécifier la valeur d'acquisition et la valeur nette comptable
  - Pouvoir affecter les immobilisations aux comptes appropriés
  - Pouvoir tenir compte des amortissements déjà pratiqués
  - Le système doit permettre de continuer l'amortissement

### US-BI-005: En tant que gestionnaire, je veux enregistrer les créances clients et dettes fournisseurs
- **Critères d'acceptation :**
  - Pouvoir saisir les montants dus par chaque client
  - Pouvoir saisir les montants dus à chaque fournisseur
  - Pouvoir rattacher ces montants aux tiers existants dans le système
  - Pouvoir spécifier les échéances pour les opérations à crédit
  - Le système doit intégrer ces montants dans la comptabilité

### US-BI-006: En tant que gestionnaire, je veux valider et verrouiller le bilan initial
- **Critères d'acceptation :**
  - Pouvoir vérifier la cohérence du bilan (actifs = passifs)
  - Pouvoir valider le bilan après vérification
  - Le système doit empêcher les modifications après validation
  - Le système doit permettre d'annuler la validation si nécessaire
  - Un historique des validations doit être conservé

### US-BI-007: En tant que gestionnaire, je veux disposer d'une analyse comparative
- **Critères d'acceptation :**
  - Pouvoir consulter le bilan initial
  - Pouvoir comparer avec l'état actuel
  - Pouvoir visualiser les mouvements depuis l'initialisation
  - Pouvoir exporter les données pour analyse
  - Le système doit fournir des indicateurs de performance

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: bilan_initial
```sql
CREATE TABLE bilan_initial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compagnie_id UUID REFERENCES compagnies(id),
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
CREATE INDEX idx_bilan_initial_date ON bilan_initial(date_bilan_initial);
CREATE INDEX idx_bilan_initial_utilisateur ON bilan_initial(utilisateur_id);
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
```

### 3.2 Index recommandés
```sql
-- Index sur la table bilan_initial
CREATE INDEX idx_bilan_initial_date ON bilan_initial(date_bilan_initial);
CREATE INDEX idx_bilan_initial_validation ON bilan_initial(est_valide, est_verifie);

-- Index sur les tables de détail
CREATE INDEX idx_bilan_initial_lignes_montant ON bilan_initial_lignes(montant_initial);
CREATE INDEX idx_stocks_bilan_initial_valeur ON stocks_bilan_initial(valeur_totale);
CREATE INDEX idx_creances_dettes_bilan_initial_montant ON creances_dettes_bilan_initial(montant_initial);
```

### 3.3 Triggers et règles d'intégrité
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

## 4. API Backend

### 4.1 Endpoints pour le bilan initial

#### POST /api/bilan-initial
- **Description:** Créer un nouveau bilan initial
- **Payload:**
```json
{
  "date_bilan_initial": "2023-01-01",
  "description": "Bilan initial de la station-service X",
  "commentaire": "Saisie des données au 1er janvier 2023"
}
```
- **Réponse:**
```json
{
  "id": "uuid-v4",
  "compagnie_id": "uuid-v4",
  "date_bilan_initial": "2023-01-01",
  "utilisateur_id": "uuid-v4",
  "description": "Bilan initial de la station-service X",
  "est_valide": false,
  "est_verifie": false,
  "commentaire": "Saisie des données au 1er janvier 2023",
  "created_at": "2023-01-01T10:00:00Z",
  "updated_at": "2023-01-01T10:00:00Z"
}
```
- **Codes d'erreur:**
  - 400: Données invalides
  - 401: Non autorisé
  - 403: Accès refusé
  - 409: Bilan initial déjà existant pour cette date

#### GET /api/bilan-initial/{id}
- **Description:** Récupérer un bilan initial spécifique avec ses détails
- **Réponse:**
```json
{
  "id": "uuid-v4",
  "date_bilan_initial": "2023-01-01",
  "description": "Bilan initial de la station-service X",
  "est_valide": false,
  "est_verifie": false,
  "commentaire": "Saisie des données au 1er janvier 2023",
  "lignes": [
    {
      "id": "uuid-v4",
      "compte_numero": "100000",
      "compte_libelle": "Capital Social",
      "montant_initial": 100000000,
      "type_solde": "credit",
      "poste_bilan": "capitaux_propres",
      "categorie_detaillee": "capital"
    }
  ],
  "immobilisations": [
    {
      "id": "uuid-v4",
      "code": "IMMO001",
      "libelle": "Station de lavage",
      "valeur_acquisition": 5000000,
      "valeur_nette_comptable": 3000000
    }
  ],
  "stocks": [
    {
      "id": "uuid-v4",
      "type_stock": "carburant",
      "carburant_libelle": "Super",
      "quantite": 10000,
      "prix_unitaire": 3200,
      "valeur_totale": 32000000
    }
  ],
  "creances_dettes": [
    {
      "id": "uuid-v4",
      "type_tiers": "client",
      "tiers_nom": "Entreprise A",
      "montant_initial": 1500000,
      "devise": "MGA"
    }
  ]
}
```

#### PUT /api/bilan-initial/{id}
- **Description:** Mettre à jour un bilan initial (avant validation)
- **Payload:** Même structure que POST mais avec l'ID
- **Codes d'erreur:**
  - 400: Données invalides ou bilan déjà validé
  - 404: Bilan non trouvé

#### POST /api/bilan-initial/{id}/valider
- **Description:** Valider le bilan initial
- **Réponse:**
```json
{
  "message": "Bilan initial validé avec succès",
  "bilan_initial": {
    "id": "uuid-v4",
    "est_valide": true,
    "date_validation": "2023-01-01T15:30:00Z"
  }
}
```
- **Codes d'erreur:**
  - 400: Bilan non équilibré
  - 403: Accès refusé pour la validation
  - 404: Bilan non trouvé

#### GET /api/bilan-initial/{id}/analyse-comparative
- **Description:** Obtenir une analyse comparative entre le bilan initial et l'état actuel
- **Réponse:**
```json
{
  "bilan_initial": {...},
  "etat_actuel": {...},
  "evolutions": {
    "actifs": {
      "montant_initial": 200000000,
      "montant_actuel": 250000000,
      "variation": 50000000
    },
    "passifs": {
      "montant_initial": 100000000,
      "montant_actuel": 80000000,
      "variation": -20000000
    },
    "capitaux_propres": {
      "montant_initial": 100000000,
      "montant_actuel": 170000000,
      "variation": 70000000
    }
  }
}
```

### 4.2 Endpoints pour les lignes du bilan initial

#### POST /api/bilan-initial/{id}/lignes
- **Description:** Ajouter une ligne au bilan initial
- **Payload:**
```json
{
  "compte_numero": "218000",
  "montant_initial": 50000000,
  "type_solde": "debit",
  "poste_bilan": "actif",
  "categorie_detaillee": "immobilisations"
}
```

#### GET /api/bilan-initial/{id}/lignes
- **Description:** Récupérer toutes les lignes du bilan initial
- **Réponse:** Liste des lignes du bilan

### 4.3 Endpoints pour les immobilisations du bilan initial

#### POST /api/bilan-initial/{id}/immobilisations
- **Description:** Ajouter une immobilisation au bilan initial
- **Payload:**
```json
{
  "code": "IMMO002",
  "libelle": "Pompe à essence",
  "categorie": "matériel",
  "date_achat": "2020-06-15",
  "valeur_acquisition": 15000000,
  "valeur_nette_comptable": 9000000,
  "amortissement_cumule": 6000000,
  "duree_amortissement": 5,
  "date_fin_amortissement": "2025-06-15",
  "observation": "Fonctionne correctement"
}
```

### 4.4 Endpoints pour les stocks du bilan initial

#### POST /api/bilan-initial/{id}/stocks
- **Description:** Ajouter un stock initial
- **Payload:**
```json
{
  "type_stock": "carburant",
  "carburant_id": "uuid-v4",
  "cuve_id": "uuid-v4",
  "quantite": 15000,
  "prix_unitaire": 3150,
  "commentaire": "Stock vérifié physiquement"
}
```

### 4.5 Endpoints pour les créances et dettes du bilan initial

#### POST /api/bilan-initial/{id}/creances-dettes
- **Description:** Ajouter une créance ou dette initiale
- **Payload:**
```json
{
  "type_tiers": "fournisseur",
  "tiers_id": "uuid-v4",
  "montant_initial": 8000000,
  "devise": "MGA",
  "date_echeance": "2023-03-01",
  "reference_piece": "FA-2023-001",
  "commentaire": "Facture non encore réglée"
}
```

## 5. Logique Métier

### 5.1 Règles de validation du bilan initial
1. Le total des postes d'actif doit être égal au total des postes de passif plus les capitaux propres
2. Chaque ligne du bilan doit être affectée à un compte comptable existant
3. Le bilan initial ne peut être modifié une fois validé
4. Le bilan initial doit avoir une date qui précède ou égale la date d'activation du système
5. Les valeurs saisies doivent être positives (sauf pour les soldes créditeurs)

### 5.2 Workflows
1. **Création du bilan initial:**
   - L'utilisateur crée un bilan initial avec une date
   - L'utilisateur ajoute les lignes de bilan (actifs, passifs, capitaux propres)
   - L'utilisateur ajoute les immobilisations existantes
   - L'utilisateur ajoute les stocks initiaux
   - L'utilisateur ajoute les créances et dettes existantes

2. **Validation du bilan initial:**
   - Vérification de l'équilibre du bilan (actifs = passifs + capitaux propres)
   - Vérification de la justesse des montants et des comptes associés
   - Vérification que le bilan n'a pas déjà été validé
   - Verrouillage du bilan après validation

3. **Analyse comparative:**
   - Récupération des valeurs initiales du bilan
   - Récupération des valeurs actuelles des postes concernés
   - Calcul des écarts et des évolutions
   - Affichage des résultats dans un format compréhensible

### 5.3 Cas particuliers
1. Le système doit permettre l'ajout de corrections mineures (écarts inférieurs à un seuil défini) si le bilan n'est pas parfaitement équilibré
2. Si le bilan initial a déjà été saisi pour une période, le système doit empêcher sa modification
3. Lors de l'initialisation, le système doit permettre de rattacher les stocks aux articles/carburants existants dans le système
4. Le système doit gérer les devises multiples si nécessaire

### 5.4 Restrictions
1. Seuls les utilisateurs avec les droits appropriés peuvent valider le bilan initial
2. Le bilan initial ne peut pas être supprimé après validation
3. Les montants doivent être justifiés par des pièces comptables
4. Le bilan initial ne peut pas contenir de comptes qui n'existent pas dans le plan comptable

### 5.5 Impacts sur d'autres modules
1. Le module de comptabilité utilisera les soldes initiaux pour les calculs
2. Le module de stocks prendra en compte les stocks initiaux comme point de départ
3. Le module de trésorerie intégrera les liquidités initiales
4. Les états financiers utiliseront les données du bilan initial comme base de comparaison

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
bilan_initial (1) -- (N) bilan_initial_lignes
bilan_initial (1) -- (N) immobilisations_bilan_initial
bilan_initial (1) -- (N) stocks_bilan_initial
bilan_initial (1) -- (N) creances_dettes_bilan_initial

bilan_initial_lignes -- plan_comptable (N) -- (1)
stocks_bilan_initial -- articles (N) -- (1)
stocks_bilan_initial -- carburants (N) -- (1)
stocks_bilan_initial -- cuves (N) -- (1)
creances_dettes_bilan_initial -- (N) clients/fournisseurs (1)
```

### 6.2 Diagramme de séquence (textuel)
```
Utilisateur -> API: Créer bilan initial
API -> DB: Enregistrer bilan initial
API -> Utilisateur: Retour ID du bilan

Utilisateur -> API: Ajouter lignes bilan
API -> DB: Enregistrer lignes
API -> Trigger: Vérifier cohérence
TRIGGER -> API: Erreur ou succès

Utilisateur -> API: Ajouter immobilisations
API -> DB: Enregistrer immobilisations
API -> Utilisateur: Confirmation

Utilisateur -> API: Ajouter stocks
API -> DB: Enregistrer stocks
API -> Utilisateur: Confirmation

Utilisateur -> API: Ajouter créances/dettes
API -> DB: Enregistrer créances/dettes
API -> Utilisateur: Confirmation

Utilisateur -> API: Valider bilan
API -> DB: Vérifier équilibre
DB -> API: Bilan équilibré
API -> DB: Mettre à jour statut
API -> Utilisateur: Bilan validé
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test de création d'un bilan initial avec des données valides
- Test de création d'un bilan initial avec des données invalides
- Test de validation d'un bilan équilibré
- Test de validation d'un bilan non équilibré (doit échouer)
- Test de l'ajout de lignes au bilan initial
- Test des triggers de cohérence

### 7.2 Tests d'intégration
- Test du workflow complet de création et validation du bilan
- Test de l'analyse comparative avec des données existantes
- Test de l'impact sur les modules de comptabilité et de stocks
- Test de la sécurité d'accès et des permissions

### 7.3 Tests de charge/performance
- Test de performance pour la validation d'un bilan avec de nombreuses lignes
- Test de concurrence si plusieurs utilisateurs essaient de modifier le même bilan
- Test de performance pour l'affichage de l'analyse comparative

### 7.4 Jeux de données de test
```sql
-- Données de test pour un bilan initial équilibré
BEGIN;

INSERT INTO bilan_initial (compagnie_id, date_bilan_initial, description) 
VALUES ('company-uuid', '2023-01-01', 'Bilan initial de test');

INSERT INTO bilan_initial_lignes (bilan_initial_id, compte_numero, montant_initial, type_solde, poste_bilan) 
VALUES 
  -- Actifs
  ('bilan-uuid', '218000', 50000000, 'debit', 'actif'),  -- Matériel et outillage
  ('bilan-uuid', '370000', 20000000, 'debit', 'actif'),  -- Stocks
  ('bilan-uuid', '530000', 10000000, 'debit', 'actif'),  -- Banque
  -- Passifs
  ('bilan-uuid', '401000', 30000000, 'credit', 'passif'), -- Fournisseurs
  -- Capitaux propres
  ('bilan-uuid', '100000', 50000000, 'credit', 'capitaux_propres'); -- Capital Social

COMMIT;
```

## 8. Checklist Développeur

### 8.1 Tâches techniques
- [ ] Créer les modèles de données (bilan_initial, bilan_initial_lignes, etc.)
- [ ] Implémenter les endpoints API REST
- [ ] Créer les vues pour l'interface utilisateur
- [ ] Implémenter les validations côté serveur
- [ ] Mettre en place les triggers de vérification de cohérence
- [ ] Créer les tests unitaires et d'intégration
- [ ] Implémenter la logique de validation du bilan
- [ ] Créer l'interface pour la saisie des données
- [ ] Implémenter l'analyse comparative
- [ ] Gérer les permissions d'accès aux fonctionnalités
- [ ] Implémenter la journalisation des actions
- [ ] Documenter les endpoints API

### 8.2 Ordre recommandé
1. Créer les modèles de données
2. Implémenter la logique de base (CRUD)
3. Mettre en place les validations
4. Créer les endpoints API
5. Implémenter les triggers de cohérence
6. Développer les interfaces utilisateur
7. Créer les tests
8. Intégrer avec les modules existants
9. Documenter le module

### 8.3 Livrables attendus
- [ ] Fichiers de migration de la base de données
- [ ] Modèles de données
- [ ] Endpoints API
- [ ] Interface utilisateur pour la gestion du bilan initial
- [ ] Tests unitaires et d'intégration
- [ ] Documentation technique
- [ ] Documentation utilisateur

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La validation du bilan initial est critique car elle définit l'état initial du système
- La vérification de l'équilibre du bilan est essentielle pour la fiabilité des états financiers
- La gestion des droits d'accès à la validation est cruciale pour la sécurité des données

### 9.2 Risques techniques
- Risque de performance si le bilan initial contient de nombreuses lignes
- Risque d'incohérence si les données du bilan initial ne correspondent pas à la réalité
- Risque de perte de données si le bilan est mal initialisé
- Risque de sécurité si des utilisateurs non autorisés accèdent aux fonctionnalités de validation

### 9.3 Dette technique potentielle
- La complexité du système de vérification de cohérence pourrait devenir difficile à maintenir
- L'intégration avec les modules existants pourrait nécessiter des ajustements fréquents
- La gestion des différentes structures de bilan selon les pays pourrait complexifier le système