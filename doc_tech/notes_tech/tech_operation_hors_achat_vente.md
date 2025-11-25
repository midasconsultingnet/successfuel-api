# Technical Specification - Opérations hors achat vente

## 1. Contexte & Objectif du Sprint

### Description métier
Ce sprint vise à implémenter les fonctionnalités permettant de gérer toutes les opérations qui ne relèvent ni des achats, ni des ventes dans le système SuccessFuel. Cela inclut la gestion des dépenses opérationnelles, des immobilisations, des ajustements de stock, des déclarations fiscales, des assurances, des contrats de maintenance, des programmes de fidélisation, et autres opérations périphériques mais essentielles à la gestion d'une station-service.

### Problème à résoudre
Actuellement, le système SuccessFuel ne dispose pas d'un module complet pour gérer les opérations périphériques qui ne sont ni des achats ni des ventes, ce qui pose problème car :
- Les dépenses opérationnelles ne sont pas correctement enregistrées
- Les immobilisations ne sont pas suivies de façon structurée
- Les ajustements de stock sont mal gérés
- Les déclarations fiscales doivent être faites en dehors du système
- Les assurances et contrats de maintenance ne sont pas suivis
- Les programmes de fidélisation ne sont pas intégrés
- L'analyse commerciale et les prévisions de demande ne sont pas disponibles

### Définition du périmètre
Le périmètre inclut :
- Gestion des dépenses opérationnelles
- Gestion des immobilisations et de leur amortissement
- Gestion des ajustements de stock (entrées/sorties non liées à achats/ventes)
- Gestion des déclarations fiscales
- Gestion des assurances
- Gestion des contrats de maintenance
- Gestion des services annexes
- Gestion des programmes de fidélisation
- Gestion des cartes de carburant
- Gestion des contrats clients
- Gestion de la qualité du carburant
- Gestion des coûts logistique
- Gestion des validations hiérarchiques
- Gestion du contrôle interne
- Gestion des incidents de sécurité
- Gestion du suivi de conformité
- Gestion des analyses commerciales
- Gestion des prévisions de demande
- Historique des actions utilisateurs

## 2. User Stories & Critères d'acceptation

### US-HORS-ACH-VENTE-001: En tant que gestionnaire, je veux gérer les dépenses opérationnelles
- **Critères d'acceptation :**
  - Pouvoir saisir les dépenses courantes de la station
  - Pouvoir associer les dépenses à des catégories spécifiques
  - Pouvoir rattacher les dépenses à des fournisseurs existants
  - Pouvoir spécifier les modes de paiement
  - Le système doit enregistrer les dépenses dans la trésorerie
  - Les dépenses doivent générer des écritures comptables

### US-HORS-ACH-VENTE-002: En tant que gestionnaire, je veux gérer les immobilisations
- **Critères d'acceptation :**
  - Pouvoir enregistrer les immobilisations de la station
  - Pouvoir spécifier la catégorie, la valeur d'acquisition et la durée d'amortissement
  - Pouvoir suivre l'amortissement en cours
  - Pouvoir gérer les mouvements d'immobilisations (cession, mise hors service, etc.)
  - Le système doit générer automatiquement les écritures comptables
  - Le système doit calculer la valeur nette comptable

### US-HORS-ACH-VENTE-003: En tant que gestionnaire, je veux gérer les ajustements de stock
- **Critères d'acceptation :**
  - Pouvoir effectuer des ajustements de stock pour perte, casse, péremption
  - Pouvoir spécifier le motif de l'ajustement
  - Le système doit mettre à jour les stocks théoriques
  - Le système doit générer des écritures comptables
  - Les ajustements doivent être tracés dans l'historique
  - Le système doit permettre d'expliquer les écarts constatés

### US-HORS-ACH-VENTE-004: En tant que gestionnaire, je veux gérer les déclarations fiscales
- **Critères d'acceptation :**
  - Pouvoir générer les déclarations fiscales (TVA, etc.) depuis le système
  - Pouvoir vérifier les montants déclarés
  - Pouvoir suivre les dates de dépôt et le statut
  - Pouvoir exporter les déclarations dans les formats requis
  - Le système doit se conformer à la réglementation en vigueur

### US-HORS-ACH-VENTE-005: En tant que gestionnaire, je veux gérer les assurances
- **Critères d'acceptation :**
  - Pouvoir enregistrer les polices d'assurance de la station
  - Pouvoir suivre les dates d'échéance
  - Pouvoir gérer les montants de couverture
  - Pouvoir joindre des documents relatifs aux assurances
  - Le système doit envoyer des alertes avant les échéances

### US-HORS-ACH-VENTE-006: En tant que gestionnaire, je veux gérer les contrats de maintenance
- **Critères d'acceptation :**
  - Pouvoir enregistrer les contrats de maintenance des équipements
  - Pouvoir spécifier la fréquence de maintenance
  - Pouvoir suivre les prochaines interventions
  - Pouvoir gérer les coûts liés aux contrats
  - Le système doit envoyer des rappels de maintenance

### US-HORS-ACH-VENTE-007: En tant que gestionnaire, je veux gérer les services annexes
- **Critères d'acceptation :**
  - Pouvoir enregistrer les services annexes proposés à la station
  - Pouvoir spécifier les prix et modalités des services
  - Pouvoir rattacher les services aux ventes
  - Le système doit gérer la facturation des services
  - Les services doivent être intégrés dans les analyses

