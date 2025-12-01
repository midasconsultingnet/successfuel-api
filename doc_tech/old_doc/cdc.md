# Cahier des Charges - SuccessFuel ERP

## Présentation du projet

**SuccessFuel** est un ERP (Enterprise Resource Planning) spécialement conçu pour la gestion complète des stations-service. Ce système informatisé permet d'automatiser, centraliser et sécuriser toutes les opérations liées à la gestion d'une station-service, de la vente de carburant aux opérations comptables et administratives.

Notre solution s'adresse aux gestionnaires de stations-service qui souhaitent moderniser leur gestion, réduire les erreurs humaines, améliorer leur traçabilité et optimiser leurs performances.

---

## Modules du système

### 1. Gestion des Structures
Ce module permet de gérer tous les éléments physiques de votre station-service :

#### 1.1. Stations-service
- Création / édition des stations
- Saisie des adresses, responsables et contacts
- Gestion des trésoreries associées à chaque station
- KPIs et indicateurs de performance
- Suivi des performances

#### 1.2. Cuves de stockage
- Enregistrement de chaque cuve (type de carburant, capacité en litres)
- Barème de jauge pour le calcul du volume selon la hauteur
- Suivi de la température pour correction volumétrique
- Contrôle d'accès aux cuves

#### 1.3. Carburants
- Gestion des différents types de carburant (essence, gasoil, pétrole)
- Suivi des prix d'achat et de vente
- Historique des évolutions de prix
- Suivi de la qualité du carburant
- Historique des coûts liés à la logistique

#### 1.4. Pistolets de distribution
- Numérotation et association à une cuve spécifique
- Suivi de l'index initial et des relevés
- Contrôle d'accès aux pistolets

#### 1.5. Familles de produits
- Gestion des produits de la boutique (alimentation, lubrifiants, etc.)
- Services annexes (lavage, atelier, restaurant)

#### 1.6. Produits
- Suivi des prix d'achat et de vente
- Stock minimal configuré
- Gestion de la TVA
- Code interne pour chaque produit
- Gestion des additifs et mélanges

#### 1.7. Fournisseurs
- Informations générales sur les fournisseurs
- Suivi du solde et des dettes
- Historique des transactions
- Historique de qualité des livraisons
- Analyse de performance des fournisseurs

#### 1.8. Clients
- Suivi du solde et des créances
- Historique des paiements
- Programme de fidélisation
- Cartes de carburant
- Contrats de ravitaillement
- Système de notation

#### 1.9. Employés
- Gestion des postes (pompiste, caissier, QM, admin, etc.)
- Suivi des salaires, avances et créances
- Indicateurs de performance
- Suivi de la productivité

#### 1.10. Trésoreries et modes de paiement
- Gestion des comptes (Banque BNI, BMOI, Caisse station, etc.)
- Modes de paiement acceptés (espèces, chèque, virement, mobile money, carte bancaire)
- Gestion des assurances
- Suivi des incidents de sécurité

---

### 2. Bilan Initial
Ce module vous permet d'établir le bilan initial de votre station-service avant l'utilisation du système :

#### 2.1. Actifs
- Immobilisations
- Stocks carburant & boutique
- Créances clients
- Banque & caisse
- Analyse comparative des actifs

#### 2.2. Passifs
- Capital social
- Réserves
- Emprunts
- Dettes fournisseurs
- Analyse comparative des passifs

---

### 3. Initialisation des Stocks
Ce module permet de configurer vos stocks au démarrage du système :

#### 3.1. Carburant
- Saisie des stocks initiaux par cuve
- Initialisation des index des pistolets
- Historique automatique
- Analyse de la qualité du carburant

#### 3.2. Boutique
- Initialisation des stocks par produit
- Valorisation initiale
- Analyse des coûts logistique

---

### 4. Gestion des Achats
Ce module gère tous vos approvisionnements :

#### 4.1. Achats carburant - Processus complet
- Création de l'achat
- Détail des produits/commandes
- Validation
- Paiement
- Livraison + mesure avant/après + écart
- Mouvement de stock
- Écritures comptables
- Mise à jour trésorerie & dette
- Modification / annulation
- Suivi des coûts logistique
- Analyse de la qualité du carburant reçu
- Évaluation des fournisseurs

