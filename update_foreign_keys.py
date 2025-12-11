import os
import re

def update_foreign_key_references():
    """Update all foreign key references from 'users' to 'utilisateur' in model files"""

    models_directory = r"D:\succes_fuel_v2\api\models"

    # Get all Python files in the models directory
    for filename in os.listdir(models_directory):
        if filename.endswith(".py") and filename != "base.py":
            filepath = os.path.join(models_directory, filename)

            # Read the file content
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Replace "users.id" with "utilisateur.id" in ForeignKey definitions
            updated_content = re.sub(
                r'ForeignKey\("users\.id"\)',
                'ForeignKey("utilisateur.id")',
                content
            )

            # Write the updated content back to the file if changes were made
            if content != updated_content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print(f"Updated foreign key in {filename}")
            else:
                print(f"No foreign key updates needed in {filename}")

if __name__ == "__main__":
    update_foreign_key_references()