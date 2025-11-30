// =============================================================================
// LIGHT SCAN RESULTS COMPONENT
// =============================================================================
// Displays results from Light Scan grouped by platform.
// Shows scan summary, platform sections, and deep scan prompt.
// =============================================================================

import React from 'react';

// Platform emoji mapping
const PLATFORM_EMOJIS = {
  facebook: '📘',
  instagram: '📷',
  linkedin: '💼',
  x: '𝕏',
};

// Platform display names
const PLATFORM_NAMES = {
  facebook: 'Facebook',
  instagram: 'Instagram',
  linkedin: 'LinkedIn',
  x: 'X (Twitter)',
};

// Platform colors for styling
const PLATFORM_COLORS = {
  facebook: 'border-blue-500 bg-blue-50',
  instagram: 'border-pink-500 bg-pink-50',
  linkedin: 'border-blue-700 bg-blue-50',
  x: 'border-gray-800 bg-gray-50',
};

/**
 * LightScanResults Component
 * 
 * Displays Light Scan results grouped by platform with:
 * - Scan summary (total results, duration)
 * - Platform sections with results
 * - Deep scan prompt at the bottom
 * 
 * @param {Object} props - Component props
 * @param {Object} props.results - Light scan results from API
 * @param {string} props.identifier - The searched identifier
 * @param {Function} props.onNewScan - Callback to start a new scan
 * @param {Function} props.onDeepScan - Callback to trigger deep scan prompt
 */
function LightScanResults({ results, identifier, onNewScan, onDeepScan }) {
  if (!results) {
    return null;
  }

  const {
    total_results,
    scan_duration_seconds,
    platforms,
    deep_scan_message,
  } = results;

  return (
    <div className="light-scan-results space-y-6">
      {/* Scan Summary */}
      <div className="scan-summary bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900">
            Light Scan Results
          </h2>
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
            Complete
          </span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-slate-50 rounded-xl">
            <p className="text-2xl font-bold text-blue-600">{total_results}</p>
            <p className="text-xs text-slate-500">Results Found</p>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-xl">
            <p className="text-2xl font-bold text-slate-700">
              {scan_duration_seconds?.toFixed(1)}s
            </p>
            <p className="text-xs text-slate-500">Scan Duration</p>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-xl">
            <p className="text-2xl font-bold text-slate-700">{platforms?.length || 0}</p>
            <p className="text-xs text-slate-500">Platforms Checked</p>
          </div>
          <div className="text-center p-3 bg-slate-50 rounded-xl">
            <p className="text-2xl font-bold text-slate-700">
              {platforms?.filter(p => p.results_count > 0).length || 0}
            </p>
            <p className="text-xs text-slate-500">With Results</p>
          </div>
        </div>
        
        <p className="mt-4 text-sm text-slate-600">
          Searched for: <span className="font-semibold">"{identifier}"</span>
        </p>
      </div>

      {/* Platform Results */}
      {platforms && platforms.length > 0 && (
        <div className="space-y-4">
          {platforms.map((platform) => (
            <PlatformSection key={platform.platform} platform={platform} />
          ))}
        </div>
      )}

      {/* No Results Message */}
      {(!platforms || platforms.every(p => p.results_count === 0)) && (
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-8 text-center">
          <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">No Results Found</h3>
          <p className="text-slate-500">
            No matching profiles were found for "{identifier}". Try a different identifier or use Deep Scan for more comprehensive results.
          </p>
        </div>
      )}

      {/* Deep Scan Prompt */}
      <div className="deep-scan-prompt bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold mb-1">Want more detailed analysis?</h3>
            <p className="text-blue-100 text-sm">
              {deep_scan_message || "Deep Scan provides comprehensive profile analysis with browser extension."}
            </p>
          </div>
          <button
            onClick={onDeepScan}
            className="whitespace-nowrap px-6 py-3 bg-white text-blue-600 font-semibold rounded-xl hover:bg-blue-50 transition-colors flex items-center gap-2"
          >
            <span>🔍</span>
            Try Deep Scan
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onNewScan}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          New Scan
        </button>
      </div>
    </div>
  );
}

/**
 * PlatformSection Component
 * 
 * Displays results for a single platform
 */
function PlatformSection({ platform }) {
  const {
    platform: platformId,
    platform_emoji,
    results_count,
    results,
  } = platform;

  const emoji = platform_emoji || PLATFORM_EMOJIS[platformId] || '🌐';
  const name = PLATFORM_NAMES[platformId] || platformId;
  const colorClass = PLATFORM_COLORS[platformId] || 'border-slate-300 bg-slate-50';

  return (
    <div className={`platform-section bg-white rounded-2xl shadow-lg shadow-slate-200/50 border-l-4 ${colorClass.split(' ')[0]} overflow-hidden`}>
      {/* Platform Header */}
      <div className={`px-6 py-4 ${colorClass.split(' ')[1]} border-b border-slate-100`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{emoji}</span>
            <h3 className="text-lg font-semibold text-slate-800">{name}</h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            results_count > 0 
              ? 'bg-green-100 text-green-800' 
              : 'bg-slate-100 text-slate-500'
          }`}>
            {results_count} {results_count === 1 ? 'result' : 'results'}
          </span>
        </div>
      </div>

      {/* Results List */}
      {results_count > 0 && results && (
        <div className="divide-y divide-slate-100">
          {results.map((result, index) => (
            <ResultCard key={index} result={result} platformId={platformId} />
          ))}
        </div>
      )}

      {/* No Results for Platform */}
      {results_count === 0 && (
        <div className="px-6 py-4 text-center text-slate-400 text-sm">
          No profiles found on {name}
        </div>
      )}
    </div>
  );
}

/**
 * ResultCard Component
 * 
 * Displays a single search result
 */
function ResultCard({ result, platformId }) {
  const { title, url, snippet } = result;

  return (
    <div className="result-card px-6 py-4 hover:bg-slate-50 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-slate-800 truncate mb-1">
            {title || 'Untitled Profile'}
          </h4>
          {snippet && (
            <p className="text-sm text-slate-500 line-clamp-2 mb-2">{snippet}</p>
          )}
          <p className="text-xs text-slate-400 truncate">{url}</p>
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          Open Profile
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  );
}

export default LightScanResults;
