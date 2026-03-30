import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { RecipeResponse, SaveRecipeResponse } from '../models/recipe.model';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private baseUrl = '/api/recipes';
  private http = inject(HttpClient);

  generateRecipe(ingredients: string[]): Observable<RecipeResponse> {
    return this.http.post<RecipeResponse>(`${this.baseUrl}/generate`, { ingredients });
  }

  saveRecipe(recipe: RecipeResponse): Observable<SaveRecipeResponse> {
    return this.http.post<SaveRecipeResponse>(`${this.baseUrl}/save`, recipe);
  }

  deleteRecipe(recipeId: string): Observable<SaveRecipeResponse> {
    return this.http.delete<SaveRecipeResponse>(`${this.baseUrl}/${recipeId}`);
  }

  getRecipes(): Observable<RecipeResponse[]> {
    return this.http.get<RecipeResponse[]>(this.baseUrl);
  }
}
