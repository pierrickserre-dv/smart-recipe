import hashlib

from google.cloud import firestore

from .schemas import RecipeResponse, SavedRecipe


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

        await user_recipes_ref.set(recipe_data, merge=True)
        return recipe_id

    def get_user_recipes(self, user_id: str, limit: int = 10) -> list[SavedRecipe]:
        recipes_ref = (
            self.db.collection("users").document(user_id).collection("recipes")
        )
        query = recipes_ref.order_by(
            "created_at", direction=firestore.Query.DESCENDING
        ).limit(limit)

        recipes = []
        for doc in query.stream():
            data = doc.to_dict()
            created_at = data.get("created_at")
            if created_at and hasattr(created_at, "isoformat"):
                data["created_at"] = created_at.isoformat()
            else:
                data["created_at"] = None
            data["id"] = doc.id
            recipes.append(SavedRecipe(**data))
        return recipes
