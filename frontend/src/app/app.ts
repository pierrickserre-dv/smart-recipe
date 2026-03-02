import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Header } from './header/header';
import { AuthService } from './services/auth';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  messageDuBackend = 'En attente du backend...';

  authService = inject(AuthService);

  private http = inject(HttpClient);

  ngOnInit() {
    this.appelerLeBackend();
  }

  appelerLeBackend() {
    this.http.get<{ message: string }>('http://localhost:8000/').subscribe({
      next: (data) => {
        this.messageDuBackend = data.message;
      },
      error: (err) => {
        this.messageDuBackend = 'Erreur·de·connexion·:·';
        console.error(err);
      },
    });
  }
}
