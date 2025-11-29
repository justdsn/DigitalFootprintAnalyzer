// =============================================================================
// ANALYZE PAGE - Modern Minimal Design
// =============================================================================

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyze } from '../services/api';

function AnalyzePage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [identifier, setIdentifier] = useState('');
  const [identifierType, setIdentifierType] = useState('username');

  const identifierTypes = [
    { value: 'username', label: 'Username', icon: '👤', placeholder: 'e.g., kasun_perera' },
    { value: 'email', label: 'Email', icon: '📧', placeholder: 'e.g., kasun@gmail.com' },
    { value: 'phone', label: 'Phone', icon: '📱', placeholder: 'e.g., 0771234567' },
    { value: 'name', label: 'Name', icon: '📝', placeholder: 'e.g., Kasun Perera' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setError('Please enter an identifier to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const results = await analyze({
        identifier: identifier.trim(),
        identifier_type: identifierType
      });
      navigate('/results', { state: { results } });
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const currentType = identifierTypes.find(t => t.value === identifierType);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 px-4">
      <div className="max-w-xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
            Analyze Your Identity
          </h1>
          <p className="text-slate-600">
            Enter any identifier to discover your digital footprint
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
            {/* Type Selector */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">
                What are you searching with?
              </label>
              <div className="grid grid-cols-4 gap-2">
                {identifierTypes.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => {
                      setIdentifierType(type.value);
                      setIdentifier('');
                      setError(null);
                    }}
                    className={`p-3 rounded-xl text-center transition-all duration-200 ${
                      identifierType === type.value
                        ? 'bg-blue-50 border-2 border-blue-500 text-blue-700'
                        : 'bg-slate-50 border-2 border-transparent text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <span className="text-xl block mb-1">{type.icon}</span>
                    <span className="text-xs font-medium">{type.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Input Field */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Enter your {currentType?.label.toLowerCase()}
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl">
                  {currentType?.icon}
                </span>
                <input
                  type={identifierType === 'email' ? 'email' : identifierType === 'phone' ? 'tel' : 'text'}
                  value={identifier}
                  onChange={(e) => {
                    setIdentifier(e.target.value);
                    setError(null);
                  }}
                  placeholder={currentType?.placeholder}
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !identifier.trim()}
              className="w-full py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-600/25"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Start Analysis
                </span>
              )}
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

        {/* Supported Platforms */}
        <div className="mt-10 text-center">
          <p className="text-sm text-slate-500 mb-4">Supported platforms</p>
          <div className="flex flex-wrap justify-center gap-4">
            {['Facebook', 'Instagram', 'X (Twitter)', 'LinkedIn'].map((platform) => (
              <span
                key={platform}
                className="px-4 py-2 bg-white rounded-lg border border-slate-200 text-sm text-slate-600"
              >
                {platform}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyzePage;
