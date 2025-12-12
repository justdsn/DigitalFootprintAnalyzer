// =============================================================================
// IMPERSONATION ALERT COMPONENT
// =============================================================================
// Warning banner component for high impersonation risk scores.
// Displays score, level, flags, and recommendations.
// =============================================================================

/**
 * ImpersonationAlert Component
 * 
 * Features:
 * - Color-coded alert based on risk level
 * - Displays impersonation score with visual indicator
 * - Lists warning flags with icons
 * - Provides actionable recommendations
 * - Collapsible sections for detailed information
 * 
 * Props:
 * - score: Impersonation risk score (0-100)
 * - level: Risk level (low/medium/high/critical)
 * - flags: Array of warning flag messages
 * - recommendations: Array of recommendation messages
 * - isLoading: Loading state indicator
 */

import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// RISK LEVEL CONFIGURATION
// =============================================================================

const RISK_LEVELS = {
  low: {
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-800',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    progressColor: 'bg-green-500',
    label: 'Low Risk',
    icon: '✓',
    description: 'Your profiles appear consistent and secure.'
  },
  medium: {
    color: 'yellow',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-800',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
    progressColor: 'bg-yellow-500',
    label: 'Medium Risk',
    icon: '⚡',
    description: 'Some inconsistencies detected. Review recommended.'
  },
  high: {
    color: 'orange',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    textColor: 'text-orange-800',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    progressColor: 'bg-orange-500',
    label: 'High Risk',
    icon: '⚠',
    description: 'Significant concerns found. Action recommended.'
  },
  critical: {
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-800',
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    progressColor: 'bg-red-500',
    label: 'Critical Risk',
    icon: '🚨',
    description: 'Potential impersonation detected. Immediate action required.'
  }
};

// =============================================================================
// IMPERSONATION ALERT COMPONENT
// =============================================================================

function ImpersonationAlert({
  score = 0,
  level = 'low',
  flags = [],
  recommendations = [],
  isLoading = false
}) {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();
  const [showDetails, setShowDetails] = useState(false);

  // ---------------------------------------------------------------------------
  // Safe Value Extraction
  // ---------------------------------------------------------------------------
  const safeScore = typeof score === 'object' ? (score.value || 0) : (score || 0);
  const safeLevel = typeof level === 'object' ? (level.value || level.level || 'low') : (level || 'low');

  // ---------------------------------------------------------------------------
  // Get risk configuration
  // ---------------------------------------------------------------------------
  const riskConfig = RISK_LEVELS[safeLevel] || RISK_LEVELS.low;

  // ---------------------------------------------------------------------------
  // Render Loading State
  // ---------------------------------------------------------------------------
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className={`rounded-xl border-2 ${riskConfig.bgColor} ${riskConfig.borderColor} overflow-hidden`}>
      {/* Header */}
      <div className="p-4 sm:p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            {/* Risk Icon */}
            <div className={`w-14 h-14 rounded-xl ${riskConfig.iconBg} flex items-center justify-center`}>
              <span className="text-3xl">{riskConfig.icon}</span>
            </div>

            {/* Risk Info */}
            <div>
              <h3 className={`text-lg font-bold ${riskConfig.textColor}`}>
                {t(`impersonation.${safeLevel}`) || riskConfig.label}
              </h3>
              <p className={`text-sm ${riskConfig.textColor} opacity-75`}>
                {t(`impersonation.${safeLevel}Description`) || riskConfig.description}
              </p>
            </div>
          </div>

          {/* Score Badge */}
          <div className="text-right">
            <div className={`text-4xl font-bold ${riskConfig.textColor}`}>
              {safeScore}
            </div>
            <div className={`text-xs ${riskConfig.textColor} opacity-75`}>
              {t('impersonation.outOf100') || '/ 100'}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="h-2 bg-white rounded-full overflow-hidden">
            <div
              className={`h-full ${riskConfig.progressColor} transition-all duration-500 ease-out`}
              style={{ width: `${safeScore}%` }}
            />
          </div>
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>{t('impersonation.safe') || 'Safe'}</span>
            <span>{t('impersonation.danger') || 'Danger'}</span>
          </div>
        </div>
      </div>

      {/* Flags Section (if any) */}
      {flags.length > 0 && (
        <div className={`px-4 sm:px-6 pb-4 ${riskConfig.bgColor}`}>
          <div className={`rounded-lg bg-white bg-opacity-60 p-4`}>
            <h4 className={`text-sm font-semibold ${riskConfig.textColor} mb-3 flex items-center space-x-2`}>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clipRule="evenodd" />
              </svg>
              <span>{t('impersonation.warningFlags') || 'Warning Flags'}</span>
            </h4>
            <ul className="space-y-2">
              {flags.map((flag, index) => {
                const flagText = typeof flag === 'object' ? (flag.text || flag.value || flag.message || JSON.stringify(flag)) : flag;
                return (
                  <li
                    key={index}
                    className={`text-sm ${riskConfig.textColor} flex items-start space-x-2`}
                  >
                    <span className="flex-shrink-0 mt-0.5">•</span>
                    <span>{flagText}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}

      {/* Expandable Details */}
      {recommendations.length > 0 && (
        <>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={`w-full px-4 sm:px-6 py-3 ${riskConfig.bgColor} border-t ${riskConfig.borderColor} flex items-center justify-between text-sm font-medium ${riskConfig.textColor} hover:bg-opacity-80 transition-colors`}
          >
            <span className="flex items-center space-x-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <span>
                {showDetails
                  ? (t('impersonation.hideRecommendations') || 'Hide Recommendations')
                  : (t('impersonation.showRecommendations') || `View ${recommendations.length} Recommendations`)
                }
              </span>
            </span>
            <svg
              className={`w-5 h-5 transform transition-transform ${showDetails ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Recommendations Panel */}
          {showDetails && (
            <div className={`px-4 sm:px-6 pb-6 ${riskConfig.bgColor}`}>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center space-x-2">
                  <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>{t('impersonation.recommendations') || 'Recommended Actions'}</span>
                </h4>
                <ul className="space-y-3">
                  {recommendations.map((rec, index) => {
                    const recText = typeof rec === 'object' ? (rec.text || rec.value || rec.message || JSON.stringify(rec)) : rec;
                    return (
                      <li
                        key={index}
                        className="flex items-start space-x-3 text-sm text-gray-700"
                      >
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-medium">
                          {index + 1}
                        </span>
                        <span className="pt-0.5">{recText}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          )}
        </>
      )}

      {/* Quick Action Buttons (for high/critical risk) */}
      {(safeLevel === 'high' || safeLevel === 'critical') && (
        <div className={`px-4 sm:px-6 pb-4 ${riskConfig.bgColor} flex flex-wrap gap-2`}>
          <button className={`px-4 py-2 rounded-lg bg-white ${riskConfig.textColor} text-sm font-medium hover:shadow-md transition-shadow flex items-center space-x-2`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{t('impersonation.reportAccount') || 'Report Suspicious Account'}</span>
          </button>
          <button className={`px-4 py-2 rounded-lg bg-white ${riskConfig.textColor} text-sm font-medium hover:shadow-md transition-shadow flex items-center space-x-2`}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{t('impersonation.getHelp') || 'Get Help'}</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default ImpersonationAlert;
