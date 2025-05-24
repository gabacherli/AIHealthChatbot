# Health Chatbot

A chatbot application for health-related questions with role-based responses for patients and healthcare professionals.

## Project Overview

This project consists of a Flask backend API, React frontend, and Qdrant vector database. The backend uses OpenAI's API to generate responses to health-related questions, with intelligent document retrieval and medical image processing capabilities. The system provides context-specific responses based on user roles and uploaded medical documents.

## Project Structure

The project is organized into three main components:

- `backend/`: Flask API with medical image processing and vector database integration
- `frontend/`: React application with Chakra UI components
- `docker-compose.yml`: Multi-service orchestration including Qdrant vector database

## Features

- **Authentication**: Secure login with username and password
- **Role-based responses**: Different responses for patients and healthcare professionals
- **Document Management**: Upload, store, and search medical documents and images
- **Medical Image Processing**: Advanced support for DICOM files, X-rays, CT scans, MRI images
- **Vector Search**: Intelligent document retrieval using Qdrant vector database
- **Context-aware Chat**: AI responses enhanced with relevant document context
- **Modern UI**: Clean, responsive interface built with Chakra UI
- **Containerized Deployment**: Full Docker support for easy deployment

## Getting Started

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker:

**Prerequisites:**
- Docker and Docker Compose installed
- OpenAI API key

**Quick Start:**

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# Clone and navigate to the project
git clone <repository-url>
cd AIHealthChatbot

# Create environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-openai-api-key-here

# Start the application
docker-compose up -d

# Access at http://localhost
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# Clone and navigate to the project
git clone <repository-url>
cd AIHealthChatbot

# Create environment file
Copy-Item .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-openai-api-key-here

# Start the application
docker-compose up -d

# Access at http://localhost
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```cmd
REM Clone and navigate to the project
git clone <repository-url>
cd AIHealthChatbot

REM Create environment file
copy .env.example .env

REM Edit .env and add your OpenAI API key
REM OPENAI_API_KEY=your-openai-api-key-here

REM Start the application
docker-compose up -d

REM Access at http://localhost
```
</details>

For detailed Docker instructions, see [DOCKER_README.md](DOCKER_README.md).

### Option 2: Manual Setup

**Prerequisites:**
- Node.js and npm
- Python 3.8+
- OpenAI API key

#### Backend Setup

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with the following variables
cat > .env << EOF
FLASK_ENV=development
DEV_JWT_KEY=your-dev-jwt-key
DEV_OPENAI_KEY=your-openai-api-key
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_COLLECTION=health_documents
UPLOAD_FOLDER=uploads/
EOF

# Run the backend
python app.py
```
</details>

<details>
<summary><strong>🪟 Windows (PowerShell)</strong></summary>

```powershell
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create a .env file with the following variables
@"
FLASK_ENV=development
DEV_JWT_KEY=your-dev-jwt-key
DEV_OPENAI_KEY=your-openai-api-key
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_COLLECTION=health_documents
UPLOAD_FOLDER=uploads/
"@ | Out-File -FilePath .env -Encoding utf8

# Run the backend
python app.py
```
</details>

<details>
<summary><strong>🪟 Windows (Command Prompt)</strong></summary>

```cmd
REM Navigate to the backend directory
cd backend

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Create a .env file manually or use:
echo FLASK_ENV=development > .env
echo DEV_JWT_KEY=your-dev-jwt-key >> .env
echo DEV_OPENAI_KEY=your-openai-api-key >> .env
echo VECTOR_DB_URL=http://localhost:6333 >> .env
echo VECTOR_DB_COLLECTION=health_documents >> .env
echo UPLOAD_FOLDER=uploads/ >> .env

REM Run the backend
python app.py
```
</details>

#### Frontend Setup

<details>
<summary><strong>🐧 Linux / 🍎 macOS / 🪟 Windows</strong></summary>

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the frontend
npm start
```

**Alternative package managers:**
```bash
# Using Yarn
yarn install
yarn start

# Using pnpm
pnpm install
pnpm start
```
</details>

**Note:** The frontend setup is identical across all platforms. Node.js and npm work the same way on Windows, macOS, and Linux.

## Usage

1. **Access the Application**:
   - Docker: Navigate to `http://localhost` (production) or `http://localhost:3000` (development)
   - Manual setup: Navigate to `http://localhost:3000`

2. **Login** with one of the demo accounts:
   - **Patient**: username: `gabriel` / password: `gabriel123`
   - **Healthcare Professional**: username: `drmurilo` / password: `drmurilo123`

3. **Chat Interface**:
   - Ask health-related questions and receive AI-powered responses
   - Responses are tailored to your role (patient vs. professional)
   - View sources and references for AI responses

4. **Document Management**:
   - Upload medical documents (PDF, DOCX, images)
   - Upload medical images (DICOM, X-rays, CT scans, MRI)
   - Search through uploaded documents
   - Download and manage your document library

## Application Architecture

The application consists of three main services:

- **Frontend** (React + Chakra UI): User interface on port 3000 (dev) or 80 (prod)
- **Backend** (Flask API): REST API on port 5000
- **Qdrant** (Vector Database): Document search and retrieval on port 6333

## Project Organization

This project follows best practices for both Flask and React:

- **Flask**: Organized using the application factory pattern with blueprints for different features
- **React**: Feature-based organization with Chakra UI components and atomic design principles
- **Docker**: Multi-service architecture with health checks and dependency management
- **Vector Database**: Qdrant for efficient document storage and semantic search

## Key Technologies

- **Backend**: Flask, OpenAI API, Qdrant, PyTorch, Transformers
- **Frontend**: React, Chakra UI, React Router, Axios
- **Medical Processing**: PyDICOM, SimpleITK, MedMNIST, PIL
- **Infrastructure**: Docker, Docker Compose, Nginx

## Documentation

### Setup and Deployment
- [Docker Deployment Guide](DOCKER_README.md) - Docker setup instructions with cross-platform commands
- [Qdrant Setup Guide](QDRANT_SETUP.md) - Vector database configuration for all platforms
- [Containerization Summary](CONTAINERIZATION_SUMMARY.md) - Architecture overview

### API and Development
- [API Documentation](API_DOCUMENTATION.md) - Complete REST API reference
- [Backend Documentation](backend/README.md) - Backend architecture and services
- [Frontend Documentation](frontend/README.md) - UI components and React structure

### Medical Features
- [Medical Image Features](MEDICAL_IMAGE_FEATURES.md) - Medical image processing capabilities
- [Medical Image Testing](backend/test_medical_images/README.md) - Testing medical image classification

For more details, see the README files in the `backend/` and `frontend/` directories.
