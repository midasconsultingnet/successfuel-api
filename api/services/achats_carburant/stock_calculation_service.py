from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Tuple
from datetime import datetime
from uuid import UUID
import logging

from ...models import Livraison, Cuve, EtatInitialCuve, MouvementStockCuve, AchatCarburant, LigneAchatCarburant, CompensationFinanciere
from ...models.achat_carburant import AvoirCompensation


class StockCalculationService:
    """
    Service pour gérer les calculs de stock théorique et les compensations automatiques
    basées sur les écarts entre quantités commandées et reçues.
    """
    
    @staticmethod
    def calculer_stock_theorique_apres_livraison(
        db: Session, 
        cuve_id: UUID, 
        date_livraison: datetime
    ) -> Dict[str, Any]:
        """
        Calcule le stock théorique d'une cuve à une date donnée en se basant 
        sur l'état initial et toutes les livraisons effectuées jusqu'à cette date.
        """
        try:
            # Récupérer l'état initial de la cuve
            etat_initial = db.query(EtatInitialCuve).filter(
                EtatInitialCuve.cuve_id == cuve_id
            ).first()
            
            if not etat_initial:
                raise ValueError(f"Aucun état initial trouvé pour la cuve {cuve_id}")
            
            # Calculer le volume total des livraisons après l'état initial jusqu'à la date spécifiée
            livraisons = db.query(Livraison).filter(
                Livraison.cuve_id == cuve_id,
                Livraison.date >= etat_initial.date_initialisation,
                Livraison.date <= date_livraison
            ).all()
            
            # Calculer le volume total livré
            volume_total_livre = sum(livraison.quantite_livree for livraison in livraisons)
            
            # Calculer le stock théorique
            stock_theorique = float(etat_initial.volume_initial_calcule) + volume_total_livre
            
            # Récupérer les mouvements de sortie pour soustraire
            mouvements_sortie = db.query(MouvementStockCuve).filter(
                MouvementStockCuve.cuve_id == cuve_id,
                MouvementStockCuve.date_mouvement >= etat_initial.date_initialisation,
                MouvementStockCuve.date_mouvement <= date_livraison,
                MouvementStockCuve.type_mouvement == 'sortie'
            ).all()
            
            volume_total_sortie = sum(mvt.quantite for mvt in mouvements_sortie)
            
            # Calculer le stock théorique final
            stock_theorique -= volume_total_sortie
            
            # Récupérer les mouvements d'ajustement
            mouvements_ajustement = db.query(MouvementStockCuve).filter(
                MouvementStockCuve.cuve_id == cuve_id,
                MouvementStockCuve.date_mouvement >= etat_initial.date_initialisation,
                MouvementStockCuve.date_mouvement <= date_livraison,
                MouvementStockCuve.type_mouvement == 'ajustement'
            ).all()
            
            volume_total_ajust = sum(mvt.quantite for mvt in mouvements_ajustement)
            stock_theorique += volume_total_ajust  # Ajouter les ajustements positifs, soustraire les négatifs
            
            return {
                "cuve_id": cuve_id,
                "date_calculee": date_livraison,
                "stock_theorique": stock_theorique,
                "volume_initial": float(etat_initial.volume_initial_calcule),
                "volume_total_livre": volume_total_livre,
                "volume_total_sortie": volume_total_sortie,
                "volume_total_ajustement": volume_total_ajust
            }
        except Exception as e:
            logging.error(f"Erreur lors du calcul du stock théorique: {str(e)}")
            raise e

    @staticmethod
    def verifier_et_creer_compensations_automatiques(db: Session, livraison_id: UUID):
        """
        Vérifie s'il y a des écarts entre les quantités commandées et livrées
        et crée automatiquement des compensations si nécessaires.
        """
        try:
            # Récupérer la livraison
            livraison = db.query(Livraison).filter(Livraison.id == livraison_id).first()
            if not livraison:
                raise ValueError(f"Livraison {livraison_id} non trouvée")
            
            # Récupérer les achats carburants associés (via les lignes d'achat et les cuves)
            # Pour cela, on cherche les lignes d'achat carburant qui concernent la même cuve et la même période
            lignes_achat = db.query(LigneAchatCarburant).filter(
                LigneAchatCarburant.cuve_id == livraison.cuve_id
            ).join(AchatCarburant).filter(
                AchatCarburant.date_achat <= livraison.date
            ).order_by(AchatCarburant.date_achat.desc()).first()
            
            if not lignes_achat:
                logging.info(f"Aucun achat associé trouvé pour la cuve {livraison.cuve_id}")
                return
            
            achat_associe = db.query(AchatCarburant).filter(
                AchatCarburant.id == lignes_achat.achat_carburant_id
            ).first()
            
            if not achat_associe:
                logging.info(f"Aucun achat associé trouvé pour la ligne {lignes_achat.id}")
                return
            
            # Comparer les quantités théoriques et réelles
            quantite_commandee = lignes_achat.quantite
            quantite_livree = livraison.quantite_livree
            
            difference_quantite = quantite_livree - quantite_commandee
            
            # Si la différence est significative, créer une compensation
            seuil_tolerance = 0.05  # 5% de tolérance
            if abs(difference_quantite / quantite_commandee) > seuil_tolerance:
                # Calculer le montant de compensation
                montant_unitaire = lignes_achat.prix_unitaire
                montant_compensation = abs(difference_quantite) * montant_unitaire
                
                # Déterminer le type de compensation
                type_compensation = "avoir_reçu" if difference_quantite < 0 else "avoir_dû"
                
                # Créer la compensation financière
                compensation = CompensationFinanciere(
                    achat_carburant_id=achat_associe.id,
                    type_compensation=type_compensation,
                    quantite_theorique=quantite_commandee,
                    quantite_reelle=quantite_livree,
                    difference=difference_quantite,
                    montant_compensation=montant_compensation,
                    motif=f"Écart constaté lors de la livraison {livraison.numero_bl or livraison.id}",
                    date_emission=datetime.utcnow()
                )
                
                db.add(compensation)
                db.commit()
                
                # Créer l'avoir de compensation correspondant
                avoir_compensation = AvoirCompensation(
                    compensation_financiere_id=compensation.id,
                    tiers_id=achat_associe.fournisseur_id,
                    montant=montant_compensation,
                    date_emission=datetime.utcnow(),
                    statut="émis",
                    utilisateur_emission_id=livraison.utilisateur_id
                )
                
                db.add(avoir_compensation)
                db.commit()
                
                logging.info(f"Compensation automatique créée pour la livraison {livraison_id}")
                
                return compensation
            else:
                logging.info(f"Pas de compensation nécessaire pour la livraison {livraison_id}, écart dans la tolérance")
                return None
        except Exception as e:
            logging.error(f"Erreur lors de la vérification des compensations automatiques: {str(e)}")
            db.rollback()
            raise e

    @staticmethod
    def verifier_ecarts_livraison_achat(db: Session, livraison_id: UUID) -> Dict[str, Any]:
        """
        Vérifie les écarts entre les quantités prévues dans les commandes et les quantités réellement livrées.
        """
        try:
            # Récupérer la livraison
            livraison = db.query(Livraison).filter(Livraison.id == livraison_id).first()
            if not livraison:
                raise ValueError(f"Livraison {livraison_id} non trouvée")

            # Récupérer les achats carburants potentiels pour cette cuve dans la période proche
            from datetime import timedelta
            date_min = livraison.date - timedelta(days=3)  # 3 jours avant
            date_max = livraison.date + timedelta(days=3)  # 3 jours après

            achats_possibles = db.query(AchatCarburant).join(
                LigneAchatCarburant
            ).filter(
                LigneAchatCarburant.cuve_id == livraison.cuve_id,
                AchatCarburant.date_achat >= date_min,
                AchatCarburant.date_achat <= date_max
            ).all()

            resultats = []
            for achat in achats_possibles:
                lignes_achat = db.query(LigneAchatCarburant).filter(
                    LigneAchatCarburant.achat_carburant_id == achat.id,
                    LigneAchatCarburant.cuve_id == livraison.cuve_id
                ).all()

                for ligne in lignes_achat:
                    ecart = {
                        "achat_id": achat.id,
                        "ligne_achat_id": ligne.id,
                        "quantite_commandee": float(ligne.quantite),
                        "quantite_livree": float(livraison.quantite_livree),
                        "ecart_absolu": abs(float(ligne.quantite) - float(livraison.quantite_livree)),
                        "ecart_pourcentage": abs((float(ligne.quantite) - float(livraison.quantite_livree)) / float(ligne.quantite)) * 100 if float(ligne.quantite) != 0 else 0
                    }
                    resultats.append(ecart)

            return {
                "livraison_id": livraison_id,
                "resultats_verification": resultats
            }
        except Exception as e:
            logging.error(f"Erreur lors de la vérification des écarts livraison-achat: {str(e)}")
            raise e

    @staticmethod
    def calculer_stock_theorique_cuve_complet(
        db: Session,
        cuve_id: UUID,
        date_calculee: datetime
    ) -> Dict[str, Any]:
        """
        Calcule le stock théorique d'une cuve à une date donnée en se basant
        sur l'état initial, les livraisons et les ventes effectuées jusqu'à cette date.
        """
        try:
            # Récupérer l'état initial de la cuve
            etat_initial = db.query(EtatInitialCuve).filter(
                EtatInitialCuve.cuve_id == cuve_id
            ).first()

            if not etat_initial:
                raise ValueError(f"Aucun état initial trouvé pour la cuve {cuve_id}")

            # Calculer le volume total des livraisons après l'état initial jusqu'à la date spécifiée
            livraisons = db.query(Livraison).filter(
                Livraison.cuve_id == cuve_id,
                Livraison.date >= etat_initial.date_initialisation,
                Livraison.date <= date_calculee
            ).all()

            # Calculer le volume total livré
            volume_total_livre = sum(livraison.quantite_livree for livraison in livraisons)

            # Calculer le volume total des ventes de carburant pour cette cuve
            # On utilise les mouvements de stock pour obtenir les ventes
            ventes = db.query(MouvementStockCuve).filter(
                MouvementStockCuve.cuve_id == cuve_id,
                MouvementStockCuve.vente_carburant_id.isnot(None),  # Ajustement pour sélectionner les mouvements liés aux ventes
                MouvementStockCuve.date_mouvement >= etat_initial.date_initialisation,
                MouvementStockCuve.date_mouvement <= date_calculee,
                MouvementStockCuve.type_mouvement == 'sortie'
            ).all()

            volume_total_vendu = sum(mvt.quantite for mvt in ventes)

            # Calculer le stock théorique
            stock_theorique = float(etat_initial.volume_initial_calcule) + volume_total_livre - volume_total_vendu

            # Récupérer les mouvements d'autres types (inventaire, ajustement) pour la correction
            mouvements_autres = db.query(MouvementStockCuve).filter(
                MouvementStockCuve.cuve_id == cuve_id,
                MouvementStockCuve.date_mouvement >= etat_initial.date_initialisation,
                MouvementStockCuve.date_mouvement <= date_calculee,
                MouvementStockCuve.type_mouvement != 'sortie',  # Exclure les sorties (ventes)
                MouvementStockCuve.type_mouvement != 'entrée'   # Exclure les entrées (livraisons)
            ).all()

            # Calculer les ajustements
            volume_total_ajust = 0
            for mvt in mouvements_autres:
                if mvt.type_mouvement == 'ajustement':
                    volume_total_ajust += float(mvt.quantite)  # Ajouter les ajustements positifs, soustraire les négatifs

            stock_theorique += volume_total_ajust

            return {
                "cuve_id": cuve_id,
                "date_calculee": date_calculee,
                "stock_theorique": stock_theorique,
                "volume_initial": float(etat_initial.volume_initial_calcule),
                "volume_total_livre": volume_total_livre,
                "volume_total_vendu": volume_total_vendu,
                "volume_total_ajustement": volume_total_ajust,
                "details": {
                    "nombre_livraisons": len(livraisons),
                    "nombre_ventes": len(ventes),
                    "nombre_ajustements": len(mouvements_autres)
                }
            }
        except Exception as e:
            logging.error(f"Erreur lors du calcul complet du stock théorique: {str(e)}")
            raise e