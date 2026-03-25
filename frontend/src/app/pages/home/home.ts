import { Component } from '@angular/core';
import { Generation } from '../../components/generation/generation';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [Generation],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  selectedIngredients: string[] = [];

  addIngredient(nom: string) {
    if (nom && !this.selectedIngredients.includes(nom)) {
      this.selectedIngredients = [...this.selectedIngredients, nom];
    }
  }

  deleteIngredient(index: number) {
    this.selectedIngredients.splice(index, 1);
  }
}
