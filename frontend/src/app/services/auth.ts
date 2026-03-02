import { Injectable, inject } from '@angular/core';
import {
  Auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  user,
} from '@angular/fire/auth';
import { toSignal } from '@angular/core/rxjs-interop';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private auth = inject(Auth);

  user = toSignal(user(this.auth));

  async register(email: string, password: string) {
    try {
      const credential = await createUserWithEmailAndPassword(this.auth, email, password);
      return credential.user;
    } catch (error) {
      console.error('Erreur de register', error);
      throw error;
    }
  }
  async login(email: string, password: string) {
    return signInWithEmailAndPassword(this.auth, email, password);
  }

  async logout() {
    return signOut(this.auth);
  }
}
