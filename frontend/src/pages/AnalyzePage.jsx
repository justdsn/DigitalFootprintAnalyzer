// =============================================================================
// ANALYZE PAGE - Modern Minimal Design with Light/Deep Scan Options
// =============================================================================

import React, { useState } from 'react';
import { lightScan, deepScan } from '../services/api';
import LightScanResults from '../components/LightScanResults';

// View states for the analyze page
const VIEW_INPUT = 'input';
const VIEW_SCAN_OPTIONS = 'scan_options';
const VIEW_LOADING = 'loading';
const VIEW_RESULTS = 'results';
const VIEW_DEEP_SCAN_MESSAGE = 'deep_scan_message';

// Identifier detection constants
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const NAME_LETTER_RATIO_THRESHOLD = 0.8;
const NAME_MIN_PARTS = 2;

/**
 * Check if the identifier is an email address
 * @param {string} identifier - The identifier to check
 * @returns {boolean} - True if it looks like an email
 */
function isEmail(identifier) {
  return EMAIL_PATTERN.test(identifier);
}

/**
 * Check if the identifier is a full name (contains spaces, mostly letters)
 * @param {string} identifier - The identifier to check
 * @returns {boolean} - True if it looks like a name
 */
function isName(identifier) {
  if (!identifier.includes(' ')) {
    return false;
  }
  
  const letterCount = (identifier.match(/[a-zA-Z\s]/g) || []).length;
  const letterRatio = letterCount / identifier.length;
  
  if (letterRatio < NAME_LETTER_RATIO_THRESHOLD) {
    return false;
  }
  
  const parts = identifier.split(' ').filter(p => p.length > 0);
  const hasEnoughParts = parts.length >= NAME_MIN_PARTS;
  const allPartsStartWithLetter = parts.every(p => /^[a-zA-Z]/.test(p));
  
  return hasEnoughParts && allPartsStartWithLetter;
}

/**
 * Detect identifier type from input string
 * @param {string} identifier - The identifier to analyze
 * @returns {string} - Detected type: 'email', 'username', or 'name'
 */
function detectIdentifierType(identifier) {
  const trimmed = identifier.trim();
  
  if (isEmail(trimmed)) {
    return 'email';
  }
  
  if (isName(trimmed)) {
    return 'name';
  }
  
  return 'username';
}

