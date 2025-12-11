#!/usr/bin/env python3
"""
Script pour compiler les fichiers .po en .mo sans avoir besoin de msgfmt
"""
import os
from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

def compile_po_to_mo(po_path, mo_path):
    """Compile un fichier .po en .mo"""
    with open(po_path, 'rb') as po_file:
        catalog = read_po(po_file)
    
    with open(mo_path, 'wb') as mo_file:
        write_mo(mo_file, catalog)

if __name__ == "__main__":
    # Compile les fichiers PO dans MO
    locales = ['fr', 'en']
    
    for locale in locales:
        po_path = f"locale/{locale}/LC_MESSAGES/messages.po"
        mo_path = f"locale/{locale}/LC_MESSAGES/messages.mo"
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(mo_path), exist_ok=True)
        
        # Compiler
        compile_po_to_mo(po_path, mo_path)
        print(f"Compilé {po_path} -> {mo_path}")