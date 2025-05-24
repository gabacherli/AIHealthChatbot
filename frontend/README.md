# Health Chatbot Frontend

This is the frontend for the Health Chatbot application. It provides a modern, responsive user interface built with React and Chakra UI for interacting with the backend API.

## Project Structure

```
frontend/
├── public/                 # Static files
│   ├── index.html          # Main HTML template
│   ├── favicon.ico         # App favicon
│   └── health-icon.svg     # Health icon
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Chat.jsx        # Main chat interface
│   │   ├── Login.jsx       # Login form
│   │   ├── Layout.jsx      # App layout wrapper
│   │   ├── ProtectedRoute.jsx # Route protection
│   │   ├── DocumentUpload.js  # File upload component
│   │   └── DocumentList.js    # Document management
│   ├── pages/              # Page components
│   │   ├── DocumentsPage.js   # Document management page
│   │   └── ChatPage/          # Chat page (feature-based)
│   ├── context/            # React contexts
│   │   └── AuthContext.jsx    # Authentication context
│   ├── services/           # API services
│   │   └── api.js             # API client and services
│   ├── features/           # Feature-based organization
│   │   ├── auth/              # Authentication feature
│   │   │   ├── components/    # Auth components
│   │   │   ├── hooks/         # Auth hooks
│   │   │   └── services/      # Auth services
│   │   └── chat/              # Chat feature
│   │       ├── components/    # Chat components
│   │       ├── hooks/         # Chat hooks
│   │       └── services/      # Chat services
│   ├── hooks/              # Custom hooks
│   ├── utils/              # Utility functions
│   ├── App.js              # Main App component
│   ├── App.css             # App styles
│   ├── index.js            # Entry point
│   └── index.css           # Global styles
```

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

## Available Scripts

- `npm start`: Start the development server
- `npm test`: Run tests
- `npm run build`: Build for production
- `npm run eject`: Eject from Create React App

## Features

- **Authentication**: Secure login with JWT token management
- **Chat Interface**: Real-time chat with AI-powered health responses
- **Document Management**: Upload, view, and manage medical documents
- **Medical Image Support**: Upload and process medical images including DICOM files
- **Role-based UI**: Different interfaces for patients and healthcare professionals
- **Responsive Design**: Mobile-friendly interface using Chakra UI
- **Source Citations**: View sources and references for AI responses
- **Dark/Light Mode**: Theme support through Chakra UI

## Key Dependencies

- **React 19**: Latest React with concurrent features
- **Chakra UI**: Modern component library for consistent design
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **React Markdown**: Markdown rendering for chat responses
- **React Icons**: Icon library
- **Framer Motion**: Animation library (used by Chakra UI)

## Component Architecture

### Chakra UI Integration

The application uses Chakra UI for consistent, accessible, and responsive design:

- **Theme System**: Consistent colors, typography, and spacing
- **Responsive Design**: Mobile-first approach with responsive breakpoints
- **Accessibility**: Built-in ARIA attributes and keyboard navigation
- **Dark Mode**: Automatic theme switching support

### Key Components

- **Layout.jsx**: Main application layout with navigation
- **Chat.jsx**: Chat interface with message history and input
- **DocumentUpload.js**: Drag-and-drop file upload with progress
- **DocumentList.js**: Document management with preview and actions
- **Login.jsx**: Authentication form with validation

### State Management

- **AuthContext**: Global authentication state
- **Local State**: Component-level state for UI interactions
- **API Integration**: Centralized API calls through services

## Development Notes

- Built with Create React App for easy development setup
- Uses modern React patterns (hooks, context, functional components)
- Follows Chakra UI design system guidelines
- Implements responsive design for mobile and desktop
- Includes error handling and loading states

## Learn More

- [Create React App Documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React Documentation](https://reactjs.org/)
- [Chakra UI Documentation](https://chakra-ui.com/)
