import { Component, inject, Input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RecipeResponse } from '../../core/models/recipe.model';
import { RecipeService } from '../../core/services/recipe.service';

export type GenerationStatus = 'idle' | 'loading' | 'success' | 'saving' | 'saved' | 'error';

@Component({
  selector: 'app-generation',
  imports: [RouterLink],
  templateUrl: './generation.html',
  styleUrl: './generation.css',
})
export class Generation {
  @Input() ingredients: string[] = [];

  recipe = signal<RecipeResponse | null>(null);

  status = signal<GenerationStatus>('idle');

  private recipeService = inject(RecipeService);

  imageBase64 = signal<string | null>(null);
  imageMimeType = signal<string>('image/jpeg');
  isLoadingImage = signal(false);

  onGenerate() {
    this.status.set('loading');
    this.recipe.set(null);

    this.recipeService.generateRecipe(this.ingredients).subscribe({
      next: (data) => {
        this.recipe.set(data);
        this.status.set('success');
        this.generateImage(data.title);
      },
      error: (err) => {
        console.error('Error during generation', err);
        this.status.set('error');
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

    if (currentRecipe && this.status() !== 'saved') {
      this.status.set('saving');

      this.recipeService.saveRecipe(currentRecipe).subscribe({
        next: (response) => {
          console.log('Recipe saved with ID: ', response.id);
          this.status.set('saved');
        },
        error: (err) => {
          console.error('Error while saving.', err);
          this.status.set('error');
        },
      });
    }
  }
}
