import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RecipeResponse } from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

@Component({
  selector: 'app-favorites',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './favorites.html',
  styleUrl: './favorites.css',
})
export class Favorites implements OnInit {
  private recipeService = inject(RecipeService);

  recipes = signal<RecipeResponse[]>([]);
  selectedRecipe = signal<RecipeResponse | null>(null);
  maxTime = signal<number | null>(null);

  filteredRecipes = computed(() => {
    const time = this.maxTime();
    const allRecipes = this.recipes();

    if (!time) return allRecipes;

    return allRecipes.filter((recipe) => {
      const prepTimeNum = parseInt(recipe.prep_time);
      return prepTimeNum <= time;
    });
  });

  ngOnInit() {
    this.loadRecipes();
  }

  loadRecipes() {
    this.recipeService.getRecipes().subscribe({
      next: (data) => this.recipes.set(data),
      error: (err) => console.error('Error during retrieval', err),
    });
  }

  onDelete(recipeId: string) {
    this.recipeService.deleteRecipe(recipeId).subscribe({
      next: () => {
        if (this.selectedRecipe()?.id === recipeId) {
          this.selectedRecipe.set(null);
        }
        this.recipes.set(
          this.recipes().filter((r) => {
            console.log('Comparison:', r.id, 'with', recipeId);
            return r.id !== recipeId;
          }),
        );
      },
    });
  }

  onSelected(recipe: RecipeResponse) {
    this.selectedRecipe.set(recipe);
  }

  onFilterChange(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    this.maxTime.set(val ? parseInt(val) : null);
  }

  adjustTime(amount: number) {
    const current = this.maxTime() ?? 0;
    const newValue = Math.max(0, current + amount);
    this.maxTime.set(newValue > 0 ? newValue : null);
  }
}