function AnalyzePage() {
  const [currentView, setCurrentView] = useState(VIEW_INPUT);
  const [error, setError] = useState(null);
  const [identifier, setIdentifier] = useState('');
  const [identifierType, setIdentifierType] = useState('');
  const [scanResults, setScanResults] = useState(null);
  const [deepScanMessage, setDeepScanMessage] = useState(null);

  // Handle identifier submission - show scan options
  const handleIdentifierSubmit = (e) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setError('Please enter an identifier to analyze');
      return;
    }
    setError(null);
    const detectedType = detectIdentifierType(identifier);
    setIdentifierType(detectedType);
    setCurrentView(VIEW_SCAN_OPTIONS);
  };

  // Handle Light Scan
  const handleLightScan = async () => {
    setCurrentView(VIEW_LOADING);
    setError(null);

    try {
      const results = await lightScan(identifierType, identifier.trim(), 'Sri Lanka');
      setScanResults(results);
      setCurrentView(VIEW_RESULTS);
    } catch (err) {
      console.error('Light scan error:', err);
      setError(err.message || 'Failed to perform light scan. Please try again.');
      setCurrentView(VIEW_SCAN_OPTIONS);
    }
  };

  // Handle Deep Scan (shows extension required message)
  const handleDeepScan = async () => {
    setCurrentView(VIEW_LOADING);
    setError(null);

    try {
      const result = await deepScan(identifierType, identifier.trim());
      setDeepScanMessage(result);
      setCurrentView(VIEW_DEEP_SCAN_MESSAGE);
    } catch (err) {
      console.error('Deep scan error:', err);
      setError(err.message || 'Failed to check deep scan availability.');
      setCurrentView(VIEW_SCAN_OPTIONS);
    }
  };

  // Reset to start new scan
  const handleNewScan = () => {
    setIdentifier('');
    setIdentifierType('');
    setScanResults(null);
    setDeepScanMessage(null);
    setError(null);
    setCurrentView(VIEW_INPUT);
  };

  // Go back to scan options
  const handleBackToOptions = () => {
    setError(null);
    setCurrentView(VIEW_SCAN_OPTIONS);
  };

  // Render based on current view
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 px-4">
      <div className={`mx-auto ${currentView === VIEW_RESULTS ? 'max-w-3xl' : 'max-w-xl'}`}>
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
            Analyze Your Digital Footprint
          </h1>
          <p className="text-slate-600">
            {currentView === VIEW_INPUT && 'Enter any identifier and we\'ll find your digital presence'}
            {currentView === VIEW_SCAN_OPTIONS && 'Choose a scan type to discover your online profiles'}
            {currentView === VIEW_LOADING && 'Scanning in progress...'}
            {currentView === VIEW_RESULTS && 'Here are the profiles we found'}
            {currentView === VIEW_DEEP_SCAN_MESSAGE && 'Deep Scan Information'}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-100 rounded-xl p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* INPUT VIEW */}
        {currentView === VIEW_INPUT && (
          <InputView
            identifier={identifier}
            setIdentifier={setIdentifier}
            setError={setError}
            onSubmit={handleIdentifierSubmit}
          />
        )}

        {/* SCAN OPTIONS VIEW */}
        {currentView === VIEW_SCAN_OPTIONS && (
          <ScanOptionsView
            identifier={identifier}
            identifierType={identifierType}
            onLightScan={handleLightScan}
            onDeepScan={handleDeepScan}
            onBack={handleNewScan}
          />
        )}

        {/* LOADING VIEW */}
        {currentView === VIEW_LOADING && (
          <LoadingView />
        )}

        {/* RESULTS VIEW */}
        {currentView === VIEW_RESULTS && (
          <LightScanResults
            results={scanResults}
            identifier={identifier}
            onNewScan={handleNewScan}
            onDeepScan={handleDeepScan}
          />
        )}

        {/* DEEP SCAN MESSAGE VIEW */}
        {currentView === VIEW_DEEP_SCAN_MESSAGE && (
          <DeepScanMessageView
            message={deepScanMessage}
            onBack={handleBackToOptions}
            onNewScan={handleNewScan}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Input View Component
 */
function InputView({ identifier, setIdentifier, setError, onSubmit }) {
  return (
    <>
      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-6 sm:p-8">
        <form onSubmit={onSubmit} className="space-y-6">
          {/* Input Field */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Enter username, email, or name
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </span>
              <input
                type="text"
                value={identifier}
                onChange={(e) => {
                  setIdentifier(e.target.value);
                  setError(null);
                }}
                placeholder="e.g., kasun_perera, kasun@gmail.com, John Perera"
                className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                autoComplete="off"
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">
              We'll automatically detect what type of identifier you entered
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!identifier.trim()}
            className="w-full py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-600/25"
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              Continue
            </span>
          </button>
        </form>

        {/* Privacy Notice */}
        <div className="mt-6 flex items-start gap-2 text-xs text-slate-500">
          <svg className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Your data is not stored. Analysis is performed in real-time and discarded immediately.</span>
        </div>
      </div>

      {/* What We Check */}
      <div className="mt-10">
        <p className="text-sm text-slate-500 text-center mb-4">What we analyze</p>
        <div className="grid grid-cols-3 gap-3">
          {[
            { icon: '👤', label: 'Usernames' },
            { icon: '📧', label: 'Emails' },
            { icon: '📝', label: 'Names' }
          ].map((item) => (
            <div
              key={item.label}
              className="flex flex-col items-center p-3 bg-white rounded-xl border border-slate-200"
            >
              <span className="text-2xl mb-1">{item.icon}</span>
              <span className="text-xs text-slate-600">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Supported Platforms */}
      <div className="mt-8 text-center">
        <p className="text-sm text-slate-500 mb-4">Checks across platforms</p>
        <div className="flex flex-wrap justify-center gap-3">
          {[
            { name: 'Facebook', emoji: '📘' },
            { name: 'Instagram', emoji: '📷' },
            { name: 'LinkedIn', emoji: '💼' },
            { name: 'X', emoji: '𝕏' }
          ].map((platform) => (
            <span
              key={platform.name}
              className="px-3 py-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-600 flex items-center gap-1"
            >
              <span>{platform.emoji}</span>
              {platform.name}
            </span>
          ))}
        </div>
      </div>
    </>
  );
}

/**
 * Scan Options View Component
 */
function ScanOptionsView({ identifier, identifierType, onLightScan, onDeepScan, onBack }) {
  return (
    <div className="space-y-6">
      {/* Identifier Display */}
      <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500 mb-1">Analyzing</p>
            <p className="text-lg font-semibold text-slate-900">"{identifier}"</p>
            <p className="text-xs text-slate-400 mt-1">
              Detected as: <span className="capitalize font-medium text-blue-600">{identifierType}</span>
            </p>
          </div>
          <button
            onClick={onBack}
            className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Change
          </button>
        </div>
      </div>

      {/* Scan Options Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Light Scan Card */}
        <div
          onClick={onLightScan}
          className="scan-card bg-white rounded-2xl shadow-lg shadow-slate-200/50 border-2 border-slate-100 hover:border-blue-500 p-6 cursor-pointer transition-all duration-200 hover:shadow-xl"
        >
          <div className="text-center mb-4">
            <span className="text-4xl">☀️</span>
          </div>
          <h3 className="text-xl font-bold text-slate-900 text-center mb-2">Light Scan</h3>
          <p className="text-sm text-slate-600 text-center mb-4">
            Quick public search using Google Dorking
          </p>
          <ul className="space-y-2 mb-6">
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              No login required
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Fast (~30 seconds)
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Finds indexed profiles
            </li>
          </ul>
          <button className="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/25">
            Start Light Scan
          </button>
        </div>

        {/* Deep Scan Card */}
        <div
          onClick={onDeepScan}
          className="scan-card bg-white rounded-2xl shadow-lg shadow-slate-200/50 border-2 border-slate-100 hover:border-indigo-500 p-6 cursor-pointer transition-all duration-200 hover:shadow-xl opacity-90"
        >
          <div className="text-center mb-4">
            <span className="text-4xl">🔍</span>
          </div>
          <h3 className="text-xl font-bold text-slate-900 text-center mb-2">Deep Scan</h3>
          <p className="text-sm text-slate-600 text-center mb-4">
            Comprehensive analysis with browser extension
          </p>
          <ul className="space-y-2 mb-6">
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Authenticated search
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Detailed PII analysis
            </li>
            <li className="flex items-center gap-2 text-sm text-slate-600">
              <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Impersonation detection
            </li>
          </ul>
          <button className="w-full py-3 bg-slate-200 text-slate-600 font-semibold rounded-xl cursor-pointer hover:bg-slate-300 transition-colors">
            Requires Extension
          </button>
        </div>
      </div>

      {/* Back Button */}
      <div className="text-center">
        <button
          onClick={onBack}
          className="text-sm text-slate-500 hover:text-slate-700 transition-colors"
        >
          ← Back to identifier input
        </button>
      </div>
    </div>
  );
}

/**
 * Loading View Component
 */
function LoadingView() {
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-12 text-center">
      <div className="flex justify-center mb-6">
        <svg className="animate-spin h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">Scanning...</h3>
      <p className="text-slate-500">Searching across social media platforms</p>
      <div className="mt-6 flex justify-center gap-2">
        <span className="px-3 py-1 bg-blue-50 text-blue-600 text-sm rounded-full">📘 Facebook</span>
        <span className="px-3 py-1 bg-pink-50 text-pink-600 text-sm rounded-full">📷 Instagram</span>
        <span className="px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full">💼 LinkedIn</span>
        <span className="px-3 py-1 bg-slate-50 text-slate-700 text-sm rounded-full">𝕏 X</span>
      </div>
    </div>
  );
}

/**
 * Deep Scan Message View Component
 */
function DeepScanMessageView({ message, onBack, onNewScan }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-8 text-center">
        <div className="mb-6">
          <span className="text-6xl">🔍</span>
        </div>
        <h3 className="text-2xl font-bold text-slate-900 mb-4">Browser Extension Required</h3>
        <p className="text-slate-600 mb-6 max-w-md mx-auto">
          {message?.message || 'Deep Scan requires the Digital Footprint Analyzer browser extension for comprehensive analysis.'}
        </p>

        {message?.extension_info && (
          <div className="bg-slate-50 rounded-xl p-6 mb-6 text-left max-w-md mx-auto">
            <h4 className="font-semibold text-slate-800 mb-3">{message.extension_info.name}</h4>
            <p className="text-sm text-slate-600 mb-4">{message.extension_info.description}</p>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-amber-100 text-amber-800 text-xs font-medium rounded-full">
                {message.extension_info.status}
              </span>
            </div>
            {message.extension_info.features && (
              <div className="mt-4">
                <p className="text-xs text-slate-500 mb-2">Features:</p>
                <p className="text-sm text-slate-600">{message.extension_info.features}</p>
              </div>
            )}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onBack}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
          >
            Try Light Scan Instead
          </button>
          <button
            onClick={onNewScan}
            className="px-6 py-3 bg-white text-slate-700 font-semibold rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors"
          >
            New Search
          </button>
        </div>
      </div>
    </div>
  );
}

export default AnalyzePage;
