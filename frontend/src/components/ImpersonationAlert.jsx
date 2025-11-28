// =============================================================================
// IMPERSONATION ALERT COMPONENT
// =============================================================================
// Warning banner component that displays impersonation risk assessment.
// Shows risk level, score, and relevant warnings for high-risk profiles.
// =============================================================================

/**
 * ImpersonationAlert Component
 * 
 * Displays a prominent warning when impersonation risk is detected.
 * Color-coded based on risk level (low, medium, high, critical).
 * 
 * Props:
 * - score: Impersonation score (0-100)
 * - riskLevel: Risk level string ('low', 'medium', 'high', 'critical')
 * - riskFactors: Object containing detected risk factors
 * - className: Optional additional CSS classes
 */

import React from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// RISK LEVEL STYLES
// =============================================================================

const RISK_STYLES = {
  low: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    icon: 'text-green-500',
    title: 'text-green-800',
    text: 'text-green-700',
    badge: 'bg-green-100 text-green-800',
    progressBg: 'bg-green-100',
    progressFill: 'bg-green-500'
  },
  medium: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    icon: 'text-amber-500',
    title: 'text-amber-800',
    text: 'text-amber-700',
    badge: 'bg-amber-100 text-amber-800',
    progressBg: 'bg-amber-100',
    progressFill: 'bg-amber-500'
  },
  high: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: 'text-orange-500',
    title: 'text-orange-800',
    text: 'text-orange-700',
    badge: 'bg-orange-100 text-orange-800',
    progressBg: 'bg-orange-100',
    progressFill: 'bg-orange-500'
  },
  critical: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    icon: 'text-red-500',
    title: 'text-red-800',
    text: 'text-red-700',
    badge: 'bg-red-100 text-red-800',
    progressBg: 'bg-red-100',
    progressFill: 'bg-red-600'
  }
};

// =============================================================================
// ICON COMPONENTS
// =============================================================================

// Shield check icon for low risk
const ShieldCheckIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

// Warning icon for medium/high risk
const WarningIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

// Alert icon for critical risk
const AlertIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

