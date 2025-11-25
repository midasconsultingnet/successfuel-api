## 🔰 1. Présentation générale du projet (mis à jour)
SuccessFuel est un ERP complet destiné à automatiser, centraliser et sécuriser la gestion des stations-service à Madagascar avec une architecture modulaire permettant son expansion en Afrique francophone.
Le système couvre la gestion opérationnelle, la comptabilité, les stocks, les achats, les ventes, les inventaires, les immobilisations, les trésoreries, les clients, les fournisseurs, les employés, les analyses de performances et les contrôles réglementaires.
Objectif : solution simple, adaptée au contexte malgache et extensible aux autres pays africains francophones, conforme aux exigences de contrôle de cuve et d'écoulement carburant.

## 🌍 MODULES SUPPLÉMENTAIRES POUR L'INTERNATIONALISATION (nouveau)

### 1. Gestion multi-pays
- Configuration des spécifications locales par pays
- Support des différentes législations fiscales
- Adaptation aux systèmes comptables locaux (OHADA, etc.)
- Gestion des devises multiples

### 2. Gestion des devises
- Support multi-devises pour transactions internationales
- Historique des taux de change
- Conversion automatique selon les taux en temps réel
- Rapports financiers dans la devise locale

### 3. Système de taxation modulaire
- Configuration des taux de taxes par pays
- Gestion des différentes structures fiscales
- Calcul automatique selon les réglementations locales
- Reporting fiscal conforme aux normes locales

### 4. Unités de mesure locales
- Gestion des différentes unités de mesure selon les pays
- Système de conversion entre unités
- Adaptation de l'interface selon les unités locales

### 5. Modèles de rapports locaux
- Modèles de rapports spécifiques par pays
- Conformité aux normes locales de reporting
- Adaptation des formats aux exigences locales

## 🧩 MODULE 1 — Gestion des structures (mis à jour)
### 1.1 Stations-service
- Création / édition
- Adresse, responsable, contacts
- Trésoreries associées
- **+ KPIs et indicateurs de performance**
- **+ Suivi des performances**

### 1.2 Cuves
- Liée à une station
- Type de carburant (gasoil, essence, pétrole)
- Capacité (litres)
- Barème de jauge
- **+ Suivi de la température pour correction volumétrique**
- **+ Contrôle d'accès aux cuves**

### 1.3 Carburants
- Types gérés
- Prix d'achat / vente
- Historique des prix
- **+ Suivi de la qualité du carburant**
- **+ Historique des coûts liés à la logistique**

### 1.4 Pistolets
- Lié à une cuve
- Index initial
- Historique des index
- **+ Contrôle des accès aux pistolets**

### 1.5 Familles produits
- Boutique
- Lubrifiant
- Services
- **+ Services annexes (lavage, atelier, restaurant)**

### 1.6 Produits
- Prix d'achat / vente
- Stock minimal
- TVA
- Code interne
- **+ Gestion des additifs et mélanges**

### 1.7 Fournisseurs
- Infos générales
- Solde / dette
- Historique
- **+ Historique de qualité des livraisons**
- **+ Analyse de performance des fournisseurs**

### 1.8 Clients
- Solde / créances
- Historique paiements
- **+ Programme de fidélisation**
- **+ Cartes de carburant**
- **+ Contrats de ravitaillement**
- **+ Système de notation**

### 1.9 Employés
- Poste (pompiste, caissier, QM, admin…)
- Salaire, avances, créances
- **+ Indicateurs de performance**
- **+ Suivi de la productivité**

### 1.10 Trésoreries et modes de paiement
- Comptes : Banque BNI, BMOI, Caisse station…
- Modes : Espèces, Chèque, Virement, Mobile Money, Carte bancaire
- **+ Gestion des assurances**
- **+ Suivi des incidents de sécurité**

## 🧩 MODULE 2 — Bilan initial (mis à jour)
### 2.1 Actifs
- Immobilisations
- Stocks carburant & boutique
- Créances clients
- Banque & caisse
- **+ Analyse comparative des actifs**

### 2.2 Passifs
- Capital social
- Réserves
- Emprunts
- Dettes fournisseurs
- **+ Analyse comparative des passifs**

## 🧩 MODULE 3 — Initialisation des stocks (mis à jour)
### 3.1 Carburant
- Stock initial par cuve
- Index initial pistolet
- Historique auto
- **+ Analyse qualité carburant**

### 3.2 Boutique
- Stock initial par produit
- Valorisation initiale
- **+ Analyse des coûts logistique**

## 🧩 MODULE 4 — Achats (mis à jour)
### 4.1 Achats carburant (processus complet)
1. Création achat
2. Détails
3. Validation
4. Paiement
5. Livraison + mesure avant/après + écart
6. Mouvement stock
7. Écritures comptables
8. Mise à jour trésorerie & dette
9-12. Modification / annulation
- **+ Suivi des coûts logistique**
- **+ Analyse de la qualité du carburant reçu**
- **+ Évaluation des fournisseurs**

