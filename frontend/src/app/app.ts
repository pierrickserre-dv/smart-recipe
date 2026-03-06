import { HttpClient } from '@angular/common/http';
import { Component, effect, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from './components/header/header';
import { AuthService } from './core/services/auth';

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
      this.http.get<{ message: string }>('/api').subscribe({
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
