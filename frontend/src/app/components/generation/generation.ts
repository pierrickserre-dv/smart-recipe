import { Component, effect, EventEmitter, inject, Input, Output, signal, untracked } from '@angular/core';
import {
  AlternativesResponse,
  RecipeResponse,
} from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

@Component({
  selector: 'app-generation',
  imports: [],
  templateUrl: './generation.html',
  styleUrl: './generation.css',
})
export class Generation {
  @Input() ingredients: string[] = [];
  @Output() recipeSaved = new EventEmitter<void>();

  recipe = signal<RecipeResponse | null>(null);
  isLoading = signal(false);
  isSaving = signal(false);
  isSaved = signal(false);

  imageBase64 = signal<string | null>(null);
  imageMimeType = signal<string>('image/jpeg');
  isLoadingImage = signal(false);

  selectedIngredients = signal<Set<string>>(new Set());
  alternatives = signal<AlternativesResponse | null>(null);
  isLoadingAlternatives = signal(false);

  private recipeService = inject(RecipeService);

  constructor() {
    effect(() => {
      this.recipe();
      untracked(() => {
        this.isSaved.set(false);
        this.imageBase64.set(null);
        this.selectedIngredients.set(new Set());
        this.alternatives.set(null);
      });
    });
  }

  onGenerate() {
    this.isLoading.set(true);
    this.recipe.set(null);

    this.recipeService.generateRecipe(this.ingredients).subscribe({
      next: (data) => {
        this.recipe.set(data);
        this.isLoading.set(false);
        this.generateImage(data.title);
      },
      error: (err) => {
        console.error('Error during generation', err);
        this.isLoading.set(false);
      },
    });
  }

  private generateImage(title: string) {
    this.isLoadingImage.set(true);
    this.recipeService.generateImage(title).subscribe({
      next: (data) => {
        this.imageBase64.set(data.image_base64);
        this.imageMimeType.set(data.mime_type);
        this.isLoadingImage.set(false);
      },
      error: (err) => {
        console.error('Error generating image', err);
        this.isLoadingImage.set(false);
      },
    });
  }

  onSave() {
    const currentRecipe = this.recipe();
    if (currentRecipe && !this.isSaved()) {
      this.isSaving.set(true);
      this.isSaved.set(true);

      this.recipeService.saveRecipe(currentRecipe).subscribe({
        next: (response) => {
          console.log('Recipe saved with ID:', response.id);
          this.isSaving.set(false);
          this.recipeSaved.emit();
        },
        error: (err) => {
          console.error('Error saving recipe', err);
          this.isSaving.set(false);
          this.isSaved.set(false);
        },
      });
    }
  }

  toggleIngredient(ingredient: string) {
    const current = new Set(this.selectedIngredients());
    if (current.has(ingredient)) {
      current.delete(ingredient);
    } else {
      current.add(ingredient);
    }
    this.selectedIngredients.set(current);
  }

  isIngredientSelected(ingredient: string): boolean {
    return this.selectedIngredients().has(ingredient);
  }

  onGetAlternatives() {
    const currentRecipe = this.recipe();
    const selected = Array.from(this.selectedIngredients());
    if (!currentRecipe || selected.length === 0) return;

    this.isLoadingAlternatives.set(true);
    this.alternatives.set(null);

    this.recipeService
      .getAlternatives({
        selected_ingredients: selected,
        original_recipe: currentRecipe,
      })
      .subscribe({
        next: (data) => {
          this.alternatives.set(data);
          this.isLoadingAlternatives.set(false);
        },
        error: (err) => {
          console.error('Error getting alternatives', err);
          this.isLoadingAlternatives.set(false);
        },
      });
  }

  applyNewRecipe() {
    const alt = this.alternatives();
    if (alt) {
      this.recipe.set(alt.new_recipe);
      this.alternatives.set(null);
      this.selectedIngredients.set(new Set());
      this.generateImage(alt.new_recipe.title);
    }
  }
}
