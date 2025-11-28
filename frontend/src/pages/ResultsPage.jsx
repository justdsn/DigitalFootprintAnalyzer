// =============================================================================
// RESULTS PAGE
// =============================================================================
// Page component for displaying analysis results.
// Shows risk score, platform URLs, variations, PII, and recommendations.
// Includes transliteration results and correlation visualization.
// =============================================================================

/**
 * ResultsPage Component
 * 
 * Sections:
 * - Summary: Username and processing time
 * - Risk Assessment: Visual risk indicator
 * - Transliteration: Sinhala to English conversion results
 * - Correlation: Cross-platform comparison (if available)
 * - Impersonation Alert: Risk assessment for multiple profiles
 * - Platform Profiles: Links to check on each platform
 * - Username Variations: List of variations to monitor
 * - Detected PII: Extracted personal information
 * - NER Entities: Named entities found
 * - Pattern Analysis: Username structure analysis
 * - Recommendations: Privacy improvement suggestions
 */

import React from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import RiskIndicator from '../components/RiskIndicator';
import ResultCard, { ResultListItem, ResultBadge, ResultEmptyState } from '../components/ResultCard';
import TransliterationDisplay from '../components/TransliterationDisplay';
import CorrelationMatrix from '../components/CorrelationMatrix';
import ImpersonationAlert from '../components/ImpersonationAlert';

// =============================================================================
// PLATFORM ICONS
// =============================================================================

const PlatformIcons = {
  facebook: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  ),
  instagram: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
    </svg>
  ),
  twitter: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
    </svg>
  ),
  linkedin: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  ),
  tiktok: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
    </svg>
  ),
  youtube: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
    </svg>
  ),
};

// Platform color classes
const platformColors = {
  facebook: 'text-blue-600 hover:text-blue-700',
  instagram: 'text-pink-600 hover:text-pink-700',
  twitter: 'text-gray-900 hover:text-gray-700',
  linkedin: 'text-blue-700 hover:text-blue-800',
  tiktok: 'text-gray-900 hover:text-gray-700',
  youtube: 'text-red-600 hover:text-red-700',
};

// =============================================================================
// RESULTS PAGE COMPONENT
// =============================================================================

