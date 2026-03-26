export interface RecipeRequest {
  ingredients: string[];
}

export interface RecipeResponse {
  title: string;
  prep_time: string;
  difficulty: string;
  ingredients_used: string[];
  instructions: string[];
}

export interface SaveRecipeResponse {
  status: string;
  message: string;
  id: string;
}
