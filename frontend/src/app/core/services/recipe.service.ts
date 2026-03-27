import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  AlternativesRequest,
  AlternativesResponse,
  ImageResponse,
  RecipeResponse,
  SavedRecipe,
  SaveRecipeResponse,
} from '../models/recipe.model';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private http = inject(HttpClient);

  generateRecipe(ingredients: string[]): Observable<RecipeResponse> {
    return this.http.post<RecipeResponse>('/api/generate', { ingredients });
  }

  saveRecipe(recipe: RecipeResponse): Observable<SaveRecipeResponse> {
    return this.http.post<SaveRecipeResponse>('/api/save', recipe);
  }

  getRecipes(): Observable<SavedRecipe[]> {
    return this.http.get<SavedRecipe[]>('/api/recipes');
  }

  generateImage(title: string): Observable<ImageResponse> {
    return this.http.post<ImageResponse>('/api/generate-image', { title });
  }

  getAlternatives(request: AlternativesRequest): Observable<AlternativesResponse> {
    return this.http.post<AlternativesResponse>('/api/alternatives', request);
  }
}
