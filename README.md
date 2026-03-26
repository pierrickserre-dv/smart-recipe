# Smart Recipe AI

**Smart Recipe AI** est une application web moderne qui utilise l'intelligence artificielle pour transformer vos ingrédients restants en recettes gastronomiques. Le projet repose sur une architecture découplée avec un backend FastAPI et un frontend Angular, intégrant les technologies Google Cloud (Gemini) et Firebase.

---

## Fonctionnalités

* **Authentification Sécurisée** : Inscription et connexion gérées par Firebase Auth (Tokens JWT).
* **Gestion Dynamique des Ingrédients** : Interface fluide pour ajouter et supprimer vos ingrédients en temps réel.
* **Génération de Recettes par IA** : Utilisation de **Gemini 2.5 Flash** pour créer des recettes complètes (Titre, Temps, Difficulté, Ingrédients, Instructions).
* **Régénération Intelligente** : Possibilité de générer une nouvelle variante de recette sans modifier votre sélection d'ingrédients, même si le panier est vidé.
* **Expérience Utilisateur (UX)** : Design "Dark Mode" épuré avec des composants réactifs, animations fluides et boutons contextuels.

---

## 🛠 Stack Technique

### Backend

* **Framework** : FastAPI (Python 3.12)
* **IA** : Google GenAI SDK (Modèle : `gemini-2.5-flash`)
* **Sécurité** : Firebase Admin SDK (Vérification des Tokens en header via Interceptor)
* **Serveur** : Uvicorn

### Frontend

* **Framework** : Angular 21.1.5 (Signals, Standalone Components)
* **Authentification** : Firebase Auth
* **Design** : CSS3 moderne (Flexbox, CSS Variables, Animations @keyframes)

---

## Installation et Configuration

### 1. Configuration du Backend

**Prérequis** : Python 3.12+ et le SDK Google Cloud installé.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Variables d'environnement (.env)

Créez un fichier `.env` dans le dossier `/backend` :

```env
GOOGLE_CLOUD_PROJECT=votre-projet-id
GOOGLE_CLOUD_LOCATION=votre-region
```

> **Note** : Assurez-vous d'avoir exécuté `gcloud auth application-default login` dans votre terminal pour l'accès à Gemini.

#### Lancement

```bash
python -m uvicorn main:app --reload
```

---

### 2. Configuration du Frontend

**Prérequis** : Node.js et Angular CLI installés.

```bash
cd frontend
npm install
```

#### Environnement

Configurez vos clés Firebase dans `src/environments/environment.local.ts` :

```ts
export const environment = {
  production: false,
  firebase: {
    apiKey: "VOTRE_API_KEY",
    authDomain: "VOTRE_AUTH_DOMAIN",
    projectId: "VOTRE_PROJECT_ID",
    storageBucket: "VOTRE_STORAGE_BUCKET",
    messagingSenderId: "VOTRE_SENDER_ID",
    appId: "VOTRE_APP_ID"
  }
};
```

#### Lancement

```bash
ng serve
```

---

## Architecture et Workflow Git

Le projet utilise un système de branches par fonctionnalité pour garantir la stabilité du code :

* `main` : Branche stable de production.
* `feat/auth` : Authentification et sécurité Firebase.
* `feat/recipe-generation-frontend` : Logique d'interface et intégration de la génération.

### Astuce Git (Changement de branche avec modifications en cours)

```bash
git stash      
git checkout <nom-de-la-branche>
git stash pop  
```

---

## Tests Backend

Suite de tests automatisés avec Pytest :

```bash
cd backend
pytest
```

---

