# Technical Specification - Module de Rapports (Mis à Jour)

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de générer les rapports comptables et de gestion de la station-service SuccessFuel. L'objectif est de fournir aux gestionnaires et comptables un ensemble d'outils de reporting complets pour surveiller la performance financière et opérationnelle de leur station-service, conformément aux normes comptables locales (OHADA) et aux besoins de gestion opérationnelle.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module de reporting complet permettant :
- De générer les états financiers comptables (bilan, compte de résultat, grand livre, balance, journal)
- De produire des rapports de gestion opérationnelle
- De suivre les indicateurs clés de performance (KPIs)
- De faire des déclarations fiscales et de suivre la conformité
- D'analyser les tendances et de faire des prévisions

### Nouvelle règle de permissions
Avec la mise à jour des règles de permissions, le **gérant de compagnie** aura automatiquement accès à toutes les fonctionnalités de ce module pour sa propre compagnie, mais ne pourra consulter des rapports que pour les données appartenant à sa compagnie.

### Définition du périmètre
Le périmètre inclut :
- Génération des rapports comptables (bilan, grand livre, balance, journal)
- Génération des déclarations fiscales
- Suivi de la conformité
- Analyse de la consommation et du rendement des pompistes/caissiers
- Analyse des stocks, dettes/créances et rentabilité
- Calcul des indicateurs KPIs
- Prévisions et analyse des tendances
- Analyse comparative entre différentes périodes
- Export des rapports dans différents formats
- Contrôle des accès aux rapports sensibles
- Planification des rapports réguliers

## 2. User Stories & Critères d'acceptation

### US-REP-001: En tant que comptable, je veux générer un bilan
- **Critères d'acceptation :**
  - Pouvoir générer un bilan à une date donnée
  - Afficher les postes d'actif et de passif de manière structurée
  - Calculer automatiquement les soldes des comptes
  - Vérifier l'équilibre entre actif et passif
  - Exporter le bilan dans différents formats (PDF, Excel)
  - Seuls les utilisateurs avec les permissions appropriées peuvent générer le bilan
  - Les gérants de compagnie peuvent générer le bilan pour leur compagnie

### US-REP-002: En tant que gestionnaire, je veux analyser les performances opérationnelles
- **Critères d'acceptation :**
  - Calculer les indicateurs de performance (KPIs)
  - Comparer les performances entre différentes périodes
  - Analyser le rendement des employés (pompistes, caissiers)
  - Afficher les tendances de vente
  - Générer des rapports comparatifs
  - Les gérants de compagnie peuvent accéder à toutes les analyses de performance pour leur compagnie

### US-REP-003: En tant que gestionnaire, je veux produire des rapports de trésorerie
- **Critères d'acceptation :**
  - Générer des états de trésorerie
  - Afficher les flux d'entrée et de sortie
  - Analyser les écarts de caisse
  - Suivre les soldes des différentes caisses
  - Comparer les soldes théoriques et réels
  - Les gérants de compagnie peuvent produire tous les rapports de trésorerie pour leur compagnie

### US-REP-004: En tant que gestionnaire, je veux analyser les stocks
- **Critères d'acceptation :**
  - Générer des rapports d'inventaire
  - Suivre l'évolution des niveaux de stock
  - Identifier les produits en rupture ou en surstock
  - Analyser les coûts de possession
  - Calculer les indicateurs de rotation des stocks
  - Les gérants de compagnie peuvent accéder à toutes les analyses de stock pour leur compagnie

### US-REP-005: En tant que gestionnaire, je veux planifier des rapports réguliers
- **Critères d'acceptation :**
  - Planifier la génération automatique de rapports
  - Définir la fréquence de génération (quotidienne, hebdomadaire, mensuelle)
  - Configurer l'envoi automatique des rapports
  - Gérer les alertes basées sur les indicateurs
  - Les gérants de compagnie peuvent planifier des rapports pour leur compagnie

## 3. Contrôles d'Accès & Permissions

### Accès aux fonctionnalités
- **Super Administrateur** : Accès complet à toutes les opérations de reporting dans le système
- **Administrateur** : Accès selon les permissions spécifiques définies
- **Gérant de Compagnie** : Accès complet à toutes les opérations de reporting pour sa propre compagnie
- **Utilisateur de Compagnie** : Accès limité selon ses permissions spécifiques

### Contrôle des données
- Tous les rapports sont filtrés selon la compagnie de l'utilisateur
- Les gérants de compagnie ne peuvent consulter que les données appartenant à leur propre compagnie
- Le système garantit que les utilisateurs n'accèdent qu'aux données pour lesquelles ils ont l'autorisation
- Les rapports croisés entre compagnies sont limités aux utilisateurs avec permissions étendues

## 4. Modèle de Données

### 4.1 Tables à créer/modifier

#### Table: rapports_financiers
```sql
CREATE TABLE rapports_financiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_rapport VARCHAR(50) NOT NULL, -- 'bilan', 'compte_resultat', 'grand_livre', 'balance', 'journal', 'tva', 'etat_tva'
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    contenu JSONB, -- Contenu du rapport au format JSON
    format_sortie VARCHAR(20) DEFAULT 'PDF', -- PDF, Excel, CSV, etc.
    statut VARCHAR(20) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Termine', 'Erreur', 'Archive')),
    utilisateur_generateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    fichier_joint TEXT, -- Lien ou nom du fichier de rapport généré
    commentaire TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_rapports_financiers_type ON rapports_financiers(type_rapport);
CREATE INDEX idx_rapports_financiers_periode ON rapports_financiers(periode_debut, periode_fin);
CREATE INDEX idx_rapports_financiers_utilisateur ON rapports_financiers(utilisateur_generateur_id);
CREATE INDEX idx_rapports_financiers_compagnie ON rapports_financiers(compagnie_id);
CREATE INDEX idx_rapports_financiers_station ON rapports_financiers(station_id);
CREATE INDEX idx_rapports_financiers_date ON rapports_financiers(created_at);
CREATE INDEX idx_rapports_financiers_statut ON rapports_financiers(statut);
```

