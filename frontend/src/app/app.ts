import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, effect, inject } from '@angular/core';
import { getIdToken } from '@angular/fire/auth';
import { RouterOutlet } from '@angular/router';
import { Header } from './header/header';
import { AuthService } from './services/auth';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  messageDuBackend = 'En attente du backend';
  authService = inject(AuthService);
  private http = inject(HttpClient);

  constructor() {
    effect(() => {
      const user = this.authService.user();
      if (user) {
        console.log('Utilisateur détecté, appel du backend');
        this.appelerLeBackend();
      }
    });
  }

  async appelerLeBackend() {
    try {
      const user = this.authService.user();
      if (!user) return;

      const token = await getIdToken(user);
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      this.http.get<{ message: string }>('http://localhost:8000', { headers }).subscribe({
        next: (data) => (this.messageDuBackend = data.message),
        error: (err) => {
          this.messageDuBackend = "Erreur d'authentification au backend";
          console.error(err);
        },
      });
    } catch (error) {
      console.error('Impossible de récupérer le token', error);
    }
  }
}
