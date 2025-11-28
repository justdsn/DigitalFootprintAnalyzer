// =============================================================================
// TRANSLITERATION DISPLAY COMPONENT
// =============================================================================
// Displays Sinhala to English transliteration results with spelling variants.
// Used in the results page to show romanized spellings for Sinhala input.
// =============================================================================

/**
 * TransliterationDisplay Component
 * 
 * Shows the original Sinhala text and its romanized English transliterations.
 * Highlights the primary transliteration and displays alternatives.
 * 
 * Props:
 * - original: Original Sinhala text
 * - transliterations: Array of romanized spelling variants
 * - isSinhala: Boolean indicating if input was Sinhala
 * - onVariantClick: Optional callback when a variant is clicked
 */

import React from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// TRANSLITERATION DISPLAY COMPONENT
// =============================================================================

function TransliterationDisplay({ 
  original, 
  transliterations = [], 
  isSinhala = false,
  onVariantClick = null,
  className = '' 
}) {
  // Get translation function from language context
  const { t } = useLanguage();

  // If no transliterations, show nothing
  if (!transliterations || transliterations.length === 0) {
    return null;
  }

  // Primary transliteration is the first one
  const primary = transliterations[0];
  // Alternatives are the rest
  const alternatives = transliterations.slice(1);

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-6 ${className}`}>
      {/* ------------------------------------------------------------------- */}
      {/* Header Section */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex items-center space-x-3 mb-4">
        {/* Icon for transliteration */}
        <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {t('transliteration.title') || 'Transliteration'}
          </h3>
          <p className="text-sm text-gray-500">
            {isSinhala 
              ? (t('transliteration.sinhalaDetected') || 'Sinhala text detected')
              : (t('transliteration.variants') || 'Spelling variants')}
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Original Text (if Sinhala) */}
      {/* ------------------------------------------------------------------- */}
      {isSinhala && original && (
        <div className="mb-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">
                {t('transliteration.original') || 'Original Sinhala'}
              </p>
              <p className="text-2xl font-medium text-gray-900">
                {original}
              </p>
            </div>
            {/* Arrow icon showing conversion */}
            <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
            <div>
              <p className="text-sm text-gray-500 mb-1">
                {t('transliteration.romanized') || 'Romanized'}
              </p>
              <p className="text-2xl font-medium text-indigo-600">
                {primary}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Primary Transliteration (if not Sinhala) */}
      {/* ------------------------------------------------------------------- */}
      {!isSinhala && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-500 mb-1">
            {t('transliteration.input') || 'Input'}
          </p>
          <p className="text-lg font-medium text-gray-900">{original || primary}</p>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Alternative Spellings */}
      {/* ------------------------------------------------------------------- */}
      {alternatives.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">
            {t('transliteration.alternativeSpellings') || 'Alternative Spellings'}
            <span className="ml-2 text-gray-400 font-normal">
              ({alternatives.length} {t('transliteration.variants') || 'variants'})
            </span>
          </p>
          <div className="flex flex-wrap gap-2">
            {alternatives.map((variant, index) => (
              <button
                key={index}
                onClick={() => onVariantClick && onVariantClick(variant)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium 
                  ${onVariantClick 
                    ? 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 cursor-pointer transition-colors' 
                    : 'bg-gray-100 text-gray-700 cursor-default'
                  }`}
                disabled={!onVariantClick}
              >
                {variant}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Info Note */}
      {/* ------------------------------------------------------------------- */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {t('transliteration.note') || 
            'Multiple spellings are common for Sri Lankan names. Try searching with these variants.'}
        </p>
      </div>
    </div>
  );
}

export default TransliterationDisplay;
