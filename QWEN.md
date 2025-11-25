# SuccessFuel — ERP pour stations-service à Madagascar

### Technologies utilisées
- **Backend** : Python, FastAPI (migration en cours), Werkzeug (v3.0.6)
- **Base de données** : PostgreSQL (avec psycopg2-binary)
- **Authentification** : PyJWT (v2.8.0), bcrypt
- **Déploiement** : Gunicorn (v22.0.0)
- **Sécurité** : Flask-CORS (v4.0.2)
- **Formatage** : autopep8
- **GraphQL** : Strawberry-GraphQL (v0.240.2) pour les requêtes flexibles
- **API** : RESTful et GraphQL pour une meilleure expérience de développement

### Nouvelles fonctionnalités
- **API GraphQL** : Accès flexible aux données avec Strawberry-GraphQL
- **Architecture modulaire** : Structure bien organisée pour la maintenance et l'extension
- **Types GraphQL** : Pour tous les modules (structures, achats, ventes, stocks, trésorerie, comptabilité)
- **Résolveurs GraphQL** : Pour toutes les opérations de lecture
