// =============================================================================
// CORRELATION MATRIX COMPONENT
// =============================================================================
// Visual grid showing cross-platform data comparison with color coding.
// Displays overlaps and contradictions between profile data.
// =============================================================================

/**
 * CorrelationMatrix Component
 * 
 * Features:
 * - Visual grid of profile comparisons
 * - Color coding: green=match, yellow=partial, red=mismatch
 * - Expandable details for each comparison
 * - Platform icons and labels
 * - Score percentages for similarity
 * 
 * Props:
 * - profiles: Array of platform profiles being compared
 * - overlaps: Array of matching information found
 * - contradictions: Array of conflicting information found
 * - isLoading: Loading state indicator
 */

import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// PLATFORM ICONS
// =============================================================================

const PLATFORM_ICONS = {
  facebook: '📘',
  twitter: '🐦',
  x: '𝕏',
  instagram: '📸',
  linkedin: '💼',
  default: '🌐'
};

const getPlatformIcon = (platform) => {
  return PLATFORM_ICONS[platform?.toLowerCase()] || PLATFORM_ICONS.default;
};

// =============================================================================
// CORRELATION MATRIX COMPONENT
// =============================================================================

function CorrelationMatrix({ 
  profiles = [], 
  overlaps = [], 
  contradictions = [],
  isLoading = false 
}) {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();
  const [expandedItem, setExpandedItem] = useState(null);

  // ---------------------------------------------------------------------------
  // Render Loading State
  // ---------------------------------------------------------------------------
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render Empty State
  // ---------------------------------------------------------------------------
  if (!profiles || profiles.length < 2) {
    return (
      <div className="card">
        <div className="text-center py-8 text-gray-400">
          <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-sm">
            {t('correlation.noProfiles') || 'Add at least 2 profiles for correlation analysis'}
          </p>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Helper Functions
  // ---------------------------------------------------------------------------

  /**
   * Get color class based on score
   */
  const getScoreColor = (score) => {
    if (score >= 90) return 'bg-green-100 text-green-800 border-green-200';
    if (score >= 70) return 'bg-lime-100 text-lime-800 border-lime-200';
    if (score >= 50) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (score >= 30) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  /**
   * Get icon for match type
   */
  const getMatchIcon = (matchType) => {
    switch (matchType) {
      case 'exact':
        return '✓';
      case 'similar':
        return '≈';
      case 'mismatch':
        return '✗';
      default:
        return '?';
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="card">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
          <span className="text-2xl">🔗</span>
          <span>{t('correlation.title') || 'Cross-Platform Correlation'}</span>
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          {t('correlation.description') || 'Comparison of profile data across platforms'}
        </p>
      </div>

      {/* Profile Cards */}
      <div className="mb-6">
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-3">
          {t('correlation.profilesAnalyzed') || 'Profiles Analyzed'}
        </p>
        <div className="flex flex-wrap gap-3">
          {profiles.map((profile, index) => (
            <div 
              key={index}
              className="inline-flex items-center px-4 py-2 bg-gray-50 rounded-lg border border-gray-200"
            >
              <span className="text-xl mr-2">{getPlatformIcon(profile.platform)}</span>
              <div>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {profile.platform}
                </p>
                <p className="text-xs text-gray-500">@{profile.username}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Overlaps Section */}
      {overlaps.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-green-500">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </span>
            <p className="text-sm font-medium text-gray-700">
              {t('correlation.overlapsFound') || 'Matching Information Found'}
            </p>
            <span className="bg-green-100 text-green-700 text-xs font-medium px-2 py-0.5 rounded-full">
              {overlaps.length}
            </span>
          </div>
          
          <div className="space-y-2">
            {overlaps.map((overlap, index) => (
              <div 
                key={index}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${getScoreColor(overlap.score)}`}
                onClick={() => setExpandedItem(expandedItem === `overlap-${index}` ? null : `overlap-${index}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold">
                      {getMatchIcon(overlap.match_type)}
                    </span>
                    <div>
                      <p className="font-medium capitalize">{overlap.field}</p>
                      <p className="text-xs opacity-75">
                        {overlap.platforms?.join(' ↔ ')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold">
                      {overlap.score?.toFixed(0)}%
                    </span>
                    <svg 
                      className={`w-4 h-4 transform transition-transform ${expandedItem === `overlap-${index}` ? 'rotate-180' : ''}`} 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {expandedItem === `overlap-${index}` && overlap.values && (
                  <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                    <p className="text-xs font-medium mb-2">{t('correlation.values') || 'Values compared:'}</p>
                    <div className="space-y-1">
                      {overlap.values.map((value, vIndex) => (
                        <div key={vIndex} className="text-sm flex items-center space-x-2">
                          <span className="text-lg">{getPlatformIcon(overlap.platforms?.[vIndex])}</span>
                          <span className="truncate max-w-xs" title={value}>{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Contradictions Section */}
      {contradictions.length > 0 && (
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-red-500">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </span>
            <p className="text-sm font-medium text-gray-700">
              {t('correlation.contradictionsFound') || 'Conflicting Information Found'}
            </p>
            <span className="bg-red-100 text-red-700 text-xs font-medium px-2 py-0.5 rounded-full">
              {contradictions.length}
            </span>
          </div>
          
          <div className="space-y-2">
            {contradictions.map((contradiction, index) => (
              <div 
                key={index}
                className="p-3 rounded-lg border border-red-200 bg-red-50 cursor-pointer transition-all hover:bg-red-100"
                onClick={() => setExpandedItem(expandedItem === `contradiction-${index}` ? null : `contradiction-${index}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-red-500">⚠</span>
                    <div>
                      <p className="font-medium text-red-800">{contradiction.description}</p>
                      <p className="text-xs text-red-600">
                        {contradiction.platforms?.join(' ↔ ')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      contradiction.severity === 'high' 
                        ? 'bg-red-200 text-red-800' 
                        : contradiction.severity === 'medium'
                          ? 'bg-orange-200 text-orange-800'
                          : 'bg-yellow-200 text-yellow-800'
                    }`}>
                      {contradiction.severity}
                    </span>
                    <svg 
                      className={`w-4 h-4 text-red-500 transform transition-transform ${expandedItem === `contradiction-${index}` ? 'rotate-180' : ''}`} 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {expandedItem === `contradiction-${index}` && contradiction.details && (
                  <div className="mt-3 pt-3 border-t border-red-200">
                    <p className="text-xs font-medium text-red-700 mb-2">{t('correlation.details') || 'Details:'}</p>
                    <div className="text-sm text-red-800 space-y-1">
                      {Object.entries(contradiction.details).map(([key, value], dIndex) => (
                        <div key={dIndex} className="flex">
                          <span className="font-medium capitalize mr-2">{key.replace(/_/g, ' ')}:</span>
                          <span className="truncate">
                            {Array.isArray(value) ? value.join(', ') : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Issues Found */}
      {overlaps.length === 0 && contradictions.length === 0 && (
        <div className="text-center py-6 text-gray-400">
          <svg className="w-10 h-10 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">
            {t('correlation.noComparisons') || 'No significant overlaps or contradictions found'}
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-500 font-medium mb-2">{t('correlation.legend') || 'Legend'}</p>
        <div className="flex flex-wrap gap-3 text-xs">
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 rounded bg-green-400"></span>
            <span>{t('correlation.exactMatch') || 'Exact Match (90-100%)'}</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 rounded bg-lime-400"></span>
            <span>{t('correlation.highMatch') || 'High Match (70-89%)'}</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 rounded bg-yellow-400"></span>
            <span>{t('correlation.partialMatch') || 'Partial Match (50-69%)'}</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 rounded bg-red-400"></span>
            <span>{t('correlation.mismatch') || 'Mismatch (<50%)'}</span>
          </span>
        </div>
      </div>
    </div>
  );
}

export default CorrelationMatrix;
