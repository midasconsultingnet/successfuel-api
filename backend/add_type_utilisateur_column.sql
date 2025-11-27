-- SQL script to add the type_utilisateur column to the utilisateurs table
-- Run this script in your PostgreSQL database to fix the admin login issue

-- Add the type_utilisateur column to the utilisateurs table
ALTER TABLE utilisateurs 
ADD COLUMN IF NOT EXISTS type_utilisateur VARCHAR(30) 
DEFAULT 'utilisateur_compagnie' 
CHECK (type_utilisateur IN ('super_administrateur', 'administrateur', 'gerant_compagnie', 'utilisateur_compagnie'));

-- Create an index on the new column for performance
CREATE INDEX IF NOT EXISTS idx_utilisateurs_type_utilisateur 
ON utilisateurs (type_utilisateur);

-- Update existing users to have a default type if they don't have one
UPDATE utilisateurs 
SET type_utilisateur = 'utilisateur_compagnie' 
WHERE type_utilisateur IS NULL;

-- For admin users that might already exist, you may want to set their type:
-- UPDATE utilisateurs 
-- SET type_utilisateur = 'administrateur' 
-- WHERE login IN ('admin', 'admin_login_here');