### US-HORS-ACH-VENTE-008: En tant que gestionnaire, je veux gérer les programmes de fidélisation
- **Critères d'acceptation :**
  - Pouvoir créer et gérer des programmes de fidélisation
  - Pouvoir définir les règles d'activation (points, réductions, etc.)
  - Pouvoir suivre les participations des clients
  - Le système doit intégrer les avantages dans les ventes
  - Pouvoir suivre l'efficacité des programmes

### US-HORS-ACH-VENTE-009: En tant que gestionnaire, je veux gérer les cartes de carburant
- **Critères d'acceptation :**
  - Pouvoir créer, activer, bloquer des cartes de carburant
  - Pouvoir rattacher les cartes à des clients spécifiques
  - Pouvoir gérer les plafonds de consommation
  - Pouvoir suivre l'utilisation des cartes
  - Pouvoir bloquer ou remplacer les cartes perdues

### US-HORS-ACH-VENTE-010: En tant que gestionnaire, je veux gérer les contrats clients
- **Critères d'acceptation :**
  - Pouvoir enregistrer les contrats clients (ravitaillement, services)
  - Pouvoir spécifier les volumes garantis et les prix contractuels
  - Pouvoir suivre la fréquence des livraisons
  - Pouvoir gérer les statuts des contrats
  - Le système doit envoyer des rappels pour les contrats expirants

### US-HORS-ACH-VENTE-011: En tant que gestionnaire, je veux gérer la qualité du carburant
- **Critères d'acceptation :**
  - Pouvoir enregistrer les contrôles de qualité du carburant
  - Pouvoir spécifier les paramètres contrôlés (densité, octane, etc.)
  - Pouvoir associer les résultats du contrôle à chaque cuve
  - Le système doit permettre de classer les contrôles comme conformes/non conformes
  - Les observations doivent être conservées dans l'historique

### US-HORS-ACH-VENTE-012: En tant que gestionnaire, je veux gérer les coûts logistique
- **Critères d'acceptation :**
  - Pouvoir associer les coûts logistique à des opérations spécifiques
  - Pouvoir distinguer les différents types de coûts (transport, stockage, etc.)
  - Le système doit calculer les coûts totaux par période
  - Pouvoir analyser les coûts par fournisseur ou type de carburant
  - Les coûts doivent être intégrés dans les analyses

## 3. Modèle de Données

### 3.1 Tables à créer/modifier

#### Table: depenses
```sql
CREATE TABLE depenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    categorie VARCHAR(100) NOT NULL,
    libelle TEXT NOT NULL,
    montant NUMERIC(18,2) NOT NULL CHECK (montant >= 0),
    date_depense DATE NOT NULL,
    mode_paiement VARCHAR(50),
    tresorerie_id UUID REFERENCES tresoreries(id),
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    projet TEXT,
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Payee', 'Annulee')) NOT NULL,
    reference_piece VARCHAR(100),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_depenses_compagnie ON depenses(compagnie_id);
CREATE INDEX idx_depenses_date ON depenses(date_depense);
CREATE INDEX idx_depenses_tresorerie ON depenses(tresorerie_id);
CREATE INDEX idx_depenses_fournisseur ON depenses(fournisseur_id);
```

#### Table: immobilisations
```sql
CREATE TABLE immobilisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    categorie VARCHAR(100) NOT NULL, -- Ex: véhicule, matériel, etc.
    date_achat DATE NOT NULL,
    valeur_acquisition NUMERIC(18,2) NOT NULL,
    valeur_nette_comptable NUMERIC(18,2) NOT NULL,
    amortissement_annuel NUMERIC(18,2) DEFAULT 0,
    duree_amortissement INTEGER DEFAULT 0, -- En années
    date_fin_amortissement DATE,
    fournisseur_id UUID REFERENCES fournisseurs(id) ON DELETE SET NULL,
    tresorerie_id UUID REFERENCES tresoreries(id), -- Pour le paiement
    utilisateur_achat_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Cede', 'Hors service', 'Vendu')) NOT NULL,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_immobilisations_compagnie ON immobilisations(compagnie_id);
CREATE INDEX idx_immobilisations_code ON immobilisations(code);
CREATE INDEX idx_immobilisations_categorie ON immobilisations(categorie);
CREATE INDEX idx_immobilisations_date_achat ON immobilisations(date_achat);
```

#### Table: mouvements_immobilisations
```sql
CREATE TABLE mouvements_immobilisations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    immobilisation_id UUID REFERENCES immobilisations(id) ON DELETE CASCADE,
    type_mouvement VARCHAR(20) NOT NULL CHECK (type_mouvement IN ('Achat', 'Amortissement', 'Cession', 'Hors service', 'Vente')),
    date_mouvement DATE NOT NULL,
    valeur_mouvement NUMERIC(18,2) NOT NULL,
    commentaire TEXT,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_mvt_immobilisations_immobilisation ON mouvements_immobilisations(immobilisation_id);
CREATE INDEX idx_mvt_immobilisations_compagnie ON mouvements_immobilisations(compagnie_id);
CREATE INDEX idx_mvt_immobilisations_date ON mouvements_immobilisations(date_mouvement);
```

