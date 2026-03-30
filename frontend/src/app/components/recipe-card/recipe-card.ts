import { Component, input, output } from '@angular/core';
import { RecipeResponse } from '../../core/models/recipe.model';

@Component({
  selector: 'app-recipe-card',
  imports: [],
  templateUrl: './recipe-card.html',
  styleUrl: './recipe-card.css',
})
export class RecipeCard {
  recipe = input.required<RecipeResponse>();

  delete = output<string>();

  onDelete() {
    const id = this.recipe().id;
    if (id) {
      this.delete.emit(id);
    }
  }
}
