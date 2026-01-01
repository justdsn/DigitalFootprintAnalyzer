// =============================================================================
// MAIN APPLICATION COMPONENT
// =============================================================================
// Root component that sets up routing, language context, and main layout.
// Provides the application shell with navigation and footer.
// =============================================================================

/**
 * Main App Component
 * 
 * Responsibilities:
 * - Sets up React Router for navigation
 * - Wraps application in LanguageProvider for i18n
 * - Renders common layout (Navbar, Footer)
 * - Defines routes for all pages
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Layout Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';

// Page Components
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import ResultsPage from './pages/ResultsPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';

// Context Providers
import { LanguageProvider } from './context/LanguageContext';

// =============================================================================
// APP COMPONENT
// =============================================================================

function App() {
  return (
    // -------------------------------------------------------------------------
    // Error Boundary - Catches JavaScript errors and displays fallback UI
    // -------------------------------------------------------------------------
    <ErrorBoundary>
      {/* Language Provider - Wraps entire app for i18n support */}
      <LanguageProvider>
        {/* React Router for client-side navigation */}
        <Router>
          {/* Main application container */}
          <div className="flex flex-col min-h-screen bg-gray-50">
            {/* ---------------------------------------------------------------------
             * Navigation Bar
             * Sticky header with navigation links and language toggle
             * --------------------------------------------------------------------- */}
            <Navbar />

            {/* ---------------------------------------------------------------------
             * Main Content Area
             * Flex-grow ensures it takes remaining space between header and footer
             * --------------------------------------------------------------------- */}
            <main className="flex-grow">
              <Routes>
                {/* Home Page - Landing page with features overview */}
                <Route path="/" element={<HomePage />} />
                
                {/* Analyze Page - Form to input username and details */}
                <Route path="/analyze" element={<AnalyzePage />} />
                
                {/* Results Page - Display analysis results */}
                <Route path="/results" element={<ResultsPage />} />
                
                {/* Privacy Policy Page */}
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                
                {/* Terms of Service Page */}
                <Route path="/terms" element={<TermsOfServicePage />} />
              </Routes>
            </main>

            {/* ---------------------------------------------------------------------
             * Footer
             * Contains links, copyright, and additional information
             * --------------------------------------------------------------------- */}
            <Footer />
          </div>
        </Router>
      </LanguageProvider>
    </ErrorBoundary>
  );
}

export default App;
