# Smart Recipe AI : frontend

Application Angular 21 de Smart Recipe AI. L'architecture, le déploiement et la configuration complète sont décrits dans le [README principal](../README.md).

## Lancer en local

Prérequis : Node.js 24, et le backend lancé sur http://localhost:8000.

```bash
npm install
cp src/environments/environment.ts src/environments/environment.local.ts
# Dans environment.local.ts, remplacer YOUR-API-KEY par la clé web Firebase
npx ng serve
```

L'application est disponible sur http://localhost:4200.

## Commandes utiles

| Commande | Rôle |
|---|---|
| `npx ng serve` | Serveur de développement (configuration `local`) |
| `npx ng build --configuration production` | Build de production dans `dist/smart-recipe-front/browser` |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |

Utilisez `npx ng` plutôt que `ng`, pour lancer la version d'Angular CLI du projet.

## Déploiement

Le frontend est publié automatiquement sur Firebase Hosting (https://sandbox-pserre.web.app) à chaque merge dans `main`, par le workflow `.github/workflows/deploy.yml`. La configuration de Firebase Hosting est dans `firebase.json`.
