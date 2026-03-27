import { Component, inject, OnInit, signal } from '@angular/core';
import { RecipeCard } from '../../../app/components/recipe-card/recipe-card';
import { RecipeResponse } from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

@Component({
  selector: 'app-favorites',
  standalone: true,
  imports: [RecipeCard],
  templateUrl: './favorites.html',
  styleUrl: './favorites.css',
})
export class Favorites implements OnInit {
  private recipeService = inject(RecipeService);

  recipes = signal<RecipeResponse[]>([]);

  ngOnInit() {
    this.loadRecipes();
  }

  loadRecipes() {
    this.recipeService.getRecipes().subscribe({
      next: (data) => this.recipes.set(data),
      error: (err) => console.error('Erreur lors de la récupération', err),
    });
  }

  onDelete(recipeId: string) {
    this.recipeService.deleteRecipe(recipeId).subscribe({
      next: () => {
        this.recipes.set(
          this.recipes().filter((r) => {
            console.log('Comparaison:', r.id, 'avec', recipeId);
            return r.id !== recipeId;
          }),
        );
      },
    });
  }
}
