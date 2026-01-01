// =============================================================================
// MAIN APPLICATION ENTRY POINT
// =============================================================================
// React application entry point. Sets up the root render with React 18's
// createRoot API and includes global styles.
// =============================================================================

/**
 * Application Entry Point
 * 
 * This file initializes the React application by:
 * 1. Importing global CSS styles (Tailwind)
 * 2. Creating the React root with StrictMode
 * 3. Rendering the main App component
 */

import React from 'react';
import ReactDOM from 'react-dom/client';

// Import global styles (includes Tailwind CSS)
import './index.css';

// Import main App component
import App from './App';

// =============================================================================
// GLOBAL ERROR HANDLERS
// =============================================================================
// Catch unhandled errors and promise rejections for debugging

window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

console.log('Starting React app...');

// =============================================================================
// ROOT RENDER
// =============================================================================
// Using React 18's createRoot API for concurrent features

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

console.log('React app rendered');
