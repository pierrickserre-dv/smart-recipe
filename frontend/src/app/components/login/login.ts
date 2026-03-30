import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: '../auth-card.css',
})
export class Login {
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  errorMessage = signal<string | null>(null);

  profileForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', Validators.required),
  });

  async onSubmit() {
    try {
      this.errorMessage.set(null);
      const email = this.profileForm.value.email ?? '';
      const password = this.profileForm.value.password ?? '';
      await this.authService.login(email, password);
      console.log('Tu es bien connecté en tant que : ', this.authService.user());
      this.router.navigate(['/']);
    } catch (error: unknown) {
      const firebaseError = error as { code?: string };

      if (
        firebaseError.code === 'auth/invalid-credential' ||
        firebaseError.code === 'auth/user-not-found'
      ) {
        this.errorMessage.set('Email ou mot de passe incorrect.');
      } else {
        this.errorMessage.set('Une erreur est survenue. Réessayez plus tard.');
      }
      console.error(error);
    }
  }
}
