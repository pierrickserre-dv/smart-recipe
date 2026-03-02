import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-register',
  imports: [FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
  authService = inject(AuthService);

  email = '';
  password = '';

  async onSubmit() {
    try {
      await this.authService.register(this.email, this.password);
      console.log(
        'Tu as bien créé un compte, tu es connecté en tant que : ',
        this.authService.user(),
      );
    } catch (error) {
      alert('Erreur de register : ' + error);
    }
  }
}
