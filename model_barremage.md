# Modèle de barremage pour les cuves

Le barremage est une table de correspondance entre la hauteur de jauge (en cm) et le volume de carburant (en litres) dans une cuve. Il est stocké comme une chaîne JSON dans le champ `barremage` d'une cuve.

## Format

Le barremage doit être une **chaîne de caractères JSON** contenant un tableau d'objets avec deux propriétés :
- `hauteur_cm` : la hauteur en centimètres
- `volume_litres` : le volume correspondant en litres

## Exemple de payload pour une requête PUT de mise à jour d'une cuve

```json
{
  "barremage": "[{\"hauteur_cm\": 0, \"volume_litres\": 0}, {\"hauteur_cm\": 10, \"volume_litres\": 500}, {\"hauteur_cm\": 20, \"volume_litres\": 1000}, {\"hauteur_cm\": 30, \"volume_litres\": 1500}, {\"hauteur_cm\": 40, \"volume_litres\": 2000}, {\"hauteur_cm\": 50, \"volume_litres\": 2500}, {\"hauteur_cm\": 60, \"volume_litres\": 3000}, {\"hauteur_cm\": 70, \"volume_litres\": 3500}, {\"hauteur_cm\": 80, \"volume_litres\": 4000}, {\"hauteur_cm\": 90, \"volume_litres\": 4500}, {\"hauteur_cm\": 100, \"volume_litres\": 5000}]"
}
```

## Remarque

Le champ `barremage` dans la requête doit être une chaîne de caractères JSON encodée. Le système décodera cette chaîne pour effectuer les calculs de volume via la méthode `calculer_volume` de la classe Cuve.