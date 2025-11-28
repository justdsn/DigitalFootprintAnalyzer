// =============================================================================
// INPUT FORM COMPONENT
// =============================================================================
// Form component for entering analysis parameters.
// Includes validation and loading states.
// =============================================================================

/**
 * InputForm Component
 * 
 * Features:
 * - Username input (required)
 * - Optional email, phone, name inputs
 * - Form validation
 * - Loading state during submission
 * - Error display
 * - Privacy notice
 */

import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

// =============================================================================
// INPUT FORM COMPONENT
// =============================================================================

function InputForm({ onSubmit, isLoading }) {
  // ---------------------------------------------------------------------------
  // Hooks
  // ---------------------------------------------------------------------------
  const { t } = useLanguage();

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    name: ''
  });

  const [errors, setErrors] = useState({});

  // ---------------------------------------------------------------------------
  // Validation Functions
  // ---------------------------------------------------------------------------
  
  /**
   * Validate email format
   */
  const validateEmail = (email) => {
    if (!email) return true; // Optional field
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  /**
   * Validate Sri Lankan phone number
   */
  const validatePhone = (phone) => {
    if (!phone) return true; // Optional field
    // Remove all non-digit characters except +
    const cleaned = phone.replace(/[^\d+]/g, '');
    // Check for Sri Lankan formats
    return (
      (cleaned.length === 10 && cleaned.startsWith('07')) ||
      (cleaned.length === 12 && cleaned.startsWith('+947')) ||
      (cleaned.length === 13 && cleaned.startsWith('00947'))
    );
  };

  /**
   * Validate entire form
   */
  const validateForm = () => {
    const newErrors = {};

    // Username is required
    if (!formData.username.trim()) {
      newErrors.username = t('analyze.errors.usernameRequired');
    }

    // Email validation (if provided)
    if (formData.email && !validateEmail(formData.email)) {
      newErrors.email = t('analyze.errors.invalidEmail');
    }

    // Phone validation (if provided)
    if (formData.phone && !validatePhone(formData.phone)) {
      newErrors.phone = t('analyze.errors.invalidPhone');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ---------------------------------------------------------------------------
  // Event Handlers
  // ---------------------------------------------------------------------------

  /**
   * Handle input change
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(formData);
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* -----------------------------------------------------------------
       * Username Field (Required)
       * ----------------------------------------------------------------- */}
      <div>
        <label htmlFor="username" className="form-label">
          {t('analyze.form.username.label')} <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder={t('analyze.form.username.placeholder')}
          className={`form-input ${errors.username ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}`}
          disabled={isLoading}
        />
        {errors.username ? (
          <p className="mt-1 text-sm text-red-500">{errors.username}</p>
        ) : (
          <p className="mt-1 text-sm text-gray-500">{t('analyze.form.username.hint')}</p>
        )}
      </div>

      {/* -----------------------------------------------------------------
       * Email Field (Optional)
       * ----------------------------------------------------------------- */}
      <div>
        <label htmlFor="email" className="form-label">
          {t('analyze.form.email.label')}
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder={t('analyze.form.email.placeholder')}
          className={`form-input ${errors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}`}
          disabled={isLoading}
        />
        {errors.email ? (
          <p className="mt-1 text-sm text-red-500">{errors.email}</p>
        ) : (
          <p className="mt-1 text-sm text-gray-500">{t('analyze.form.email.hint')}</p>
        )}
      </div>

      {/* -----------------------------------------------------------------
       * Phone Field (Optional)
       * ----------------------------------------------------------------- */}
      <div>
        <label htmlFor="phone" className="form-label">
          {t('analyze.form.phone.label')}
        </label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          placeholder={t('analyze.form.phone.placeholder')}
          className={`form-input ${errors.phone ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}`}
          disabled={isLoading}
        />
        {errors.phone ? (
          <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
        ) : (
          <p className="mt-1 text-sm text-gray-500">{t('analyze.form.phone.hint')}</p>
        )}
      </div>

      {/* -----------------------------------------------------------------
       * Name Field (Optional)
       * ----------------------------------------------------------------- */}
      <div>
        <label htmlFor="name" className="form-label">
          {t('analyze.form.name.label')}
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder={t('analyze.form.name.placeholder')}
          className="form-input"
          disabled={isLoading}
        />
        <p className="mt-1 text-sm text-gray-500">{t('analyze.form.name.hint')}</p>
      </div>

      {/* -----------------------------------------------------------------
       * Privacy Notice
       * ----------------------------------------------------------------- */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-blue-800">{t('analyze.privacy.title')}</h4>
            <p className="text-sm text-blue-600 mt-1">{t('analyze.privacy.description')}</p>
          </div>
        </div>
      </div>

      {/* -----------------------------------------------------------------
       * Submit Button
       * ----------------------------------------------------------------- */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full btn-primary py-4 text-lg"
      >
        {isLoading ? (
          <span className="flex items-center justify-center space-x-2">
            {/* Loading Spinner */}
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{t('analyze.form.analyzing')}</span>
          </span>
        ) : (
          t('analyze.form.submit')
        )}
      </button>
    </form>
  );
}

export default InputForm;
