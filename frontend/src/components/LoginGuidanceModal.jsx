// =============================================================================
// LOGIN GUIDANCE MODAL
// =============================================================================
// Modal component that guides users through logging into social platforms
// before starting a deep scan.
// =============================================================================

import React from 'react';

// Platform info with icons and colors
const PLATFORM_INFO = {
    facebook: {
        name: 'Facebook',
        emoji: '📘',
        color: 'bg-blue-600',
        hoverColor: 'hover:bg-blue-700',
        icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
        )
    },
    instagram: {
        name: 'Instagram',
        emoji: '📷',
        color: 'bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500',
        hoverColor: 'hover:opacity-90',
        icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
            </svg>
        )
    },
    linkedin: {
        name: 'LinkedIn',
        emoji: '💼',
        color: 'bg-blue-700',
        hoverColor: 'hover:bg-blue-800',
        icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
            </svg>
        )
    },
    x: {
        name: 'X (Twitter)',
        emoji: '𝕏',
        color: 'bg-black',
        hoverColor: 'hover:bg-gray-900',
        icon: (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
        )
    }
};

/**
 * Login Guidance Modal Component
 * 
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether modal is open
 * @param {Function} props.onClose - Close handler
 * @param {Object} props.authStatus - Auth status for each platform
 * @param {Function} props.onLoginClick - Handler when user clicks login button
 * @param {Function} props.onProceed - Handler when user proceeds with scan
 * @param {string[]} props.selectedPlatforms - Platforms selected for scan
 */
function LoginGuidanceModal({
    isOpen,
    onClose,
    authStatus = {},
    onLoginClick,
    onProceed,
    selectedPlatforms = ['facebook', 'instagram', 'linkedin', 'x'],
    isChecking = false
}) {
    // Count logged in / not logged in platforms
    const loggedInPlatforms = selectedPlatforms.filter(p => authStatus[p]?.isLoggedIn);
    const notLoggedInPlatforms = selectedPlatforms.filter(p => !authStatus[p]?.isLoggedIn);
    const allLoggedIn = notLoggedInPlatforms.length === 0;

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="flex min-h-full items-center justify-center p-4">
                <div className="relative bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 transform transition-all">
                    {/* Header */}
                    <div className="text-center mb-6">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Platform Authentication</h2>
                        <p className="text-gray-600">
                            {isChecking ? (
                                'Checking your login status...'
                            ) : allLoggedIn ? (
                                'Great! You\'re logged into all selected platforms.'
                            ) : (
                                `Please log into the following platform${notLoggedInPlatforms.length > 1 ? 's' : ''} for a complete deep scan.`
                            )}
                        </p>
                    </div>

                    {/* Loading state */}
                    {isChecking && (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                        </div>
                    )}

                    {/* Platform list - Only show platforms that need login */}
                    {!isChecking && (
                        <div className="space-y-3 mb-6">
                            {notLoggedInPlatforms.map(platformKey => {
                                const platform = PLATFORM_INFO[platformKey];
                                const status = authStatus[platformKey];
                                const isLoggedIn = status?.isLoggedIn;

                                if (!platform) return null;

                                return (
                                    <div
                                        key={platformKey}
                                        className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${isLoggedIn
                                            ? 'bg-green-50 border-green-200'
                                            : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-white`}>
                                                {platform.icon}
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                                                <p className={`text-sm ${isLoggedIn ? 'text-green-600' : 'text-gray-500'}`}>
                                                    {isLoggedIn ? '✓ Logged in' : 'Login required'}
                                                </p>
                                            </div>
                                        </div>

                                        {isLoggedIn ? (
                                            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                </svg>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => onLoginClick(platformKey)}
                                                className={`px-4 py-2 ${platform.color} ${platform.hoverColor} text-white rounded-lg text-sm font-medium transition-colors`}
                                            >
                                                Login
                                            </button>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Actions */}
                    {!isChecking && (
                        <div className="flex flex-col gap-3">
                            {allLoggedIn ? (
                                <button
                                    onClick={onProceed}
                                    className="w-full py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-semibold transition-colors flex items-center justify-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                    Start Deep Scan
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={onProceed}
                                        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-colors"
                                    >
                                        Continue with {loggedInPlatforms.length} platform{loggedInPlatforms.length !== 1 ? 's' : ''}
                                    </button>
                                    <p className="text-center text-sm text-gray-500">
                                        You can scan platforms you're logged into now, and add more later.
                                    </p>
                                </>
                            )}

                            <button
                                onClick={onClose}
                                className="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    )}

                    {/* Info note */}
                    {!isChecking && !allLoggedIn && (
                        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                            <div className="flex gap-2">
                                <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p className="text-sm text-amber-800">
                                    <strong>Why login?</strong> Deep scan accesses your social media profiles to analyze your digital footprint. We don't store your credentials.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default LoginGuidanceModal;
