import { Routes } from '@angular/router';
import { authGuard } from './auth-guard';
import { Login } from './login/login';
import { Home } from './pages/home/home';
import { Register } from './register/register';

export const routes: Routes = [
  {
    path: '',
    component: Home,
    canActivate: [authGuard],
  },
  {
    path: 'login',
    component: Login,
  },
  {
    path: 'register',
    component: Register,
  },
  {
    path: '**',
    redirectTo: '',
  },
];
