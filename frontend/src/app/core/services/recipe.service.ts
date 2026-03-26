import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { RecipeResponse } from '../models/recipe.model';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private apiUrl = '/api/generate';
  private http = inject(HttpClient);

  generateRecipe(ingredients: string[]): Observable<RecipeResponse> {
    return this.http.post<RecipeResponse>(this.apiUrl, { ingredients });
  }

  saveRecipe(recipe: RecipeResponse): Observable<any> {
    return this.http.post<any>('/api/save', recipe);
  }
}