#### Table: ajustements_stock
```sql
CREATE TABLE ajustements_stock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    cuve_id UUID REFERENCES cuves(id) ON DELETE CASCADE, -- Pour les carburants
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    type_ajustement VARCHAR(20) NOT NULL CHECK (type_ajustement IN ('Entree', 'Sortie', 'Perte', 'Casse', 'Peremption')),
    quantite NUMERIC(18,3) NOT NULL, -- Positive pour entrée, négative pour sortie
    motif TEXT NOT NULL,
    utilisateur_id UUID REFERENCES utilisateurs(id),
    date_ajustement DATE NOT NULL,
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_ajustements_stock_article ON ajustements_stock(article_id);
CREATE INDEX idx_ajustements_stock_cuve ON ajustements_stock(cuve_id);
CREATE INDEX idx_ajustements_stock_station ON ajustements_stock(station_id);
CREATE INDEX idx_ajustements_stock_compagnie ON ajustements_stock(compagnie_id);
CREATE INDEX idx_ajustements_stock_date ON ajustements_stock(date_ajustement);
```

#### Table: declarations_fiscales
```sql
CREATE TABLE declarations_fiscales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_declaration VARCHAR(50) NOT NULL, -- TVA, autres taxes
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    montant_total NUMERIC(18,2) NOT NULL,
    montant_declare NUMERIC(18,2) NOT NULL,
    ecart NUMERIC(18,2) GENERATED ALWAYS AS (montant_declare - montant_total) STORED,
    date_depot DATE,
    statut VARCHAR(20) DEFAULT 'En attente' CHECK (statut IN ('En attente', 'Soumis', 'Traite', 'Retour')),
    fichier_joint TEXT, -- Lien ou nom du fichier de déclaration
    utilisateur_depose_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_declarations_fiscales_compagnie ON declarations_fiscales(compagnie_id);
CREATE INDEX idx_declarations_fiscales_type ON declarations_fiscales(type_declaration);
CREATE INDEX idx_declarations_fiscales_periode ON declarations_fiscales(periode_debut, periode_fin);
```

#### Table: assurances
```sql
CREATE TABLE assurances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_assurance VARCHAR(50) NOT NULL, -- responsabilité civile, incendie, vol, etc.
    compagnie_assurance VARCHAR(100) NOT NULL,
    numero_police VARCHAR(50) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    montant_couverture NUMERIC(18,2) NOT NULL,
    prime_annuelle NUMERIC(18,2) NOT NULL,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    fichier_joint TEXT, -- Lien ou nom du fichier de police
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_assurances_compagnie ON assurances(compagnie_id);
CREATE INDEX idx_assurances_station ON assurances(station_id);
CREATE INDEX idx_assurances_numero_police ON assurances(numero_police);
CREATE INDEX idx_assurances_date_fin ON assurances(date_fin);
```

#### Table: contrats_maintenance
```sql
CREATE TABLE contrats_maintenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    type_contrat VARCHAR(50) NOT NULL, -- pompe, cuve, caisse, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    cout_mensuel NUMERIC(18,2) NOT NULL,
    frequence INT, -- En mois
    prochaine_intervention DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé')),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_contrats_maintenance_compagnie ON contrats_maintenance(compagnie_id);
CREATE INDEX idx_contrats_maintenance_station ON contrats_maintenance(station_id);
CREATE INDEX idx_contrats_maintenance_fournisseur ON contrats_maintenance(fournisseur_id);
CREATE INDEX idx_contrats_maintenance_date_fin ON contrats_maintenance(date_fin);
```

#### Table: services_annexes
```sql
CREATE TABLE services_annexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_service VARCHAR(50) NOT NULL, -- lavage, atelier, restaurant
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    prix_unitaire NUMERIC(18,2) NOT NULL,
    unite_mesure VARCHAR(20) DEFAULT 'Unité',
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Supprimé')),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_services_annexes_compagnie ON services_annexes(compagnie_id);
CREATE INDEX idx_services_annexes_station ON services_annexes(station_id);
CREATE INDEX idx_services_annexes_type ON services_annexes(type_service);
```

#### Table: programme_fidelite
```sql
CREATE TABLE programme_fidelite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    type_programme VARCHAR(50) NOT NULL, -- points, réduction, etc.
    seuil_activation NUMERIC(18,2) DEFAULT 0, -- Montant/quantité requis
    benefice TEXT, -- Description du bénéfice
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif', 'Expiré')),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_programme_fidelite_compagnie ON programme_fidelite(compagnie_id);
CREATE INDEX idx_programme_fidelite_statut ON programme_fidelite(statut);
CREATE INDEX idx_programme_fidelite_date_fin ON programme_fidelite(date_fin);
```

#### Table: cartes_carburant
```sql
CREATE TABLE cartes_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    numero_carte VARCHAR(50) UNIQUE NOT NULL,
    date_activation DATE NOT NULL,
    date_expiration DATE,
    solde_carte NUMERIC(18,2) DEFAULT 0,
    plafond_mensuel NUMERIC(18,2), -- NULL pour illimité
    statut VARCHAR(20) DEFAULT 'Active' CHECK (statut IN ('Active', 'Inactive', 'Bloquee', 'Perdue', 'Remplacee')),
    utilisateur_creation_id UUID REFERENCES utilisateurs(id),
    utilisateur_blocage_id UUID REFERENCES utilisateurs(id), -- Qui a bloqué la carte
    motif_blocage TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_cartes_carburant_compagnie ON cartes_carburant(compagnie_id);
CREATE INDEX idx_cartes_carburant_client ON cartes_carburant(client_id);
CREATE INDEX idx_cartes_carburant_numero_carte ON cartes_carburant(numero_carte);
CREATE INDEX idx_cartes_carburant_date_expiration ON cartes_carburant(date_expiration);
CREATE INDEX idx_cartes_carburant_statut ON cartes_carburant(statut);
```

