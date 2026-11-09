import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  EquipmentRequest,
  EquipmentResponse,
  ImageResponse,
  RecipeResponse,
  SaveRecipeRequest,
  SaveRecipeResponse,
} from '../models/recipe.model';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private baseUrl = '/api/recipes';
  private http = inject(HttpClient);

  generateRecipe(ingredients: string[]): Observable<RecipeResponse> {
    return this.http.post<RecipeResponse>(`${this.baseUrl}/generate`, { ingredients });
  }

  saveRecipe(request: SaveRecipeRequest): Observable<SaveRecipeResponse> {
    return this.http.post<SaveRecipeResponse>(`${this.baseUrl}/save`, request);
  }

  deleteRecipe(recipeId: string): Observable<SaveRecipeResponse> {
    return this.http.delete<SaveRecipeResponse>(`${this.baseUrl}/${recipeId}`);
  }

  getRecipes(): Observable<RecipeResponse[]> {
    return this.http.get<RecipeResponse[]>(this.baseUrl);
  }

  generateImage(title: string): Observable<ImageResponse> {
    return this.http.post<ImageResponse>(`${this.baseUrl}/generate-image`, { title });
  }

  getEquipment(): Observable<EquipmentResponse> {
    return this.http.get<EquipmentResponse>(`${this.baseUrl}/account/equipment`);
  }

  updateEquipment(equipment: string[]): Observable<EquipmentResponse> {
    const payload: EquipmentRequest = { equipment };
    return this.http.put<EquipmentResponse>(`${this.baseUrl}/account/equipment`, payload);
  }
}
