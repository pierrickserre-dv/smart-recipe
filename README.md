# Smart Recipe AI

**Smart Recipe AI** génère des recettes de cuisine à partir des ingrédients que l'on a sous la main, grâce à Gemini (Vertex AI). Elle génère aussi une photo du plat, tient compte des ustensiles disponibles, et permet d'enregistrer ses recettes en favoris.

- **Application :** https://sandbox-pserre.web.app
- **API :** https://api-649608669244.europe-west1.run.app

---

## Fonctionnalités

- **Authentification** par email et mot de passe (Firebase Authentication). Les inscriptions publiques sont désactivées : les comptes se créent depuis la console Firebase.
- **Génération de recettes** à partir d'une liste d'ingrédients, en n'utilisant que ces ingrédients et quelques basiques (sel, poivre, huile, beurre, eau, ail).
- **Recette alternative** : retirer ou ajouter des ingrédients à une recette générée, puis en régénérer une variante.
- **Photo du plat** générée pour chaque recette.
- **Équipement** : l'utilisateur indique ses ustensiles, et les recettes en tiennent compte.
- **Favoris** : enregistrer, consulter, filtrer par temps de préparation et supprimer ses recettes.

---

## Stack technique

| Partie | Technologies |
|---|---|
| **Frontend** | Angular 21 (standalone components, signals), AngularFire |
| **Backend** | FastAPI (Python 3.12), Pydantic, Uvicorn |
| **IA** | Vertex AI : `gemini-3.8-flash` (recettes) et `gemini-3.1-flash-lite-image` (images) |
| **Données** | Firestore (recettes, équipement) et Cloud Storage (images) |
| **Authentification** | Firebase Authentication |
| **Hébergement** | Cloud Run (backend) et Firebase Hosting (frontend) |
| **CI/CD** | GitHub Actions, avec Workload Identity Federation |

---

## Architecture cloud

Tout est hébergé sur le projet GCP `sandbox-pserre`.

- **Le frontend** est compilé en fichiers statiques (HTML, JS, CSS) et servi par **Firebase Hosting**. Son code s'exécute dans le navigateur de l'utilisateur.
- **L'authentification** passe par **Firebase Authentication**. Le frontend obtient un token, qu'il envoie au backend à chaque appel.
- **Le backend** est une image Docker stockée dans **Artifact Registry** et exécutée par **Cloud Run**. Il vérifie le token, puis appelle :
  - **Vertex AI** (Gemini) pour générer les recettes et les images ;
  - **Firestore** pour lire et écrire les recettes et l'équipement ;
  - **Cloud Storage** pour stocker les images des recettes, rendues publiques. Le navigateur les affiche directement depuis le bucket.

### Ce qui se passe lors d'une génération

1. L'utilisateur saisit ses ingrédients. Le frontend récupère son token Firebase.
2. Le frontend appelle `POST /recipes/generate` avec le token.
3. Le backend vérifie le token, lit l'équipement de l'utilisateur dans Firestore, puis envoie à Gemini un prompt avec les ingrédients et l'équipement.
4. Gemini renvoie une recette au format JSON. Le backend vérifie qu'elle n'utilise que des ingrédients autorisés, puis la renvoie.
5. Le frontend appelle `POST /recipes/generate-image`. Le backend demande une image à Gemini et la renvoie en base64.

### Ressources GCP

| Ressource | Nom | Rôle |
|---|---|---|
| Cloud Run | `api` (europe-west1) | Exécute le backend. 2 instances maximum |
| Artifact Registry | `smart-recipe` (europe-west1) | Stocke les images Docker du backend, taguées avec le hash du commit |
| Firebase Hosting | site `sandbox-pserre` | Sert les fichiers du frontend |
| Firebase Authentication | | Gère les comptes utilisateurs |
| Firestore | base `(default)` (eur3) | Recettes dans `users/{uid}/recipes`, équipement dans `users/{uid}` |
| Cloud Storage | `sandbox-pserre.firebasestorage.app` | Images des recettes, rendues publiques |
| Vertex AI | région `global` | Modèles Gemini |

### Variables d'environnement du service Cloud Run

| Variable | Valeur | Rôle |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | `sandbox-pserre` | Projet GCP utilisé par les clients Google |
| `GOOGLE_CLOUD_LOCATION` | `global` | Région Vertex AI des modèles Gemini |
| `CORS_ORIGINS` | `["https://sandbox-pserre.web.app"]` | Origines autorisées à appeler l'API depuis un navigateur |

### Comptes de service

Chaque compte n'a que les droits nécessaires à son rôle.