function ImpersonationAlert({ 
  score = 0, 
  riskLevel = 'low', 
  riskFactors = {},
  className = '' 
}) {
  const { t } = useLanguage();
  
  // Get styles based on risk level
  const styles = RISK_STYLES[riskLevel] || RISK_STYLES.low;
  
  // Get the appropriate icon
  const getIcon = () => {
    switch (riskLevel) {
      case 'low':
        return <ShieldCheckIcon className={`w-6 h-6 ${styles.icon}`} />;
      case 'critical':
        return <AlertIcon className={`w-6 h-6 ${styles.icon}`} />;
      default:
        return <WarningIcon className={`w-6 h-6 ${styles.icon}`} />;
    }
  };

  // Get risk level translation key
  const getRiskLevelText = () => {
    const key = `impersonation.levels.${riskLevel}`;
    const translations = {
      low: 'Low Risk',
      medium: 'Medium Risk',
      high: 'High Risk',
      critical: 'Critical Risk'
    };
    return t(key) || translations[riskLevel] || 'Unknown Risk';
  };

  // Get risk description
  const getRiskDescription = () => {
    const descriptions = {
      low: t('impersonation.descriptions.low') || 
        'Profiles appear consistent. No significant impersonation indicators detected.',
      medium: t('impersonation.descriptions.medium') || 
        'Some inconsistencies detected. Review the comparison details below.',
      high: t('impersonation.descriptions.high') || 
        'Significant inconsistencies found. Possible impersonation risk.',
      critical: t('impersonation.descriptions.critical') || 
        'High likelihood of impersonation. Immediate attention recommended.'
    };
    return descriptions[riskLevel] || descriptions.low;
  };

  // Format risk factors for display
  const getRiskFactorItems = () => {
    const items = [];
    
    if (riskFactors.typosquatting?.detected) {
      items.push({
        label: t('impersonation.factors.typosquatting') || 'Typosquatting Detected',
        detail: `Usernames: ${riskFactors.typosquatting.usernames?.join(' → ')}`,
        severity: 'high'
      });
    }
    
    if (riskFactors.name_mismatch) {
      items.push({
        label: t('impersonation.factors.nameMismatch') || 'Name Mismatch',
        detail: `Different names used across platforms`,
        severity: riskFactors.name_mismatch.severity
      });
    }
    
    if (riskFactors.location_mismatch) {
      items.push({
        label: t('impersonation.factors.locationMismatch') || 'Location Mismatch',
        detail: `Different locations stated`,
        severity: 'medium'
      });
    }
    
    if (riskFactors.email_mismatch) {
      items.push({
        label: t('impersonation.factors.emailMismatch') || 'Email Mismatch',
        detail: `Different email addresses`,
        severity: 'medium'
      });
    }
    
    if (riskFactors.suspicious_bio_similarity) {
      items.push({
        label: t('impersonation.factors.bioSimilarity') || 'Suspicious Bio Similarity',
        detail: `${Math.round(riskFactors.suspicious_bio_similarity.score * 100)}% similar bios`,
        severity: 'low'
      });
    }
    
    return items;
  };

  const riskFactorItems = getRiskFactorItems();

  return (
    <div className={`rounded-xl ${styles.bg} ${styles.border} border-2 p-6 ${className}`}>
      {/* ------------------------------------------------------------------- */}
      {/* Header with Score */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getIcon()}
          <div>
            <h3 className={`text-lg font-semibold ${styles.title}`}>
              {t('impersonation.title') || 'Impersonation Risk Assessment'}
            </h3>
            <p className={`text-sm ${styles.text}`}>
              {getRiskDescription()}
            </p>
          </div>
        </div>
        
        {/* Score Badge */}
        <div className={`px-4 py-2 rounded-lg ${styles.badge} text-center`}>
          <div className="text-2xl font-bold">{score}</div>
          <div className="text-xs uppercase tracking-wide">{getRiskLevelText()}</div>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Progress Bar */}
      {/* ------------------------------------------------------------------- */}
      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1">
          <span className={styles.text}>
            {t('impersonation.score') || 'Risk Score'}
          </span>
          <span className={styles.text}>{score}/100</span>
        </div>
        <div className={`h-2 rounded-full ${styles.progressBg}`}>
          <div 
            className={`h-2 rounded-full ${styles.progressFill} transition-all duration-500`}
            style={{ width: `${score}%` }}
          />
        </div>
        {/* Score scale labels */}
        <div className="flex justify-between text-xs mt-1 text-gray-400">
          <span>{t('impersonation.scaleLow') || 'Low'}</span>
          <span>{t('impersonation.scaleHigh') || 'High'}</span>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Risk Factors List */}
      {/* ------------------------------------------------------------------- */}
      {riskFactorItems.length > 0 && (
        <div className="mt-4 pt-4 border-t border-dashed border-gray-200">
          <h4 className={`text-sm font-medium ${styles.title} mb-2`}>
            {t('impersonation.factorsTitle') || 'Detected Risk Factors'}
          </h4>
          <ul className="space-y-2">
            {riskFactorItems.map((item, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <svg 
                  className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                    item.severity === 'high' ? 'text-red-500' : 
                    item.severity === 'medium' ? 'text-amber-500' : 'text-gray-400'
                  }`} 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fillRule="evenodd" 
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
                    clipRule="evenodd" 
                  />
                </svg>
                <div>
                  <span className={`font-medium ${styles.text}`}>{item.label}</span>
                  <p className={`text-sm opacity-75 ${styles.text}`}>{item.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Action Suggestions for High Risk */}
      {/* ------------------------------------------------------------------- */}
      {(riskLevel === 'high' || riskLevel === 'critical') && (
        <div className="mt-4 pt-4 border-t border-dashed border-gray-200">
          <h4 className={`text-sm font-medium ${styles.title} mb-2`}>
            {t('impersonation.recommendations') || 'Recommended Actions'}
          </h4>
          <ul className={`text-sm space-y-1 ${styles.text}`}>
            <li>• {t('impersonation.actions.verify') || 'Verify the authenticity of these profiles'}</li>
            <li>• {t('impersonation.actions.report') || 'Report suspicious accounts to the platform'}</li>
            <li>• {t('impersonation.actions.monitor') || 'Monitor these profiles for further activity'}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default ImpersonationAlert;
