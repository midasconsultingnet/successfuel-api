from sqlalchemy import Column, String, Integer, DateTime, Boolean, Numeric, Text, Date, Time, ForeignKey, CheckConstraint
from sqlalchemy.schema import CheckConstraint as SchemaCheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text
from database.database import Base
from datetime import datetime
import uuid

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"), nullable=True)  # Pour les carburants
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    stock_theorique = Column(Numeric(18,3), default=0)
    stock_reel = Column(Numeric(18,3), default=0)
    # Le champ ecart_stock est calculé dans la base de données comme (stock_reel - stock_theorique)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    est_initial = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Champs qui seront ajoutés via le script d'initialisation
    # stock_minimal = Column(Numeric(18,3), default=0)
    # stock_maximal = Column(Numeric(18,3), default=0)
    # prix_unitaire = Column(Numeric(18,4), default=0)
    # date_initialisation = Column(Date)
    # utilisateur_initialisation = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    # observation_initialisation = Column(Text)

    __table_args__ = (
        SchemaCheckConstraint("stock_theorique >= 0", name="stocks_stock_theorique_check"),
        SchemaCheckConstraint("stock_reel >= 0", name="stocks_stock_reel_check"),
    )


# Modèle pour l'analyse de la qualité du carburant initial
class QualiteCarburantInitial(Base):
    __tablename__ = "qualite_carburant_initial"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    carburant_id = Column(UUID(as_uuid=True), ForeignKey("carburants.id"))
    date_analyse = Column(Date, nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    densite = Column(Numeric(8,4))  # Ex: 0.8350 kg/L
    indice_octane = Column(Integer)  # Ex: 95 pour SP95
    soufre_ppm = Column(Numeric(10,2))  # Partie par million
    type_additif = Column(String(100))  # Type d'additif utilisé
    commentaire_qualite = Column(Text)
    resultat_qualite = Column(String(20))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        SchemaCheckConstraint("resultat_qualite IN ('Conforme', 'Non conforme', 'En attente')", name="check_resultat_qualite"),
    )


# Modèle pour l'analyse des coûts logistiques initiaux
class CoutLogistiqueStockInitial(Base):
    __tablename__ = "couts_logistique_stocks_initial"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_cout = Column(String(50), nullable=False)  # 'transport', 'stockage', 'manutention', 'assurance', 'autres'
    description = Column(Text)
    montant = Column(Numeric(18,2), nullable=False)
    date_cout = Column(Date, nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"))
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"))
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    utilisateur_saisie_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# Modèle pour le bilan initial global
class BilanInitialStocks(Base):
    __tablename__ = "bilan_initial_stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    date_bilan = Column(Date, nullable=False)
    commentaire = Column(Text)
    valeur_totale_stocks = Column(Numeric(18,2), default=0)
    nombre_elements = Column(Integer, default=0)
    statut = Column(String(20), default='Brouillon')
    utilisateur_validation_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    date_validation = Column(Date)
    est_valide = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        SchemaCheckConstraint("statut IN ('Brouillon', 'En cours', 'Termine', 'Validé')", name="check_bilan_initial_stocks_statut"),
    )


