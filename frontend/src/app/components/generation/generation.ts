import { Component, ElementRef, inject, Input, signal, ViewChild } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RecipeResponse, SaveRecipeRequest } from '../../core/models/recipe.model';
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
  @ViewChild('recipeCard') recipeCardRef?: ElementRef<HTMLElement>;

  recipe = signal<RecipeResponse | null>(null);

  status = signal<GenerationStatus>('idle');

  private recipeService = inject(RecipeService);

  imageBase64 = signal<string | null>(null);
  imageMimeType = signal<string>('image/jpeg');
  isLoadingImage = signal(false);

  /** Indices of recipe ingredients excluded from the next alternative generation. */
  removedIngredientIndices = signal<Set<number>>(new Set());

  /** Extra ingredients the user adds for the next alternative (not shown in the current recipe list). */
  additionalIngredients = signal<string[]>([]);

  isRegenerating = signal(false);

  private pendingScroll = false;

  onGenerate() {
    this.resetIngredientEditing();
    this.status.set('loading');
    this.recipe.set(null);

    this.recipeService.generateRecipe(this.ingredients).subscribe({
      next: (data) => {
        this.recipe.set(data);
        this.status.set('success');
        this.generateImage(data.title);
        this.scrollToRecipeCardAfterRender();
      },
      error: (err) => {
        console.error('Error during generation', err);
        this.status.set('error');
      },
    });
  }

  private resetIngredientEditing(): void {
    this.removedIngredientIndices.set(new Set());
    this.additionalIngredients.set([]);
  }

  toggleIngredientRemoval(index: number): void {
    if (this.isRegenerating()) {
      return;
    }
    this.removedIngredientIndices.update((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }

  isIngredientRemoved(index: number): boolean {
    return this.removedIngredientIndices().has(index);
  }

  effectiveIngredientsForAlternative(): string[] {
    const r = this.recipe();
    if (!r) {
      return [];
    }
    const removed = this.removedIngredientIndices();
    const fromRecipe = r.ingredients_used.filter((_, i) => !removed.has(i));
    const extra = this.additionalIngredients();
    const merged = [...fromRecipe, ...extra].map((s) => s.trim()).filter(Boolean);

    const seen = new Set<string>();
    const out: string[] = [];
    for (const item of merged) {
      const key = item.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        out.push(item);
      }
    }
    return out;
  }

  addExtraIngredient(raw: string): void {
    if (this.isRegenerating()) {
      return;
    }
    const name = raw.trim();
    if (!name) {
      return;
    }
    const key = name.toLowerCase();
    const r = this.recipe();
    const fromRecipe = r
      ? r.ingredients_used.filter((_, i) => !this.removedIngredientIndices().has(i))
      : [];
    if (
      fromRecipe.some((x) => x.toLowerCase() === key) ||
      this.additionalIngredients().some((x) => x.toLowerCase() === key)
    ) {
      return;
    }
    this.additionalIngredients.update((list) => [...list, name]);
  }

  removeAdditionalIngredient(index: number): void {
    if (this.isRegenerating()) {
      return;
    }
    this.additionalIngredients.update((list) => list.filter((_, i) => i !== index));
  }

  onGenerateAlternative(): void {
    const ings = this.effectiveIngredientsForAlternative();
    if (ings.length === 0 || this.isRegenerating()) {
      return;
    }
    this.isRegenerating.set(true);
    this.recipeService.generateRecipe(ings).subscribe({
      next: (data) => {
        this.resetIngredientEditing();
        this.recipe.set(data);
        this.status.set('success');
        this.isRegenerating.set(false);
        this.generateImage(data.title);
        this.scrollToRecipeCardAfterRender();
      },
      error: (err) => {
        console.error('Error during alternative generation', err);
        this.isRegenerating.set(false);
        this.status.set('error');
      },
    });
  }

  private generateImage(title: string) {
    this.imageBase64.set(null);
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

  private scrollToRecipeCardAfterRender(): void {
    this.pendingScroll = true;
    requestAnimationFrame(() => {
      const card = this.recipeCardRef?.nativeElement;
      if (!card) {
        return;
      }
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
      this.pendingScroll = false;
    });
  }

  onSave() {
    const currentRecipe = this.recipe();

    if (currentRecipe && this.status() !== 'saved' && !this.isRegenerating()) {
      this.status.set('saving');

      const saveRequest: SaveRecipeRequest = {
        title: currentRecipe.title,
        prep_time: currentRecipe.prep_time,
        difficulty: currentRecipe.difficulty,
        ingredients_used: currentRecipe.ingredients_used,
        instructions: currentRecipe.instructions,
        image_base64: this.imageBase64() ?? undefined,
        image_mime_type: this.imageBase64() ? this.imageMimeType() : undefined,
      };

      this.recipeService.saveRecipe(saveRequest).subscribe({
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
