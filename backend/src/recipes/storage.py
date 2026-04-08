import base64
import hashlib
import uuid

from src.storage.google_storage import GoogleStorageService


def upload_recipe_image(
    gcs: GoogleStorageService,
    user_id: str,
    recipe_id: str,
    image_base64: str,
    mime_type: str = "image/jpeg",
) -> str:
    """Upload a base64-encoded image and return its public URL."""
    extension = "jpg" if "jpeg" in mime_type else mime_type.split("/")[-1]
    unique_suffix = uuid.uuid4().hex[:8]
    object_name = f"recipes/{user_id}/{recipe_id}_{unique_suffix}.{extension}"

    image_bytes = base64.b64decode(image_base64)
    md5_hex = hashlib.md5(image_bytes).hexdigest()

    return gcs.upload_bytes_make_public(
        object_name,
        image_bytes,
        mime_type,
        md5_hex=md5_hex,
    )


def delete_recipe_image(gcs: GoogleStorageService, image_url: str) -> None:
    """Delete a recipe image from storage using its public URL."""
    gcs.delete_by_public_url(image_url)
