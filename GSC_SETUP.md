# Google Cloud Storage Integration 🌤️

Your TikTok RSS generator now automatically uploads JSON files to Google Cloud Storage after each successful generation!

## ✅ What's Included

1. **Automatic Upload**: JSON files are uploaded to GCS immediately after generation
2. **Error Handling**: Graceful fallback if GCS is not configured
3. **Metadata**: Rich metadata attached to uploaded files
4. **Optional**: GCS is completely optional - the script works without it

## 🚀 Quick Setup

### 1. Install Google Cloud CLI (if not already installed)

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Authenticate and Create Bucket

```bash
# Login to Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create a bucket (replace with your desired name)
gsutil mb gs://your-tiktok-rss-bucket

# Make bucket publicly readable (optional)
gsutil iam ch allUsers:objectViewer gs://your-tiktok-rss-bucket
```

### 3. Configure Environment Variables

```bash
# Set bucket name
export GCS_BUCKET_NAME="your-tiktok-rss-bucket"

# Optional: Use service account credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### 4. Test Configuration

```bash
python test_gcs.py
```

## 📁 File Structure in GCS

After upload, your files will be organized as:

```
gs://your-bucket/
├── tiktok-data/
│   ├── json/
│   │   ├── user1.json
│   │   ├── user2.json
│   │   └── user3.json
│   └── index.json (created by gcs_uploader.py)
```

## 🔧 Configuration Options

### Option 1: Environment Variables (Recommended)

```bash
export GCS_BUCKET_NAME="your-tiktok-rss-bucket"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### Option 2: Edit config.py

```python
# In config.py
GCS_BUCKET_NAME = "your-tiktok-rss-bucket"
GCS_CREDENTIALS_PATH = "path/to/credentials.json"
```

## 🔐 Authentication Methods

### Method 1: Default Credentials (Easiest)

```bash
gcloud auth application-default login
```

### Method 2: Service Account (Production)

```bash
# Create service account
gcloud iam service-accounts create tiktok-rss-uploader --display-name="TikTok RSS Uploader"

# Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:tiktok-rss-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create ~/tiktok-rss-credentials.json \
  --iam-account=tiktok-rss-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS="~/tiktok-rss-credentials.json"
```

## 📊 What Gets Uploaded

Each JSON file is uploaded with:

- **Content**: Complete TikTok user data and videos
- **Metadata**:
  - `uploaded_at`: Timestamp of upload
  - `source`: "tiktok-rss-generator"
  - `user`: TikTok username
  - `file_size`: File size in bytes
- **Content-Type**: `application/json`
- **Path**: `tiktok-data/json/{username}.json`

## 🛠️ Manual Upload Tools

### Upload All JSON Files

```bash
python gcs_uploader.py your-bucket-name
```

### Upload with Custom Path

```python
from gcs_uploader import GCSUploader

uploader = GCSUploader("your-bucket-name")
uploader.upload_file("json/user.json", "custom/path/user.json")
```

### Create Index File

```bash
python gcs_uploader.py your-bucket-name
# This automatically creates an index.json with all file metadata
```

## 🔍 Monitoring Uploads

The main script will show upload status:

```
✅ Generated RSS: rss/user.xml and JSON: json/user.json
☁️  Uploaded json/user.json to gs://your-bucket/tiktok-data/json/user.json
```

If GCS is not configured:

```
⚠️  GCS bucket not configured for user, skipping upload
```

## 🚨 Troubleshooting

### Import Error

```
❌ Google Cloud Storage not available. Install with: pip install google-cloud-storage
```

**Solution**: Run `pip install google-cloud-storage`

### Permission Denied

```
❌ Failed to upload: 403 Permission denied
```

**Solutions**:

- Check bucket name is correct
- Verify authentication: `gcloud auth list`
- Check IAM permissions
- Try: `gcloud auth application-default login`

### Bucket Not Found

```
❌ Failed to upload: 404 Bucket not found
```

**Solution**: Create bucket with `gsutil mb gs://your-bucket-name`

### Configuration Issues

```
⚠️  GCS bucket not configured
```

**Solution**: Set `GCS_BUCKET_NAME` environment variable or update `config.py`

## 📈 Usage Patterns

### Development

- Use `gcloud auth application-default login`
- Set `GCS_BUCKET_NAME` environment variable
- Run normally: `python postprocessing.py`

### Production/CI

- Use service account credentials
- Set both `GCS_BUCKET_NAME` and `GOOGLE_APPLICATION_CREDENTIALS`
- Consider using IAM roles instead of key files

### No GCS

- Simply don't set `GCS_BUCKET_NAME`
- Script works normally, just skips uploads
- No errors or interruptions

## 🎯 Benefits

1. **Automatic Backup**: Your data is safely stored in the cloud
2. **Scalability**: GCS handles any amount of data
3. **Accessibility**: Access your data from anywhere
4. **Integration**: Easy to integrate with other GCP services
5. **Optional**: Zero impact if not configured

## 🔗 Useful Links

- [Google Cloud Storage Docs](https://cloud.google.com/storage/docs)
- [Authentication Guide](https://cloud.google.com/docs/authentication)
- [gsutil Reference](https://cloud.google.com/storage/docs/gsutil)
- [IAM Roles](https://cloud.google.com/storage/docs/access-control/iam-roles)

---

Your JSON files now automatically backup to Google Cloud Storage! 🎉
