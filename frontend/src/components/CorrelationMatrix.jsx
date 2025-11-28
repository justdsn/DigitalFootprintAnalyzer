// =============================================================================
// CORRELATION MATRIX COMPONENT
// =============================================================================
// Displays cross-platform PII correlation results in a visual grid format.
// Shows overlaps and contradictions between different social media profiles.
// =============================================================================

/**
 * CorrelationMatrix Component
 * 
 * Visualizes the comparison of PII across multiple social media platforms.
 * Shows which fields match, differ, or are missing between profiles.
 * 
 * Props:
 * - profiles: Array of profile objects that were compared
 * - overlaps: Array of overlap results (matching information)
 * - contradictions: Array of contradiction results (conflicting information)
 * - className: Optional additional CSS classes
 */

import React from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// PLATFORM COLORS
// =============================================================================

const PLATFORM_COLORS = {
  facebook: 'bg-blue-500',
  instagram: 'bg-gradient-to-tr from-purple-500 to-pink-500',
  twitter: 'bg-gray-900',
  linkedin: 'bg-blue-700',
  tiktok: 'bg-black',
  youtube: 'bg-red-600',
  default: 'bg-gray-500'
};

const getPlatformColor = (platform) => {
  return PLATFORM_COLORS[platform?.toLowerCase()] || PLATFORM_COLORS.default;
};

// =============================================================================
// OVERLAP BADGE COMPONENT
// =============================================================================

function OverlapBadge({ overlap }) {
  const matchPercentage = Math.round(overlap.match_score * 100);
  
  // Determine color based on match score
  const getBadgeColor = () => {
    if (matchPercentage >= 90) return 'bg-green-100 text-green-700 border-green-200';
    if (matchPercentage >= 70) return 'bg-blue-100 text-blue-700 border-blue-200';
    return 'bg-amber-100 text-amber-700 border-amber-200';
  };

  return (
    <div className={`p-3 rounded-lg border ${getBadgeColor()}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium capitalize">{overlap.field}</span>
        <span className="text-sm font-semibold">{matchPercentage}%</span>
      </div>
      <p className="text-sm opacity-80">{overlap.description}</p>
      <div className="flex flex-wrap gap-1 mt-2">
        {overlap.platforms.map((platform, idx) => (
          <span 
            key={idx}
            className="px-2 py-0.5 rounded text-xs font-medium bg-white/50"
          >
            {platform}
          </span>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// CONTRADICTION BADGE COMPONENT
// =============================================================================

function ContradictionBadge({ contradiction }) {
  // Determine color based on severity
  const getBadgeColor = () => {
    if (contradiction.severity === 'high') return 'bg-red-100 text-red-700 border-red-200';
    if (contradiction.severity === 'medium') return 'bg-orange-100 text-orange-700 border-orange-200';
    return 'bg-amber-100 text-amber-700 border-amber-200';
  };

  return (
    <div className={`p-3 rounded-lg border ${getBadgeColor()}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium capitalize">{contradiction.field}</span>
        <span className="text-xs font-semibold uppercase px-2 py-0.5 rounded bg-white/50">
          {contradiction.severity}
        </span>
      </div>
      <p className="text-sm opacity-80">{contradiction.description}</p>
      <div className="flex items-center gap-2 mt-2 text-sm">
        <span className="px-2 py-0.5 rounded bg-white/50">
          {contradiction.platforms[0]}: {contradiction.values[0]}
        </span>
        <span>≠</span>
        <span className="px-2 py-0.5 rounded bg-white/50">
          {contradiction.platforms[1]}: {contradiction.values[1]}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

function CorrelationMatrix({ 
  profiles = [], 
  overlaps = [], 
  contradictions = [],
  className = '' 
}) {
  const { t } = useLanguage();

  // If no data, show empty state
  if (profiles.length === 0 && overlaps.length === 0 && contradictions.length === 0) {
    return null;
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-6 ${className}`}>
      {/* ------------------------------------------------------------------- */}
      {/* Header */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {t('correlation.title') || 'Cross-Platform Comparison'}
          </h3>
          <p className="text-sm text-gray-500">
            {t('correlation.subtitle') || 'Analyzing profiles across platforms'}
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Profiles Being Compared */}
      {/* ------------------------------------------------------------------- */}
      {profiles.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            {t('correlation.profilesCompared') || 'Profiles Compared'}
          </h4>
          <div className="flex flex-wrap gap-2">
            {profiles.map((profile, idx) => (
              <div 
                key={idx}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 border border-gray-200"
              >
                <div className={`w-2 h-2 rounded-full ${getPlatformColor(profile.platform)}`} />
                <span className="font-medium text-gray-900 capitalize">{profile.platform}</span>
                <span className="text-gray-500">@{profile.username}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Overlaps Section */}
      {/* ------------------------------------------------------------------- */}
      {overlaps.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {t('correlation.overlaps') || 'Matching Information'}
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700">
              {overlaps.length}
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {overlaps.map((overlap, idx) => (
              <OverlapBadge key={idx} overlap={overlap} />
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Contradictions Section */}
      {/* ------------------------------------------------------------------- */}
      {contradictions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <svg className="w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {t('correlation.contradictions') || 'Conflicting Information'}
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-700">
              {contradictions.length}
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {contradictions.map((contradiction, idx) => (
              <ContradictionBadge key={idx} contradiction={contradiction} />
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Summary when no overlaps or contradictions */}
      {/* ------------------------------------------------------------------- */}
      {overlaps.length === 0 && contradictions.length === 0 && profiles.length > 0 && (
        <div className="text-center py-6 text-gray-500">
          <svg className="w-12 h-12 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>{t('correlation.noMatches') || 'No significant matches or conflicts found'}</p>
        </div>
      )}
    </div>
  );
}

export default CorrelationMatrix;
