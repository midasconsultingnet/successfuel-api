from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.database import Base
from datetime import datetime
import uuid

class Pays(Base):
    __tablename__ = "pays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_pays = Column(String(3), unique=True, nullable=False)  # Ex: FRA, MDG, SEN, CIV
    nom_pays = Column(String(100), nullable=False)
    devise_principale = Column(String(3), nullable=False)  # Code ISO de la devise
    taux_tva_par_defaut = Column(Numeric(5,2), default=0)
    systeme_comptable = Column(String(50), default='OHADA')  # Ex: OHADA, FRANCE, etc.
    date_application_tva = Column(Date)
    statut = Column(String(20), default='Actif')  # CHECK (statut IN ('Actif', 'Inactif'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Compagnie(Base):
    __tablename__ = "compagnies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(150), nullable=False)
    adresse = Column(Text)
    telephone = Column(String(30))
    email = Column(String(150))
    nif = Column(String(50))  # Numéro d'identification fiscale
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    devise_principale = Column(String(3), default='MGA')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Module(Base):
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    libelle = Column(String(100), unique=True, nullable=False)
    statut = Column(String(20), default='Actif')  # CHECK (statut IN ('Actif', 'Inactif'))

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    libelle = Column(String(100), nullable=False)  # Ex: 'lire_ventes', 'creer_vente', 'modifier_vente', 'supprimer_vente'
    description = Column(Text)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"))
    statut = Column(String(20), default='Actif')  # CHECK (statut IN ('Actif', 'Inactif'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Profil(Base):
    __tablename__ = "profils"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    libelle = Column(String(100), nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # La compagnie qui a créé le profil
    description = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ProfilPermission(Base):
    __tablename__ = "profil_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profil_id = Column(UUID(as_uuid=True), ForeignKey("profils.id"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False)

class Station(Base):
    __tablename__ = "stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    telephone = Column(String(30))
    email = Column(String(150))
    adresse = Column(Text)
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(50), unique=True, nullable=False)
    mot_de_passe = Column(Text, nullable=False)
    nom = Column(String(150), nullable=False)
    profil_id = Column(UUID(as_uuid=True), ForeignKey("profils.id"))
    email = Column(String(150))
    telephone = Column(String(30))
    stations_user = Column(JSONB, default=[])  # Liste des UUID des stations auxquelles l'utilisateur a accès
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    last_login = Column(DateTime(timezone=True))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class FamilleArticle(Base):
    __tablename__ = "familles_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(100), nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle la famille d'articles appartient
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("familles_articles.id"))  # Référence à la famille parente (NULL si racine)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class PlanComptable(Base):
    __tablename__ = "plan_comptable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(20), unique=True, nullable=False)  # Numéro de compte comptable (ex: 100000)
    intitule = Column(String(255), nullable=False)  # Nom du compte (ex: Capital & Réserves)
    classe = Column(String(5), nullable=False)  # Classe comptable (ex: 1, 2, etc.)
    type_compte = Column(String(100), nullable=False)  # Type de compte (ex: Capitaux Propres)
    sens_solde = Column(String(10))  # CHECK (sens_solde IN ('D', 'C')) # Sens de solde
    compte_parent_id = Column(UUID(as_uuid=True), ForeignKey("plan_comptable.id"))  # Lien vers le compte parent
    description = Column(Text)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    est_compte_racine = Column(Boolean, default=False)
    est_compte_de_resultat = Column(Boolean, default=False)
    est_compte_actif = Column(Boolean, default=True)
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    est_specifique_pays = Column(Boolean, default=False)
    code_pays = Column(String(3))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TypeTiers(Base):
    __tablename__ = "type_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    libelle = Column(String(100), nullable=False)
    num_compte = Column(String(10))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle l'article appartient
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(40), unique=True, nullable=False)
    libelle = Column(String(150), nullable=False)
    codebarre = Column(String(100), unique=True)
    famille_id = Column(UUID(as_uuid=True), ForeignKey("familles_articles.id"))
    unite = Column(String(20), default='Litre')
    # unite_principale = Column(String(10), ForeignKey("unites_mesure.code_unite"))
    # unite_stock = Column(String(10), ForeignKey("unites_mesure.code_unite"))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle l'article appartient
    type_article = Column(String(20), default='produit')  # CHECK (type_article IN ('produit', 'service'))
    prix_achat = Column(Numeric(18,4), default=0)
    prix_vente = Column(Numeric(18,4), default=0)
    tva = Column(Numeric(5,2), default=0)
    taxes_applicables = Column(JSONB, default=[])  # Liste des IDs de taxes
    stock_minimal = Column(Numeric(18,3), default=0)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Carburant(Base):
    __tablename__ = "carburants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(40), unique=True, nullable=False)
    libelle = Column(String(150), nullable=False)
    type = Column(String(50), nullable=False)  # Ex: "Essence", "Gasoil", "Pétrole"
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    prix_achat = Column(Numeric(18,4), default=0)
    prix_vente = Column(Numeric(18,4), default=0)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Cuve(Base):
    __tablename__ = "cuves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    code = Column(String(40), nullable=False)
    capacite = Column(Numeric(18,3), nullable=False)  # CHECK (capacite >= 0)
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburants.id"))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle la cuve appartient (via la station)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Pompe(Base):
    __tablename__ = "pompes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    code = Column(String(40), unique=True, nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle la pompe appartient (via la cuve/station)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Pistolet(Base):
    __tablename__ = "pistolets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(40), nullable=False)
    pompe_id = Column(UUID(as_uuid=True), ForeignKey("pompes.id"))
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"), nullable=False)
    index_initiale = Column(Numeric(18,3), default=0)  # Index initial du pistolet
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle le pistolet appartient (via la cuve/station)
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(150), nullable=False)
    adresse = Column(Text)
    telephone = Column(String(30))
    nif = Column(String(50))
    email = Column(String(150))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle le client appartient
    station_ids = Column(JSONB, default=[])  # Optionnel : station à laquelle le client est rattaché
    type_tiers_id = Column(UUID(as_uuid=True), ForeignKey("type_tiers.id"))
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    nb_jrs_creance = Column(Integer, default=0)
    solde_comptable = Column(Numeric(18,2), default=0)  # Solde actuel du client
    solde_confirme = Column(Numeric(18,2), default=0)  # Solde confirmé lors des rapprochements
    date_dernier_rapprochement = Column(DateTime(timezone=True))  # Dernière date de rapprochement
    devise_facturation = Column(String(3), default='MGA')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(150), nullable=False)
    adresse = Column(Text)
    telephone = Column(String(30))
    nif = Column(String(50))
    email = Column(String(150))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle le fournisseur appartient
    station_ids = Column(JSONB, default=[])  # Optionnel : station à laquelle le fournisseur est rattaché
    type_tiers_id = Column(UUID(as_uuid=True), ForeignKey("type_tiers.id"))
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    nb_jrs_creance = Column(Integer, default=0)
    solde_comptable = Column(Numeric(18,2), default=0)  # Solde actuel du fournisseur
    solde_confirme = Column(Numeric(18,2), default=0)  # Solde confirmé lors des rapprochements
    date_dernier_rapprochement = Column(DateTime(timezone=True))  # Dernière date de rapprochement
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Employe(Base):
    __tablename__ = "employes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(150), nullable=False)
    prenom = Column(String(150))
    adresse = Column(Text)
    telephone = Column(String(30))
    poste = Column(String(100))  # Poste occupé (ex: pompiste, caissier, etc.)
    salaire_base = Column(Numeric(18,2), default=0)
    station_ids = Column(JSONB, default=[])  # Liste des stations auxquelles l'employé est rattaché
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle l'employé appartient
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MethodePaiement(Base):
    __tablename__ = "methode_paiment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_tresorerie = Column(String(100), nullable=False)
    mode_paiement = Column(JSONB, default=[])
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Tresorerie(Base):
    __tablename__ = "tresoreries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    libelle = Column(String(100), nullable=False)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))  # Compagnie à laquelle la trésorerie appartient
    station_ids = Column(JSONB, default=[])  # Optionnel : station à laquelle la trésorerie est rattachée
    solde = Column(Numeric(18,2), default=0)  # CHECK (solde >= -1000000000)
    devise_code = Column(String(3), default='MGA')
    taux_change = Column(Numeric(15,6), default=1.000000)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    type_tresorerie = Column(UUID(as_uuid=True), ForeignKey("methode_paiment.id"))
    methode_paiement = Column(JSONB, default=[])
    statut = Column(String(20), default='Actif', nullable=False)  # CHECK (statut IN ('Actif', 'Inactif', 'Supprime'))
    solde_theorique = Column(Numeric(18,2), default=0)  # Solde recalculé à partir des mouvements
    solde_reel = Column(Numeric(18,2), default=0)  # Solde réel vérifié (par exemple lors des rapprochements)
    date_dernier_rapprochement = Column(DateTime(timezone=True))  # Dernière date de rapprochement
    utilisateur_dernier_rapprochement = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))  # Utilisateur qui a effectué le dernier rapprochement
    type_tresorerie_libelle = Column(String(50))  # Pour identifier la caisse boutique/principale, etc.
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)