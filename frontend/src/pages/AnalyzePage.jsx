// =============================================================================
// ANALYZE PAGE - Modern Minimal Design
// =============================================================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyze } from '../services/api';
import { detectExtension, startDeepScanViaExtension, setExtensionId } from '../utils/extensionBridge';

function AnalyzePage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [identifier, setIdentifier] = useState('');
  const [extensionReady, setExtensionReady] = useState(false);
  const [showExtensionSetup, setShowExtensionSetup] = useState(false);
  const [extensionIdInput, setExtensionIdInput] = useState('');
  const [scanMode, setScanMode] = useState('light'); // 'light' or 'deep'

  useEffect(() => {
    // Check for extension on mount
    checkExtension();
  }, []);

  const checkExtension = async () => {
    const isInstalled = await detectExtension();
    setExtensionReady(isInstalled);
  };

  const handleConnectExtension = () => {
    if (extensionIdInput.trim()) {
      setExtensionId(extensionIdInput.trim());
      setExtensionReady(true);
      setShowExtensionSetup(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setError('Please enter an identifier to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Send only the identifier - backend will auto-detect the type
      const results = await analyze({
        identifier: identifier.trim()
      });
      navigate('/results', { state: { results } });
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeepScan = async () => {
    if (!identifier.trim()) {
      setError('Please enter an identifier to scan');
      return;
    }

    if (!extensionReady) {
      setShowExtensionSetup(true);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Automatically trigger extension
      const result = await startDeepScanViaExtension({
        identifierType: 'username',
        identifierValue: identifier.trim(),
        platforms: ['facebook', 'instagram', 'linkedin', 'x']
      });

      // Extension returns results - display them
      navigate('/results', { state: { results: result } });

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 px-4">
      <div className="max-w-xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
            Analyze Your Digital Footprint
          </h1>
          <p className="text-slate-600">
            Enter any identifier and we'll find your digital presence
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-6 sm:p-8">
          {/* Error Alert */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-100 rounded-xl p-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Input Field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Enter username, email, phone, or name
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
                  placeholder="e.g., kasun_perera, kasun@gmail.com, 0771234567"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  disabled={isLoading}
                  autoComplete="off"
                />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                We'll automatically detect what type of identifier you entered
              </p>
            </div>

            {/* Scan Mode Toggle */}
            <div className="flex gap-2 mb-4">
              <button
                type="button"
                onClick={() => setScanMode('light')}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                  scanMode === 'light'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Light Scan
                </span>
              </button>
              <button
                type="button"
                onClick={() => setScanMode('deep')}
                className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                  scanMode === 'deep'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Deep Scan
                </span>
              </button>
            </div>

            {/* Submit Button */}
            <button
              type={scanMode === 'light' ? 'submit' : 'button'}
              onClick={scanMode === 'deep' ? handleDeepScan : undefined}
              disabled={isLoading || !identifier.trim() || (scanMode === 'deep' && !extensionReady)}
              className="w-full py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-600/25"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {scanMode === 'deep' ? 'Scanning...' : 'Analyzing...'}
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={scanMode === 'deep' ? 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' : 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'} />
                  </svg>
                  {scanMode === 'deep' ? '🔍 Start Deep Scan' : 'Start Analysis'}
                </span>
              )}
            </button>

            {/* Extension Warning */}
            {scanMode === 'deep' && !extensionReady && (
              <div className="mt-4 bg-amber-50 border border-amber-100 rounded-xl p-4 flex items-start gap-3">
                <svg className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm text-amber-700 font-medium">Extension not connected</p>
                  <button 
                    onClick={() => setShowExtensionSetup(true)}
                    className="mt-1 text-sm text-amber-700 underline hover:text-amber-800"
                  >
                    Setup Extension Now
                  </button>
                </div>
              </div>
            )}
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
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { icon: '👤', label: 'Usernames' },
              { icon: '📧', label: 'Emails' },
              { icon: '📱', label: 'Phone Numbers' },
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
            {['Facebook', 'Instagram', 'X', 'LinkedIn'].map((platform) => (
              <span
                key={platform}
                className="px-3 py-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-600"
              >
                {platform}
              </span>
            ))}
          </div>
        </div>

        {/* Extension Setup Modal */}
        {showExtensionSetup && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 sm:p-8">
                <div className="flex justify-between items-start mb-6">
                  <h2 className="text-2xl font-bold text-slate-900">🔌 Connect Extension</h2>
                  <button
                    onClick={() => setShowExtensionSetup(false)}
                    className="text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <p className="text-slate-600 mb-6">
                  To use Deep Scan, you need the Chrome extension installed and connected.
                </p>

                <div className="space-y-6">
                  <div className="bg-slate-50 rounded-xl p-6">
                    <h3 className="font-semibold text-slate-900 mb-3">Step 1: Install Extension</h3>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-slate-600">
                      <li>Open Chrome and go to <code className="bg-white px-2 py-1 rounded text-xs">chrome://extensions</code></li>
                      <li>Enable "Developer mode" (toggle in top right)</li>
                      <li>Click "Load unpacked"</li>
                      <li>Select the <code className="bg-white px-2 py-1 rounded text-xs">extension/</code> folder from this project</li>
                    </ol>
                  </div>

                  <div className="bg-slate-50 rounded-xl p-6">
                    <h3 className="font-semibold text-slate-900 mb-3">Step 2: Get Extension ID</h3>
                    <p className="text-sm text-slate-600 mb-4">
                      After installing, the extension will show its ID. You can find it:
                    </p>
                    <ul className="list-disc list-inside space-y-2 text-sm text-slate-600 mb-4">
                      <li>In the extension popup (click the extension icon)</li>
                      <li>Or on the <code className="bg-white px-2 py-1 rounded text-xs">chrome://extensions</code> page under the extension card</li>
                    </ul>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Paste Extension ID:
                      </label>
                      <input
                        type="text"
                        value={extensionIdInput}
                        onChange={(e) => setExtensionIdInput(e.target.value)}
                        placeholder="e.g., abcdefghijklmnopqrstuvwxyz123456"
                        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={handleConnectExtension}
                      disabled={!extensionIdInput.trim()}
                      className="flex-1 py-3 px-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    >
                      Connect Extension
                    </button>
                    <button
                      onClick={() => setShowExtensionSetup(false)}
                      className="px-6 py-3 bg-slate-100 text-slate-700 font-semibold rounded-xl hover:bg-slate-200 transition-all duration-200"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalyzePage;
