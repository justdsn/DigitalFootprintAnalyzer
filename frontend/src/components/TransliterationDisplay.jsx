// =============================================================================
// TRANSLITERATION DISPLAY COMPONENT
// =============================================================================
// Component to display Sinhala to English transliteration results.
// Shows original text, detection status, and all romanized variants.
// =============================================================================

/**
 * TransliterationDisplay Component
 * 
 * Features:
 * - Displays original Sinhala text
 * - Shows Sinhala detection indicator
 * - Lists primary transliterations
 * - Expands to show spelling variants
 * - Copy-to-clipboard functionality
 * 
 * Props:
 * - original: Original Sinhala text
 * - isSinhala: Whether text was detected as Sinhala
 * - transliterations: Primary transliteration results
 * - variants: Alternative spelling variants
 * - isLoading: Loading state indicator
 */

import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// TRANSLITERATION DISPLAY COMPONENT
// =============================================================================

function TransliterationDisplay({ 
  original, 
  isSinhala, 
  transliterations, 
  variants,
  isLoading = false 
}) {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();
  const [showAllVariants, setShowAllVariants] = useState(false);
  const [copiedText, setCopiedText] = useState(null);

  // ---------------------------------------------------------------------------
  // Event Handlers
  // ---------------------------------------------------------------------------

  /**
   * Copy text to clipboard
   */
  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // ---------------------------------------------------------------------------
  // Render Loading State
  // ---------------------------------------------------------------------------
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-10 bg-gray-200 rounded mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render Empty State
  // ---------------------------------------------------------------------------
  if (!original) {
    return null;
  }

  // Combine all results for display
  const allResults = [...(transliterations || []), ...(variants || [])];
  const displayVariants = showAllVariants ? allResults : allResults.slice(0, 3);
  const hasMoreVariants = allResults.length > 3;

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="card">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <span className="text-2xl">🔤</span>
            <span>{t('transliteration.title') || 'Transliteration Results'}</span>
          </h3>
          
          {/* Sinhala Detection Badge */}
          {isSinhala !== undefined && (
            <span 
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isSinhala 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {isSinhala ? (
                <>
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {t('transliteration.sinhalaDetected') || 'Sinhala Detected'}
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {t('transliteration.notSinhala') || 'Not Sinhala'}
                </>
              )}
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {t('transliteration.description') || 'Sinhala text converted to romanized English variants'}
        </p>
      </div>

      {/* Original Text */}
      <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-100">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-purple-600 font-medium uppercase tracking-wider mb-1">
              {t('transliteration.original') || 'Original Text'}
            </p>
            <p className="text-2xl font-medium text-purple-900">{original}</p>
          </div>
          <button
            onClick={() => handleCopy(original)}
            className="p-2 text-purple-500 hover:text-purple-700 hover:bg-purple-100 rounded-lg transition-colors"
            title="Copy original"
          >
            {copiedText === original ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Transliteration Results */}
      {allResults.length > 0 ? (
        <div className="space-y-3">
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">
            {t('transliteration.variants') || 'Romanized Variants'}
          </p>
          
          <div className="flex flex-wrap gap-2">
            {displayVariants.map((variant, index) => (
              <div 
                key={index}
                className={`
                  group inline-flex items-center px-4 py-2 rounded-lg border
                  ${index === 0 
                    ? 'bg-blue-50 border-blue-200 text-blue-800' 
                    : 'bg-gray-50 border-gray-200 text-gray-700'
                  }
                  hover:shadow-sm transition-all
                `}
              >
                <span className="font-medium">{variant}</span>
                <button
                  onClick={() => handleCopy(variant)}
                  className="ml-2 p-1 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 transition-opacity"
                  title="Copy"
                >
                  {copiedText === variant ? (
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  )}
                </button>
                {index === 0 && (
                  <span className="ml-2 text-xs bg-blue-200 text-blue-700 px-2 py-0.5 rounded-full">
                    {t('transliteration.primary') || 'Primary'}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Show More/Less Toggle */}
          {hasMoreVariants && (
            <button
              onClick={() => setShowAllVariants(!showAllVariants)}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-1"
            >
              <span>
                {showAllVariants 
                  ? (t('transliteration.showLess') || 'Show less')
                  : `${t('transliteration.showMore') || 'Show'} ${allResults.length - 3} ${t('transliteration.moreVariants') || 'more variants'}`
                }
              </span>
              <svg 
                className={`w-4 h-4 transform transition-transform ${showAllVariants ? 'rotate-180' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}
        </div>
      ) : (
        <div className="text-center py-4 text-gray-400">
          <p className="text-sm">
            {t('transliteration.noResults') || 'No transliterations available'}
          </p>
        </div>
      )}
    </div>
  );
}

export default TransliterationDisplay;
