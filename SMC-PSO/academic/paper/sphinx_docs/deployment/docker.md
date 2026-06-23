# Docker Deployment Guide

**Complete guide to containerizing and deploying the DIP-SMC-PSO framework using Docker.**



## Table of Contents

- [Quick Start](#quick-start)
- [Building Images](#building-images)
- [Multi-Stage Builds](#multi-stage-builds)
- [Docker Compose](#docker-compose)
- [Volume Mounting](#volume-mounting)
- [GPU Support](#gpu-support)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)



## Quick Start

### Prerequisites

- Docker 20.10+ installed ([Install Docker](https://docs.docker.com/get-docker/))
- 4GB+ RAM available
- 2GB+ disk space

### Pull and Run Pre-Built Image

```bash
# Pull latest image from Docker Hub
docker pull thesadeq/dip-smc-pso:latest

# Run Streamlit UI (web interface)
docker run -d -p 8501:8501 --name dip-smc-pso thesadeq/dip-smc-pso:latest

# Access UI at http://localhost:8501
```

## Run CLI Simulation

```bash
# Run single simulation
docker run --rm thesadeq/dip-smc-pso:latest \
  python simulate.py --controller classical_smc --duration 5.0

# Run with custom config
docker run --rm -v $(pwd)/custom_config.yaml:/app/config.yaml \
  thesadeq/dip-smc-pso:latest \
  python simulate.py --config /app/config.yaml
```

## Interactive Shell

```bash
# Launch interactive shell inside container
docker run -it --rm thesadeq/dip-smc-pso:latest /bin/bash

# Inside container:
root@container:/app# python simulate.py --controller sta_smc --plot
root@container:/app# pytest tests/ -v
```



## Building Images

### Basic Build

Create `Dockerfile` in project root:

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command: run Streamlit UI
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build:**
```bash
docker build -t dip-smc-pso:dev .
```

**Run:**
```bash
docker run -p 8501:8501 dip-smc-pso:dev
```



## Multi-Stage Builds

**Optimize image size and build time with multi-stage Dockerfile:**

```dockerfile
# ==========================================
# Stage 1: Builder - Compile dependencies
# ==========================================
FROM python:3.9-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ==========================================
# Stage 2: Runtime - Minimal production image
# ==========================================
FROM python:3.9-slim

WORKDIR /app

# Install only runtime dependencies (no compilers)
RUN apt-get update && apt-get install -y \
    libopenblas0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels -r requirements.txt \
    && rm -rf /tmp/wheels

# Copy project source code
COPY src/ ./src/
COPY config.yaml simulate.py streamlit_app.py ./

# Create non-root user for security
RUN useradd -m -u 1000 dip && chown -R dip:dip /app
USER dip

# Expose ports
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Benefits:**
- **Image size**: ~2GB → ~400MB (5x smaller)
- **Build time**: Cached wheels speed up rebuilds
- **Security**: No build tools in production image
- **Non-root**: Runs as unprivileged user

**Build:**
```bash
docker build -f Dockerfile.multistage -t dip-smc-pso:optimized .
```



## Docker Compose

**For multi-service deployments (HIL simulation, separate controller/plant):**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Plant Server (Hardware-in-the-Loop)
  plant-server:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: dip-plant-server
    command: python -m src.hil.plant_server
    ports:
      - "5555:5555"  # ZMQ server port
    environment:
      - PLANT_PORT=5555
      - LOG_LEVEL=INFO
    networks:
      - dip-network
    restart: unless-stopped

  # Controller Client
  controller-client:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: dip-controller-client
    command: python -m src.hil.controller_client --server plant-server:5555
    depends_on:
      - plant-server
    environment:
      - CONTROLLER_TYPE=classical_smc
      - LOG_LEVEL=INFO
    networks:
      - dip-network
    restart: unless-stopped

  # Streamlit UI
  streamlit-ui:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: dip-streamlit-ui
    ports:
      - "8501:8501"
    volumes:
      - ./results:/app/results  # Persist results
      - ./config.yaml:/app/config.yaml  # Custom config
    networks:
      - dip-network
    restart: unless-stopped

  # PSO Optimization Worker
  pso-worker:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    container_name: dip-pso-worker
    command: python simulate.py --controller classical_smc --run-pso --save /app/results/optimized_gains.json
    volumes:
      - ./results:/app/results
    networks:
      - dip-network
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G

networks:
  dip-network:
    driver: bridge
```

**Usage:**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f streamlit-ui

# Scale PSO workers (parallel optimization)
docker-compose up -d --scale pso-worker=4

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```



## Volume Mounting

**Persist results, configs, and logs outside containers:**

### Configuration Files

```bash
# Mount custom config
docker run -v $(pwd)/custom_config.yaml:/app/config.yaml \
  dip-smc-pso:latest \
  python simulate.py --config /app/config.yaml
```

## Results and Logs

```bash
# Mount results directory
docker run -v $(pwd)/results:/app/results \
  dip-smc-pso:latest \
  python simulate.py --controller sta_smc --save /app/results/simulation.json

# Results saved to ./results/simulation.json on host
```

## Development Mode (Live Code Reload)

```bash
# Mount source code for development
docker run -p 8501:8501 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config.yaml:/app/config.yaml \
  dip-smc-pso:dev

# Changes to src/ reflected immediately in container
```

## Notebook Directory

```bash
# Mount notebooks for Jupyter
docker run -p 8888:8888 \
  -v $(pwd)/notebooks:/app/notebooks \
  dip-smc-pso:latest \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```



## GPU Support

**Accelerate PSO optimization and simulations with GPU:**

### Prerequisites

1. NVIDIA GPU with CUDA support
2. [NVIDIA Docker runtime](https://github.com/NVIDIA/nvidia-docker) installed

### GPU-Enabled Dockerfile

```dockerfile
# Dockerfile.gpu
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA support (if using neural network controllers)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app
WORKDIR /app

CMD ["python", "simulate.py"]
```

## Running with GPU

```bash
# Build GPU image
docker build -f Dockerfile.gpu -t dip-smc-pso:gpu .

# Run with GPU access
docker run --gpus all dip-smc-pso:gpu \
  python simulate.py --controller adaptive_smc --run-pso --iterations 1000

# Check GPU usage inside container
docker run --gpus all dip-smc-pso:gpu nvidia-smi
```

## Docker Compose with GPU

```yaml
version: '3.8'

services:
  pso-gpu-worker:
    image: dip-smc-pso:gpu
    container_name: dip-pso-gpu
    command: python simulate.py --run-pso --use-gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```



## Production Deployment

### Cloud Platforms

#### AWS ECS (Elastic Container Service)

```bash
# Tag for AWS ECR
docker tag dip-smc-pso:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/dip-smc-pso:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/dip-smc-pso:latest

# Deploy to ECS (using task definition)
aws ecs update-service --cluster dip-cluster --service dip-smc-pso --force-new-deployment
```

## Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/my-project/dip-smc-pso

# Deploy to Cloud Run
gcloud run deploy dip-smc-pso \
  --image gcr.io/my-project/dip-smc-pso \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```

## Azure Container Instances

```bash
# Push to Azure Container Registry
az acr build --registry myregistry --image dip-smc-pso:latest .

# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name dip-smc-pso \
  --image myregistry.azurecr.io/dip-smc-pso:latest \
  --dns-name-label dip-smc-pso \
  --ports 8501
```

## Kubernetes

**Deploy at scale with Kubernetes:**

`deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dip-smc-pso
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dip-smc-pso
  template:
    metadata:
      labels:
        app: dip-smc-pso
    spec:
      containers:
      - name: dip-smc-pso
        image: dip-smc-pso:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"

apiVersion: v1
kind: Service
metadata:
  name: dip-smc-pso-service
spec:
  selector:
    app: dip-smc-pso
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get services  # Get external IP
```



## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8501: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8501
lsof -i :8501  # On Mac/Linux
netstat -ano | findstr :8501  # On Windows

# Kill process or use different port
docker run -p 8502:8501 dip-smc-pso:latest
```

## 2. Out of Memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```bash
# Increase Docker memory limit (Docker Desktop → Preferences → Resources)
# Or limit container memory explicitly
docker run -m 4g dip-smc-pso:latest
```

## 3. Permission Denied (Volume Mounts)

**Error:**
```
Permission denied: '/app/results/output.json'
```

**Solution:**
```bash
# Run as current user (not root)
docker run -u $(id -u):$(id -g) -v $(pwd)/results:/app/results dip-smc-pso:latest

# Or fix permissions on host
chmod -R 777 ./results
```

## 4. CUDA/GPU Not Found

**Error:**
```
RuntimeError: CUDA driver version is insufficient for CUDA runtime version
```

**Solution:**
```bash
# Update NVIDIA drivers on host
# Verify nvidia-docker runtime installed
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check Docker daemon.json includes nvidia runtime
cat /etc/docker/daemon.json
# Should have: "runtimes": {"nvidia": {"path": "nvidia-container-runtime"}}
```

## 5. Slow Build Times

**Solution:**
```bash
# Use BuildKit for parallel builds
DOCKER_BUILDKIT=1 docker build -t dip-smc-pso:fast .

# Cache pip packages
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t dip-smc-pso:cached .

# Use multi-stage build (see above)
```

## Debug Mode

```bash
# Run container with verbose logging
docker run -e LOG_LEVEL=DEBUG dip-smc-pso:latest

# Inspect running container
docker exec -it <container_id> /bin/bash

# View logs
docker logs -f <container_id>

# Inspect image layers
docker history dip-smc-pso:latest
```



## Best Practices

### Security

1. **Use multi-stage builds** - Remove build tools from production images
2. **Run as non-root user** - Use `USER` directive in Dockerfile
3. **Scan for vulnerabilities** - `docker scan dip-smc-pso:latest`
4. **Pin base image versions** - Use `python:3.9.18-slim` not `python:3.9-slim`
5. **Minimize attack surface** - Only install necessary packages

### Performance

1. **Use `.dockerignore`** - Exclude unnecessary files from build context:
   ```
   .git
   .pytest_cache
   __pycache__
   *.pyc
   tests/
   docs/
   notebooks/
   .archive/
   results/
   ```

2. **Layer caching** - Order Dockerfile commands from least to most frequently changed:
   ```dockerfile
   # Changes rarely → early layers
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Changes often → late layers
   COPY src/ ./src/
   ```

3. **Multi-stage builds** - Reduce final image size by 5-10x

### Reproducibility

1. **Pin all versions** - In `requirements.txt` use `numpy==1.24.3` not `numpy>=1.24`
2. **Use fixed base image tags** - `python:3.9.18-slim` not `python:latest`
3. **Document build process** - Include `Dockerfile` and `docker-compose.yml` in repo
4. **Tag images with git commit** - `docker build -t dip-smc-pso:$(git rev-parse --short HEAD) .`



## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [NVIDIA Docker](https://github.com/NVIDIA/nvidia-docker)
- [Kubernetes Documentation](https://kubernetes.io/docs/)



**Last Updated:** 2025-10-09
**Maintainer:** DIP-SMC-PSO Team
