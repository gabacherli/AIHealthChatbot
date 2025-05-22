# Health Chatbot Frontend

This is the frontend for the Health Chatbot application. It provides a user interface for interacting with the backend API.

## Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── assets/             # Static assets
│   │   ├── images/         # Image files
│   │   └── styles/         # Global styles
│   │       ├── global.css  # Global CSS
│   │       └── variables.css # CSS variables
│   ├── components/         # Reusable components
│   │   ├── common/         # Common components
│   │   │   ├── Button/     # Button component
│   │   │   └── Input/      # Input component
│   │   └── layout/         # Layout components
│   │       ├── Header/     # Header component
│   │       ├── Footer/     # Footer component
│   │       └── Layout/     # Layout component
│   ├── features/           # Feature-based organization
│   │   ├── auth/           # Auth feature
│   │   │   ├── components/ # Auth components
│   │   │   ├── hooks/      # Auth hooks
│   │   │   ├── services/   # Auth services
│   │   │   └── pages/      # Auth pages
│   │   └── chat/           # Chat feature
│   │       ├── components/ # Chat components
│   │       ├── hooks/      # Chat hooks
│   │       ├── services/   # Chat services
│   │       └── pages/      # Chat pages
│   ├── hooks/              # Custom hooks
│   ├── pages/              # Page components
│   │   ├── LoginPage/      # Login page
│   │   └── ChatPage/       # Chat page
│   ├── services/           # API services
│   ├── utils/              # Utility functions
│   ├── App.js              # Main App component
│   └── index.js            # Entry point
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

- **Authentication**: Login with username and password
- **Chat**: Send messages to the chatbot and receive responses
- **Role-based content**: Different content for patients and professionals

## Dependencies

- React
- React Router
- Axios

## Learn More

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
