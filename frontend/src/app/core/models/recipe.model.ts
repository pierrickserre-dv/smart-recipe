export interface RecipeRequest {
  ingredients: string[];
}

export interface RecipeResponse {
  id?: string;
  title: string;
  prep_time: string;
  difficulty: string;
  ingredients_used: string[];
  instructions: string[];
  image_url?: string;
}

export interface SaveRecipeRequest {
  title: string;
  prep_time: string;
  difficulty: string;
  ingredients_used: string[];
  instructions: string[];
  image_base64?: string;
  image_mime_type?: string;
}

export interface SaveRecipeResponse {
  status: string;
  message: string;
  id: string;
}

export interface SuccessResponse {
  status: string;
  message: string;
}

export interface ImageResponse {
  image_base64: string;
  mime_type: string;
}