#### Table: contrats_clients
```sql
CREATE TABLE contrats_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    type_contrat VARCHAR(50) NOT NULL, -- ravitaillement, stationnement, etc.
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    volume_garanti NUMERIC(18,3), -- En litres
    prix_contractuel NUMERIC(18,4), -- Prix convenu
    frequence_livraison INTEGER, -- En jours
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Expiré', 'Annulé', 'Suspendu')),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_contrats_clients_compagnie ON contrats_clients(compagnie_id);
CREATE INDEX idx_contrats_clients_client ON contrats_clients(client_id);
CREATE INDEX idx_contrats_clients_date_fin ON contrats_clients(date_fin);
CREATE INDEX idx_contrats_clients_statut ON contrats_clients(statut);
```

#### Table: qualite_carburant
```sql
CREATE TABLE qualite_carburant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    cuve_id UUID REFERENCES cuves(id),
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    type_controle VARCHAR(50) NOT NULL, -- densité, octane, etc.
    valeur_relevee VARCHAR(50), -- Valeur mesurée
    valeur_standard VARCHAR(50), -- Valeur attendue
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme')),
    observation TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_qualite_carburant_compagnie ON qualite_carburant(compagnie_id);
CREATE INDEX idx_qualite_carburant_carburant ON qualite_carburant(carburant_id);
CREATE INDEX idx_qualite_carburant_cuve ON qualite_carburant(cuve_id);
CREATE INDEX idx_qualite_carburant_date ON qualite_carburant(date_controle);
```

#### Table: couts_logistique
```sql
CREATE TABLE couts_logistique (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_cout VARCHAR(50) NOT NULL, -- transport, stockage, assurance, etc.
    description TEXT,
    montant NUMERIC(18,2) NOT NULL,
    date_cout DATE NOT NULL,
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    fournisseur_id UUID REFERENCES fournisseurs(id),
    utilisateur_saisie_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_couts_logistique_compagnie ON couts_logistique(compagnie_id);
CREATE INDEX idx_couts_logistique_station ON couts_logistique(station_id);
CREATE INDEX idx_couts_logistique_carburant ON couts_logistique(carburant_id);
CREATE INDEX idx_couts_logistique_fournisseur ON couts_logistique(fournisseur_id);
CREATE INDEX idx_couts_logistique_date ON couts_logistique(date_cout);
```

#### Table: validations_hierarchiques
```sql
CREATE TABLE validations_hierarchiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(50) NOT NULL,  -- Ex: 'annulation_vente', 'modification_stock'
    seuil_montant NUMERIC(18,2),         -- Montant à partir duquel validation est requise
    niveau_validation INTEGER DEFAULT 1, -- Niveau hiérarchique requis pour validation
    profil_autorise_id UUID REFERENCES profils(id), -- Profil autorisé à valider
    statut VARCHAR(20) DEFAULT 'Actif' CHECK (statut IN ('Actif', 'Inactif'))
);

-- Index pour les performances
CREATE INDEX idx_validations_hierarchiques_operation_type ON validations_hierarchiques(operation_type);
CREATE INDEX idx_validations_hierarchiques_profil ON validations_hierarchiques(profil_autorise_id);
```

#### Table: controle_interne
```sql
CREATE TABLE controle_interne (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_controle VARCHAR(50) NOT NULL, -- controle_caisse, controle_stock, etc.
    element_controle VARCHAR(100), -- Numéro de caisse, cuve, etc.
    date_controle DATE NOT NULL,
    utilisateur_controle_id UUID REFERENCES utilisateurs(id),
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Anomalie', 'Non applicable')),
    montant_ecart NUMERIC(18,2) DEFAULT 0, -- Ecart constaté
    commentaire TEXT,
    statut VARCHAR(20) DEFAULT 'Terminé' CHECK (statut IN ('Planifié', 'En cours', 'Terminé', 'En attente')),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_controle_interne_compagnie ON controle_interne(compagnie_id);
CREATE INDEX idx_controle_interne_date ON controle_interne(date_controle);
CREATE INDEX idx_controle_interne_type ON controle_interne(type_controle);
```

#### Table: incidents_securite
```sql
CREATE TABLE incidents_securite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_incident VARCHAR(50) NOT NULL CHECK (type_incident IN ('Fuite', 'Accident', 'Vol', 'Intrusion', 'Autre')),
    date_incident TIMESTAMPTZ NOT NULL,
    description TEXT NOT NULL,
    gravite INTEGER CHECK (gravite BETWEEN 1 AND 5), -- 1 = mineur, 5 = majeur
    statut VARCHAR(20) DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert', 'En cours', 'Résolu', 'Fermé')),
    utilisateur_declare_id UUID REFERENCES utilisateurs(id),
    utilisateur_traite_id UUID REFERENCES utilisateurs(id),
    action_corrective TEXT,
    date_resolution TIMESTAMPTZ,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_incidents_securite_compagnie ON incidents_securite(compagnie_id);
CREATE INDEX idx_incidents_securite_station ON incidents_securite(station_id);
CREATE INDEX idx_incidents_securite_date ON incidents_securite(date_incident);
CREATE INDEX idx_incidents_securite_type ON incidents_securite(type_incident);
```

