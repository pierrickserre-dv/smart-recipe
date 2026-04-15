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

    async def get_user_equipment(self, user_id: str) -> list[str]:
        user_ref = self.db.collection("users").document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return []

        raw_equipment = user_doc.to_dict().get("equipment", [])
        if not isinstance(raw_equipment, list):
            return []

        normalized: list[str] = []
        seen: set[str] = set()
        for item in raw_equipment:
            if not isinstance(item, str):
                continue
            value = item.strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(value)
        return normalized

    async def save_user_equipment(self, user_id: str, equipment: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in equipment:
            value = item.strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(value)

        user_ref = self.db.collection("users").document(user_id)
        user_ref.set({"equipment": normalized}, merge=True)
        return normalized
