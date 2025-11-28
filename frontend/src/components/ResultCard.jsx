// =============================================================================
// RESULT CARD COMPONENT
// =============================================================================
// Reusable card component for displaying result sections.
// Used throughout the results page for consistent styling.
// =============================================================================

/**
 * ResultCard Component
 * 
 * A styled card component for displaying result sections.
 * Includes title, optional subtitle, and icon.
 * 
 * Props:
 * - title: Card title
 * - subtitle: Optional description
 * - icon: Optional icon element
 * - children: Card content
 * - className: Additional CSS classes
 */

import React from 'react';

// =============================================================================
// RESULT CARD COMPONENT
// =============================================================================

function ResultCard({ title, subtitle, icon, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {/* Card Header */}
      {(title || subtitle) && (
        <div className="mb-4">
          <div className="flex items-center space-x-3">
            {/* Icon (if provided) */}
            {icon && (
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center text-primary-600">
                {icon}
              </div>
            )}
            
            <div>
              {/* Title */}
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              
              {/* Subtitle */}
              {subtitle && (
                <p className="text-sm text-gray-500">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Card Content */}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}

// =============================================================================
// RESULT LIST ITEM COMPONENT
// =============================================================================

/**
 * ResultListItem Component
 * 
 * A single item in a result list with label and value.
 */
export function ResultListItem({ label, value, valueClassName = '' }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-600">{label}</span>
      <span className={`font-medium ${valueClassName || 'text-gray-900'}`}>
        {value}
      </span>
    </div>
  );
}

// =============================================================================
// RESULT BADGE COMPONENT
// =============================================================================

/**
 * ResultBadge Component
 * 
 * A badge/tag component for displaying items in a list.
 */
export function ResultBadge({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'bg-gray-100 text-gray-700',
    primary: 'bg-primary-100 text-primary-700',
    accent: 'bg-accent-100 text-accent-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
  };

  return (
    <span 
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
}

// =============================================================================
// RESULT EMPTY STATE COMPONENT
// =============================================================================

/**
 * ResultEmptyState Component
 * 
 * Displayed when a result section has no data.
 */
export function ResultEmptyState({ message = 'No data found' }) {
  return (
    <div className="text-center py-4 text-gray-400">
      <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p className="text-sm">{message}</p>
    </div>
  );
}

export default ResultCard;
