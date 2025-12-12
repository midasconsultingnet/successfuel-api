# Contexte – Gestion des Trésoreries d’une Compagnie Multi-Stations

## 1. Principe général
Dans le système, la trésorerie représente un **moyen de paiement** ou un **compte de liquidités** utilisé par la compagnie et ses stations-service.

Une compagnie peut disposer de plusieurs trésoreries globales :  
- Caisse  
- Mobile money  
- Banque  
- Carte prépayée  
- Coffre  
- Etc.

Chaque trésorerie appartient à la **compagnie**, et non à une station.  
Cependant, les mouvements financiers sont suivis **par station** et **par utilisateur**, ce qui permet un audit détaillé et une gestion fine.

---

## 2. Structure en 3 niveaux
### 2.1 Trésoreries globales (niveau compagnie)
Ce sont les types de trésoreries.

Exemples :
- `Caisse`
- `Banque BNI`
- `Mobile Money – Mvola`
- `Mobile Money – Orange Money`
- `Compte interne`

Ces trésoreries sont :
- uniques au niveau compagnie  
- configurées une fois  
- accessibles à toutes les stations

### 2.2 Trésoreries station (instances par station)
Chaque station utilise les trésoreries globales, mais possède son propre solde.

Exemple si la compagnie a 2 stations (A, B) et 3 trésoreries (Caisse, Banque, Mobile money) :

| Trésorerie globale | Station | Trésorerie station |
|--------------------|---------|--------------------|
| Caisse             | A       | Caisse–A           |
| Banque BNI         | A       | Banque–A           |
| Mobile Money       | A       | Mobile–A           |
| Caisse             | B       | Caisse–B           |
| Banque BNI         | B       | Banque–B           |
| Mobile Money       | B       | Mobile–B           |

Chaque station a son propre solde, ses propres mouvements et ses propres contrôles.

### 2.3 Mouvements de trésorerie
Toutes les opérations financières sont enregistrées dans une table unique contenant les attributs :

- `tresorerie_globale_id`
- `tresorerie_station_id`
- `station_id`
- `user_id`
- `type_operation_id`
- `montant`
- `direction` (entrée / sortie)
- `mode_paiement_id`
- `date_operation`
- `référence` (facture, BL, vente, ticket…)
- `description`

---

## 3. Méthodes de paiement
Chaque trésorerie peut définir **une ou plusieurs méthodes de paiement**.

Exemple :

### Caisse
- Espèces
- Chèque reçu
- Chèque émis
- Bons internes
- Coupons

### Mobile Money
- Mvola
- Orange Money
- Airtel Money

### Banque
- Virement bancaire
- Dépôt guichet
- Débit carte
- Crédit carte

Chaque méthode de paiement :
- appartient à une trésorerie globale  
- est utilisée par toutes les stations  
- peut être activée / désactivée  

### Importance
Les méthodes de paiement permettent :
- une meilleure catégorisation des entrées et sorties  
- un suivi précis en comptabilité  
- un contrôle poussé des accès utilisateurs  

---

## 4. Utilisateurs et permissions
L’accès aux trésoreries est contrôlé par un système RBAC.

### Un utilisateur peut :
- accéder seulement aux trésoreries des stations auxquelles il est affecté  
- ne voir que les méthodes de paiement autorisées pour lui  
- effectuer seulement certains types d’opération :
  - encaissement
  - décaissement
  - transfert
  - consultation

### Exemple
Marc est pompiste à la station A :
- Accès uniquement : **Caisse–A** et **Mobile Money–A**  
- Méthodes autorisées : Espèces, Mobile Money  
- Pas le droit d’utiliser la Banque–A  
- Pas le droit de faire un transfert sortant

---

## 5. Types d’opérations financières

### 5.1 Entrées
- Ven