### 4.2 Achats boutique
1. Création + famille
2. Produits
3. Bon de commande
4-9. Paiement, stock, écritures, modification, annulation
- **+ Suivi des performances des produits**

## 🧩 MODULE 5 — Ventes (mis à jour)
### 5.1 Ventes carburant
1-11. Création, détails, index, paiement (cash/crédit/écart pompiste), trésorerie, stock, écritures, modification, annulation
- **+ Suivi des performances pompistes**
- **+ Analyse de rendement**
- **+ Suivi des écarts anormaux**

### 5.2 Ventes boutique
- Ticket de caisse
- Paiement
- Arrêt de compte caissier
- **+ Analyse de performance caissiers**

### 5.3 Ventes services
- Création, paiement, arrêt caissier
- **+ Suivi de la productivité**

## 🧩 MODULE 6 — Inventaires (mis à jour)
### 6.1 Carburant
- Mesure hauteur + barémage
- Écart réel/théorique
- Inventaire partiel ou complet
- **+ Analyse des écarts anormaux**
- **+ Suivi des températures**

### 6.2 Boutique
- Saisie quantités réelles
- Calcul écart + justification
- **+ Analyse des tendances d'écart**

## 🧩 MODULE 7 — Opérations hors achats/ventes (mis à jour)
### 7.1 Dépenses courantes
- Catégories charges
- Paiement immédiat/partiel/dette
- **+ Analyse des tendances de charges**

### 7.2 Paiement salaires
- Génération mensuelle
- Fiche de paie
- **+ Suivi de productivité**

### 7.3 Immobilisations & investissements
- Enregistrement achat/sortie trésorerie
- **+ Suivi des coûts et efficacité**

### 7.4 Recouvrement créances
- **+ Analyse de performance du recouvrement**

### 7.5 Règlement dettes fournisseurs
- **+ Analyse des délais de paiement**

## 🧩 MODULE 8 — Ajustements (mis à jour)
### 8.1 Stock boutique
- Sortie périmés/cassés
- **+ Analyse des causes de péremption**

### 8.2 Réinitialisation index pistolet (sécurisée)
- **+ Suivi des validations hiérarchiques**

## 🧩 MODULE 9 — Rapports (mis à jour)
### 9.1 Comptabilité
- Bilan, Grand livre, Balance, Journal
- **+ Déclarations fiscales**
- **+ Suivi de conformité**

### 9.2 Gestion station
- Consommation, rendement pompistes/caissiers, stocks, dettes/créances, rentabilité
- **+ Indicateurs KPIs**
- **+ Prévisions et tendances**
- **+ Analyse comparative**

## 🧩 SECTION SPÉCIALE — Dépôt de garantie (mis à jour)
1. Enregistrement (client, montant, paiement, écriture passif)
2. Utilisation (paiement dette/vente/écart)
3. Remboursement
4. Historique complet + solde visible client
- **+ Suivi des contrats de fidélité**

## 🧩 SECTION AMÉLIORÉE — Gestion des indicateurs de performance

### 1. KPIs opérationnels
- Litres vendus par type de carburant
- Marge brute par produit
- Indicateur de rendement des pompistes
- Indicateur de productivité
- Analyse comparative des performances

### 2. Gestion fiscale et réglementaire
- Gestion des obligations fiscales (TVA, autres taxes)
- Intégration des obligations de déclaration
- Suivi des normes de sécurité et conformité réglementaire
- Génération des rapports exigés par les autorités

### 3. Gestion des risques opérationnels
- Suivi des écarts anormaux
- Gestion des assurances
- Suivi des incidents de sécurité
- Contrôle des accès aux cuves et aux pompes

### 4. Analyse et prévision commerciale
- Analyse des tendances de vente
- Prévision de la demande
- Optimisation des prix
- Analyse de la clientèle fidèle vs occasionnelle

### 5. Gestion des services annexes
- Gestion des services de station-service
- Comptabilisation des services rendus
- Suivi des contrats de maintenance

### 6. Gestion des contrôles internes
- Contrôle des écarts de caisse automatiques
- Suivi des opérations suspects
- Validation hiérarchisée des transactions importantes
- Journalisation des modifications critiques

### 7. Gestion des relations clients avancées
- Programmes de fidélisation
- Cartes de carburant
- Contrats de ravitaillement à long terme
- Système de notation des clients

### 8. Optimisation de la gestion de carburant
- Suivi des températures pour la correction volumétrique
- Gestion des mélanges d'additifs
- Suivi de la qualité du carburant
- Analyse des coûts de transport et de stockage

## 🧩 SECTION MÉMOIRE — Gestion des profils et permissions RBAC

### 1. Architecture de la gestion des permissions
Le système SuccessFuel implémente un système RBAC (Role-Based Access Control) qui permet :
- À chaque gérant de définir ses propres profils utilisateurs selon ses besoins
- Une gestion fine des droits d'accès basée sur les profils
- Une attribution spécifique de stations aux utilisateurs
- Un système de validation hiérarchique pour les opérations sensibles

