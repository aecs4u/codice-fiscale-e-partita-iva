#!/usr/bin/env python3
"""
Cloud Run entry point for Lighthouse.

This is a simple, direct approach for Cloud Run deployment.
"""

import os
from pathlib import Path

from codice_fiscale.config import settings  # noqa: E402
from lcodice_fiscale.main import app  # noqa: E402 - import after env var set

# Set Cloud Function environment flag (for compatibility)
# NOTE: This must be set BEFORE importing the app
os.environ['GOOGLE_CLOUD_FUNCTION'] = '1'

# Import settings to get configuration

# Download database from Cloud Storage if configured and doesn't exist locally
if settings.gcs_database_bucket:
    db_path = Path(settings.database_local_path)

    if not db_path.exists():
        print(f"📥 Downloading database from {settings.gcs_database_bucket}...")
        try:
            from google.cloud import storage

            # Parse GCS URL: gs://bucket-name/path/to/file
            gcs_url = settings.gcs_database_bucket
            if not gcs_url.startswith("gs://"):
                raise ValueError(f"Invalid GCS URL: {gcs_url}")

            # Remove gs:// prefix and split bucket/path
            gcs_path = gcs_url[5:]  # Remove 'gs://'
            bucket_name, blob_path = gcs_path.split('/', 1)

            # Download from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            # Ensure parent directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            blob.download_to_filename(str(db_path))
            print(f"✅ Database downloaded successfully to {db_path}")
        except Exception as e:
            print(f"⚠️  Failed to download database: {e}")
            print(f"ℹ️  Starting with empty database - will be created automatically")
    else:
        print(f"✅ Database already exists at {db_path}")

# Import and expose the FastAPI app directly

# This is the ASGI application that will be run by uvicorn
# No need for complex wrappers - just expose the FastAPI app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Starting FastAPI server on 0.0.0.0:{port}")
    print(f"📍 Health check: http://0.0.0.0:{port}/health")
    print(f"📖 API docs: http://0.0.0.0:{port}/docs")
    
    # Run the server directly
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )