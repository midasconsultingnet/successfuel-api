from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

class EtatFinancierService:
    def generer_grand_livre(self, db: Session, compagnie_id, date_debut, date_fin):
        """Générer le grand livre pour une période"""
        result = db.execute(text("""
            SELECT * FROM grand_livre_avec_solde
            WHERE compagnie_id = :compagnie_id
              AND date_ecriture BETWEEN :debut AND :fin
            ORDER BY numero_compte, date_ecriture, ecriture_id
        """), {
            "compagnie_id": str(compagnie_id),
            "debut": date_debut,
            "fin": date_fin
        })
        
        return result.fetchall()
    
    def generer_compte_resultat(self, db: Session, compagnie_id, date_debut, date_fin):
        """Générer le compte de résultat pour une période"""
        result = db.execute(text("""
            SELECT * FROM compte_resultat
            WHERE compagnie_id = :compagnie_id
              AND (:debut IS NULL OR :fin IS NULL OR EXISTS (
                  SELECT 1 FROM grand_livre 
                  WHERE compte_id = compte_id 
                    AND date_ecriture BETWEEN :debut AND :fin
              ))
        """), {
            "compagnie_id": str(compagnie_id),
            "debut": date_debut,
            "fin": date_fin
        })
        
        return result.fetchall()
    
    def generer_bilan(self, db: Session, compagnie_id, date_fin):
        """Générer le bilan pour une date donnée"""
        result = db.execute(text("""
            SELECT * FROM bilan_comptable
            WHERE compagnie_id = :compagnie_id
        """), {"compagnie_id": str(compagnie_id)})
        
        return result.fetchall()
    
    def generer_bilan_consolide(self, db: Session, compagnie_id):
        """Générer le bilan consolidé pour une compagnie"""
        result = db.execute(text("""
            SELECT * FROM bilan_consolide
            WHERE compagnie_id = :compagnie_id
        """), {"compagnie_id": str(compagnie_id)})
        
        return result.fetchone()