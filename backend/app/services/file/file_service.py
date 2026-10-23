import mimetypes
from datetime import datetime, timezone
from typing import Tuple
from fastapi import UploadFile
import httpx

from .mim_type_mapper import MIME_TYPE_MAP
from .minio_service import MinioService



class FileService:
    def __init__(self, minio_service: MinioService, base_upload_path: str, cdn_base_path: str, custom_http_proxy: str = None):
        self.minio_service = minio_service
        self.base_upload_path = base_upload_path
        self.cdn_base_path = cdn_base_path

        self.http_client = httpx.AsyncClient(
            proxy=custom_http_proxy if custom_http_proxy else None,
        )


    async def upload(self, file: UploadFile, title: str, file_source: str) -> str:
        # Read the file content
        file_content = await file.read()
        
        # Process and upload the file
        cdn_path = self._process_and_upload(
            file_content=file_content,
            filename=file.filename,
            title=title,
            file_source=file_source
        )
        
        return cdn_path

    async def download_and_upload(self, url: str, title: str, file_source: str) -> str:
        # Download the file from the URL
        file_content, filename = await self._download_file_from_url(url)

        # add unique timestamp at the beginning of title
        title = f"{int(datetime.now(timezone.utc).timestamp())}_{title}"

        # Process and upload the file
        cdn_path = self._process_and_upload(
            file_content=file_content,
            filename=filename,
            title=title,
            file_source=file_source
        )
        
        return cdn_path

    async def _download_file_from_url(self, url: str) -> Tuple[bytes, str]:
        try:
            response = await self.http_client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Extract filename from URL
            filename = url.split("/")[-1].split("?")[0]

            # Try to get filename from content-disposition header
            if "content-disposition" in response.headers:
                content_disposition = response.headers["content-disposition"]
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"')

            # Get content type and add extension if needed
            content_type = response.headers.get("content-type", "").split(";")[0].strip()

            if "." not in filename and content_type:
                ext = mimetypes.guess_extension(content_type)
                if ext:
                    filename += ext

            return response.content, filename

        except httpx.HTTPError as e:
            raise ValueError(f"Failed to download file from URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while downloading the file: {str(e)}")

    def _process_and_upload(
        self, file_content: bytes, filename: str, title: str, file_source: str
    ) -> str:
        # Detect and validate the file's MIME type
        mime_type, file_category = self._detect_and_validate_mime_type(filename)
        
        # Get the appropriate file extension
        extension = self._get_file_extension(mime_type)
        
        # Build storage and CDN paths
        storage_path = self._build_storage_path(title, file_source, file_category, extension)
        cdn_path = self._build_cdn_path(title, file_source, file_category, extension)
        
        # Check if file already exists
        if self.minio_service.check_file_exists(storage_path):
            raise ValueError(f"File already exists at path: {storage_path}")
        
        # Upload to MinIO
        self.minio_service.upload_image(
            file_path=storage_path,
            file_contents=file_content
        )
        
        return cdn_path

    def _detect_and_validate_mime_type(self, filename: str) -> Tuple[str, str]:
        mime_type, _ = mimetypes.guess_type(filename)

        if not mime_type:
            raise ValueError(f"Could not determine MIME type for file: {filename}")

        if mime_type.lower() not in MIME_TYPE_MAP:
            raise ValueError(f"Unsupported file type: {mime_type}")

        file_category = MIME_TYPE_MAP.get(mime_type.lower(), "other")
        return mime_type, file_category

    def _get_file_extension(self, mime_type: str) -> str:
        extension = mimetypes.guess_extension(mime_type)
        if extension is None:
            raise ValueError(f"Could not determine file extension for MIME type: {mime_type}")
        return extension

    def _build_storage_path(
        self, title: str, file_source: str, file_category: str, extension: str
    ) -> str:
        safe_filename = self._create_safe_filename(title, extension)
        return f"{self.base_upload_path}/{file_category}/{file_source}/{safe_filename}"

    def _build_cdn_path(
        self, title: str, file_source: str, file_category: str, extension: str
    ) -> str:
        safe_filename = self._create_safe_filename(title, extension)
        return f"{self.cdn_base_path}/{file_category}/{file_source}/{safe_filename}"

    def _create_safe_filename(self, title: str, extension: str) -> str:
        # Remove extension from title if present
        base_name = title.rsplit(".", 1)[0]
        
        # Sanitize the filename
        safe_name = self._sanitize_filename(base_name.strip().lower())
        
        return f"{safe_name}{extension}"

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        return "".join(
            char if char.isalnum() or char in ("_", "-", ".") else "_"
            for char in filename
        )

