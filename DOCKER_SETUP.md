# Docker Setup for TikTok RSS Generator 🐳

Run your TikTok RSS generator in Docker for consistent, portable deployment across any environment.

## 🚀 Quick Start

### 1. Initial Setup

```bash
# One-time setup
./docker-manager.sh setup
```

### 2. Configure Environment

```bash
# Edit the environment file
nano .env

# Add your GCS bucket name
GCS_BUCKET_NAME=your-tiktok-rss-bucket
```

### 3. Run the Generator

```bash
# Run once
./docker-manager.sh run

# Or start in background
./docker-manager.sh start

# Or run with scheduler (every 4 hours)
./docker-manager.sh scheduler
```

## 📁 Files Created

- **`Dockerfile`** - Main container definition
- **`docker-compose.yml`** - Multi-container orchestration  
- **`.dockerignore`** - Build optimization
- **`.env.example`** - Environment template
- **`docker-manager.sh`** - Management script

## 🛠️ Docker Manager Commands

```bash
./docker-manager.sh [command]
```

| Command | Description |
|---------|-------------|
| `setup` | Initial setup with environment file |
| `build` | Build the Docker image |
| `run` | Run the container once |
| `start` | Start container in background |
| `scheduler` | Start with 4-hour scheduler |
| `stop` | Stop running containers |
| `logs` | Show container logs |
| `shell` | Open shell in container |
| `clean` | Clean up containers and images |

## 🏗️ Manual Docker Commands

### Build Image

```bash
docker build -t tiktok-rss:latest .
```

### Run Once

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/rss:/app/rss" \
  -v "$(pwd)/json:/app/json" \
  -v "$(pwd)/thumbnails:/app/thumbnails" \
  -v "$(pwd)/subscriptions.csv:/app/subscriptions.csv" \
  -v "$(pwd)/config.py:/app/config.py" \
  tiktok-rss:latest
```

### Run with Docker Compose

```bash
# Run once
docker-compose up

# Run in background
docker-compose up -d

# Run scheduler (every 4 hours)
docker-compose --profile scheduler up -d
```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# Required
GCS_BUCKET_NAME=your-tiktok-rss-bucket

# Optional
GCS_CREDENTIALS_PATH=./credentials/gcs-credentials.json
TZ=UTC
```

### Volume Mounts

- `./rss:/app/rss` - RSS output files
- `./json:/app/json` - JSON output files  
- `./thumbnails:/app/thumbnails` - Downloaded thumbnails
- `./subscriptions.csv:/app/subscriptions.csv` - User list
- `./config.py:/app/config.py` - Configuration
- `./credentials:/app/credentials` - GCS credentials

### Google Cloud Storage Setup

```bash
# Create credentials directory
mkdir -p credentials

# Place your service account key
cp ~/gcs-credentials.json credentials/gcs-credentials.json

# Or use default credentials (in container)
# gcloud auth application-default login
```

## 📊 Container Features

### Base Image

- **Python 3.11-slim** for security and size optimization
- **Playwright** with Chromium browser installed
- **System dependencies** for web scraping

### Security

- Non-root user execution
- Minimal attack surface
- Read-only credential mounts

### Performance  

- **Multi-stage build** optimization
- **Layer caching** for faster rebuilds
- **Resource limits** (1GB RAM, 0.5 CPU)

### Monitoring

- **Health checks** for container status
- **Structured logging** to stdout
- **Exit code handling** for orchestration

## 🔄 Scheduler Mode

Run continuously with 4-hour intervals:

```bash
# Start scheduler
./docker-manager.sh scheduler

# View logs
./docker-manager.sh logs

# Stop scheduler  
./docker-manager.sh stop
```

The scheduler:

- Runs `postprocessing.py` every 4 hours
- Automatically restarts on failure
- Uploads to GCS after each run
- Maintains persistent data volumes

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
./docker-manager.sh logs

# Check environment
cat .env

# Test in interactive mode
./docker-manager.sh shell
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER rss json thumbnails

# Or run with user mapping
docker run --user $(id -u):$(id -g) ...
```

### Network Issues

```bash
# Check container networking
docker network ls

# Run with host networking (less secure)
docker run --network host ...
```

### Memory Issues

```bash
# Check resource usage
docker stats

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

## 🎯 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml tiktok-rss
```

### Kubernetes

```bash
# Generate Kubernetes manifests
kompose convert

# Deploy to cluster
kubectl apply -f tiktok-rss-deployment.yaml
```

### Cloud Platforms

- **Google Cloud Run** - Serverless containers
- **AWS ECS** - Elastic Container Service  
- **Azure Container Instances** - Managed containers

## 📈 Monitoring & Logging

### Container Logs

```bash
# Follow logs
docker-compose logs -f

# Logs for specific service
docker-compose logs -f tiktok-rss-scheduler
```

### Health Monitoring

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Detailed health info
docker inspect --format='{{.State.Health.Status}}' tiktok-rss-generator
```

### External Monitoring

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation

## 🔒 Security Considerations

### Secrets Management

- Never put credentials in images
- Use Docker secrets or volume mounts
- Rotate credentials regularly

### Network Security

- Use private networks when possible
- Limit container privileges
- Keep base images updated

### Data Security

- Encrypt sensitive volumes
- Use read-only mounts where possible
- Regular security scans

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Playwright in Docker](https://playwright.dev/docs/docker)
- [Google Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)

---

Your TikTok RSS generator is now fully containerized! 🎉
