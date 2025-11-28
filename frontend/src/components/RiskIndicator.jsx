// =============================================================================
// RISK INDICATOR COMPONENT
// =============================================================================
// Visual component for displaying risk assessment results.
// Includes score, level, and progress indicator.
// =============================================================================

/**
 * RiskIndicator Component
 * 
 * Features:
 * - Circular progress indicator for risk score
 * - Color-coded risk level (low/medium/high)
 * - Animated progress bar
 * - Descriptive text based on risk level
 */

import React from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// RISK INDICATOR COMPONENT
// =============================================================================

function RiskIndicator({ score, level }) {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();

  // ---------------------------------------------------------------------------
  // Risk Level Configuration
  // ---------------------------------------------------------------------------
  const riskConfig = {
    low: {
      color: 'text-green-500',
      bgColor: 'bg-green-500',
      lightBg: 'bg-green-100',
      label: t('results.risk.low'),
      description: t('results.risk.lowDescription'),
      strokeColor: '#22c55e',
    },
    medium: {
      color: 'text-amber-500',
      bgColor: 'bg-amber-500',
      lightBg: 'bg-amber-100',
      label: t('results.risk.medium'),
      description: t('results.risk.mediumDescription'),
      strokeColor: '#f59e0b',
    },
    high: {
      color: 'text-red-500',
      bgColor: 'bg-red-500',
      lightBg: 'bg-red-100',
      label: t('results.risk.high'),
      description: t('results.risk.highDescription'),
      strokeColor: '#ef4444',
    },
  };

  const config = riskConfig[level] || riskConfig.low;

  // ---------------------------------------------------------------------------
  // Calculate Circle Progress
  // ---------------------------------------------------------------------------
  // SVG circle calculations
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="card">
      {/* Header */}
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        {t('results.risk.title')}
      </h3>

      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* -------------------------------------------------------------------
         * Circular Progress Indicator
         * ------------------------------------------------------------------- */}
        <div className="relative">
          <svg width="180" height="180" className="transform -rotate-90">
            {/* Background Circle */}
            <circle
              cx="90"
              cy="90"
              r={radius}
              stroke="#e5e7eb"
              strokeWidth="12"
              fill="none"
            />
            {/* Progress Circle */}
            <circle
              cx="90"
              cy="90"
              r={radius}
              stroke={config.strokeColor}
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          
          {/* Score Display in Center */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold ${config.color}`}>
              {score}
            </span>
            <span className="text-sm text-gray-500">
              {t('results.risk.score')}
            </span>
          </div>
        </div>

        {/* -------------------------------------------------------------------
         * Risk Level Details
         * ------------------------------------------------------------------- */}
        <div className="flex-1 text-center md:text-left">
          {/* Risk Level Badge */}
          <div className={`inline-flex items-center px-4 py-2 rounded-full ${config.lightBg} ${config.color} font-semibold mb-4`}>
            {/* Icon based on level */}
            {level === 'low' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            {level === 'medium' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            )}
            {level === 'high' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            {config.label}
          </div>

          {/* Description */}
          <p className="text-gray-600">
            {config.description}
          </p>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-500 mb-1">
              <span>0</span>
              <span>100</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${config.bgColor} rounded-full transition-all duration-1000 ease-out`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RiskIndicator;
