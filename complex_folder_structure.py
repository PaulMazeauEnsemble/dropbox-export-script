import dropbox
import csv
import os

ACCESS_TOKEN = ''

dbx = dropbox.Dropbox(ACCESS_TOKEN)

# Fonction pour lister les fichiers d'un sous-dossier de prénom
def list_person_files(folder):
    files_info = {'mp3': {}, 'image': None}
    
    try:
        result = dbx.files_list_folder(folder)
        print(f"Exploration du dossier : {folder}")
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                # Récupère l'image
                if entry.name.endswith(('.jpg', '.jpeg', '.png')):
                    image_link = dbx.files_get_temporary_link(entry.path_lower).link
                    files_info['image'] = image_link
                    print(f"Image trouvée : {entry.name} - {files_info['image']}")
            elif isinstance(entry, dropbox.files.FolderMetadata):
                # Explorer les sous-dossiers VA et VF
                subfolder_result = dbx.files_list_folder(entry.path_lower)
                for sub_entry in subfolder_result.entries:
                    if isinstance(sub_entry, dropbox.files.FileMetadata) and sub_entry.name.endswith('.mp3'):
                        link = dbx.files_get_temporary_link(sub_entry.path_lower).link
                        project_name = os.path.splitext(sub_entry.name)[0].split('_')[-1]
                        # Ajouter le préfixe VF ou VA avec un espace
                        prefix = entry.name.upper() 
                        files_info['mp3'][f"{prefix} {project_name}"] = link
                        print(f"MP3 trouvé : {sub_entry.name} - Projet : {prefix} {project_name}")
    except dropbox.exceptions.ApiError as err:
        print(f"Erreur lors de l'accès au dossier {folder}: {err}")
    
    return files_info

def explore_folder(folder):
    talents = {}
    
    try:
        result = dbx.files_list_folder(folder)
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                # Pour chaque sous-dossier (chaque prénom)
                person_folder = entry.path_lower
                person_name = entry.name
                print(f"Prénom trouvé : {person_name}")
                
                # Lister les fichiers MP3 et l'image
                person_files = list_person_files(person_folder)
                talents[person_name] = person_files
                        
    except dropbox.exceptions.ApiError as err:
        print(f"Erreur lors de l'exploration du dossier {folder}: {err}")
    
    return talents

# Fonction pour générer le fichier CSV
def generate_csv(talents, output_file='talents.csv'):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Trouver le nombre maximum de projets pour un talent
        max_projects = max(len(files['mp3']) for files in talents.values())
        
        # Créer les en-têtes dynamiquement
        fieldnames = ['Nom', 'Image']
        for i in range(1, max_projects + 1):
            fieldnames.extend([f'Projet {i}', f'MP3 {i}'])
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for name, files in talents.items():
            row = {'Nom': name, 'Image': files['image'] or ''}
            for i, (project, mp3_link) in enumerate(files['mp3'].items(), start=1):
                row[f'Projet {i}'] = project
                row[f'MP3 {i}'] = mp3_link
            writer.writerow(row)

if __name__ == "__main__":
    # Path du dossier à parcourir
    folder_path = '/TAlents site/HOMMES/HOMMES BILINGUES'
    
    talents_info = explore_folder(folder_path)
    
    # Générer le fichier CSV
    generate_csv(talents_info, './results/talents_hommes_bilingues.csv')

    print("Le fichier CSV a été généré avec succès.")