#### 4.2. Achats boutique
- Création + affectation à une famille de produits
- Gestion des produits
- Bon de commande
- Paiement, mouvement de stock, écritures comptables
- Modification / annulation
- Suivi des performances des produits

---

### 5. Gestion des Ventes
Ce module gère toutes les ventes effectuées dans votre station :

#### 5.1. Ventes carburant
- Processus complet de création
- Détails des ventes
- Saisie des index de pistolet
- Paiement (cash/crédit/écart pompiste)
- Mise à jour trésorerie
- Mise à jour stock
- Écritures comptables
- Modification / annulation
- Suivi des performances pompistes
- Analyse de rendement
- Suivi des écarts anormaux

#### 5.2. Ventes boutique
- Émission de tickets de caisse
- Paiement
- Arrêt de compte caissier
- Analyse de performance des caissiers

#### 5.3. Ventes services
- Création
- Paiement
- Arrêt de compte caissier
- Suivi de la productivité

---

### 6. Inventaires
Ce module permet de contrôler vos stocks :

#### 6.1. Inventaire carburant
- Mesure de la hauteur dans les cuves
- Calcul via barème
- Écart réel/théorique
- Inventaire partiel ou complet
- Analyse des écarts anormaux
- Suivi des températures

#### 6.2. Inventaire boutique
- Saisie des quantités réelles
- Calcul de l'écart + justification
- Analyse des tendances d'écart

---

### 7. Opérations hors achats/ventes
Ce module gère vos autres opérations :

#### 7.1. Dépenses courantes
- Catégorisation des charges
- Paiement immédiat/partiel/dette
- Analyse des tendances de charges

#### 7.2. Paiement salaires
- Génération mensuelle des fiches de paie
- Suivi de productivité

#### 7.3. Immobilisations & investissements
- Enregistrement achat/sortie trésorerie
- Suivi des coûts et efficacité

#### 7.4. Recouvrement créances
- Analyse de performance du recouvrement

#### 7.5. Règlement dettes fournisseurs
- Analyse des délais de paiement

---

### 8. Ajustements
- Stock boutique : sortie des périmés/cassés
- Analyse des causes de péremption
- Réinitialisation sécurisée des index de pistolets
- Suivi des validations hiérarchiques

---

### 9. Dépôt de Garantie
- Enregistrement (client, montant, paiement, écriture au passif)
- Utilisation (paiement dette/vente/écart)
- Remboursement
- Historique complet + solde visible client
- Suivi des contrats de fidélité

---

### 10. Gestion des indicateurs de performance

#### 10.1. KPIs opérationnels
- Litres vendus par type de carburant
- Marge brute par produit
- Indicateur de rendement des pompistes
- Indicateur de productivité
- Analyse comparative des performances

#### 10.2. Gestion fiscale et réglementaire
- Gestion des obligations fiscales (TVA, autres taxes)
- Intégration des obligations de déclaration
- Suivi des normes de sécurité et conformité réglementaire
- Génération des rapports exigés par les autorités

#### 10.3. Gestion des risques opérationnels
- Suivi des écarts anormaux
- Gestion des assurances
- Suivi des incidents de sécurité
- Contrôle des accès aux cuves et aux pompes

#### 10.4. Analyse et prévision commerciale
- Analyse des tendances de vente
- Prévision de la demande
- Optimisation des prix
- Analyse de la clientèle fidèle vs occasionnelle

#### 10.5. Gestion des services annexes
- Gestion des services de station-service
- Comptabilisation des services rendus
- Suivi des contrats de maintenance

#### 10.6. Gestion des contrôles internes
- Contrôle des écarts de caisse automatiques
- Suivi des opérations suspectes
- Validation hiérarchisée des transactions importantes
- Journalisation des modifications critiques

#### 10.7. Gestion des relations clients avancées
- Programmes de fidélisation
- Cartes de carburant
- Contrats de ravitaillement à long terme
- Système de notation des clients

#### 10.8. Optimisation de la gestion de carburant
- Suivi des températures pour la correction volumétrique
- Gestion des mélanges d'additifs
- Suivi de la qualité du carburant
- Analyse des coûts de transport et de stockage

---

### 11. Gestion des profils et permissions RBAC

