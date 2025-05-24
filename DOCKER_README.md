# Docker Deployment Guide

This guide explains how to run the AI Health Chatbot application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- OpenAI API key

## Quick Start

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# 1. Clone the repository and navigate to the project directory
git clone <repository-url>
cd AIHealthChatbot

# 2. Create environment file
cp .env.example .env

# 3. Edit the .env file and add your OpenAI API key
# Required
# OPENAI_API_KEY=your-openai-api-key-here
#
# Optional (will use defaults if not provided)
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-key-here

# 4. Start the application
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:5000
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# 1. Clone the repository and navigate to the project directory
git clone <repository-url>
cd AIHealthChatbot

# 2. Create environment file
Copy-Item .env.example .env

# 3. Edit the .env file and add your OpenAI API key
# Required
# OPENAI_API_KEY=your-openai-api-key-here
#
# Optional (will use defaults if not provided)
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-key-here

# 4. Start the application
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:5000
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```cmd
REM 1. Clone the repository and navigate to the project directory
git clone <repository-url>
cd AIHealthChatbot

REM 2. Create environment file
copy .env.example .env

REM 3. Edit the .env file and add your OpenAI API key
REM Required
REM OPENAI_API_KEY=your-openai-api-key-here
REM
REM Optional (will use defaults if not provided)
REM SECRET_KEY=your-secret-key-here
REM JWT_SECRET_KEY=your-jwt-secret-key-here

REM 4. Start the application
docker-compose up -d

REM 5. Access the application
REM Frontend: http://localhost
REM Backend API: http://localhost:5000
```
</details>

## Development Mode

For development with hot reloading:

<details>
<summary><strong>🐧 Linux / 🍎 macOS / 🪟 Windows</strong></summary>

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Or run in background
docker-compose -f docker-compose.dev.yml up -d
```
</details>

**Development mode features:**
- Mount source code as volumes for hot reloading
- Run backend in development mode
- Run frontend with development server on port 3000
- Access frontend at: http://localhost:3000
- Access backend API at: http://localhost:5000
- Access Qdrant at: http://localhost:6333

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `SECRET_KEY`: Flask secret key (defaults to dev key)
- `JWT_SECRET_KEY`: JWT secret key (defaults to dev key)
- `FLASK_ENV`: Environment (production/development)
- `DEV_JWT_KEY`: Development JWT key
- `DEV_OPENAI_KEY`: Development OpenAI key
- `PROD_JWT_KEY`: Production JWT key
- `PROD_OPENAI_KEY`: Production OpenAI key

## Docker Commands

<details>
<summary><strong>🐧 Linux / 🍎 macOS / 🪟 Windows</strong></summary>

### Production Commands
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up --build

# Scale services
docker-compose up -d --scale backend=2
```

### Development Commands
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View development logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
docker-compose -f docker-compose.dev.yml down

# Rebuild development services
docker-compose -f docker-compose.dev.yml up --build
```

### Maintenance Commands
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```
</details>

**Note:** Docker commands are identical across all platforms. The Docker CLI works the same way on Windows, macOS, and Linux.

## Service Architecture

- **Frontend**: React app served by Nginx on port 80 (production) or port 3000 (development)
- **Backend**: Flask API on port 5000
- **Qdrant**: Vector database on port 6333 (HTTP) and 6334 (gRPC)
- **Network**: Internal Docker network for service communication
- **Volumes**: Persistent storage for Qdrant data and uploaded files

## Health Checks

All services include health checks:
- **Backend**: `GET /api/health`
- **Frontend**: HTTP check on port 80
- **Qdrant**: Storage metadata check and HTTP API availability

## Troubleshooting

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs qdrant

# Restart a service
docker-compose restart backend
docker-compose restart qdrant

# Access service shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec qdrant sh

# Check Qdrant status
curl http://localhost:6333/health

# View collections
curl http://localhost:6333/collections

# Access Qdrant web UI
open http://localhost:6333/dashboard  # macOS
xdg-open http://localhost:6333/dashboard  # Linux
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# Check service status
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs qdrant

# Restart a service
docker-compose restart backend
docker-compose restart qdrant

# Access service shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec qdrant sh

# Check Qdrant status
Invoke-RestMethod http://localhost:6333/health

# View collections
Invoke-RestMethod http://localhost:6333/collections

# Access Qdrant web UI
Start-Process http://localhost:6333/dashboard
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```cmd
REM Check service status
docker-compose ps

REM View service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs qdrant

REM Restart a service
docker-compose restart backend
docker-compose restart qdrant

REM Access service shell
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec qdrant sh

REM Check Qdrant status (requires curl)
curl http://localhost:6333/health

REM View collections (requires curl)
curl http://localhost:6333/collections

REM Access Qdrant web UI
start http://localhost:6333/dashboard
```
</details>

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your `.env` file
2. Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
3. Consider using Docker secrets for sensitive data
4. Set up proper SSL/TLS termination
5. Configure proper logging and monitoring

## Security Considerations

- Change default secret keys in production
- Use environment-specific API keys
- Consider using Docker secrets for sensitive data
- Implement proper SSL/TLS termination
- Regular security updates for base images

## Demo Accounts

The application includes demo accounts for testing:
- **Patient**: username: `gabriel`, password: `gabriel123`
- **Professional**: username: `drmurilo`, password: `drmurilo123`
