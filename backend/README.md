# Health Chatbot Backend

This is the backend for the Health Chatbot application. It provides an API for the frontend to interact with.

## Project Structure

```
backend/
├── app.py                  # Entry point
├── tests/                  # Test directory
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   ├── test_auth.py
│   └── test_chat.py
├── src/
│   ├── __init__.py         # Application factory
│   ├── config/             # Configuration
│   │   ├── __init__.py
│   │   ├── base.py         # Base configuration
│   │   ├── development.py  # Development config
│   │   └── production.py   # Production config
│   ├── api/                # API resources
│   │   ├── __init__.py
│   │   ├── auth/           # Auth feature
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   └── chat/           # Chat feature
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── service.py
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── embedding_service.py
│   │   └── prompt_builder.py
│   └── utils/              # Utilities
│       ├── __init__.py
│       ├── document_loader.py
│       └── error_handlers.py
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   FLASK_ENV=development
   DEV_JWT_KEY=your-dev-jwt-key
   DEV_OPENAI_KEY=your-openai-api-key
   ```

## Running the Application

Run the application with:
```
python app.py
```

The API will be available at `http://localhost:5000`.

## Running Tests

Run tests with:
```
pytest
```

## API Endpoints

### Authentication

- `POST /api/auth/login`: Login with username and password
  - Request: `{ "username": "string", "password": "string" }`
  - Response: `{ "token": "string", "role": "string" }`

### Chat

- `POST /api/chat/chat`: Send a message to the chatbot
  - Request: `{ "question": "string" }`
  - Response: `{ "answer": "string" }`
  - Requires authentication