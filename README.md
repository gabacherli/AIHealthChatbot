# Health Chatbot

A chatbot application for health-related questions with role-based responses for patients and healthcare professionals.

## Project Overview

This project consists of a Flask backend API and a React frontend. The backend uses OpenAI's API to generate responses to health-related questions, with context-specific retrieval based on the user's role (patient or healthcare professional).

## Project Structure

The project is organized into two main directories:

- `backend/`: Contains the Flask API
- `frontend/`: Contains the React application

## Features

- **Authentication**: Login with username and password
- **Role-based responses**: Different responses for patients and healthcare professionals
- **Context-specific retrieval**: Retrieves relevant context for answering questions
- **Chat interface**: User-friendly chat interface for asking questions

## Getting Started

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker:

**Prerequisites:**
- Docker and Docker Compose installed
- OpenAI API key

**Quick Start:**
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

For detailed Docker instructions, see [DOCKER_README.md](DOCKER_README.md).

### Option 2: Manual Setup

**Prerequisites:**
- Node.js and npm
- Python 3.8+
- OpenAI API key

#### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with the following variables:
   ```
   FLASK_ENV=development
   DEV_JWT_KEY=your-dev-jwt-key
   DEV_OPENAI_KEY=your-openai-api-key
   ```

6. Run the backend:
   ```
   python app.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the frontend:
   ```
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Login with one of the demo accounts:
   - Patient: username: gabriel / password: gabriel123
   - Professional: username: drmurilo / password: drmurilo123
3. Start chatting with the health chatbot

## Project Organization

This project follows best practices for both Flask and React:

- **Flask**: Organized using the application factory pattern with blueprints for different features
- **React**: Organized using a feature-based approach with atomic design principles for components

For more details, see the README files in the `backend/` and `frontend/` directories.
