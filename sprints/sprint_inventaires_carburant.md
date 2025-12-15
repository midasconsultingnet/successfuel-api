# Sprint: Module Inventaires Carburant

## Objectif
Implémenter la gestion complète des inventaires physiques de carburant par cuve dans une station-service, avec comparaison entre stocks théoriques et réels, gestion des écarts, audit et sécurité.

## Spécifications détaillées

### 1. Gestion des inventaires
#### 1.1. Fonctions principales
- Création, modification et suppression d'inventaires carburant
- Champs: cuve, carburant, quantité réelle, date/heure, statut, commentaires (optionnel), utilisateur ayant effectué la saisie, méthode de mesure (manuel, jauge digitale, sonde automatique)
- La station est automatiquement déterminée selon l'utilisateur connecté

#### 1.2. Statuts possibles
- **Brouillon**:
  - saisie initiale
  - modification libre
  - suppression possible
- **En cours**:
  - mesure physique en cours
  - modification limitée
  - verrouillage de certaines données
- **Terminé**:
  - données physiques saisies
  - calcul automatique des écarts
  - modification restreinte
- **Validé**:
  - validation par responsable
  - aucune modification possible sauf correction par workflow
- **Rapproché**:
  - comparaison avec stock théorique
  - écarts traités
- **Clôturé**:
  - inventaire finalisé
  - verrouillage total

#### 1.3. Calcul de l'écart
- Écart = Quantité réelle – Stock théorique
- Classification automatique: perte, évaporation, anomalie/erreur, surplus (écart positif)
- Détection automatique des écarts significatifs:
  - seuil paramétrable selon le type de carburant (essence, diesel, etc.)
  - seuil variable selon la saison (évaporation plus importante en été)
  - seuil selon la capacité de la cuve
  - seuil paramétrable par station ou par produit
  - notifications en cas d’écart hors tolérance

#### 1.4. Gestion des erreurs de saisie
- Selon statut:
  - Brouillon: totalement modifiable
  - En cours / Terminé: modifiable selon règle
  - Validé / Rapproché / Clôturé: modification impossible → correction via workflow d’ajustement

### 2. Comparaison Stock Réel vs Théorique
#### 2.1. Calcul du stock théorique
- Basé sur: l'état initial défini dans la table etat_initial_cuve plus les mouvements ultérieurs (entrées: livraisons, transferts; sorties: ventes, mouvements internes), corrections précédentes
- Règles du module Structure de la Compagnie

#### 2.2. Affichage des écarts
- Affichage détaillé dans l'interface
- Code couleur selon seuils configurés:
  - vert = écart acceptable (dans les limites de tolérance)
  - orange = écart moyen (hors tolérance mais non critique)
  - rouge = écart important (hors tolérance critique)
- Historique des écarts par cuve visible par période

#### 2.3. Configuration des seuils de tolérance
- Seuils différenciés selon le type de carburant (essence, diesel, etc.)
- Seuils variables selon la saison (évaporation plus importante en été)
- Seuils selon la capacité de la cuve
- Seuils adaptatifs basés sur l'historique des écarts
- Seuils configurables par station, type de carburant, ou selon les conditions opérationnelles
- Paramétrage des seuils bas, moyen et élevé pour chaque configuration

### 3. Gestion des écarts
#### 3.1. Classification des écarts
- pertes techniques (évaporation, dilatation, conditions météo)
- anomalies humaines (erreur de mesure, erreur de reporting)
- écarts plus (surplus)
- pertes non identifiées (vol, fuite, erreur d’entrée théorique)

#### 3.2. Traitement des écarts négatifs
- Analyse du type de perte: technique, humaine, fuite/vol
- Actions possibles: ajustement du stock réel, ouverture d’un incident, création automatique de créance envers un employé via le module Financier, demande d’enquête interne, remontée d’alerte au siège

#### 3.3. Traitement des écarts positifs (surplus)
- Analyse approfondie: erreur précédente dans les mouvements, double comptabilisation, erreur de livraison
- Actions possibles: correction du stock théorique, documentation obligatoire, escalade si surplus élevé, validation par un niveau supérieur (chef de réseau, comptable, direction)

#### 3.4. Correction automatique du stock
- Ajustement automatique du stock réel en fonction de la nature de l’écart
- Journalisation obligatoire
- Mise à jour instantanée dans les autres modules

#### 3.5. Historique et audit
- Journal complet: date, utilisateur, ancienne valeur, nouvelle valeur, justification
- Conservation à long terme (7 à 10 ans selon réglementaire)

### 4. Historique des inventaires
#### 4.1. Traçabilité complète
- Historique des écarts par cuve
- Historique des corrections
- Historique des mesures physiques
- Versioning des inventaires

#### 4.2. Données de jauge
- Possibilité d’intégrer: données automatiques de sondes, jauges manuelles, photos (preuve de mesure)

### 5. Sécurité & Rôles
#### 5.1. Accès contrôlés
- Basé sur le RBAC: gerant_compagnie, utilisateur_compagnie, auditeur, direction
- Accès limité par station + rôle

#### 5.2. Contrôles de sécurité
- Double validation pour: écarts importants, corrections sensibles
- Vérification des droits avant chaque action
- Journalisation de toutes les actions sensibles
- Blocage des modifications sur inventaire validé / clôturé

## Livrables
- API REST pour la gestion des inventaires carburant
- Modèles de données (inventaires, écarts, historique, audit)
- Interface d’administration:
  - saisie d’inventaire
  - traitement des écarts
  - tableau de suivi par station / réseau
- Moteur de calcul des écarts
- Moteur de classification des écarts
- Workflow de validation multi-niveaux
- Tests unitaires
- Tests d’intégration
- Documentation technique + Swagger