import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, TranslateModule],
  templateUrl: './register.html',
  styleUrl: '../auth-card.css',
})
export class Register {
  authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  submitted = false;
  errorMessage = signal<string | null>(null);

  profileForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(8)]),
  });

  async onSubmit() {
    try {
      const email = this.profileForm.value.email ?? '';
      const password = this.profileForm.value.password ?? '';
      await this.authService.register(email, password);
      this.router.navigate(['/']);
    } catch (error) {
      console.error(error);
    }
  }
}
