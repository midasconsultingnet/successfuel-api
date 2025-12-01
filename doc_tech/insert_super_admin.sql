-- Requête pour créer un super administrateur
INSERT INTO utilisateurs (
    login, 
    mot_de_passe, 
    nom, 
    profil_id, 
    email, 
    type_utilisateur, 
    statut, 
    compagnie_id
) VALUES (
    'super', 
    '$2b$12$L6bHr4j6w9l3b5n7u8v2xoy3z7r5t6y4u9i8o7p6n5m4l3k2j1h0g', 
    'Super Administrateur', 
    NULL, 
    'super@entreprise.com', 
    'super_administrateur', 
    'Actif', 
    NULL
);