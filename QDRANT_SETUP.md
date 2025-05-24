# Qdrant Service Setup

This document explains the new decoupled Qdrant setup for the AI Health Chatbot.

## Overview

The Qdrant vector database has been decoupled from the Flask application and now runs as a separate Docker service. This eliminates concurrent access issues and makes the system more robust and scalable.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │     Qdrant      │
│   (React App)   │◄──►│  (Flask API)    │◄──►│ (Vector DB)     │
│   Port: 3000    │    │   Port: 5000    │    │   Port: 6333    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Services

### Qdrant Service
- **Image**: `qdrant/qdrant:latest`
- **Ports**:
  - `6333`: HTTP API
  - `6334`: gRPC API
- **Volume**: `qdrant-data-dev` (persistent storage)
- **Health Check**: `http://localhost:6333/health`

### Backend Service
- **Environment Variables**:
  - `VECTOR_DB_URL=http://qdrant:6333`
  - `VECTOR_DB_COLLECTION=health_documents`
- **Dependencies**: Waits for Qdrant to be healthy before starting

## Quick Start

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# Stop existing services
docker-compose -f docker-compose.dev.yml down

# Start new stack
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# Stop existing services
docker-compose -f docker-compose.dev.yml down

# Start new stack
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```cmd
REM Stop existing services
docker-compose -f docker-compose.dev.yml down

REM Start new stack
docker-compose -f docker-compose.dev.yml up -d

REM Check status
docker-compose -f docker-compose.dev.yml ps
```
</details>

## Testing the Setup

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# 1. Run Migration Script (if available)
python3 migrate_qdrant_data.py

# 2. Run Test Suite (if available)
python3 test_new_setup.py

# 3. Manual Testing
# Open frontend: http://localhost:3000
# Login as gabriel/gabriel123
# Go to Document Management tab
# Upload a document
# Verify it appears in the list
```
</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

```cmd
REM 1. Run Migration Script (if available)
python migrate_qdrant_data.py

REM 2. Run Test Suite (if available)
python test_new_setup.py

REM 3. Manual Testing
REM Open frontend: http://localhost:3000
REM Login as gabriel/gabriel123
REM Go to Document Management tab
REM Upload a document
REM Verify it appears in the list
```
</details>

**Manual Testing Steps:**
1. Open frontend: http://localhost:3000
2. Login as `gabriel/gabriel123`
3. Go to Document Management tab
4. Upload a document
5. Verify it appears in the list

## Service URLs

- **Frontend**: http://localhost:3000 (development) or http://localhost (production)
- **Backend API**: http://localhost:5000
- **Qdrant API**: http://localhost:6333
- **Qdrant Web UI**: http://localhost:6333/dashboard
- **Qdrant gRPC**: localhost:6334

## Benefits of New Setup

1. **No Concurrent Access Issues**: Each service has its own Qdrant connection
2. **Better Scalability**: Qdrant can be scaled independently
3. **Easier Debugging**: Clear separation of concerns
4. **Persistent Data**: Data survives container restarts
5. **Production Ready**: Follows Docker best practices

## Troubleshooting

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

### Qdrant Service Not Starting
```bash
# Check logs
docker logs health-chatbot-qdrant-dev

# Restart service
docker-compose -f docker-compose.dev.yml restart qdrant
```

### Backend Can't Connect to Qdrant
```bash
# Check if Qdrant is healthy
curl http://localhost:6333/health

# Check backend logs
docker logs health-chatbot-backend-dev
```

### Data Migration Issues
```bash
# Check if old data exists
ls -la backend/qdrant_data/

# Run migration with verbose output
python3 migrate_qdrant_data.py
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

### Qdrant Service Not Starting
```powershell
# Check logs
docker logs health-chatbot-qdrant-dev

# Restart service
docker-compose -f docker-compose.dev.yml restart qdrant
```

### Backend Can't Connect to Qdrant
```powershell
# Check if Qdrant is healthy
Invoke-RestMethod http://localhost:6333/health

# Check backend logs
docker logs health-chatbot-backend-dev
```

### Data Migration Issues
```powershell
# Check if old data exists
Get-ChildItem backend/qdrant_data/ -Force

# Run migration with verbose output
python migrate_qdrant_data.py
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

### Qdrant Service Not Starting
```cmd
REM Check logs
docker logs health-chatbot-qdrant-dev

REM Restart service
docker-compose -f docker-compose.dev.yml restart qdrant
```

### Backend Can't Connect to Qdrant
```cmd
REM Check if Qdrant is healthy (requires curl)
curl http://localhost:6333/health

REM Check backend logs
docker logs health-chatbot-backend-dev
```

### Data Migration Issues
```cmd
REM Check if old data exists
dir backend\qdrant_data\

REM Run migration with verbose output
python migrate_qdrant_data.py
```
</details>

## Environment Variables

### Development (.env)
```env
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_COLLECTION=health_documents
```

### Docker Compose
```env
VECTOR_DB_URL=http://qdrant:6333
VECTOR_DB_COLLECTION=health_documents
```

## Data Persistence

- **Development**: `qdrant-data-dev` Docker volume
- **Production**: `qdrant-data` Docker volume
- **Location**: Managed by Docker, typically in `/var/lib/docker/volumes/`

## Monitoring

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

### Health Checks
```bash
# Qdrant health check
curl http://localhost:6333/health

# Backend health check
curl http://localhost:5000/api/health
```

### Collection Info
```bash
# Get collection information
curl http://localhost:6333/collections/health_documents

# Get point count (requires jq)
curl http://localhost:6333/collections/health_documents | jq '.result.points_count'
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

### Health Checks
```powershell
# Qdrant health check
Invoke-RestMethod http://localhost:6333/health

# Backend health check
Invoke-RestMethod http://localhost:5000/api/health
```

### Collection Info
```powershell
# Get collection information
Invoke-RestMethod http://localhost:6333/collections/health_documents

# Get point count
$response = Invoke-RestMethod http://localhost:6333/collections/health_documents
$response.result.points_count
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

### Health Checks
```cmd
REM Qdrant health check (requires curl)
curl http://localhost:6333/health

REM Backend health check (requires curl)
curl http://localhost:5000/api/health
```

### Collection Info
```cmd
REM Get collection information (requires curl)
curl http://localhost:6333/collections/health_documents

REM Get point count (requires curl and jq)
curl http://localhost:6333/collections/health_documents | jq ".result.points_count"
```
</details>

## Next Steps

1. Test document upload functionality
2. Verify chat responses use uploaded documents
3. Monitor performance and logs
4. Consider adding Qdrant authentication for production