| Compte | Utilisé par | Rôles | Portée |
|---|---|---|---|
| `smart-recipe-api` | Le backend sur Cloud Run | Agent Platform User (Vertex AI) | Projet |
| | | Cloud Datastore User (Firestore) | Projet |
| | | Storage Object Admin | Bucket des images uniquement |
| `github-deployer` | GitHub Actions | Cloud Run Developer | Projet |
| | | Firebase Hosting Admin | Projet |
| | | Service Usage Consumer | Projet |
| | | Artifact Registry Writer | Dépôt `smart-recipe` uniquement |
| | | Service Account User | Compte `smart-recipe-api` uniquement |

Aucun de ces comptes n'a de clé JSON : Cloud Run fournit automatiquement les accès de `smart-recipe-api`, et GitHub Actions utilise Workload Identity Federation.

### Maîtrise des coûts

- Alerte de budget mensuelle sur le projet, et plafond de dépenses sur Vertex AI.
- Cloud Run limité à 2 instances, et à zéro instance en l'absence de trafic.
- Inscriptions désactivées dans Firebase Authentication.

---

## Démarche DevOps

### Branches

- `main` : la version en production. Chaque merge déclenche un déploiement.
- `dev` : la branche d'intégration, où arrivent les fonctionnalités terminées.

1. Créer une branche à partir de `dev` : `feat/...`, `fix/...`, `docs/...`.
2. Ouvrir une pull request vers `dev`. La CI vérifie le code.
3. Pour mettre en production, ouvrir une pull request de `dev` vers `main`, et la merger avec **Create a merge commit**.
4. Resynchroniser `dev` avec `main` : `git push origin origin/main:dev`.

### Pipeline CI/CD

La **CI** vérifie le code de chaque pull request. Le **CD** déploie automatiquement chaque merge dans `main`.

| Workflow | Déclencheur | Ce qu'il fait |
|---|---|---|
| `backend.yml` | Push et pull request touchant `backend/` | Ruff (format et lint), puis Pytest |
| `frontend.yml` | Push et pull request touchant `frontend/` | ESLint, puis build Angular |
| `deploy.yml` | Push sur `main`, ou manuellement | Build et push de l'image, déploiement Cloud Run, puis build et publication du frontend |

`deploy.yml` contient trois jobs, qui s'enchaînent avec `needs` :

| Job | Ce qu'il fait |
|---|---|
| `image` | Construit l'image Docker du backend, taguée avec le hash du commit, et la pousse sur Artifact Registry |
| `cloud-run` | Déploie cette image sur Cloud Run, ce qui crée une nouvelle révision |
| `frontend` | Génère `environment.prod.ts`, compile le frontend et le publie sur Firebase Hosting |

Si un job échoue, les suivants sont ignorés, et la version en production reste inchangée.

### Authentification de GitHub Actions auprès de GCP

GitHub Actions n'utilise aucune clé stockée. Il s'authentifie par **Workload Identity Federation** :

1. Le workflow demande à GitHub un jeton signé, qui atteste qu'il vient du dépôt `pierrickserre-dv/smart-recipe`. Il faut pour cela la permission `id-token: write`.
2. Il présente ce jeton au pool `github` de GCP.
3. GCP vérifie la signature du jeton auprès de GitHub, ainsi que la condition sur le dépôt.
4. GCP accorde un accès temporaire (environ une heure) en tant que `github-deployer`, avec lequel le workflow déploie.

| Élément | Valeur |
|---|---|
| Pool | `github` |
| Provider | `github-actions`, émetteur `https://token.actions.githubusercontent.com` |
| Condition | `assertion.repository == 'pierrickserre-dv/smart-recipe'` |
| Autorisation | Le dépôt a le rôle Workload Identity User sur `github-deployer` |

Configuration côté GitHub (**Settings → Secrets and variables → Actions**) :

| Nom | Type | Rôle |
|---|---|---|
| `GCP_WIF_PROVIDER` | Variable | Identifiant complet du provider |
| `GCP_DEPLOYER_SA` | Variable | Email de `github-deployer` |
| `FIREBASE_API_KEY` | Secret | Clé web Firebase, injectée dans `environment.prod.ts` au build |

---

## Développement local

### Prérequis

