# Liste des bugs identifiés dans le système

## 1. Bug d'importation dans le module stock
**Fichier:** `api/models/__init__.py`, ligne 9  
**Problème:** `ImportError: cannot import name 'Stock' from 'api.models.stock'`  
**Cause:** La classe `Stock` n'existe pas dans le fichier `api/models/stock.py`, seule `StockProduit` existe  
**Solution:** Remplacer `from .stock import Stock` par `from .stock import StockProduit` dans `api/models/__init__.py`

## 2. Bug d'importation dans le routeur stocks
**Fichier:** `api/stocks/router.py`, ligne 5  
**Problème:** Mauvais alias pour le modèle `Stock`  
**Cause:** Suite au bug précédent, l'importation `from ..models import Stock as StockModel` est incorrect  
**Solution:** Remplacer `Stock` par `StockProduit` dans l'importation

## 3. Incohérence de modèle dans le module stock
**Fichier:** `api/models/stock.py`  
**Problème:** La classe `StockProduit` ne contient pas le champ `station_id`  
**Cause:** Le routeur dans `api/stocks/router.py` utilise `station_id`, mais le modèle ne le contient pas  
**Solution:** Ajouter le champ `station_id` à la classe `StockProduit` et une contrainte d'unicité

## 4. Bug dans la fonction de service stock
**Fichier:** `api/services/stock_service.py`  
**Problème:** La fonction `mettre_a_jour_stock_produit` ne gère pas le `station_id`  
**Cause:** Le service n'a pas été mis à jour pour tenir compte du `station_id`  
**Solution:** Ajouter le paramètre `station_id` à cette fonction

## 5. Bug dans le routeur stocks
**Fichier:** `api/stocks/router.py`  
**Problème:** L'endpoint `create_mouvement_stock` n'inclut pas le `station_id`  
**Cause:** Le `station_id` n'est pas fourni dans le paramètre de la fonction  
**Solution:** Ajouter `station_id` aux paramètres de la fonction et l'utiliser dans la création du mouvement

## 6. Bug de modèle dans `MouvementStock`
**Fichier:** `api/models/mouvement_stock.py`  
**Problème:** La classe `MouvementStock` ne contient pas le champ `station_id`  
**Cause:** Le modèle n'a pas été mis à jour pour refléter la dépendance avec la station  
**Solution:** Ajouter le champ `station_id` à la classe `MouvementStock`

## 7. Bug dans le calcul de coût moyen pondéré
**Fichier:** `api/services/stock_service.py`  
**Problème:** La fonction `calculer_cout_moyen_pondere` ne tient pas compte du `station_id`  
**Cause:** Le calcul ne fait pas la distinction entre les différentes stations  
**Solution:** Ajouter le paramètre `station_id` à cette fonction

## 8. Bug d'importation dans le routeur compagnie
**Fichier:** `api/compagnie/router.py`, ligne 8  
**Problème:** `ImportError: cannot import name 'EtatInitialCuve' from 'api.models'`  
**Cause:** La classe `EtatInitialCuve` n'est pas exportée dans `api/models/__init__.py`  
**Solution:** Ajouter `EtatInitialCuve` à l'importation dans `api/models/__init__.py`

## 9. Bug d'importation dans le routeur inventaire
**Fichier:** `api/inventaire/router.py`, ligne 9  
**Problème:** `ImportError: cannot import name 'Cuve' from 'api.models'`  
**Cause:** La référence de clé étrangère dans la classe `Cuve` est incorrecte (`station.id` au lieu de `stations.id`)  
**Solution:** Corriger la déclaration de la clé étrangère dans la classe `Cuve`

## 10. Bug dans le schéma de stock
**Fichier:** `api/stocks/schemas.py`  
**Problème:** Le schéma `StockCreate` ne contient pas le champ `station_id`  
**Cause:** Le schéma n'a pas été mis à jour pour refléter la dépendance avec la station  
**Solution:** Ajouter le champ `station_id` au schéma `StockCreate` et ajouter `StockResponse`

