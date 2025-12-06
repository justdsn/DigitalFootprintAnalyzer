// =============================================================================
// RESULTS PAGE
// =============================================================================
// Completely redesigned to focus on Sri Lanka context, clear PII exposure,
// and actionable recommendations.
// =============================================================================

import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import RiskIndicator from '../components/RiskIndicator';

// =============================================================================
// ICONS & ASSETS
// =============================================================================

const Icons = {
  facebook: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
    </svg>
  ),
  instagram: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
    </svg>
  ),
  twitter: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  ),
  x: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  ),
  linkedin: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  ),
  check: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  alert: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  external: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  )
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

const getPlatformColor = (platform) => {
  const colors = {
    facebook: 'bg-blue-600',
    instagram: 'bg-pink-600',
    twitter: 'bg-gray-900',
    x: 'bg-gray-900',
    linkedin: 'bg-blue-700',
  };
  return colors[platform?.toLowerCase()] || 'bg-gray-500';
};

const getRiskColor = (level) => {
  switch (level?.toLowerCase()) {
    case 'critical': return 'text-red-600 bg-red-50 border-red-200';
    case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'low': return 'text-green-600 bg-green-50 border-green-200';
    default: return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

const getRiskBadgeColor = (level) => {
  switch (level?.toLowerCase()) {
    case 'critical': return 'bg-red-100 text-red-800';
    case 'high': return 'bg-orange-100 text-orange-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'low': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

// Helper to safely extract string values from potentially nested objects
const safeExtractValue = (value, defaultValue = '') => {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  if (typeof value === 'object') {
    // Handle {type, value} structure from deep scan
    if (value.value !== undefined) return String(value.value);
    if (value.level !== undefined) return String(value.level);
    if (value.text !== undefined) return String(value.text);
    if (value.name !== undefined) return String(value.name);
    // Fallback to JSON string for debugging
    return JSON.stringify(value);
  }
  return String(value) || defaultValue;
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

function ResultsPage() {
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const { results } = location.state || {};

  // Redirect if no results
  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center max-w-md w-full">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Results Found</h2>
          <p className="text-gray-600 mb-6">Please start a new analysis to see your digital footprint.</p>
          <Link to="/analyze" className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 transition-colors w-full">
            Start Analysis
          </Link>
        </div>
      </div>
    );
  }

  // Determine scan type and extract data
  const isDeepScan = !!(results?.scanId || results?.backendAnalysis);
  const riskScore = safeExtractValue(results.risk_score || results.backendAnalysis?.risk_assessment?.score, 0);
  const riskLevel = safeExtractValue(results.risk_level || results.backendAnalysis?.risk_assessment?.level, 'low');

  // Extract PII items
  const exposedPii = results.exposed_pii || results.backendAnalysis?.exposed_pii || [];
  const piiArray = Array.isArray(exposedPii) ? exposedPii : [];

  // Group PII by risk
  const criticalPii = piiArray.filter(p => safeExtractValue(p.risk_level) === 'critical');
  const highPii = piiArray.filter(p => safeExtractValue(p.risk_level) === 'high');
  const mediumPii = piiArray.filter(p => safeExtractValue(p.risk_level) === 'medium');
  const lowPii = piiArray.filter(p => safeExtractValue(p.risk_level) === 'low');

  // Extract Impersonation Risks
  const impersonationRisks = results.impersonation_risks || results.backendAnalysis?.impersonation_risks || [];

  // DEBUG: Log results structure
  console.log('[ResultsPage] Full results:', JSON.stringify(results, null, 2));
  console.log('[ResultsPage] exposedPii:', exposedPii);
  console.log('[ResultsPage] impersonationRisks:', impersonationRisks);

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      {/* -----------------------------------------------------------------------
       * HEADER
       * ----------------------------------------------------------------------- */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="flex items-center text-slate-500 hover:text-slate-700 mr-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-xl font-bold text-slate-900">Analysis Report</h1>
            <span className="mx-3 text-slate-300">|</span>
            <span className="text-slate-600 font-mono bg-slate-100 px-2 py-1 rounded text-sm">
              {safeExtractValue(results.identifier) || safeExtractValue(results.username) || 'Unknown Target'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => window.print()}
              className="hidden sm:flex items-center px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Save PDF
            </button>
            <Link
              to="/analyze"
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              New Scan
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* -----------------------------------------------------------------------
         * EXECUTIVE SUMMARY
         * ----------------------------------------------------------------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Risk Score Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 h-full flex flex-col items-center justify-center text-center">
              <h2 className="text-lg font-semibold text-slate-700 mb-4">Overall Privacy Risk</h2>
              <RiskIndicator score={riskScore} level={riskLevel} />
              <p className="mt-4 text-sm text-slate-500">
                Based on exposed PII and public footprint
              </p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 h-full">
              <h2 className="text-lg font-semibold text-slate-700 mb-6">Exposure Summary</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 bg-red-50 rounded-xl border border-red-100 text-center">
                  <div className="text-3xl font-bold text-red-600 mb-1">{criticalPii.length}</div>
                  <div className="text-xs font-medium text-red-800 uppercase tracking-wide">Critical Items</div>
                </div>
                <div className="p-4 bg-orange-50 rounded-xl border border-orange-100 text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-1">{highPii.length}</div>
                  <div className="text-xs font-medium text-orange-800 uppercase tracking-wide">High Risk</div>
                </div>
                <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-100 text-center">
                  <div className="text-3xl font-bold text-yellow-600 mb-1">{mediumPii.length}</div>
                  <div className="text-xs font-medium text-yellow-800 uppercase tracking-wide">Medium Risk</div>
                </div>
                <div className="p-4 bg-purple-50 rounded-xl border border-purple-100 text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-1">{impersonationRisks.length}</div>
                  <div className="text-xs font-medium text-purple-800 uppercase tracking-wide">Impersonation</div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-900 mb-2">Analysis Scope</h3>
                <div className="flex flex-wrap gap-2">
                  {['Facebook', 'Instagram', 'LinkedIn', 'X (Twitter)'].map(platform => (
                    <span key={platform} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white border border-slate-200 text-slate-600">
                      {platform}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* -----------------------------------------------------------------------
         * CRITICAL EXPOSURE ALERT (If any)
         * ----------------------------------------------------------------------- */}
        {(criticalPii.length > 0 || highPii.length > 0) && (
          <div className="mb-8">
            <div className="bg-white rounded-2xl shadow-card overflow-hidden border-2 border-red-100">
              <div className="bg-red-50 px-6 py-4 border-b border-red-100 flex items-center">
                <span className="text-2xl mr-3">🚨</span>
                <div>
                  <h2 className="text-lg font-bold text-red-900">Critical Data Exposure Detected</h2>
                  <p className="text-sm text-red-700">The following sensitive information is publicly visible. Immediate action recommended.</p>
                </div>
              </div>

              <div className="divide-y divide-slate-100">
                {[...criticalPii, ...highPii].map((item, idx) => {
                  const itemType = safeExtractValue(item.type, 'unknown');
                  const itemValue = safeExtractValue(item.value, '');
                  const platformName = safeExtractValue(item.platform_name || item.platform, 'Unknown');
                  const sourceUrl = typeof item.source === 'object' ? null : item.source;
                  const itemRiskLevel = safeExtractValue(item.risk_level, 'low');
                  const isCritical = itemRiskLevel === 'critical';

                  return (
                    <div key={idx} className="p-6 hover:bg-slate-50 transition-colors">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="flex items-start gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isCritical ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'}`}>
                            {itemType.includes('phone') ? '📱' : itemType.includes('email') ? '📧' : itemType.includes('address') ? '🏠' : '⚠️'}
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${isCritical ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                                {itemRiskLevel}
                              </span>
                              <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">
                                {itemType.replace(/_/g, ' ')}
                              </span>
                            </div>
                            <div className="font-mono text-lg font-semibold text-slate-900 mb-1">
                              "{itemValue}"
                            </div>
                            <div className="flex items-center text-sm text-slate-500">
                              <span>Exposed on </span>
                              <span className="font-medium text-slate-900 mx-1">{platformName}</span>
                            </div>
                          </div>
                        </div>

                        {sourceUrl && (
                          <div className="flex items-center gap-3 sm:self-center">
                            <a
                              href={sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
                            >
                              View Profile
                              {Icons.external}
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* -----------------------------------------------------------------------
           * LEFT COLUMN: Impersonation & Other PII
           * ----------------------------------------------------------------------- */}
          <div className="lg:col-span-2 space-y-8">

            {/* Impersonation Detection */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">Impersonation Detection</h2>
                    <p className="text-sm text-slate-500">Accounts using similar usernames</p>
                  </div>
                </div>
                {impersonationRisks.length === 0 && (
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium flex items-center gap-1">
                    {Icons.check} No Risks Found
                  </span>
                )}
              </div>

              <div className="p-6">
                {impersonationRisks.length > 0 ? (
                  <div className="space-y-4">
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
                      <div className="flex items-start gap-3">
                        <span className="text-xl">⚠️</span>
                        <div>
                          <p className="text-sm font-medium text-amber-900">
                            We found {impersonationRisks.length} potential impersonation risks.
                          </p>
                          <p className="text-xs text-amber-700 mt-1">
                            Verify if these accounts belong to you. If not, they might be impersonating you.
                          </p>
                        </div>
                      </div>
                    </div>

                    {impersonationRisks.map((risk, idx) => {
                      // Fix: Use correct keys from backend ImpersonationDetector
                      const profileName = safeExtractValue(risk.profile_name, 'Unknown Profile');
                      const profileUrl = safeExtractValue(risk.profile_url, '#');
                      const platform = safeExtractValue(risk.platform, 'unknown');
                      const riskLevel = safeExtractValue(risk.risk_level, 'low');
                      const confidence = safeExtractValue(risk.confidence_score, 0);
                      const similarity = Math.round(confidence * 100);

                      // Extract username from URL for display
                      let username = '';
                      try {
                        if (profileUrl && profileUrl !== '#') {
                          const urlObj = new URL(profileUrl);
                          const pathParts = urlObj.pathname.split('/').filter(p => p);
                          if (pathParts.length > 0) {
                            username = pathParts[pathParts.length - 1];
                          }
                        }
                      } catch (e) {
                        username = '';
                      }

                      // Platform config
                      const platformConfig = {
                        'facebook': { emoji: '📘', name: 'Facebook', color: 'bg-blue-50 border-blue-200 text-blue-700' },
                        'instagram': { emoji: '📷', name: 'Instagram', color: 'bg-pink-50 border-pink-200 text-pink-700' },
                        'twitter': { emoji: '🐦', name: 'Twitter', color: 'bg-sky-50 border-sky-200 text-sky-700' },
                        'x': { emoji: '𝕏', name: 'X', color: 'bg-slate-50 border-slate-300 text-slate-700' },
                        'linkedin': { emoji: '💼', name: 'LinkedIn', color: 'bg-blue-50 border-blue-300 text-blue-800' },
                      };

                      const pConfig = platformConfig[platform.toLowerCase()] || { emoji: '🌐', name: platform, color: 'bg-slate-50 border-slate-200 text-slate-600' };

                      return (
                        <div key={idx} className="border border-slate-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow bg-white">
                          <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div className="flex items-start gap-3">
                              {/* Avatar / Icon */}
                              <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0 ${pConfig.color.split(' ')[0]}`}>
                                {pConfig.emoji}
                              </div>

                              <div>
                                <h3 className="font-bold text-slate-900">{profileName}</h3>
                                {username && <p className="text-sm text-slate-500 font-mono">@{username}</p>}

                                <div className="mt-2 flex items-center gap-2 flex-wrap">
                                  <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${riskLevel === 'high' ? 'bg-red-100 text-red-700' :
                                      riskLevel === 'medium' ? 'bg-orange-100 text-orange-700' :
                                        'bg-green-100 text-green-700'
                                    }`}>
                                    {riskLevel} Risk
                                  </span>
                                  <span className="text-xs text-slate-400">•</span>
                                  <span className="text-xs text-slate-500">{similarity}% Match</span>
                                  <span className="text-xs text-slate-400">•</span>
                                  <span className="text-xs text-slate-500 capitalize">{pConfig.name}</span>
                                </div>
                              </div>
                            </div>

                            <a
                              href={profileUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex-shrink-0 px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 w-full sm:w-auto"
                            >
                              View Profile
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-slate-900">Clean Record</h3>
                    <p className="text-slate-500 max-w-sm mx-auto mt-1">
                      We didn't find any suspicious accounts using your username on other platforms.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Medium & Low Risk PII */}
            {(mediumPii.length > 0 || lowPii.length > 0) && (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <h2 className="text-lg font-bold text-slate-900">Other Exposed Information</h2>
                  <p className="text-sm text-slate-500">Less critical, but good to clean up</p>
                </div>
                <div className="divide-y divide-slate-100">
                  {[...mediumPii, ...lowPii].map((item, idx) => {
                    const itemType = safeExtractValue(item.type, 'unknown');
                    const itemValue = safeExtractValue(item.value, '');
                    const platformName = safeExtractValue(item.platform_name || item.platform, 'Unknown');
                    const itemRiskLevel = safeExtractValue(item.risk_level, 'low');

                    return (
                      <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50">
                        <div className="flex items-center gap-4">
                          <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center text-slate-500">
                            {itemType.includes('loc') ? '📍' : itemType.includes('work') ? '💼' : '📝'}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-900">{itemValue}</p>
                            <div className="flex items-center gap-2 text-xs text-slate-500">
                              <span className="uppercase font-bold">{itemType}</span>
                              <span>•</span>
                              <span>{platformName}</span>
                            </div>
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${itemRiskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                          {itemRiskLevel}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* -----------------------------------------------------------------------
           * RIGHT COLUMN: Context & Recommendations
           * ----------------------------------------------------------------------- */}
          <div className="lg:col-span-1 space-y-8">

            {/* Sri Lanka Context Card */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-lg text-white overflow-hidden">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-2xl">🇱🇰</span>
                  <h2 className="text-lg font-bold">Sri Lanka Context</h2>
                </div>

                <div className="space-y-4 text-blue-50 text-sm">
                  <p>
                    Your digital footprint in Sri Lanka carries specific risks. Here's what you need to know:
                  </p>

                  {criticalPii.some(p => safeExtractValue(p.type)?.includes('phone')) && (
                    <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                      <p className="font-semibold text-white mb-1">📞 Phone Exposure</p>
                      <p>Exposed numbers are often targeted by:</p>
                      <ul className="list-disc list-inside mt-1 opacity-90">
                        <li>Fake lottery scams (Dialog/Mobitel)</li>
                        <li>WhatsApp impersonation attacks</li>
                        <li>Unsolicited marketing calls</li>
                      </ul>
                    </div>
                  )}

                  <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                    <p className="font-semibold text-white mb-1">👮 Report Cybercrime</p>
                    <p>If you are a victim of online harassment or fraud:</p>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="font-mono bg-white/20 px-2 py-1 rounded">1919</span>
                      <span>Police Hotline</span>
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="font-mono bg-white/20 px-2 py-1 rounded">cert.gov.lk</span>
                      <span>Sri Lanka CERT</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Checklist */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200">
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-lg font-bold text-slate-900">Recommended Actions</h2>
                <p className="text-sm text-slate-500">Steps to secure your footprint</p>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  {criticalPii.length > 0 && (
                    <label className="flex items-start gap-3 p-3 bg-red-50 rounded-xl border border-red-100 cursor-pointer">
                      <input type="checkbox" className="mt-1 w-4 h-4 text-red-600 rounded border-red-300 focus:ring-red-500" />
                      <span className="text-sm text-red-800 font-medium">
                        Remove critical PII (Phone/Address) from public profiles immediately
                      </span>
                    </label>
                  )}

                  <label className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-xl cursor-pointer">
                    <input type="checkbox" className="mt-1 w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" />
                    <span className="text-sm text-slate-700">
                      Enable Two-Factor Authentication (2FA) on all social accounts
                    </span>
                  </label>

                  <label className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-xl cursor-pointer">
                    <input type="checkbox" className="mt-1 w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" />
                    <span className="text-sm text-slate-700">
                      Review "Tagged Photos" settings on Facebook & Instagram
                    </span>
                  </label>

                  {impersonationRisks.length > 0 && (
                    <label className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-xl cursor-pointer">
                      <input type="checkbox" className="mt-1 w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" />
                      <span className="text-sm text-slate-700">
                        Report impersonation accounts to respective platforms
                      </span>
                    </label>
                  )}
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