#### Table: historique_rapports
```sql
CREATE TABLE historique_rapports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom_rapport VARCHAR(100) NOT NULL, -- Nom du rapport (ex: "Bilan mensuel")
    type_rapport VARCHAR(50) NOT NULL, -- Type de rapport
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    utilisateur_demandeur_id UUID REFERENCES utilisateurs(id),
    utilisateur_generation_id UUID REFERENCES utilisateurs(id),
    statut VARCHAR(20) DEFAULT 'Demande' CHECK (statut IN ('Demande', 'En cours', 'Termine', 'Erreur', 'Archive')),
    parametres JSONB, -- Paramètres utilisés pour la génération
    resultat_generation TEXT, -- Résultat de la génération (succès/erreur)
    date_demande TIMESTAMPTZ DEFAULT now(),
    date_generation TIMESTAMPTZ,
    date_consultation TIMESTAMPTZ,
    est_a_jour BOOLEAN DEFAULT FALSE,
    compagnie_id UUID REFERENCES compagnies(id),
    station_id UUID REFERENCES stations(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_rapports_type ON historique_rapports(type_rapport);
CREATE INDEX idx_historique_rapports_periode ON historique_rapports(periode_debut, periode_fin);
CREATE INDEX idx_historique_rapports_demandeur ON historique_rapports(utilisateur_demandeur_id);
CREATE INDEX idx_historique_rapports_generation ON historique_rapports(utilisateur_generation_id);
CREATE INDEX idx_historique_rapports_date ON historique_rapports(created_at);
CREATE INDEX idx_historique_rapports_a_jour ON historique_rapports(est_a_jour);
```

### 4.2 Relations
- `rapports_financiers.utilisateur_generateur_id` → `utilisateurs.id` (One-to-Many)
- `rapports_financiers.compagnie_id` → `compagnies.id` (One-to-Many)
- `rapports_financiers.station_id` → `stations.id` (One-to-Many)
- `historique_rapports.utilisateur_demandeur_id` → `utilisateurs.id` (One-to-Many)
- `historique_rapports.utilisateur_generation_id` → `utilisateurs.id` (One-to-Many)
- `historique_rapports.compagnie_id` → `compagnies.id` (One-to-Many)
- `historique_rapports.station_id` → `stations.id` (One-to-Many)

### 4.3 Triggers et règles d'intégrité
```sql
-- Trigger pour vérifier que la période de fin est postérieure à la période de début
CREATE OR REPLACE FUNCTION verifier_periode_rapport()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.periode_fin < NEW.periode_debut THEN
        RAISE EXCEPTION 'La période de fin (%s) doit être postérieure à la période de début (%s)', NEW.periode_fin, NEW.periode_debut;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger pour la table rapports_financiers
CREATE TRIGGER trigger_verifier_periode_rapport
    BEFORE INSERT OR UPDATE ON rapports_financiers
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();

-- Création du trigger pour la table historique_rapports
CREATE TRIGGER trigger_verifier_periode_historique
    BEFORE INSERT OR UPDATE ON historique_rapports
    FOR EACH ROW
    EXECUTE FUNCTION verifier_periode_rapport();
```

### 4.4 Contrôles de Sécurité et Permissions
Afin de s'assurer que les nouvelles règles de permissions sont respectées, les tables critiques (rapports_financiers, historique_rapports) incluent un champ `compagnie_id` pour garantir que chaque utilisateur n'accède qu'aux données de sa propre compagnie. Les requêtes devront filtrer systématiquement selon ce champ pour respecter les nouvelles règles de permissions.

- Les gérants de compagnie auront un accès complet aux données appartenant à leur propre compagnie
- Les super administrateurs auront un accès global à toutes les données
- Les administrateurs et utilisateurs auront un accès limité selon leurs permissions spécifiques

## 5. Dépendances avec d'autres modules

### Module comptable
- Les rapports comptables sont générés à partir des données comptables
- Les états financiers utilisent les soldes des comptes

### Module des ventes
- Les rapports de performance utilisent les données de ventes
- Les analyses de rendement sont basées sur les ventes par employé

### Module des stocks
- Les rapports d'inventaire sont basés sur les mouvements de stock
- Les analyses de rotation utilisent les données de stock

### Module de trésorerie
- Les rapports de trésorerie sont générés à partir des mouvements
- Les analyses de caisse proviennent du module de trésorerie

## 6. Tests & Validation

### Tests de validation des permissions
- Vérifier que les gérants de compagnie ont accès à toutes les fonctionnalités de reporting pour leur compagnie
- S'assurer que les utilisateurs ne peuvent pas accéder aux données d'autres compagnies
- Tester que les rapports ne contiennent que les données autorisées

### Tests de sécurité
- Valider que les contrôles d'accès empêchent les accès non autorisés
- Vérifier que les données sont correctement filtrées selon la compagnie
- S'assurer que les exports de rapports respectent les contrôles d'accès