# Documentation du Projet: API de Gestion de Fichiers via FTP

## Introduction

Cette API permet de gérer des fichiers sur un serveur FTP. Elle propose des fonctionnalités telles que l'obtention des caractéristiques d'un fichier, la liste des fichiers et dossiers, l'upload de fichiers, ainsi que la création et suppression de dossiers.

## Prérequis

- **Python 3.7+**
- **Serveur FTP** avec les informations d'identification.
- **Accès au serveur** pour installer des dépendances et déployer l'application.

## Installation

### 1. Cloner le dépôt du projet

Clone le projet depuis le dépôt git (ou récupère les fichiers du projet) :

```bash
git clone https://github.com/roy98/pythonFTPFileManager-API.git
cd pythonFTPFileManager-API
```

### 2. Installer les dépendances

Installe les bibliothèques Python nécessaires :

```bash
pip install -r requirements.txt
```

**Contenu du fichier `requirements.txt` :**

```text
Flask==2.3.2
gunicorn==21.2.0
```

### 3. Configurer le fichier `config.py`

Crée un fichier `config.py` à la racine du projet avec le contenu suivant :

```python
# config.py

FTP_CONFIG = {
    'host': 'test.rebex.net', // url du serveur ftp sans ftp://
    'port': 21,
    'user': 'your_username',
    'password': 'your_password'
}
```

Remplace les valeurs par celles correspondant à ton serveur FTP.

## Démarrer l'API en développement

Pour tester l'API en environnement de développement :

```bash
python pythonFTPFileManager.py
```

Accède à l'API via `http://127.0.0.1:5000`.

## Déploiement en Production avec Gunicorn

### 1. Installer Gunicorn

```bash
pip install gunicorn
```

### 2. Lancer l'API avec Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 pythonFTPFileManager:app
```

Cette commande lance l'application avec 4 workers, accessible à `http://0.0.0.0:8000`.

### 3. (Optionnel) Configurer Nginx en tant que Proxy

**Exemple de configuration Nginx :**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /route/vers/fichier/static/du/projet/si/il/y/en/a;
    }
}
```

- **server_name** : Remplace `yourdomain.com` par ton domaine.
- **proxy_pass** : Redirige vers Gunicorn.

## Endpoints de l'API

### 1. Obtenir les caractéristiques d'un fichier

- **Endpoint**: `/file-info`
- **Méthode**: GET
- **Paramètres**:

  - `path`: Chemin complet du fichier sur le serveur FTP.
- **Exemple**:

  ```bash
  curl "http://127.0.0.1:5000/file-info?path=/path/to/file.txt"
  ```
- **Réponse** (si le fichier existe) :

  ```json
  {
      "exists": true,
      "name": "file.txt",
      "extension": ".txt",
      "size": 12345,
      "path": "/path/to/file.txt"
  }
  ```
- **Réponse** (si le fichier n'existe pas) :

  ```json
  {
      "exists": false,
      "path": "/path/to/file.txt"
  }
  ```

### 2. Lister les fichiers d'un dossier

- **Endpoint**: `/list-files`
- **Méthode**: GET
- **Paramètres**:

  - `directory`: Chemin complet du dossier sur le serveur FTP.
- **Exemple**:

  ```bash
  curl "http://127.0.0.1:5000/list-files?directory=/path/to/directory"
  ```
- **Réponse** :

  ```json
  [
      "file1.txt",
      "file2.pdf",
      "image.png"
  ]
  ```

### 3. Lister les sous-dossiers d'un dossier

- **Endpoint**: `/list-folders`
- **Méthode**: GET
- **Paramètres**:

  - `directory`: Chemin complet du dossier sur le serveur FTP.
- **Exemple**:

  ```bash
  curl "http://127.0.0.1:5000/list-folders?directory=/path/to/directory"
  ```
- **Réponse** :

  ```json
  [
      "subfolder1",
      "subfolder2",
      "subfolder3"
  ]
  ```

### 4. Téléverser un fichier dans un dossier

- **Endpoint**: `/upload-file`
- **Méthode**: POST
- **Paramètres**:

  - `directory`: Chemin complet du dossier où le fichier doit être téléversé.
  - `file`: Le fichier à téléverser (via un formulaire `multipart/form-data`).
- **Exemple**:

  ```bash
  curl -F "file=@/local/path/to/file.txt" -F "directory=/path/to/directory" http://127.0.0.1:5000/upload-file
  ```
- **Réponse** :

  ```json
  {
      "message": "File uploaded successfully",
      "filename": "file.txt"
  }
  ```

### 5. Créer un sous-dossier

- **Endpoint**: `/create-folder`
- **Méthode**: POST
- **Paramètres**:

  - `directory`: Chemin complet du dossier parent.
  - `folder_name`: Nom du sous-dossier à créer.
- **Exemple**:

  ```bash
  curl -X POST -d "directory=/path/to/parent" -d "folder_name=new_folder" http://127.0.0.1:5000/create-folder
  ```
- **Réponse** :

  ```json
  {
      "message": "Folder 'new_folder' created successfully"
  }
  ```

### 6. Supprimer un fichier

- **Endpoint**: `/delete-file`
- **Méthode**: DELETE
- **Paramètres**:

  - `directory`: Chemin complet du dossier parent.
  - `filename`: Nom du fichier à supprimer.
- **Exemple**:

  ```bash
  curl -X DELETE -d "directory=/path/to/directory" -d "filename=file.txt" http://127.0.0.1:5000/delete-file
  ```
- **Réponse** :

  ```json
  {
      "message": "File 'file.txt' deleted successfully"
  }
  ```

### 7. Supprimer un dossier

- **Endpoint**: `/delete-folder`
- **Méthode**: DELETE
- **Paramètres**:

  - `directory`: Chemin complet du dossier parent.
  - `folder_name`: Nom du dossier à supprimer.
  - `force_deletion`: `true` pour forcer la suppression d'un dossier non vide.
- **Exemple**:

  ```bash
  curl -X DELETE -d "directory=/path/to/parent" -d "folder_name=folder_to_delete" -d "force_deletion=true" http://127.0.0.1:5000/delete-folder
  ```
- **Réponse** :

  ```json
  {
      "message": "Folder 'folder_to_delete' deleted successfully"
  }
  ```

## Conclusion

Cette documentation fournit toutes les informations nécessaires pour installer, configurer, et utiliser l'API de gestion de fichiers FTP. Pour un déploiement en production, assure-toi de suivre les étapes de déploiement avec Gunicorn et de configurer un serveur proxy comme Nginx si nécessaire.