#### 11.1. Architecture de la gestion des permissions
- Système RBAC (Role-Based Access Control) qui permet :
  - À chaque gérant de définir ses propres profils utilisateurs selon ses besoins
  - Une gestion fine des droits d'accès basée sur les profils
  - Une attribution spécifique de stations aux utilisateurs
  - Un système de validation hiérarchique pour les opérations sensibles
  - Une hiérarchie d'utilisateurs clairement définie avec des responsabilités spécifiques

#### 11.2. Structure des profils
- Modules : Regroupement fonctionnel des permissions (ventes, achats, stocks, etc.)
- Permissions : Actions spécifiques (lire, créer, modifier, supprimer, annuler)
- Profils : Ensemble de permissions attribué à un utilisateur
- Associations : Lien entre profils et permissions

#### 11.3. Gestion des stations par utilisateur
- Chaque utilisateur est limité à des stations spécifiques
- Le champ `stations_user` (JSONB) permet de restreindre les opérations à certaines stations
- Permet une gestion géographique fine des accès

#### 11.4. Suivi et validation des actions
- Journalisation : Toutes les actions des utilisateurs sont enregistrées avec détails
- Validations hiérarchiques : Système de validation selon le montant ou le type d'opération
- Contrôles d'accès : Seuls les gérants peuvent créer des profils et assigner des permissions

#### 11.5. Hiérarchie des utilisateurs et responsabilités
- Super administrateur : Accès complet à toutes les fonctionnalités, création d'autres administrateurs, gestion des gérants compagnie
- Administrateur : Accès limité selon les permissions définies par le super administrateur
- Gérant compagnie : Gestion des utilisateurs de sa compagnie et définition de leurs permissions
- Utilisateur compagnie : Accès limité selon ses permissions spécifiques
- Distinction des endpoints : Authentification séparée pour administrateurs et utilisateurs

#### 11.6. Sécurité et surveillance
- Contrôles d'accès : Seuls les gérants peuvent créer des profils et assigner des permissions
- Journalisation : Toutes les actions sensibles sont enregistrées
- Surveillance proactive : Système d'alertes pour les actions sensibles et écarts de comportement

---

### 12. Sécurité du système

#### 12.1. Protection contre les injections SQL
- Requêtes préparées : Toutes les requêtes utilisent des paramètres positionnels ou nommés
- Validation des entrées : Tous les champs utilisateur sont validés avant insertion dans la base
- Types de données stricts : Utilisation de types spécifiques (UUID, NUMERIC, etc.) pour chaque champ
- Contrôle d'accès à la base : Utilisation de rôles PostgreSQL avec permissions limitées

#### 12.2. Authentification et autorisation
- Authentification sécurisée : Jetons d'authentification chiffrés avec hachage et durée de vie limitée
- Hachage des mots de passe : Utilisation de bcrypt ou équivalent avec sel (salt)
- Système RBAC : Gestion des permissions granulaires avec profils personnalisables
- Validation hiérarchique : Système de validation pour les opérations sensibles

#### 12.3. Protection des données sensibles
- Chiffrement des données critiques : Mots de passe, données financières, etc.
- Masquage des données sensibles : Numéros de compte partiellement masqués
- Journalisation sécurisée : Les traces d'audit ne contiennent pas les données sensibles en clair

#### 12.4. Journalisation et surveillance
- Journalisation détaillée : Toutes les actions critiques sont enregistrées
- Surveillance proactive : Détection des anomalies et comportements suspects
- Table des tentatives de connexion : Suivi des connexions réussies/échouées
- Table des événements de sécurité : Suivi des incidents de sécurité

#### 12.5. Contrôles d'accès
- Accès limité aux stations : Chaque utilisateur est limité à des stations spécifiques
- Validation hiérarchique : Processus de validation selon le montant/type d'opération
- Contrôle des modifications sensibles : Surveillance des opérations critiques
- Politiques de sécurité configurables : Paramètres de sécurité personnalisables
- Classification des utilisateurs : Distinction entre super administrateur, administrateur, gérant compagnie et utilisateur compagnie
- Séparation des endpoints : Authentification distincte pour administrateurs et utilisateurs standards avec blocage des accès croisés

#### 12.6. Sécurité des communications
- Utilisation du protocole HTTPS : Toutes les communications sont chiffrées
- Protection contre les attaques CSRF : Jetons CSRF pour les opérations sensibles
- Validation des origines des requêtes : Vérification de la provenance des appels

