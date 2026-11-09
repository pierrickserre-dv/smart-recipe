import { Routes } from '@angular/router';
import { Login } from './components/login/login';
import { Register } from './components/register/register';
import { authGuard } from './core/guards/auth-guard';
import { loginGuard } from './core/guards/login-guard';
import { Favorites } from './pages/favorites/favorites';
import { Home } from './pages/home/home';
import { Equipment } from './pages/equipment/equipment';
import { Welcome } from './pages/welcome/welcome';

export const routes: Routes = [
  {
    path: '',
    component: Home,
    canActivate: [authGuard],
  },
  {
    path: 'favorites',
    component: Favorites,
    canActivate: [authGuard],
  },
  {
    path: 'equipment',
    component: Equipment,
    canActivate: [authGuard],
  },
  {
    path: 'welcome',
    component: Welcome,
    canActivate: [loginGuard],
    children: [
      { path: 'login', component: Login },
      { path: 'register', component: Register },
      { path: '', redirectTo: 'login', pathMatch: 'full' },
    ],
  },
  {
    path: '**',
    redirectTo: 'welcome',
  },
];
