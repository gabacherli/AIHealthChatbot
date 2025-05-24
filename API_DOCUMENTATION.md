# AI Health Chatbot API Documentation

This document provides comprehensive documentation for the AI Health Chatbot REST API.

## Base URL

- **Development**: `http://localhost:5000/api`
- **Production**: `http://your-domain.com/api`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Authentication

#### POST /auth/login

Authenticate a user and receive a JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "jwt-token-string",
  "role": "patient|professional"
}
```

**Status Codes:**
- `200`: Success
- `401`: Invalid credentials
- `400`: Missing username or password

---

### Chat

#### POST /chat

Send a message to the AI chatbot and receive a response.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Request:**
```json
{
  "question": "What are the symptoms of diabetes?"
}
```

**Response:**
```json
{
  "answer": "Diabetes symptoms include increased thirst, frequent urination...",
  "sources": [
    {
      "source": "diabetes_guide.pdf",
      "page": 3
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `400`: No question provided
- `401`: Unauthorized
- `500`: Server error

---

### Document Management

#### POST /documents/upload

Upload a document for processing and storage.

**Headers:**
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data`

**Request:**
- Form data with file field containing the document

**Supported File Types:**
- Documents: PDF, DOCX, TXT, CSV, XLSX
- Images: JPG, PNG, BMP, TIFF
- Medical: DICOM (.dcm, .dicom, .ima, .img)

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document_id": "uuid-string",
  "filename": "document.pdf"
}
```

**Status Codes:**
- `200`: Success
- `400`: No file provided or invalid file type
- `401`: Unauthorized
- `500`: Processing error

#### GET /documents/list

List all documents for the authenticated user.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "documents": [
    {
      "filename": "medical_report.pdf",
      "upload_date": "2024-01-15T10:30:00Z",
      "file_size": 1024000,
      "file_type": "PDF",
      "medical_image_type": null
    },
    {
      "filename": "chest_xray.dcm",
      "upload_date": "2024-01-14T15:45:00Z",
      "file_size": 2048000,
      "file_type": "DICOM",
      "medical_image_type": "Chest X-ray"
    }
  ]
}
```

#### GET /documents/download/<filename>

Download a specific document.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Parameters:**
- `filename`: Name of the file to download

**Response:**
- File download with appropriate content type

**Status Codes:**
- `200`: Success
- `404`: File not found
- `401`: Unauthorized

#### DELETE /documents/delete/<filename>

Delete a specific document.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Parameters:**
- `filename`: Name of the file to delete

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

**Status Codes:**
- `200`: Success
- `404`: File not found
- `401`: Unauthorized

#### POST /documents/search

Search through uploaded documents.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Request:**
```json
{
  "query": "diabetes treatment",
  "filters": {
    "user_role": "patient",
    "file_type": "PDF"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Diabetes treatment involves...",
      "metadata": {
        "source": "diabetes_guide.pdf",
        "page": 5,
        "user_role": "patient",
        "upload_date": "2024-01-15T10:30:00Z"
      },
      "score": 0.95
    }
  ]
}
```

---

### Health Check

#### GET /health

Check the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "service": "health-chatbot-backend",
  "version": "1.0.0",
  "environment": "development"
}
```

**Status Codes:**
- `200`: Service is healthy
- `500`: Service is unhealthy

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common error status codes:
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Missing or invalid authentication
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

## Rate Limiting

Currently, no rate limiting is implemented, but it's recommended for production deployments.

## Medical Image Processing

The API includes advanced medical image processing capabilities:

### Supported Medical Image Types

- **DICOM Files**: Full metadata extraction and analysis
- **X-rays**: Chest, bone, dental X-rays
- **CT Scans**: All body regions
- **MRI Images**: T1, T2, FLAIR, DWI sequences
- **Ultrasounds**: Abdominal, cardiac, obstetric
- **Mammography**: Digital mammograms, tomosynthesis

### Medical Image Metadata

When medical images are uploaded, additional metadata is extracted:

```json
{
  "medical_image_type": "Chest X-ray",
  "dicom_metadata": {
    "patient_id": "anonymized",
    "study_date": "2024-01-15",
    "modality": "CR",
    "body_part": "CHEST"
  },
  "ai_analysis": {
    "image_quality": "good",
    "anatomical_region": "thorax",
    "keywords": ["chest", "lungs", "heart"]
  }
}
```

## Demo Accounts

For testing purposes, the following demo accounts are available:

- **Patient Account**:
  - Username: `gabriel`
  - Password: `gabriel123`
  - Role: `patient`

- **Healthcare Professional Account**:
  - Username: `drmurilo`
  - Password: `drmurilo123`
  - Role: `professional`
