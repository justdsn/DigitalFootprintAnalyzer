// =============================================================================
// INTERACTIVE LOADING COMPONENT
// =============================================================================
// Shows real-time progress during deep scan with platform status cards,
// progress bar, rotating tips, and time tracking
// =============================================================================

import React, { useState, useEffect } from 'react';

const TIPS = [
  "💡 Deep scans check multiple social media platforms simultaneously",
  "🔒 All data is processed locally and never stored permanently",
  "⚡ Extension keeps the service worker alive during long scans",
  "🎯 We detect usernames, emails, phone numbers, and full names",
  "🌐 Scanning across Facebook, Instagram, X, and LinkedIn",
  "🔍 Deep scans may take 1-3 minutes depending on the number of platforms",
  "📊 Results include correlation analysis and risk assessment",
  "✨ Your privacy is our priority - no tracking, no data retention"
];

const PLATFORM_INFO = {
  facebook: { name: 'Facebook', emoji: '📘', color: 'blue' },
  instagram: { name: 'Instagram', emoji: '📷', color: 'pink' },
  linkedin: { name: 'LinkedIn', emoji: '💼', color: 'blue' },
  x: { name: 'X (Twitter)', emoji: '𝕏', color: 'gray' }
};

function InteractiveLoading({ 
  platforms = ['facebook', 'instagram', 'linkedin', 'x'],
  currentPlatform = null,
  completedPlatforms = [],
  progress = 0,
  onCancel 
}) {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // Rotate tips every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % TIPS.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Update elapsed time every second
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  // Calculate estimated time remaining
  const estimatedTotal = platforms.length * 30; // Rough estimate: 30 seconds per platform
  const estimatedRemaining = Math.max(0, estimatedTotal - elapsedTime);

  // Format time as mm:ss
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get platform status
  const getPlatformStatus = (platform) => {
    if (completedPlatforms.includes(platform)) {
      return 'completed';
    } else if (currentPlatform === platform) {
      return 'scanning';
    }
    return 'pending';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <svg className="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Deep Scan in Progress
          </h1>
          <p className="text-slate-600">
            Analyzing your digital footprint across multiple platforms
          </p>
        </div>

        {/* Progress Bar */}
        <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100 p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-slate-700">Overall Progress</span>
            <span className="text-sm font-semibold text-blue-600">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          {/* Time Information */}
          <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Elapsed: {formatTime(elapsedTime)}
              </span>
              {estimatedRemaining > 0 && (
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  Est. remaining: ~{formatTime(estimatedRemaining)}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Platform Status Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          {platforms.map((platform) => {
            const info = PLATFORM_INFO[platform] || { name: platform, emoji: '🔍', color: 'gray' };
            const status = getPlatformStatus(platform);
            
            return (
              <div
                key={platform}
                className={`bg-white rounded-xl shadow-md border-2 transition-all duration-300 p-4 ${
                  status === 'completed'
                    ? 'border-green-200 bg-green-50'
                    : status === 'scanning'
                    ? 'border-blue-400 bg-blue-50 shadow-lg'
                    : 'border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{info.emoji}</span>
                    <div>
                      <h3 className="font-semibold text-slate-900">{info.name}</h3>
                      <p className={`text-xs ${
                        status === 'completed'
                          ? 'text-green-600'
                          : status === 'scanning'
                          ? 'text-blue-600'
                          : 'text-slate-500'
                      }`}>
                        {status === 'completed' && '✓ Completed'}
                        {status === 'scanning' && '⟳ Scanning...'}
                        {status === 'pending' && '○ Pending'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Status Icon */}
                  {status === 'completed' && (
                    <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                  {status === 'scanning' && (
                    <svg className="w-6 h-6 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                  )}
                  {status === 'pending' && (
                    <svg className="w-6 h-6 text-slate-300" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Rotating Tips */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 p-6 mb-6">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm text-slate-700 leading-relaxed transition-all duration-500">
                {TIPS[currentTipIndex]}
              </p>
            </div>
          </div>
        </div>

        {/* Cancel Button */}
        {onCancel && (
          <div className="text-center">
            <button
              onClick={onCancel}
              className="px-6 py-2.5 bg-white border-2 border-slate-300 text-slate-700 font-medium rounded-xl hover:bg-slate-50 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 transition-all duration-200"
            >
              Cancel Scan
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default InteractiveLoading;