### 2. Structure des profils
- **Modules** : Regroupement fonctionnel des permissions (ventes, achats, stocks, etc.)
- **Permissions** : Actions spécifiques (lire, créer, modifier, supprimer, annuler)
- **Profils** : Ensemble de permissions attribué à un utilisateur
- **Associations** : Lien entre profils et permissions

### 3. Gestion des stations par utilisateur
- Chaque utilisateur est limité à des stations spécifiques
- Le champ `stations_user` (JSONB) permet de restreindre les opérations à certaines stations
- Permet une gestion géographique fine des accès

### 4. Suivi et validation des actions
- **Journalisation** : Toutes les actions des utilisateurs sont enregistrées avec détails
- **Validations hiérarchiques** : Système de validation selon le montant ou le type d'opération
- **Contrôles d'accès** : Seuls les gérants peuvent créer des profils et assigner des permissions

### 5. Sécurité et surveillance
- **Contrôles d'accès** : Seuls les gérants peuvent créer des profils et assigner des permissions
- **Journalisation** : Toutes les actions sensibles sont enregistrées
- **Surveillance proactive** : Système d'alertes pour les actions sensibles et écarts de comportement

## 🧩 SECTION MÉMOIRE — Sécurité du système

### 1. Protection contre les injections SQL
- **Requêtes préparées** : Toutes les requêtes utilisent des paramètres positionnels ou nommés
- **Validation des entrées** : Tous les champs utilisateur sont validés avant insertion dans la base
- **Types de données stricts** : Utilisation de types spécifiques (UUID, NUMERIC, etc.) pour chaque champ
- **Contrôle d'accès à la base** : Utilisation de rôles PostgreSQL avec permissions limitées

## 🧩 SECTION MÉMOIRE — Architecture modulaire pour l'internationalisation

### 1. Flexibilité du système
- **Architecture modulaire** : Système conçu avec des modules interchangeables pour s'adapter aux spécificités locales
- **Configuration dynamique** : Paramètres configurables par pays sans modification du code source
- **Système de plugins** : Support des spécificités locales via un système de plugins configurables
- **API standardisée** : Interfaces standardisées avec modules spécifiques selon la localisation

### 2. Gestion des spécifications locales
- **Système de pays** : Support des spécificités de chaque pays (taxes, devises, unités de mesure, etc.)
- **Modules configurables** : Activation/désactivation de fonctionnalités selon les besoins locaux
- **Paramètres régionaux** : Adaptation des formats, unités, et processus selon la localisation
- **Reporting localisé** : Génération de rapports selon les normes locales

### 2. Authentification et autorisation
- **Authentification sécurisée** : Jetons d'authentification chiffrés avec hachage et durée de vie limitée
- **Hachage des mots de passe** : Utilisation de bcrypt ou équivalent avec sel (salt)
- **Système RBAC** : Gestion des permissions granulaires avec profils personnalisables
- **Validation hiérarchique** : Système de validation pour les opérations sensibles

### 3. Protection des données sensibles
- **Chiffrement des données critiques** : Mots de passe, données financières, etc.
- **Masquage des données sensibles** : Numéros de compte partiellement masqués
- **Journalisation sécurisée** : Les traces d'audit ne contiennent pas les données sensibles en clair

### 4. Journalisation et surveillance
- **Journalisation détaillée** : Toutes les actions critiques sont enregistrées
- **Surveillance proactive** : Détection des anomalies et comportements suspects
- **Table des tentatives de connexion** : Suivi des connexions réussies/échouées
- **Table des événements de sécurité** : Suivi des incidents de sécurité

### 5. Contrôles d'accès
- **Accès limité aux stations** : Chaque utilisateur est limité à des stations spécifiques
- **Validation hiérarchique** : Processus de validation selon le montant/type d'opération
- **Contrôle des modifications sensibles** : Surveillance des opérations critiques
- **Politiques de sécurité configurables** : Paramètres de sécurité personnalisables

### 6. Sécurité des communications
- **Utilisation du protocole HTTPS** : Toutes les communications sont chiffrées
- **Protection contre les attaques CSRF** : Jetons CSRF pour les opérations sensibles
- **Validation des origines des requêtes** : Vérification de la provenance des appels

### 7. Gestion des erreurs sécurisée
- **Messages d'erreur non divulguants** : Ne révèlent pas d'informations internes
- **Journalisation des erreurs** : Toutes les erreurs sont enregistrées pour surveillance
- **Gestion personnalisée des exceptions** : Évite les fuites d'informations

### 8. Sauvegarde et récupération
- **Sauvegardes cryptées** : Données sauvegardées de manière sécurisée
- **Politique de rotation** : Gestion sécurisée des versions de sauvegarde
- **Procédures de récupération testées** : Processus validés régulièrement