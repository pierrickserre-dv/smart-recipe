import hashlib

from google.cloud import firestore

from .schemas import RecipeResponse


class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()

    async def save_recipe_for_user(self, user_id: str, recipe: RecipeResponse):
        recipe_id = hashlib.md5(recipe.title.lower().strip().encode()).hexdigest()
        user_recipes_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("recipes")
            .document(recipe_id)
        )

        recipe_data = recipe.model_dump()

        recipe_data["created_at"] = firestore.SERVER_TIMESTAMP

        user_recipes_ref.set(recipe_data, merge=True)
        return recipe_id
