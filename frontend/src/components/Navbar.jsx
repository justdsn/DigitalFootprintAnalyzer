// =============================================================================
// NAVBAR COMPONENT
// =============================================================================
// Main navigation bar with responsive design and language toggle.
// Includes mobile hamburger menu for smaller screens.
// =============================================================================

/**
 * Navbar Component
 * 
 * Features:
 * - Logo and branding
 * - Navigation links (Home, Analyze)
 * - Language toggle button
 * - Mobile responsive with hamburger menu
 * - Sticky positioning with backdrop blur
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import LanguageToggle from './LanguageToggle';

// =============================================================================
// NAVBAR COMPONENT
// =============================================================================

function Navbar() {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();
  const location = useLocation();
  
  // Mobile menu state
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // ---------------------------------------------------------------------------
  // Helper Functions
  // ---------------------------------------------------------------------------
  
  /**
   * Check if a path is currently active
   */
  const isActive = (path) => location.pathname === path;

  /**
   * Toggle mobile menu
   */
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  /**
   * Close mobile menu (for link clicks)
   */
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* -------------------------------------------------------------------
           * Logo and Brand
           * ------------------------------------------------------------------- */}
          <Link 
            to="/" 
            className="flex items-center space-x-3"
            onClick={closeMobileMenu}
          >
            {/* Logo Icon */}
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
              <svg 
                className="w-6 h-6 text-white" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" 
                />
              </svg>
            </div>
            {/* Brand Name */}
            <span className="text-lg font-display font-semibold text-gray-900 hidden sm:block">
              {t('app.name')}
            </span>
          </Link>

          {/* -------------------------------------------------------------------
           * Desktop Navigation Links
           * ------------------------------------------------------------------- */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`font-medium transition-colors duration-200 ${
                isActive('/') 
                  ? 'text-primary-600' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              {t('nav.home')}
            </Link>
            <Link
              to="/analyze"
              className={`font-medium transition-colors duration-200 ${
                isActive('/analyze') 
                  ? 'text-primary-600' 
                  : 'text-gray-600 hover:text-primary-600'
              }`}
            >
              {t('nav.analyze')}
            </Link>
            
            {/* Language Toggle */}
            <LanguageToggle />
          </div>

          {/* -------------------------------------------------------------------
           * Mobile Menu Button
           * ------------------------------------------------------------------- */}
          <div className="md:hidden flex items-center space-x-4">
            <LanguageToggle />
            <button
              onClick={toggleMobileMenu}
              className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                // Close icon
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                // Hamburger icon
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ---------------------------------------------------------------------
       * Mobile Menu Dropdown
       * --------------------------------------------------------------------- */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100">
          <div className="px-4 py-4 space-y-3">
            <Link
              to="/"
              onClick={closeMobileMenu}
              className={`block px-4 py-2 rounded-lg font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {t('nav.home')}
            </Link>
            <Link
              to="/analyze"
              onClick={closeMobileMenu}
              className={`block px-4 py-2 rounded-lg font-medium transition-colors ${
                isActive('/analyze') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {t('nav.analyze')}
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
