import { Component, inject, Input, signal } from '@angular/core';
import { RecipeResponse } from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

@Component({
  selector: 'app-generation',
  imports: [],
  templateUrl: './generation.html',
  styleUrl: './generation.css',
})
export class Generation {
  @Input() ingredients: string[] = [];

  recipe = signal<RecipeResponse | null>(null);
  isLoading = signal<boolean>(false);

  private recipeService = inject(RecipeService);

  onGenerate() {
    this.isLoading.set(true);
    this.recipe.set(null);

    this.recipeService.generateRecipe(this.ingredients).subscribe({
      next: (data) => {
        this.recipe.set(data);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error during generation', err);
        this.isLoading.set(false);
      },
    });
  }
}
