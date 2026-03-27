import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { RecipeResponse, SaveRecipeResponse } from '../models/recipe.model';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private apiUrl = '/api/generate';
  private http = inject(HttpClient);

  generateRecipe(ingredients: string[]): Observable<RecipeResponse> {
    return this.http.post<RecipeResponse>(this.apiUrl, { ingredients });
  }

  saveRecipe(recipe: RecipeResponse): Observable<SaveRecipeResponse> {
    return this.http.post<SaveRecipeResponse>('/api/recipe', recipe);
  }

  deleteRecipe(recipeId: string): Observable<SaveRecipeResponse> {
    return this.http.delete<SaveRecipeResponse>(`/api/recipes/${recipeId}`);
  }

  getRecipes(): Observable<RecipeResponse[]> {
    return this.http.get<RecipeResponse[]>('/api/recipes');
  }
}
