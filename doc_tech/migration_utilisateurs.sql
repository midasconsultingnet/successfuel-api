-- Migration pour ajouter la gestion des types d'utilisateurs dans SuccessFuel

-- 1. Ajouter la colonne type_utilisateur à la table utilisateurs
ALTER TABLE utilisateurs 
ADD COLUMN IF NOT EXISTS type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' 
CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie'));

-- 2. Mettre à jour les utilisateurs existants avec un type par défaut (facultatif selon votre cas)
-- UPDATE utilisateurs SET type_utilisateur = 'administrateur' WHERE profil_id IN (
--    SELECT id FROM profils WHERE libelle LIKE '%admin%'
-- );

-- 3. Ajouter un index pour améliorer les performances de recherche par type d'utilisateur
CREATE INDEX IF NOT EXISTS idx_utilisateurs_type ON utilisateurs(type_utilisateur);

-- 4. Modifier la table auth_tokens pour distinguer les endpoints
ALTER TABLE auth_tokens 
ADD COLUMN IF NOT EXISTS type_endpoint VARCHAR(20) DEFAULT 'utilisateur' 
CHECK (type_endpoint IN ('administrateur', 'utilisateur'));

-- 5. Ajouter un index pour améliorer les performances de recherche par type d'endpoint
CREATE INDEX IF NOT EXISTS idx_auth_tokens_endpoint ON auth_tokens(type_endpoint);

-- 6. Créer la table tentatives_acces_non_autorise pour suivre les tentatives d'accès interdites
CREATE TABLE IF NOT EXISTS tentatives_acces_non_autorise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID REFERENCES utilisateurs(id),
    endpoint_accesse VARCHAR(20) NOT NULL,
    endpoint_autorise VARCHAR(20),
    ip_connexion VARCHAR(45),
    statut VARCHAR(20) DEFAULT 'Traite' CHECK (statut IN ('EnAttente', 'Traite', 'Enquete')),
    compagnie_id UUID REFERENCES compagnies(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. Ajouter des indexes pour les analyses de sécurité
CREATE INDEX IF NOT EXISTS idx_tentatives_acces_non_autorise_date ON tentatives_acces_non_autorise(created_at);
CREATE INDEX IF NOT EXISTS idx_tentatives_acces_non_autorise_utilisateur ON tentatives_acces_non_autorise(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_tentatives_acces_non_autorise_endpoint ON tentatives_acces_non_autorise(endpoint_accesse);

-- 8. Mettre à jour la table tentatives_connexion pour inclure le type d'endpoint et le type d'utilisateur
ALTER TABLE tentatives_connexion 
ADD COLUMN IF NOT EXISTS type_endpoint VARCHAR(20) DEFAULT 'utilisateur' 
CHECK (type_endpoint IN ('administrateur', 'utilisateur')),
ADD COLUMN IF NOT EXISTS type_utilisateur VARCHAR(30) DEFAULT 'utilisateur_compagnie' 
CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie'));

-- 9. Ajouter des indexes pour filtrer par type d'endpoint et type d'utilisateur
CREATE INDEX IF NOT EXISTS idx_tentatives_connexion_endpoint ON tentatives_connexion(type_endpoint);
CREATE INDEX IF NOT EXISTS idx_tentatives_connexion_type ON tentatives_connexion(type_utilisateur);

-- 10. Mettre à jour le champ updated_at pour les tables concernées
-- Ajouter un trigger pour la table utilisateurs si ce n'est pas déjà fait
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Créer le trigger pour la table utilisateurs
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_utilisateurs_updated_at') THEN
        CREATE TRIGGER update_utilisateurs_updated_at
            BEFORE UPDATE ON utilisateurs
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;