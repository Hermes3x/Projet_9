# LITReview

Application web Django permettant de demander et publier des critiques de livres ou d’articles, d’afficher un flux personnalisé et de suivre d’autres utilisateurs.

## 1. Prérequis

- Python 3.11+ (adapter à ta version exacte)
- pip
- Git

## 2. Installation

```bash
git clone <URL_DU_REPO>
cd 'Projet_9\litrevu'
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
python -m pip install -r requirements.txt
```

## 3. Base de données

Le projet utilise SQLite.

- Un fichier `db.sqlite3` est inclus avec des données de test.  
- Sinon, pour repartir d’une base vide :

```bash
python manage.py migrate
python manage.py createsuperuser
```

Suivre les instructions pour créer un compte admin.

## 4. Lancement de l’application

```bash
python manage.py runserver
```

Puis ouvrir [http://127.0.0.1:8000](http://127.0.0.1:8000) dans un navigateur.

## 5. Authentification

- Page d’inscription : `/signup/`
- Page de connexion : `/login/`
- Page de déconnexion : `/logout/`

Un utilisateur non connecté a accès uniquement à l’inscription et la connexion.

## 6. Fonctionnalités principales

Pour un utilisateur connecté :

- **Flux** (`/feed/`)  
  - Affiche les tickets et critiques:
    - de l’utilisateur courant
    - des utilisateurs suivis
    - les critiques en réponse aux tickets de l’utilisateur
  - Trié par date décroissante (plus récents en premier).

- **Tickets**
  - Créer un ticket (« Demander une critique »)
  - Modifier / supprimer ses propres tickets
  - Créer une critique en réponse à un ticket

- **Critiques**
  - Créer une critique en réponse à un ticket existant
  - Créer un ticket et une critique en une seule étape
  - Modifier / supprimer ses propres critiques

- **Abonnements**
  - Suivre un utilisateur en entrant son nom d’utilisateur
  - Afficher la liste des utilisateurs suivis
  - Se désabonner d’un utilisateur

## 7. Structure du projet

- `authentication/` : modèle utilisateur personnalisé, vues et templates d’authentification
- `blog/` : modèles Ticket, Review, UserFollows, vues du flux, posts, abonnements
- `litrevu/` : configuration du projet (settings, urls, base.html, statiques globaux)
- `static/` : fichiers CSS (ex. `style.css`)
- `templates/` : templates racine si nécessaire (ex. `base.html`)

## 8. Configuration de développement

Les fichiers statiques sont servis par Django en développement.

- `STATIC_URL = 'static/'`
- `STATICFILES_DIRS = [BASE_DIR / "static"]` (si utilisé)
- `MEDIA_URL = 'media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`

Les fichiers uploadés (images des tickets) sont accessibles via `/media/`.

## 9. Qualité du code

Le projet suit autant que possible les recommandations PEP8.

Pour vérifier la conformité :

```bash
flake8
```

(Assurez-vous d’avoir installé flake8 : `pip install flake8`.)

Optionnellement, vous pouvez utiliser Black pour le formatage automatique :

```bash
black .
```

## 10. Sécurité / secrets

Ce projet est destiné à un usage local / pédagogique.  
Pour une utilisation en production, vous devez :

- déplacer `SECRET_KEY` dans des variables d’environnement,
- désactiver `DEBUG`,
- configurer correctement `ALLOWED_HOSTS`.
