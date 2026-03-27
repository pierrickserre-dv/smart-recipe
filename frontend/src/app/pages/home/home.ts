import { Component, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Generation } from '../../components/generation/generation';
import { RecipeService } from '../../core/services/recipe.service';
import { SavedRecipe } from '../../core/models/recipe.model';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [Generation, DatePipe],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  selectedIngredients: string[] = [];
  recentRecipes = signal<SavedRecipe[]>([]);
  isLoadingHistory = signal(false);
  expandedRecipeId = signal<string | null>(null);

  private recipeService = inject(RecipeService);

  ngOnInit() {
    this.loadRecentRecipes();
  }

  loadRecentRecipes() {
    this.isLoadingHistory.set(true);
    this.recipeService.getRecipes().subscribe({
      next: (recipes) => {
        this.recentRecipes.set(recipes);
        this.isLoadingHistory.set(false);
      },
      error: (err) => {
        console.error('Error loading recipes', err);
        this.isLoadingHistory.set(false);
      },
    });
  }

  toggleRecipe(id: string) {
    this.expandedRecipeId.set(this.expandedRecipeId() === id ? null : id);
  }

  addIngredient(nom: string) {
    if (nom && !this.selectedIngredients.includes(nom)) {
      this.selectedIngredients = [...this.selectedIngredients, nom];
    }
  }

  deleteIngredient(index: number) {
    this.selectedIngredients.splice(index, 1);
  }
}