## 11. Bug dans les endpoints de stock
**Fichier:** `api/stocks/router.py`  
**Problème:** Les endpoints utilisent `schemas.StockCreate` comme schéma de réponse  
**Cause:** Ce schéma ne contient pas tous les champs de la classe `StockProduit`  
**Solution:** Utiliser `schemas.StockResponse` comme schéma de réponse

## 12. Bug de référence étrangère dans la classe Station
**Fichier:** `api/models/compagnie.py`  
**Problème:** `ForeignKey("compagnie.id")` au lieu de `ForeignKey("compagnies.id")`  
**Cause:** Incohérence dans le nommage de la table de référence  
**Solution:** Corriger la déclaration de la clé étrangère dans la classe `Station`

## 13. Bug de modèle manquant
**Fichier:** `api/models/compagnie.py`  
**Problème:** La classe `Compagnie` référence `ForeignKey("pays.id")` mais la classe `Pays` n'existe pas  
**Cause:** Aucun modèle n'existe pour la table `pays`  
**Solution:** Créer un modèle `Pays` et l'importer dans `api/models/__init__.py`

## 14. Bug de nom de schéma dans le routeur produits
**Fichier:** `api/produits/router.py`, ligne 246  
**Problème:** `NameError: name 'LotSchema' is not defined`  
**Cause:** Le schéma `LotSchema` n'existe pas dans `api/produits/schemas.py`  
**Solution:** Ajouter un schéma `LotResponse` et utiliser ce schéma dans les endpoints

## 15. Bug de type dans les routeurs de produits
**Fichier:** `api/produits/router.py`
**Problème:** Les paramètres `produit_id` sont typés comme `int` au lieu de `str` (UUID)
**Cause:** Incohérence avec le reste du système qui utilise des UUID
**Solution:** Changer le type de `produit_id` de `int` à `str`

## 16. Bug dans les endpoints de lots dupliqués
**Fichier:** `api/produits/router.py`
**Problème:** Il y a deux endpoints GET et POST pour les lots, l'un (lignes 246-258) est correctement mis à jour, l'autre (lignes 332-361) utilise encore des schémas incorrects
**Cause:** Les endpoints dupliqués n'ont pas été uniformisés après la correction du premier
**Solution:** Mettre à jour les endpoints à la ligne 332 et 361 pour utiliser le schéma `LotResponse` au lieu de `LotCreate` et corriger le type de `produit_id` de `int` à `str`

## 17. Mauvaise utilisation des schémas de réponse
**Fichier:** Multiples fichiers dans `api/`
**Problème:** De nombreux endpoints utilisent des schémas de type `...Create` comme schémas de réponse au lieu de schémas de type `...Response`
**Cause:** Manque de schémas de réponse appropriés dans les fichiers `schemas.py` et/ou mauvaise attribution des schémas de réponse
**Solution:** Créer des schémas de réponse (`...Response`) pour chaque modèle et les utiliser comme schémas de réponse pour les endpoints GET et POST

## 18. Import manquant pour status
**Fichier:** Multiples fichiers dans `api/`
**Problème:** Le module `status` de FastAPI est utilisé avec `status.HTTP_...` mais n'est pas explicitement importé dans les fichiers concernés
**Cause:** L'import `from fastapi import status` est manquant dans les fichiers qui utilisent `status.HTTP_...`
**Solution:** Ajouter l'import `from fastapi import status` dans tous les fichiers qui utilisent `status.HTTP_...`

## 19. Erreur d'importation dans la route de login
**Fichier:** `api/auth/router.py`
**Problème:** L'import de `status` est correctement fait dans la route d'authentification
**Cause:** Cela explique pourquoi les modules d'authentification fonctionnent correctement
**Solution:** Réviser la compréhension de la propagation de l'importation de `status` dans les modules qui l'importent indirectement