import { Component, effect, inject, Input, signal, untracked } from '@angular/core';
import { RecipeResponse } from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

export type GenerationStatus = 'idle' | 'loading' | 'success' | 'saving' | 'saved' | 'error';

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
  isSaving = signal<boolean>(false);
  isSaved = signal<boolean>(false);

  status = signal<GenerationStatus>('idle');

  private recipeService = inject(RecipeService);

  constructor() {
    effect(() => {
      this.recipe();

      untracked(() => {
        if (this.status() === 'saved') {
          this.status.set('success');
        }
      });
    });
  }

  onGenerate() {
    this.status.set('loading');
    this.recipe.set(null);

    this.recipeService.generateRecipe(this.ingredients).subscribe({
      next: (data) => {
        this.recipe.set(data);
        this.status.set('success');
      },
      error: (err) => {
        console.error('Error during generation', err);
        this.status.set('error');
      },
    });
  }

  onSave() {
    this.isSaving.set(true);

    const currentRecipe = this.recipe();
    if (currentRecipe && !this.isSaved()) {
      this.status.set('success');

      this.recipeService.saveRecipe(currentRecipe).subscribe({
        next: (response) => {
          console.log('Recette sauvegardée avec ID: ', response.id);
          this.status.set('saved');
        },
        error: (err) => {
          console.error('Erreur lors de la sauvegarde ', err);
          this.status.set('error');
        },
      });
    }
  }
}