#### 12.7. Gestion des erreurs sécurisée
- Messages d'erreur non divulguants : Ne révèlent pas d'informations internes
- Journalisation des erreurs : Toutes les erreurs sont enregistrées pour surveillance
- Gestion personnalisée des exceptions : Évite les fuites d'informations

#### 12.8. Sauvegarde et récupération
- Sauvegardes cryptées : Données sauvegardées de manière sécurisée
- Politique de rotation : Gestion sécurisée des versions de sauvegarde
- Procédures de récupération testées : Processus validés régulièrement

---

### 13. Rapports
Ce module fournit tous les états et analyses nécessaires :

#### 13.1. Comptabilité
- Bilan, grand livre, balance, journal
- Déclarations fiscales
- Suivi de conformité

#### 13.2. Gestion station
- Consommation, rendement pompistes/caissiers, stocks, dettes/créances, rentabilité
- Indicateurs KPIs
- Prévisions et tendances
- Analyse comparative

---

### 14. Gestion des Utilisateurs et Sécurité
- Création de profils utilisateurs avec droits d'accès
- Attribution de stations spécifiques à chaque utilisateur
- Journalisation de toutes les actions
- Contrôles de sécurité (connexions, accès)
- Validation hiérarchique pour les opérations sensibles

---

### 15. Indicateurs de Performance (KPIs)
Le système calcule automatiquement de nombreux indicateurs pour vous aider à piloter votre activité :

- Litres vendus par type de carburant
- Marge brute par produit
- Rendement des pompistes
- Productivité horaire
- Analyse comparative des performances
- Suivi des écarts anormaux
- Rentabilité par station

---

### 16. Fonctionnalités d'Internationalisation
Pour les clients souhaitant déployer le système dans plusieurs pays africains :

#### 16.1. Gestion multi-pays
- Configuration des spécifications locales par pays
- Support des différentes législations fiscales
- Adaptation aux systèmes comptables locaux (OHADA, etc.)
- Gestion des devises multiples

#### 16.2. Gestion des devises
- Support multi-devises pour transactions internationales
- Historique des taux de change
- Conversion automatique selon les taux en temps réel
- Rapports financiers dans la devise locale

#### 16.3. Système de taxation modulaire
- Configuration des taux de taxes par pays
- Gestion des différentes structures fiscales
- Calcul automatique selon les réglementations locales
- Reporting fiscal conforme aux normes locales

#### 16.4. Unités de mesure locales
- Gestion des différentes unités de mesure selon les pays
- Système de conversion entre unités
- Adaptation de l'interface selon les unités locales

#### 16.5. Modèles de rapports locaux
- Modèles de rapports spécifiques par pays
- Conformité aux normes locales de reporting
- Adaptation des formats aux exigences locales

#### 16.6. Architecture modulaire pour l'internationalisation
- Flexibilité du système
  - Architecture modulaire : Système conçu avec des modules interchangeables pour s'adapter aux spécificités locales
  - Configuration dynamique : Paramètres configurables par pays sans modification du code source
  - Système de plugins : Support des spécificités locales via un système de plugins configurables
  - API standardisée : Interfaces standardisées avec modules spécifiques selon la localisation
- Gestion des spécifications locales
  - Système de pays : Support des spécificités de chaque pays (taxes, devises, unités de mesure, etc.)
  - Modules configurables : Activation/désactivation de fonctionnalités selon les besoins locaux
  - Paramètres régionaux : Adaptation des formats, unités, et processus selon la localisation
  - Reporting localisé : Génération de rapports selon les normes locales

---

## Avantages du système

1. **Traçabilité complète** : Toutes les opérations sont enregistrées et traçables
2. **Sécurité des données** : Protection contre les fraudes et erreurs
3. **Conformité réglementaire** : Respect des obligations légales
4. **Amélioration de la productivité** : Automatisation des tâches répétitives
5. **Meilleure gestion** : KPIs en temps réel pour la prise de décision
6. **Réduction des coûts** : Moins d'erreurs et de pertes
7. **Flexibilité** : Adaptation à votre mode de gestion
8. **Internationalisation** : Adaptabilité à d'autres pays africains francophones

## Support et accompagnement

- Installation et paramétrage initial
- Formation de vos équipes
- Assistance technique continue
- Mises à jour régulières
- Support téléphonique et en ligne