- Python 3.12 (par exemple avec [uv](https://docs.astral.sh/uv/))
- Node.js 24 (par exemple avec [fnm](https://github.com/Schniz/fnm))
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- Docker Desktop, pour tester l'image du backend

### Accès à Google Cloud

En local, le backend utilise votre compte Google, via les Application Default Credentials.

```bash
gcloud auth login
gcloud config set project sandbox-pserre
gcloud auth application-default login
```

### Backend

```bash
cd backend
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements-dev.txt
cp env_example .env
python -m uvicorn main:app --reload
```

L'API est disponible sur http://localhost:8000, et sa documentation interactive sur http://localhost:8000/docs.

En local, le backend utilise **les mêmes Firestore et Cloud Storage que la production** : les recettes enregistrées pendant les tests sont de vraies données.

### Frontend

```bash
cd frontend
npm install
cp src/environments/environment.ts src/environments/environment.local.ts
# Dans environment.local.ts, remplacer YOUR-API-KEY par la clé web Firebase
npx ng serve
```

L'application est disponible sur http://localhost:4200. Utilisez `npx ng` plutôt que `ng`, pour lancer la version d'Angular CLI du projet.

### Fichiers de configuration du frontend

| Fichier | Utilisé par | Dans git |
|---|---|---|
| `environment.ts` | Build de la CI | Oui, sans vraie clé |
| `environment.local.ts` | `ng serve` | Non |
| `environment.prod.ts` | `ng build --configuration production` | Non, il est généré par `deploy.yml` |

### Tests et qualité

```bash
# Backend, depuis backend/
uvx ruff format --check .
uvx ruff check .
PYTHONPATH=. pytest src/tests

# Frontend, depuis frontend/
npm run lint
npx ng build --configuration production
```

### Dépendances Python

`requirements.in` liste les dépendances directes, et `requirements.txt` est généré avec leurs versions exactes. Ne modifiez pas `requirements.txt` à la main :

```bash
uv pip compile requirements.in -o requirements.txt --python-version 3.12
```

Les outils de test sont dans `requirements-dev.txt`, et ne sont pas installés dans l'image Docker.

---

## Structure du projet

```text
.
├── .github/workflows/
│   ├── backend.yml          CI du backend
│   ├── frontend.yml         CI du frontend
│   └── deploy.yml           Déploiement continu
├── backend/
│   ├── Dockerfile
│   ├── main.py              Application FastAPI et CORS
│   ├── requirements.in      Dépendances directes
│   ├── requirements.txt     Dépendances figées (généré)
│   └── src/
│       ├── config.py        Configuration (variables d'environnement)
│       ├── auth/            Vérification des tokens Firebase
│       ├── recipes/         Routes, appels à Gemini, Firestore, images
│       ├── storage/         Accès à Cloud Storage
│       └── tests/
└── frontend/
    ├── firebase.json        Configuration de Firebase Hosting
    └── src/app/
        ├── pages/           home, favorites, equipment, welcome
        ├── components/      generation, recipe-card, header, login, register
        └── core/            services, guards, interceptor, modèles
```

### Routes de l'API

Toutes les routes sous `/recipes` exigent un token Firebase (`Authorization: Bearer <token>`).

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/` | Vérifie que l'API répond |
| `POST` | `/recipes/generate` | Génère une recette |
| `POST` | `/recipes/generate-image` | Génère la photo d'une recette |
| `POST` | `/recipes/save` | Enregistre une recette et sa photo |
| `GET` | `/recipes` | Liste les recettes enregistrées |
| `DELETE` | `/recipes/{recipe_id}` | Supprime une recette et sa photo |
| `GET` | `/recipes/account/equipment` | Lit l'équipement de l'utilisateur |
| `PUT` | `/recipes/account/equipment` | Enregistre l'équipement de l'utilisateur |

---

## Déploiement manuel

Le déploiement est automatique à chaque merge dans `main`. Ces commandes ne servent qu'en cas de besoin, par exemple si GitHub Actions est indisponible.

**Backend**, depuis `backend/` :

```bash
IMAGE=europe-west1-docker.pkg.dev/sandbox-pserre/smart-recipe/api:$(git rev-parse --short HEAD)
docker build -t $IMAGE .
docker push $IMAGE
gcloud run services update api --project=sandbox-pserre --region=europe-west1 --image=$IMAGE
```

**Frontend**, depuis `frontend/`, avec un `environment.prod.ts` pointant vers l'URL Cloud Run :

```bash
npx ng build --configuration production
npx firebase-tools deploy --only hosting --project sandbox-pserre
```

**Revenir à une version précédente :** dans la console Cloud Run (onglet **Revisions**, puis **Manage traffic**) ou dans la console Firebase Hosting (historique des versions).

---

## Pistes d'amélioration

- Traduction FR/EN : reprendre la branche `feat/language`.
- Tests unitaires du frontend : `ng test` échoue, car la configuration `development` n'existe pas dans `angular.json`.
- Infrastructure as code : décrire les ressources GCP avec Terraform.
- Appels à Gemini asynchrones, pour ne pas bloquer le serveur pendant une génération.
