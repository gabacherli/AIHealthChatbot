# Health Chatbot Backend

This is the backend for the Health Chatbot application. It provides a comprehensive REST API for authentication, chat functionality, document management, and medical image processing.

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
│   │   ├── auth/           # Authentication
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   ├── chat/           # Chat functionality
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   ├── documents/      # Document management
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── health/         # Health checks
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_db_service.py
│   │   └── prompt_builder.py
│   └── utils/              # Utilities
│       ├── __init__.py
│       ├── document_processor.py
│       ├── medical_image_classifier.py
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
   VECTOR_DB_URL=http://localhost:6333
   VECTOR_DB_COLLECTION=health_documents
   UPLOAD_FOLDER=uploads/
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

- `POST /api/chat`: Send a message to the chatbot
  - Request: `{ "question": "string" }`
  - Response: `{ "answer": "string", "sources": [{"source": "string", "page": number}] }`
  - Requires authentication

### Document Management

- `POST /api/documents/upload`: Upload a document
  - Request: Multipart form data with file
  - Response: `{ "message": "string", "document_id": "string", "filename": "string" }`
  - Supports: PDF, DOCX, TXT, CSV, XLSX, images, DICOM files
  - Requires authentication

- `GET /api/documents/list`: List user's documents
  - Response: `{ "documents": [{"filename": "string", "upload_date": "string", "file_size": number}] }`
  - Requires authentication

- `GET /api/documents/download/<filename>`: Download a document
  - Response: File download
  - Requires authentication

- `DELETE /api/documents/delete/<filename>`: Delete a document
  - Response: `{ "message": "string" }`
  - Requires authentication

- `POST /api/documents/search`: Search documents
  - Request: `{ "query": "string", "filters": {} }`
  - Response: `{ "results": [{"content": "string", "metadata": {}}] }`
  - Requires authentication

### Health Check

- `GET /api/health`: Service health status
  - Response: `{ "status": "healthy", "service": "string", "version": "string" }`

## Features

### Medical Image Processing

The backend supports advanced medical image processing:

- **DICOM Support**: Full DICOM metadata extraction and analysis
- **Medical Image Classification**: Automatic classification of medical image types
- **Enhanced Medical Context**: Specialized processing for medical images
- **Supported Formats**: DICOM (.dcm, .dicom), standard images (.jpg, .png, etc.)

### Vector Database Integration

- **Qdrant Integration**: Efficient vector storage and retrieval
- **Semantic Search**: Context-aware document search
- **User Isolation**: Documents are isolated by user ID
- **Role-based Access**: Different access patterns for patients vs. professionals

### Document Processing

- **Multi-format Support**: PDF, DOCX, TXT, CSV, XLSX, images
- **Chunking Strategy**: Intelligent text chunking for optimal retrieval
- **Metadata Extraction**: Rich metadata for enhanced search
- **Medical Context**: Specialized processing for medical documents