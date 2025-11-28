// =============================================================================
// LANGUAGE CONTEXT
// =============================================================================
// Provides internationalization (i18n) support for the application.
// Supports English and Sinhala languages.
// =============================================================================

/**
 * Language Context
 * 
 * This context provides:
 * - Current language state (en/si)
 * - Language toggle function
 * - Translation function (t) for accessing localized strings
 * 
 * Usage:
 * ```jsx
 * const { language, toggleLanguage, t } = useLanguage();
 * <h1>{t('welcome')}</h1>
 * ```
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// Import translation files
import en from '../i18n/en.json';
import si from '../i18n/si.json';

// =============================================================================
// TRANSLATIONS MAP
// =============================================================================
// Maps language codes to their translation files

const translations = {
  en,  // English translations
  si   // Sinhala translations
};

// =============================================================================
// CONTEXT CREATION
// =============================================================================

const LanguageContext = createContext();

// =============================================================================
// LANGUAGE PROVIDER COMPONENT
// =============================================================================

/**
 * LanguageProvider Component
 * 
 * Wraps the application to provide language context to all children.
 * Manages language state and provides translation utilities.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export function LanguageProvider({ children }) {
  // ---------------------------------------------------------------------------
  // State: Current language (defaults to English)
  // ---------------------------------------------------------------------------
  const [language, setLanguage] = useState('en');

  // ---------------------------------------------------------------------------
  // Toggle Language Function
  // ---------------------------------------------------------------------------
  // Switches between English and Sinhala
  const toggleLanguage = useCallback(() => {
    setLanguage(prevLang => prevLang === 'en' ? 'si' : 'en');
  }, []);

  // ---------------------------------------------------------------------------
  // Set Specific Language Function
  // ---------------------------------------------------------------------------
  const setLang = useCallback((lang) => {
    if (translations[lang]) {
      setLanguage(lang);
    }
  }, []);

  // ---------------------------------------------------------------------------
  // Translation Function
  // ---------------------------------------------------------------------------
  /**
   * Get translated string by key
   * 
   * Supports nested keys using dot notation: "home.welcome"
   * Falls back to key if translation not found
   * 
   * @param {string} key - Translation key (supports dot notation for nesting)
   * @param {Object} params - Optional parameters for interpolation
   * @returns {string} Translated string or key if not found
   */
  const t = useCallback((key, params = {}) => {
    // Get current language translations
    const currentTranslations = translations[language] || translations.en;
    
    // Support nested keys using dot notation
    const keys = key.split('.');
    let value = currentTranslations;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Key not found, return the key itself
        console.warn(`Translation missing for key: ${key}`);
        return key;
      }
    }
    
    // If value is not a string, return the key
    if (typeof value !== 'string') {
      return key;
    }
    
    // Handle parameter interpolation (e.g., "Hello, {name}!")
    let result = value;
    Object.entries(params).forEach(([paramKey, paramValue]) => {
      result = result.replace(new RegExp(`{${paramKey}}`, 'g'), paramValue);
    });
    
    return result;
  }, [language]);

  // ---------------------------------------------------------------------------
  // Context Value
  // ---------------------------------------------------------------------------
  const contextValue = {
    language,           // Current language code ('en' or 'si')
    setLanguage: setLang, // Function to set specific language
    toggleLanguage,     // Function to toggle between languages
    t,                  // Translation function
    isEnglish: language === 'en',
    isSinhala: language === 'si'
  };

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

// =============================================================================
// CUSTOM HOOK
// =============================================================================

/**
 * useLanguage Hook
 * 
 * Custom hook to access language context.
 * Must be used within a LanguageProvider.
 * 
 * @returns {Object} Language context value
 * @throws {Error} If used outside LanguageProvider
 */
export function useLanguage() {
  const context = useContext(LanguageContext);
  
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  
  return context;
}

// Default export for the context
export default LanguageContext;