function ResultsPage() {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();

  // Get results from navigation state
  const { results } = location.state || {};

  // ---------------------------------------------------------------------------
  // Redirect if no results
  // ---------------------------------------------------------------------------
  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-white rounded-2xl shadow-card p-8">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Results Found</h2>
            <p className="text-gray-600 mb-6">Please run an analysis first to see results.</p>
            <Link to="/analyze" className="btn-primary">
              Start Analysis
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* -------------------------------------------------------------------
         * Page Header
         * ------------------------------------------------------------------- */}
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-display font-bold text-gray-900 mb-4">
            {t('results.title')}
          </h1>
          <p className="text-lg text-gray-600">
            {t('results.subtitle')}
          </p>
        </div>

        {/* -------------------------------------------------------------------
         * Summary Card
         * ------------------------------------------------------------------- */}
        <div className="bg-white rounded-2xl shadow-card p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('results.summary.title')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-500">{t('results.summary.username')}</p>
                <p className="font-semibold text-gray-900">@{results.username}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-500">{t('results.summary.processingTime')}</p>
                <p className="font-semibold text-gray-900">{results.processing_time_ms} {t('common.milliseconds')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* -------------------------------------------------------------------
         * Risk Assessment
         * ------------------------------------------------------------------- */}
        <div className="mb-8">
          <RiskIndicator score={results.risk_score} level={results.risk_level} />
        </div>

        {/* -------------------------------------------------------------------
         * Transliteration Results (if available)
         * Shows Sinhala to English conversion with spelling variants
         * ------------------------------------------------------------------- */}
        {results.transliteration && results.transliteration.transliterations?.length > 0 && (
          <div className="mb-8">
            <TransliterationDisplay
              original={results.transliteration.original}
              transliterations={results.transliteration.transliterations}
              isSinhala={results.transliteration.is_sinhala}
            />
          </div>
        )}

        {/* -------------------------------------------------------------------
         * Correlation Results (if available)
         * Shows cross-platform comparison and impersonation risk
         * ------------------------------------------------------------------- */}
        {results.correlation && (
          <>
            {/* Impersonation Alert for medium/high risk */}
            {(results.correlation.risk_level === 'medium' || 
              results.correlation.risk_level === 'high' || 
              results.correlation.risk_level === 'critical') && (
              <div className="mb-8">
                <ImpersonationAlert
                  score={results.correlation.impersonation_score}
                  riskLevel={results.correlation.risk_level}
                  riskFactors={results.correlation.analysis_details?.risk_factors || {}}
                />
              </div>
            )}

            {/* Correlation Matrix */}
            {(results.correlation.overlaps?.length > 0 || 
              results.correlation.contradictions?.length > 0) && (
              <div className="mb-8">
                <CorrelationMatrix
                  profiles={results.correlation.analysis_details?.profiles || []}
                  overlaps={results.correlation.overlaps}
                  contradictions={results.correlation.contradictions}
                />
              </div>
            )}
          </>
        )}

        {/* -------------------------------------------------------------------
         * Two Column Layout
         * ------------------------------------------------------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* -----------------------------------------------------------------
           * Platform Profiles
           * ----------------------------------------------------------------- */}
          <ResultCard
            title={t('results.platforms.title')}
            subtitle={t('results.platforms.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            }
          >
            <div className="space-y-3">
              {Object.entries(results.platform_urls).map(([platform, data]) => (
                <a
                  key={platform}
                  href={data.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors ${platformColors[platform] || 'text-gray-600'}`}
                >
                  <div className="flex items-center space-x-3">
                    {PlatformIcons[platform]}
                    <span className="font-medium">{data.name}</span>
                  </div>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              ))}
            </div>
          </ResultCard>

          {/* -----------------------------------------------------------------
           * Pattern Analysis
           * ----------------------------------------------------------------- */}
          <ResultCard
            title={t('results.patterns.title')}
            subtitle={t('results.patterns.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          >
            <div>
              <ResultListItem 
                label={t('results.patterns.length')} 
                value={`${results.pattern_analysis.length} ${t('common.characters')}`} 
              />
              <ResultListItem 
                label={t('results.patterns.hasNumbers')} 
                value={results.pattern_analysis.has_numbers ? t('common.yes') : t('common.no')}
                valueClassName={results.pattern_analysis.has_numbers ? 'text-amber-600' : 'text-green-600'}
              />
              <ResultListItem 
                label={t('results.patterns.hasUnderscores')} 
                value={results.pattern_analysis.has_underscores ? t('common.yes') : t('common.no')} 
              />
              <ResultListItem 
                label={t('results.patterns.numberDensity')} 
                value={`${(results.pattern_analysis.number_density * 100).toFixed(0)}%`}
                valueClassName={results.pattern_analysis.number_density > 0.3 ? 'text-amber-600' : 'text-green-600'}
              />
              <ResultListItem 
                label={t('results.patterns.suspiciousPatterns')} 
                value={results.pattern_analysis.has_suspicious_patterns ? t('common.yes') : t('common.no')}
                valueClassName={results.pattern_analysis.has_suspicious_patterns ? 'text-red-600' : 'text-green-600'}
              />
            </div>
          </ResultCard>
        </div>

        {/* -------------------------------------------------------------------
         * Username Variations
         * ------------------------------------------------------------------- */}
        <div className="mb-8">
          <ResultCard
            title={t('results.variations.title')}
            subtitle={t('results.variations.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            }
          >
            {results.variations.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {results.variations.slice(0, 20).map((variation) => (
                  <ResultBadge key={variation} variant={variation === results.username ? 'primary' : 'default'}>
                    {variation}
                  </ResultBadge>
                ))}
                {results.variations.length > 20 && (
                  <ResultBadge variant="accent">+{results.variations.length - 20} more</ResultBadge>
                )}
              </div>
            ) : (
              <ResultEmptyState message="No variations generated" />
            )}
          </ResultCard>
        </div>

        {/* -------------------------------------------------------------------
         * Two Column Layout - PII and Entities
         * ------------------------------------------------------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* -----------------------------------------------------------------
           * Detected PII
           * ----------------------------------------------------------------- */}
          <ResultCard
            title={t('results.pii.title')}
            subtitle={t('results.pii.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          >
            <div className="space-y-4">
              {/* Emails */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.pii.emails')}</h4>
                {results.extracted_pii.emails?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.extracted_pii.emails.map((email, index) => (
                      <ResultBadge key={index} variant="warning">{email}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>

              {/* Phones */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.pii.phones')}</h4>
                {results.extracted_pii.phones?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.extracted_pii.phones.map((phone, index) => (
                      <ResultBadge key={index} variant="warning">{phone}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>

              {/* Mentions */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.pii.mentions')}</h4>
                {results.extracted_pii.mentions?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.extracted_pii.mentions.map((mention, index) => (
                      <ResultBadge key={index} variant="primary">{mention}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>
            </div>
          </ResultCard>

          {/* -----------------------------------------------------------------
           * NER Entities
           * ----------------------------------------------------------------- */}
          <ResultCard
            title={t('results.entities.title')}
            subtitle={t('results.entities.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            }
          >
            <div className="space-y-4">
              {/* Persons */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.entities.persons')}</h4>
                {results.ner_entities.persons?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.ner_entities.persons.map((person, index) => (
                      <ResultBadge key={index} variant="primary">{person}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>

              {/* Locations */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.entities.locations')}</h4>
                {results.ner_entities.locations?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.ner_entities.locations.map((location, index) => (
                      <ResultBadge key={index} variant="accent">{location}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>

              {/* Organizations */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">{t('results.entities.organizations')}</h4>
                {results.ner_entities.organizations?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {results.ner_entities.organizations.map((org, index) => (
                      <ResultBadge key={index} variant="success">{org}</ResultBadge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">None detected</p>
                )}
              </div>
            </div>
          </ResultCard>
        </div>

        {/* -------------------------------------------------------------------
         * Recommendations
         * ------------------------------------------------------------------- */}
        <div className="mb-8">
          <ResultCard
            title={t('results.recommendations.title')}
            subtitle={t('results.recommendations.subtitle')}
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            }
          >
            {results.recommendations?.length > 0 ? (
              <ul className="space-y-3">
                {results.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 flex items-center justify-center mt-0.5">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p className="text-gray-700">{recommendation}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <ResultEmptyState message="No recommendations available" />
            )}
          </ResultCard>
        </div>

        {/* -------------------------------------------------------------------
         * Action Buttons
         * ------------------------------------------------------------------- */}
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button
            onClick={() => navigate('/analyze')}
            className="btn-primary"
          >
            {t('results.actions.newAnalysis')}
          </button>
          <button
            onClick={() => window.print()}
            className="btn-secondary"
          >
            {t('results.actions.print')}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
