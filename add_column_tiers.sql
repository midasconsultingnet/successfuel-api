-- Ajouter la colonne manquante donnees_personnelles à la table tiers
ALTER TABLE tiers ADD COLUMN IF NOT EXISTS donnees_personnelles JSONB;

-- Ajouter la colonne manquante station_ids à la table tiers
ALTER TABLE tiers ADD COLUMN IF NOT EXISTS station_ids JSONB DEFAULT '[]';

-- Ajouter la colonne manquante metadonnees à la table tiers
ALTER TABLE tiers ADD COLUMN IF NOT EXISTS metadonnees JSONB;