#### Table: suivi_conformite
```sql
CREATE TABLE suivi_conformite (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_norme VARCHAR(50) NOT NULL, -- sécurité, qualité, fiscalité
    libelle VARCHAR(100) NOT NULL,
    description TEXT,
    date_prevue DATE NOT NULL,
    date_realisee DATE,
    resultat VARCHAR(20) CHECK (resultat IN ('Conforme', 'Non conforme', 'En attente', 'Non applicable')),
    responsable_id UUID REFERENCES utilisateurs(id),
    observation TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_suivi_conformite_compagnie ON suivi_conformite(compagnie_id);
CREATE INDEX idx_suivi_conformite_date_prevue ON suivi_conformite(date_prevue);
CREATE INDEX idx_suivi_conformite_type_norme ON suivi_conformite(type_norme);
```

#### Table: analyse_commerciale
```sql
CREATE TABLE analyse_commerciale (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    type_analyse VARCHAR(50) NOT NULL, -- tendance_vente, comportement_client, etc.
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    resultat JSONB, -- Données d'analyse au format JSON
    commentaire TEXT,
    utilisateur_analyse_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_analyse_commerciale_compagnie ON analyse_commerciale(compagnie_id);
CREATE INDEX idx_analyse_commerciale_station ON analyse_commerciale(station_id);
CREATE INDEX idx_analyse_commerciale_periode ON analyse_commerciale(periode_debut, periode_fin);
```

#### Table: prevision_demande
```sql
CREATE TABLE prevision_demande (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carburant_id UUID REFERENCES carburants(id),
    station_id UUID REFERENCES stations(id),
    date_prevision DATE NOT NULL,
    quantite_prevue NUMERIC(18,3) NOT NULL, -- En litres
    methode_prevision VARCHAR(50) NOT NULL, -- historique, saisonnalité, etc.
    confiance_prevision NUMERIC(5,2) CHECK (confiance_prevision BETWEEN 0 AND 100),
    commentaire TEXT,
    utilisateur_prevision_id UUID REFERENCES utilisateurs(id),
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_prevision_demande_compagnie ON prevision_demande(compagnie_id);
CREATE INDEX idx_prevision_demande_station ON prevision_demande(station_id);
CREATE INDEX idx_prevision_demande_carburant ON prevision_demande(carburant_id);
CREATE INDEX idx_prevision_demande_date ON prevision_demande(date_prevision);
```

#### Table: historique_actions_utilisateurs
```sql
CREATE TABLE historique_actions_utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    action VARCHAR(100) NOT NULL,       -- Ex: 'creation_vente', 'modification_stock'
    module VARCHAR(50) NOT NULL,        -- Ex: 'ventes', 'stocks'
    sous_module VARCHAR(50),            -- Ex: 'carburant', 'boutique'
    objet_id UUID,                      -- ID de l'objet affecté
    donnees_avant JSONB,                -- Données avant modification
    donnees_apres JSONB,                -- Données après modification
    ip_utilisateur VARCHAR(45),
    poste_utilisateur VARCHAR(100),
    session_id VARCHAR(100),
    statut_action VARCHAR(20) DEFAULT 'Reussie' CHECK (statut_action IN ('Reussie', 'Echouee', 'Bloquee')),
    commentaire TEXT,
    compagnie_id UUID REFERENCES compagnies(id), -- Référence corrigée
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour les performances
CREATE INDEX idx_historique_actions_compagnie ON historique_actions_utilisateurs(compagnie_id);
CREATE INDEX idx_historique_actions_utilisateur ON historique_actions_utilisateurs(utilisateur_id);
CREATE INDEX idx_historique_actions_module ON historique_actions_utilisateurs(module);
CREATE INDEX idx_historique_actions_action ON historique_actions_utilisateurs(action);
```

## 4. API Backend

### 4.1 Gestion des dépenses
- **POST** `/api/depenses` - Créer une dépense
  - Payload: `{categorie, libelle, montant, date_depense, mode_paiement, tresorerie_id, fournisseur_id, projet, reference_piece}`
  - Réponse: `{id, ...donnees_depense}`

- **GET** `/api/depenses` - Lister les dépenses
  - Paramètres: `?date_debut&date_fin&categorie&statut&compagnie_id`
  - Réponse: `[{id, libelle, montant, date_depense, statut}, ...]`

- **GET** `/api/depenses/{id}` - Consulter une dépense
  - Réponse: `{id, ...toutes_les_donnees_de_depense}`

