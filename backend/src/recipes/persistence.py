import hashlib

from google.cloud import firestore

from .schemas import SaveRecipeRequest


class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()

    async def save_recipe_for_user(
        self,
        user_id: str,
        recipe: SaveRecipeRequest,
        image_url: str | None = None,
    ) -> str:
        recipe_id = hashlib.md5(recipe.title.lower().strip().encode()).hexdigest()
        user_recipes_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("recipes")
            .document(recipe_id)
        )

        recipe_data = recipe.model_dump(exclude={"image_base64", "image_mime_type"})
        recipe_data["created_at"] = firestore.SERVER_TIMESTAMP

        if image_url:
            recipe_data["image_url"] = image_url

        user_recipes_ref.set(recipe_data, merge=True)
        return recipe_id

    async def delete_recipe_for_user(self, user_id: str, recipe_id: str) -> str | None:
        doc_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("recipes")
            .document(recipe_id)
        )
        doc = doc_ref.get()
        image_url = doc.to_dict().get("image_url") if doc.exists else None
        doc_ref.delete()
        return image_url

    async def get_recipes(self, user_id: str, limit: int = 10):
        query = (
            self.db.collection("users")
            .document(user_id)
            .collection("recipes")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        recipes = []
        for doc in query.stream():
            recipe_data = doc.to_dict()
            recipe_data["id"] = doc.id
            recipes.append(recipe_data)
        return recipes
