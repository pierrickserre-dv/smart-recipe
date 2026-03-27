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

export interface SavedRecipe extends RecipeResponse {
  id: string;
  created_at: string | null;
}

export interface SaveRecipeResponse {
  status: string;
  message: string;
  id: string;
}

export interface ImageResponse {
  image_base64: string;
  mime_type: string;
}

export interface AlternativesRequest {
  selected_ingredients: string[];
  original_recipe: RecipeResponse;
}

export interface IngredientAlternative {
  original: string;
  alternatives: string[];
}

export interface AlternativesResponse {
  suggestions: IngredientAlternative[];
  new_recipe: RecipeResponse;
}
