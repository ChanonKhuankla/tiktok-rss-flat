#!/usr/bin/env python3
"""
Google Cloud Storage Uploader for TikTok RSS JSON files
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from google.cloud import storage
from google.oauth2 import service_account


class GCSUploader:
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """
        Initialize GCS uploader

        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to service account JSON file (optional if using default credentials)
        """
        self.bucket_name = bucket_name

        # Initialize the client
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            # Use default credentials (environment variable GOOGLE_APPLICATION_CREDENTIALS)
            self.client = storage.Client()

        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, local_file_path: str, gcs_file_path: str = None) -> bool:
        """
        Upload a single file to GCS

        Args:
            local_file_path: Path to local file
            gcs_file_path: Path in GCS bucket (if None, uses local filename)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(local_file_path):
                print(f"❌ Local file not found: {local_file_path}")
                return False

            if gcs_file_path is None:
                gcs_file_path = os.path.basename(local_file_path)

            blob = self.bucket.blob(gcs_file_path)

            # Set content type based on file extension
            if local_file_path.endswith('.json'):
                blob.content_type = 'application/json'
            elif local_file_path.endswith('.xml'):
                blob.content_type = 'application/xml'
            elif local_file_path.endswith('.jpg') or local_file_path.endswith('.jpeg'):
                blob.content_type = 'image/jpeg'

            blob.upload_from_filename(local_file_path)

            print(
                f"✅ Uploaded {local_file_path} to gs://{self.bucket_name}/{gcs_file_path}")
            return True

        except Exception as e:
            print(f"❌ Error uploading {local_file_path}: {e}")
            return False

    def upload_json_folder(self, json_folder: str = "json", prefix: str = "tiktok-data/json/") -> List[str]:
        """
        Upload all JSON files from the json folder

        Args:
            json_folder: Local folder containing JSON files
            prefix: GCS path prefix for uploaded files

        Returns:
            List of successfully uploaded file paths
        """
        uploaded_files = []

        if not os.path.exists(json_folder):
            print(f"❌ JSON folder not found: {json_folder}")
            return uploaded_files

        json_files = list(Path(json_folder).glob("*.json"))

        if not json_files:
            print(f"⚠️  No JSON files found in {json_folder}")
            return uploaded_files

        print(f"📁 Found {len(json_files)} JSON files to upload")

        for json_file in json_files:
            gcs_path = f"{prefix}{json_file.name}"
            if self.upload_file(str(json_file), gcs_path):
                uploaded_files.append(str(json_file))

        return uploaded_files

    def upload_with_metadata(self, local_file_path: str, gcs_file_path: str = None, metadata: dict = None) -> bool:
        """
        Upload file with custom metadata

        Args:
            local_file_path: Path to local file
            gcs_file_path: Path in GCS bucket
            metadata: Custom metadata dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(local_file_path):
                print(f"❌ Local file not found: {local_file_path}")
                return False

            if gcs_file_path is None:
                gcs_file_path = os.path.basename(local_file_path)

            blob = self.bucket.blob(gcs_file_path)

            # Set content type
            if local_file_path.endswith('.json'):
                blob.content_type = 'application/json'
            elif local_file_path.endswith('.xml'):
                blob.content_type = 'application/xml'

            # Add metadata
            if metadata:
                blob.metadata = metadata

            # Add standard metadata
            blob.metadata = blob.metadata or {}
            blob.metadata.update({
                'uploaded_at': datetime.utcnow().isoformat(),
                'source': 'tiktok-rss-generator',
                'file_size': str(os.path.getsize(local_file_path))
            })

            blob.upload_from_filename(local_file_path)

            print(
                f"✅ Uploaded {local_file_path} to gs://{self.bucket_name}/{gcs_file_path} with metadata")
            return True

        except Exception as e:
            print(f"❌ Error uploading {local_file_path}: {e}")
            return False

    def create_index_file(self, uploaded_files: List[str], index_path: str = "tiktok-data/index.json") -> bool:
        """
        Create an index file listing all uploaded files

        Args:
            uploaded_files: List of uploaded file paths
            index_path: GCS path for the index file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            index_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "total_files": len(uploaded_files),
                "files": []
            }

            for file_path in uploaded_files:
                file_name = os.path.basename(file_path)
                user_name = file_name.replace('.json', '')

                # Try to read the JSON file to get additional info
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        video_count = len(data.get('videos', []))
                        last_updated = data.get('updated')
                except:
                    video_count = 0
                    last_updated = None

                index_data["files"].append({
                    "user": user_name,
                    "filename": file_name,
                    "gcs_path": f"tiktok-data/json/{file_name}",
                    "video_count": video_count,
                    "last_updated": last_updated,
                    "file_size": os.path.getsize(file_path)
                })

            # Upload index as a blob
            blob = self.bucket.blob(index_path)
            blob.content_type = 'application/json'
            blob.metadata = {
                'uploaded_at': datetime.utcnow().isoformat(),
                'source': 'tiktok-rss-generator-index',
                'type': 'index'
            }

            blob.upload_from_string(
                json.dumps(index_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )

            print(
                f"✅ Created index file at gs://{self.bucket_name}/{index_path}")
            return True

        except Exception as e:
            print(f"❌ Error creating index file: {e}")
            return False


def get_gcs_config():
    """Get GCS configuration from environment variables or config file"""
    # Try environment variables first
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    # Try config file
    if not bucket_name:
        try:
            import config
            bucket_name = getattr(config, 'GCS_BUCKET_NAME', None)
            credentials_path = getattr(config, 'GCS_CREDENTIALS_PATH', None)
        except:
            pass

    return bucket_name, credentials_path


def upload_json_files(bucket_name: str = None, credentials_path: str = None) -> bool:
    """
    Main function to upload JSON files to GCS

    Args:
        bucket_name: GCS bucket name
        credentials_path: Path to service account JSON

    Returns:
        bool: True if successful, False otherwise
    """
    if not bucket_name:
        bucket_name, creds_path = get_gcs_config()
        credentials_path = credentials_path or creds_path

    if not bucket_name:
        print("❌ GCS bucket name not provided!")
        print("Set environment variable: export GCS_BUCKET_NAME='your-bucket-name'")
        print("Or add GCS_BUCKET_NAME to config.py")
        return False

    try:
        uploader = GCSUploader(bucket_name, credentials_path)

        print(f"🚀 Starting upload to GCS bucket: {bucket_name}")

        # Upload JSON files
        uploaded_files = uploader.upload_json_folder()

        if uploaded_files:
            print(f"📊 Successfully uploaded {len(uploaded_files)} files")

            # Create index file
            uploader.create_index_file(uploaded_files)

            return True
        else:
            print("❌ No files were uploaded")
            return False

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        bucket_name = sys.argv[1]
        credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
        upload_json_files(bucket_name, credentials_path)
    else:
        print("Usage:")
        print("  python gcs_uploader.py <bucket-name> [credentials-path]")
        print("  or set environment variables:")
        print("  export GCS_BUCKET_NAME='your-bucket-name'")
        print("  export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
        upload_json_files()
