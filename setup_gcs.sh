#!/bin/bash

# Google Cloud Storage Setup Script for TikTok RSS
echo "🌤️  Google Cloud Storage Setup for TikTok RSS"
echo "============================================="

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  Google Cloud CLI not found."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "After installation, run:"
    echo "  gcloud auth login"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo ""
fi

# Install Google Cloud Storage library
echo "📦 Installing Google Cloud Storage library..."
source venv/bin/activate
pip install google-cloud-storage

echo ""
echo "🔧 GCS Setup Instructions:"
echo ""
echo "1. Create a GCS bucket:"
echo "   gsutil mb gs://your-tiktok-rss-bucket"
echo ""
echo "2. Create a service account (optional, for production):"
echo "   gcloud iam service-accounts create tiktok-rss-uploader \\"
echo "     --display-name=\"TikTok RSS Uploader\""
echo ""
echo "3. Grant permissions to the service account:"
echo "   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\"
echo "     --member=\"serviceAccount:tiktok-rss-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com\" \\"
echo "     --role=\"roles/storage.objectAdmin\""
echo ""
echo "4. Create and download credentials (optional):"
echo "   gcloud iam service-accounts keys create ~/tiktok-rss-credentials.json \\"
echo "     --iam-account=tiktok-rss-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com"
echo ""
echo "5. Set environment variables:"
echo "   export GCS_BUCKET_NAME=\"your-tiktok-rss-bucket\""
echo "   export GOOGLE_APPLICATION_CREDENTIALS=\"~/tiktok-rss-credentials.json\""
echo ""
echo "6. Or update config.py with your bucket name"
echo ""
echo "📖 For more details, see: https://cloud.google.com/storage/docs/quickstart"

# Create a sample .env file
cat > .env.example << EOF
# Google Cloud Storage Configuration
GCS_BUCKET_NAME=your-tiktok-rss-bucket
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

# Alternative: Use default credentials (if you're running on GCP)
# gcloud auth application-default login
EOF

echo ""
echo "📄 Created .env.example file with sample configuration"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Test your configuration with:"
echo "  python gcs_uploader.py your-bucket-name"