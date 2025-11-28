// =============================================================================
// LANGUAGE TOGGLE COMPONENT
// =============================================================================
// Button component to toggle between English and Sinhala languages.
// Uses LanguageContext for state management.
// =============================================================================

/**
 * LanguageToggle Component
 * 
 * A simple button that toggles between English and Sinhala.
 * Displays the name of the language to switch to.
 */

import React from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// LANGUAGE TOGGLE COMPONENT
// =============================================================================

function LanguageToggle() {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { language, toggleLanguage, t } = useLanguage();

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-primary-600 hover:bg-gray-100 transition-all duration-200"
      aria-label={`Switch to ${language === 'en' ? 'Sinhala' : 'English'}`}
    >
      {/* Globe Icon */}
      <svg 
        className="w-4 h-4" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" 
        />
      </svg>
      
      {/* Language Text */}
      <span>{t('nav.language')}</span>
    </button>
  );
}

export default LanguageToggle;
