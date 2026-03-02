import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  authService = inject(AuthService);

  email = '';
  password = '';

  async onSubmit() {
    try {
      await this.authService.login(this.email, this.password);
      console.log('Tu es bien connecté en tant que : ', this.authService.user());
    } catch (error) {
      alert('Erreur de connexion : ' + error);
    }
  }
}
