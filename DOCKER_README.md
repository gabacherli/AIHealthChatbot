# Docker Deployment Guide

This guide explains how to run the AI Health Chatbot application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- OpenAI API key

## Quick Start

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd AIHealthChatbot
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit the `.env` file and add your OpenAI API key:**
   ```bash
   # Required
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Optional (will use defaults if not provided)
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

4. **Start the application:**
   ```bash
   docker-compose up -d
   ```

5. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

## Development Mode

For development with hot reloading:

```bash
docker-compose -f docker-compose.dev.yml up
```

This will:
- Mount source code as volumes for hot reloading
- Run backend in development mode
- Run frontend with development server on port 3000

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

### Build and start services
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

### Rebuild services
```bash
docker-compose up --build
```

### Scale services
```bash
docker-compose up -d --scale backend=2
```

## Service Architecture

- **Frontend**: React app served by Nginx on port 80
- **Backend**: Flask API on port 5000
- **Network**: Internal Docker network for service communication

## Health Checks

Both services include health checks:
- Backend: `GET /api/health`
- Frontend: HTTP check on port 80

## Troubleshooting

### Check service status
```bash
docker-compose ps
```

### View service logs
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Restart a service
```bash
docker-compose restart backend
```

### Access service shell
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

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
