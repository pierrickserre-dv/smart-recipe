import base64

from google.cloud import storage


class GoogleStorageService:
    """Reusable Google Cloud Storage helper; bucket and client are injected."""

    def __init__(
        self,
        bucket_name: str,
        *,
        client: storage.Client | None = None,
    ):
        self._client = client if client is not None else storage.Client()
        self._bucket_name = bucket_name
        self._bucket = self._client.bucket(bucket_name)

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    def upload_bytes_make_public(
        self,
        object_name: str,
        data: bytes,
        content_type: str,
        *,
        md5_hex: str | None = None,
    ) -> str:
        """Upload bytes, set object public, return public URL."""
        blob = self._bucket.blob(object_name)
        if md5_hex:
            blob.md5_hash = base64.b64encode(bytes.fromhex(md5_hex)).decode("utf-8")
        blob.upload_from_string(data, content_type=content_type)
        blob.make_public()
        return blob.public_url

    def delete_by_public_url(self, public_url: str) -> None:
        """Best-effort delete using a URL that contains ``{bucket_name}/``."""
        try:
            blob_name = public_url.split(f"{self._bucket_name}/")[-1]
            self._bucket.blob(blob_name).delete()
        except Exception:
            pass
