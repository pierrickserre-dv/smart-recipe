from google.cloud import firestore

from .schemas import RecipeResponse


class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()

    async def save_recipe_for_user(self, user_id: str, recipe: RecipeResponse):
        user_recipes_ref = (
            self.db.collection("users").document(user_id).collection("recipes")
        )

        recipe_data = recipe.model_dump()

        recipe_data["created_at"] = firestore.SERVER_TIMESTAMP

        _, doc_ref = user_recipes_ref.add(recipe_data)
        return doc_ref.id
