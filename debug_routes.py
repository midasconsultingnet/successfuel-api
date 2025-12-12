#!/usr/bin/env python3
"""
Script de débogage pour identifier la route problématique causant l'erreur FastAPI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_routes():
    """Vérifier chaque route pour identifier laquelle cause l'erreur"""
    try:
        print("Chargement de l'API pour identifier la route problématique...")
        
        # Importation progressive pour identifier le problème
        from api.main import app
        
        print(f"L'application FastAPI a été chargée avec succès !")
        print(f"Nombre de routes : {len(app.routes)}")
        
        # Afficher les routes
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                print(f"Méthode: {route.methods}, Chemin: {route.path}")
                
        return True
    except Exception as e:
        print(f"Erreur lors du chargement de l'application: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Démarrage du débogage des routes FastAPI...")
    success = check_routes()
    
    if success:
        print("\nToutes les routes semblent valides.")
    else:
        print("\nDes erreurs ont été détectées dans les routes.")

if __name__ == "__main__":
    main()