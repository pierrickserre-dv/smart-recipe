import base64
import hashlib
import uuid

from google.cloud import storage

from src.config import settings


class CloudStorageService:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.storage_bucket)

    def upload_recipe_image(
        self,
        user_id: str,
        recipe_id: str,
        image_base64: str,
        mime_type: str = "image/jpeg",
    ) -> str:
        """Upload a base64-encoded image to Cloud Storage and return its public URL."""
        extension = "jpg" if "jpeg" in mime_type else mime_type.split("/")[-1]
        unique_suffix = uuid.uuid4().hex[:8]
        blob_name = f"recipes/{user_id}/{recipe_id}_{unique_suffix}.{extension}"

        image_bytes = base64.b64decode(image_base64)

        content_hash = hashlib.md5(image_bytes).hexdigest()
        blob = self.bucket.blob(blob_name)
        blob.md5_hash = base64.b64encode(bytes.fromhex(content_hash)).decode("utf-8")

        blob.upload_from_string(image_bytes, content_type=mime_type)
        blob.make_public()

        return blob.public_url

    def delete_recipe_image(self, image_url: str) -> None:
        """Delete an image from Cloud Storage by its public URL."""
        try:
            blob_name = image_url.split(f"{settings.storage_bucket}/")[-1]
            blob = self.bucket.blob(blob_name)
            blob.delete()
        except Exception:
            pass