# Modèle pour les lignes du bilan initial
class BilanInitialStocksLigne(Base):
    __tablename__ = "bilan_initial_stocks_lignes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bilan_initial_stocks_id = Column(UUID(as_uuid=True), ForeignKey("bilan_initial_stocks.id"), nullable=False)
    type_element = Column(String(20), nullable=False)
    element_id = Column(UUID(as_uuid=True), nullable=False)  # ID de la cuve ou de l'article
    description_element = Column(Text)
    quantite = Column(Numeric(18,3), nullable=False)
    unite_mesure = Column(String(10))
    prix_unitaire = Column(Numeric(18,4), nullable=False)
    valeur_totale = Column(Numeric(18,2))  # Générée à partir de quantité * prix_unitaire
    taux_tva = Column(Numeric(5,2), default=0)
    montant_tva = Column(Numeric(18,2))
    montant_ht = Column(Numeric(18,2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        SchemaCheckConstraint("type_element IN ('carburant', 'article_boutique', 'autre')", name="check_type_element_bilan_initial_stocks_ligne"),
    )


class StockMouvement(Base):
    __tablename__ = "stocks_mouvements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"), nullable=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    type_mouvement = Column(String(20), nullable=False)
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)  # Pour calcul CUMP
    cout_total = Column(Numeric(18,2))
    date_mouvement = Column(Date, nullable=False)
    reference_operation = Column(String(100))  # Référence à l'opération d'origine
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    commentaire = Column(Text)
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    valeur_stock_avant = Column(Numeric(18,2), default=0)  # Valeur du stock avant le mouvement
    valeur_stock_apres = Column(Numeric(18,2), default=0)  # Valeur du stock après le mouvement
    cout_unitaire_moyen_apres = Column(Numeric(18,4), default=0)  # CUMP après le mouvement
    est_initial = Column(Boolean, default=False)
    operation_initialisation_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        SchemaCheckConstraint("type_mouvement IN ('Entree', 'Sortie', 'Ajustement', 'Inventaire', 'Initial')", name="check_type_mouvement_valid"),
    )


class MouvementStock(Base):
    __tablename__ = "mouvements_stock"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    type_mouvement = Column(String(20), nullable=False)  # 'Entree', 'Sortie', 'Transfert', 'Ajustement'
    article_id = Column(UUID(as_uuid=True), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    fournisseur_id = Column(UUID(as_uuid=True), ForeignKey("fournisseurs.id"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    date_mouvement = Column(Date, nullable=False)
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    observation = Column(Text)
    reference_externe = Column(String(100))
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    pays_id = Column(UUID(as_uuid=True), ForeignKey("pays.id"))
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MouvementStockDetail(Base):
    __tablename__ = "mouvements_stock_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mouvement_id = Column(UUID(as_uuid=True), ForeignKey("mouvements_stock.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Inventaire(Base):
    __tablename__ = "inventaire"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    date_inventaire = Column(Date, nullable=False)
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    type_inventaire = Column(String(20), default='Complet')  # 'Complet', 'Partiel', 'Spécial'
    observation = Column(Text)
    statut = Column(String(20), default='En cours')  # 'En cours', 'Terminé', 'Annulé'
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class InventaireDetail(Base):
    __tablename__ = "inventaire_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventaire_id = Column(UUID(as_uuid=True), ForeignKey("inventaire.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    stock_theorique = Column(Numeric(18,3), default=0)
    stock_reel = Column(Numeric(18,3), default=0)
    ecart = Column(Numeric(18,3), default=0)
    observation = Column(Text)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class TransfertStock(Base):
    __tablename__ = "transfert_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, nullable=False)
    date_transfert = Column(Date, nullable=False)
    heure_transfert = Column(Time, nullable=False)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"))
    station_origine_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    station_destination_id = Column(UUID(as_uuid=True), ForeignKey("stations.id"), nullable=False)
    observation = Column(Text)
    statut = Column(String(20), default='En cours')  # 'En cours', 'Terminé', 'Annulé'
    compagnie_id = Column(UUID(as_uuid=True), ForeignKey("compagnies.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TransfertStockDetail(Base):
    __tablename__ = "transfert_stock_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transfert_id = Column(UUID(as_uuid=True), ForeignKey("transfert_stock.id"), nullable=False)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    cuve_origine_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    cuve_destination_id = Column(UUID(as_uuid=True), ForeignKey("cuves.id"))
    quantite = Column(Numeric(18,3), nullable=False)
    prix_unitaire = Column(Numeric(18,4), default=0)
    valeur_totale = Column(Numeric(18,2), default=0)
    statut = Column(String(20), default='Actif')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)