- **PUT** `/api/depenses/{id}` - Modifier une dépense
  - Payload: `{categorie, libelle, montant, date_depense, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

- **DELETE** `/api/depenses/{id}` - Supprimer une dépense
  - Réponse: `{success: true}`

### 4.2 Gestion des immobilisations
- **POST** `/api/immobilisations` - Créer une immobilisation
  - Payload: `{code, libelle, categorie, date_achat, valeur_acquisition, duree_amortissement, fournisseur_id, tresorerie_id, observation}`
  - Réponse: `{id, ...donnees_immobilisation}`

- **GET** `/api/immobilisations` - Lister les immobilisations
  - Paramètres: `?categorie&statut&date_achat&compagnie_id`
  - Réponse: `[{id, code, libelle, categorie, valeur_nette_comptable, statut}, ...]`

- **GET** `/api/immobilisations/{id}` - Consulter une immobilisation
  - Réponse: `{id, ...toutes_les_donnees_immobilisation}`

- **PUT** `/api/immobilisations/{id}` - Modifier une immobilisation
  - Payload: `{libelle, categorie, observation, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

- **DELETE** `/api/immobilisations/{id}` - Supprimer une immobilisation
  - Réponse: `{success: true}`

### 4.3 Gestion des ajustements de stock
- **POST** `/api/ajustements-stock` - Créer un ajustement de stock
  - Payload: `{article_id, cuve_id, station_id, type_ajustement, quantite, motif, commentaire}`
  - Réponse: `{id, ...donnees_ajustement}`

- **GET** `/api/ajustements-stock` - Lister les ajustements de stock
  - Paramètres: `?date_debut&date_fin&type_ajustement&station_id&compagnie_id`
  - Réponse: `[{id, type_ajustement, quantite, motif, date_ajustement}, ...]`

- **GET** `/api/ajustements-stock/{id}` - Consulter un ajustement de stock
  - Réponse: `{id, ...toutes_les_donnees_ajustement}`

### 4.4 Gestion des déclarations fiscales
- **POST** `/api/declarations-fiscales` - Créer une déclaration fiscale
  - Payload: `{type_declaration, periode_debut, periode_fin, montant_declare, fichier_joint}`
  - Réponse: `{id, ...donnees_declaration}`

- **GET** `/api/declarations-fiscales` - Lister les déclarations fiscales
  - Paramètres: `?type&periode_debut&periode_fin&statut&compagnie_id`
  - Réponse: `[{id, type_declaration, periode_debut, periode_fin, montant_declare, statut}, ...]`

- **PUT** `/api/declarations-fiscales/{id}/depot` - Déposer une déclaration
  - Payload: `{date_depot}`
  - Réponse: `{id, statut, date_depot}`

### 4.5 Gestion des assurances
- **POST** `/api/assurances` - Créer une assurance
  - Payload: `{station_id, type_assurance, compagnie_assurance, numero_police, date_debut, date_fin, montant_couverture, prime_annuelle, fichier_joint}`
  - Réponse: `{id, ...donnees_assurance}`

- **GET** `/api/assurances` - Lister les assurances
  - Paramètres: `?type&date_fin&statut&compagnie_id`
  - Réponse: `[{id, numero_police, type_assurance, date_fin, statut}, ...]`

- **PUT** `/api/assurances/{id}` - Modifier une assurance
  - Payload: `{date_fin, fichier_joint, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

### 4.6 Gestion des contrats de maintenance
- **POST** `/api/contrats-maintenance` - Créer un contrat de maintenance
  - Payload: `{station_id, fournisseur_id, type_contrat, libelle, description, date_debut, date_fin, cout_mensuel, frequence}`
  - Réponse: `{id, ...donnees_contrat}`

- **GET** `/api/contrats-maintenance` - Lister les contrats de maintenance
  - Paramètres: `?type&date_fin&statut&compagnie_id`
  - Réponse: `[{id, libelle, type_contrat, date_fin, prochaine_intervention, statut}, ...]`

- **PUT** `/api/contrats-maintenance/{id}` - Modifier un contrat de maintenance
  - Payload: `{date_fin, prochaine_intervention, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

### 4.7 Gestion des services annexes
- **POST** `/api/services-annexes` - Créer un service annexe
  - Payload: `{station_id, type_service, libelle, description, prix_unitaire, unite_mesure}`
  - Réponse: `{id, ...donnees_service}`

- **GET** `/api/services-annexes` - Lister les services annexes
  - Paramètres: `?type&statut&compagnie_id`
  - Réponse: `[{id, libelle, type_service, prix_unitaire, statut}, ...]`

- **PUT** `/api/services-annexes/{id}` - Modifier un service annexe
  - Payload: `{prix_unitaire, statut, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

### 4.8 Gestion des programmes de fidélisation
- **POST** `/api/programmes-fidelite` - Créer un programme de fidélité
  - Payload: `{libelle, description, type_programme, seuil_activation, benefice, date_debut, date_fin}`
  - Réponse: `{id, ...donnees_programme}`

- **GET** `/api/programmes-fidelite` - Lister les programmes de fidélité
  - Paramètres: `?statut&compagnie_id`
  - Réponse: `[{id, libelle, type_programme, seuil_activation, statut}, ...]`

- **PUT** `/api/programmes-fidelite/{id}` - Modifier un programme de fidélité
  - Payload: `{statut, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

### 4.9 Gestion des cartes de carburant
- **POST** `/api/cartes-carburant` - Créer une carte de carburant
  - Payload: `{client_id, numero_carte, date_activation, date_expiration, plafond_mensuel}`
  - Réponse: `{id, ...donnees_carte}`

- **GET** `/api/cartes-carburant` - Lister les cartes de carburant
  - Paramètres: `?statut&client_id&compagnie_id`
  - Réponse: `[{id, numero_carte, date_expiration, solde_carte, statut}, ...]`

- **PUT** `/api/cartes-carburant/{id}/bloquer` - Bloquer une carte de carburant
  - Payload: `{motif_blocage}`
  - Réponse: `{id, statut, motif_blocage}`

### 4.10 Gestion des contrats clients
- **POST** `/api/contrats-clients` - Créer un contrat client
  - Payload: `{client_id, type_contrat, libelle, description, date_debut, date_fin, volume_garanti, prix_contractuel, frequence_livraison}`
  - Réponse: `{id, ...donnees_contrat}`

- **GET** `/api/contrats-clients` - Lister les contrats clients
  - Paramètres: `?type&statut&client_id&compagnie_id`
  - Réponse: `[{id, libelle, type_contrat, date_fin, volume_garanti, statut}, ...]`

- **PUT** `/api/contrats-clients/{id}` - Modifier un contrat client
  - Payload: `{statut, ...}`
  - Réponse: `{id, ...donnees_mises_a_jour}`

### 4.11 Gestion de la qualité du carburant
- **POST** `/api/qualite-carburant` - Enregistrer un contrôle de qualité
  - Payload: `{carburant_id, cuve_id, date_controle, type_controle, valeur_relevee, valeur_standard, resultat, observation}`
  - Réponse: `{id, ...donnees_controle}`

- **GET** `/api/qualite-carburant` - Lister les contrôles de qualité
  - Paramètres: `?carburant_id&date_debut&date_fin&resultat&compagnie_id`
  - Réponse: `[{id, type_controle, resultat, date_controle}, ...]`

### 4.12 Gestion des coûts logistique
- **POST** `/api/couts-logistique` - Enregistrer un coût logistique
  - Payload: `{type_cout, description, montant, date_cout, carburant_id, station_id, fournisseur_id}`
  - Réponse: `{id, ...donnees_cout}`

- **GET** `/api/couts-logistique` - Lister les coûts logistique
  - Paramètres: `?type&date_debut&date_fin&carburant_id&fournisseur_id&compagnie_id`
  - Réponse: `[{id, type_cout, montant, date_cout}, ...]`

### 4.13 Gestion du contrôle interne
- **POST** `/api/controle-interne` - Enregistrer un contrôle interne
  - Payload: `{type_controle, element_controle, date_controle, resultat, montant_ecart, commentaire}`
  - Réponse: `{id, ...donnees_controle}`

- **GET** `/api/controle-interne` - Lister les contrôles internes
  - Paramètres: `?type&date_debut&date_fin&resultat&compagnie_id`
  - Réponse: `[{id, type_controle, resultat, date_controle}, ...]`

## 5. Logique Métier

### 5.1 Règles de validation des dépenses
- Une dépense ne peut être enregistrée sans association à une trésorerie si le mode de paiement l'exige
- Le montant d'une dépense doit être strictement positif
- La date de la dépense ne peut être postérieure à la date du jour
- Une dépense en attente ne peut pas dépasser un seuil défini avant validation hiérarchique

### 5.2 Règles de gestion des immobilisations
- La valeur nette comptable d'une immobilisation ne peut pas être négative
- L'amortissement annuel est calculé comme valeur_acquisition / duree_amortissement
- Une immobilisation active ne peut pas être supprimée, seulement mise hors service
- Lors de la cession d'une immobilisation, le gain ou la perte est calculé comme différence entre le prix de cession et la valeur nette comptable

### 5.3 Règles de gestion des ajustements de stock
- Les ajustements de stock doivent avoir un motif valide
- Les ajustements importants (dépassant un seuil défini) nécessitent une validation hiérarchique
- Les ajustements affectent les stocks théoriques et génèrent des écritures comptables
- Les ajustements sont tracés avec l'utilisateur responsable

### 5.4 Règles de gestion des déclarations fiscales
- Les montants déclarés ne doivent pas différer excessivement des montants calculés dans le système
- Les déclarations fiscales doivent être conformes aux réglementations en vigueur
- Les dates de dépôt ne doivent pas dépasser les dates limites légales
- Les déclarations doivent pouvoir être exportées dans les formats requis par les autorités fiscales

### 5.5 Règles de gestion des assurances
- Les polices d'assurance doivent être renouvelées avant leur date d'expiration
- Les alertes sont envoyées automatiquement avant les échéances
- Les couvertures d'assurance doivent être adaptées aux besoins de la station
- Les documents d'assurance doivent être accessible dans le système

### 5.6 Règles de gestion des contrats de maintenance
- Les dates de prochaines interventions sont calculées automatiquement à partir de la fréquence
- Les alertes sont envoyées avant les dates de maintenance planifiées
- Les coûts de maintenance sont intégrés dans les analyses financières
- Les contrats en cours sont visibles dans les écrans de gestion

### 5.7 Règles de gestion des validations hiérarchiques
- Les opérations sensibles nécessitent une validation avant d'être exécutées
- Le niveau de validation dépend du montant ou du type de l'opération
- Les validations sont tracées avec l'utilisateur qui les effectue
- Les validations sont nécessaires pour des seuils définis dans les paramètres

### 5.8 Impacts sur d'autres modules
- Les dépenses affectent les soldes de trésorerie
- Les immobilisations affectent les écritures comptables et les états financiers
- Les ajustements de stock affectent les calculs de rentabilité
- Les cartes de carburant affectent les ventes de carburant
- Les contrats clients influencent les prévisions de vente

## 6. Diagrammes / Séquences

### 6.1 Schéma ERD (textuel)
```
compagnies ||--o{ stations : appartient
compagnies ||--o{ utilisateurs : appartient
stations ||--o{ depenses : station
stations ||--o{ immobilisations : station
stations ||--o{ assurances : station
stations ||--o{ contrats_maintenance : station
stations ||--o{ services_annexes : station
stations ||--o{ qualite_carburant : station
stations ||--o{ couts_logistique : station

utilisateurs ||--o{ depenses : utilisateur
utilisateurs ||--o{ immobilisations : utilisateur_achat
utilisateurs ||--o{ ajustements_stock : utilisateur
utilisateurs ||--o{ declarations_fiscales : utilisateur_depose
utilisateurs ||--o{ qualite_carburant : utilisateur_controle
utilisateurs ||--o{ couts_logistique : utilisateur_saisie

fournisseurs ||--o{ depenses : fournisseur
fournisseurs ||--o{ immobilisations : fournisseur
fournisseurs ||--o{ contrats_maintenance : fournisseur
fournisseurs ||--o{ couts_logistique : fournisseur

tresoreries ||--o{ depenses : tresorerie
tresoreries ||--o{ immobilisations : tresorerie

articles ||--o{ ajustements_stock : article
cuves ||--o{ ajustements_stock : cuve
cuves ||--o{ qualite_carburant : cuve

carburants ||--o{ qualite_carburant : carburant
carburants ||--o{ couts_logistique : carburant

clients ||--o{ cartes_carburant : client
clients ||--o{ contrats_clients : client

profils ||--o{ validations_hierarchiques : profil_autorise
```

### 6.2 Diagramme de séquence (textuel) - Enregistrement d'une dépense
```
Client -> API: POST /api/depenses
API -> Validations: Valider les données
Validations -> API: Données valides
API -> DepensesRepo: Créer la dépense
DepensesRepo -> DB: Insérer dans la table dépenses
DB -> DepensesRepo: Données insérées
DepensesRepo -> API: Dépense créée
API -> Journal: Générer écriture comptable
Journal -> API: Écriture générée
API -> Client: Retourner la dépense créée
```

## 7. Tests Requis

### 7.1 Tests unitaires
- Test des validations de dépenses (montant positif, date valide)
- Test des calculs d'amortissement des immobilisations
- Test des calculs de valeur nette comptable
- Test des validations de seuils pour les ajustements de stock
- Test des calculs d'écarts pour les déclarations fiscales
- Test des validations hiérarchiques

### 7.2 Tests d'intégration
- Test de l'ensemble du workflow de création d'une dépense
- Test de la génération automatique des écritures comptables
- Test de l'ensemble du workflow de gestion d'une immobilisation
- Test de la mise à jour des stocks suite à un ajustement
- Test de la création et du suivi d'une carte de carburant
- Test de la génération des déclarations fiscales

### 7.3 Tests de charge/performance
- Test de performance de chargement des listes de dépenses
- Test de performance de création massive de contrôles de qualité
- Test de performance de génération des déclarations fiscales
- Test de performance de recherche d'immobilisations

### 7.4 Jeux de données de test
- Jeu de données de test pour les dépenses avec différents montants, dates et types
- Jeu de données d'immobilisations avec différentes catégories et durées d'amortissement
- Jeu de données d'assurances avec différentes dates d'échéance
- Jeu de données de contrats de maintenance avec différents types et fréquences
- Jeu de données de cartes de carburant avec différents statuts

## 8. Checklist Développeur

### 8.1 Tâches techniques détaillées
- [ ] Création des modèles de données (dépenses, immobilisations, ajustements de stock, etc.)
- [ ] Création des endpoints API pour chaque fonctionnalité
- [ ] Implémentation des validations de données
- [ ] Génération automatique des écritures comptables
- [ ] Mise en place des validations hiérarchiques
- [ ] Création des interfaces utilisateur
- [ ] Gestion des permissions et des rôles
- [ ] Mise en place de la journalisation des actions
- [ ] Création des vues de reporting
- [ ] Mise en place des alertes et notifications
- [ ] Intégration avec les modules existants (stocks, trésorerie, comptabilité)

### 8.2 Ordre recommandé
1. Déploiement des modèles de base (dépenses, immobilisations)
2. Développement des endpoints d'API
3. Création des interfaces de base
4. Intégration avec les modules existants
5. Développement des fonctionnalités avancées (validations hiérarchiques, alertes)
6. Mise en place des tests
7. Documentation et déploiement

### 8.3 Livrables attendus
- [ ] Code source des nouvelles fonctionnalités
- [ ] Documentation technique des endpoints API
- [ ] Documentation utilisateur des nouvelles fonctionnalités
- [ ] Scripts de migration de base de données
- [ ] Jeux de tests unitaires et d'intégration
- [ ] Documentation des procédures d'exploitation

## 9. Risques & Points de vigilance

### 9.1 Points sensibles
- La gestion des validations hiérarchiques doit être robuste pour éviter les contournements
- Les calculs d'amortissement doivent être précis et conformes aux normes comptables
- La gestion des dates d'échéance pour les assurances et contrats nécessite une attention particulière
- La traçabilité des ajustements de stock doit être complète pour des raisons de contrôle interne

### 9.2 Risques techniques
- Risque de performances si les requêtes sur les dépenses et immobilisations ne sont pas correctement indexées
- Risque d'incohérence comptable si les écritures générées automatiquement sont incorrectes
- Risque de données incorrectes si les validations ne sont pas suffisamment strictes
- Risque de sécurité si les accès aux documents d'assurance ne sont pas correctement gérés

### 9.3 Dette technique potentielle
- Gestion des dates d'échéance dans les interfaces : solution temporaire avec alertes manuelles
- Calculs d'amortissement complexes : implémentation progressive des différents systèmes d'amortissement
- Intégration avec les modules existants : nécessitera des adaptations futures pour une meilleure intégration
- Gestion des documents joints : solution de stockage simple à améliorer avec un système de gestion documentaire plus évolué