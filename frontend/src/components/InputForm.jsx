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
 * - Single identifier input with type selector
 * - Support for username, email, phone, or name
 * - Form validation based on selected type
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
  // Identifier Types Configuration
  // ---------------------------------------------------------------------------
  const identifierTypes = [
    { value: 'username', label: 'Username', icon: '👤', placeholder: 'e.g., john_doe' },
    { value: 'email', label: 'Email', icon: '📧', placeholder: 'e.g., john@example.com' },
    { value: 'phone', label: 'Phone Number', icon: '📱', placeholder: 'e.g., 0771234567' },
    { value: 'name', label: 'Name', icon: '📝', placeholder: 'e.g., John Perera' }
  ];

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const [formData, setFormData] = useState({
    identifier: '',
    identifierType: 'username'
  });

  const [errors, setErrors] = useState({});

  // ---------------------------------------------------------------------------
  // Validation Functions
  // ---------------------------------------------------------------------------
  
  /**
   * Validate email format
   */
  const validateEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  /**
   * Validate Sri Lankan phone number
   */
  const validatePhone = (phone) => {
    // Remove all non-digit characters except +
    const cleaned = phone.replace(/[^\d+]/g, '');
    // Check for Sri Lankan formats or general formats
    return (
      (cleaned.length === 10 && cleaned.startsWith('07')) ||
      (cleaned.length === 12 && cleaned.startsWith('+947')) ||
      (cleaned.length === 13 && cleaned.startsWith('00947')) ||
      (cleaned.length >= 10 && cleaned.length <= 15) // Allow international numbers
    );
  };

  /**
   * Validate username
   */
  const validateUsername = (username) => {
    return username.trim().length >= 1;
  };

  /**
   * Validate name
   */
  const validateName = (name) => {
    return name.trim().length >= 2;
  };

  /**
   * Validate entire form based on identifier type
   */
  const validateForm = () => {
    const newErrors = {};
    const { identifier, identifierType } = formData;

    if (!identifier.trim()) {
      newErrors.identifier = 'This field is required';
      setErrors(newErrors);
      return false;
    }

    switch (identifierType) {
      case 'email':
        if (!validateEmail(identifier)) {
          newErrors.identifier = 'Please enter a valid email address';
        }
        break;
      case 'phone':
        if (!validatePhone(identifier)) {
          newErrors.identifier = 'Please enter a valid phone number';
        }
        break;
      case 'username':
        if (!validateUsername(identifier)) {
          newErrors.identifier = 'Please enter a valid username';
        }
        break;
      case 'name':
        if (!validateName(identifier)) {
          newErrors.identifier = 'Please enter a valid name (at least 2 characters)';
        }
        break;
      default:
        break;
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
    if (errors.identifier) {
      setErrors({});
    }
  };

  /**
   * Handle identifier type change
   */
  const handleTypeChange = (type) => {
    setFormData(prev => ({
      ...prev,
      identifierType: type,
      identifier: '' // Clear input when type changes
    }));
    setErrors({});
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      // Transform form data to API format
      const apiData = {
        identifier: formData.identifier.trim(),
        identifier_type: formData.identifierType
      };
      onSubmit(apiData);
    }
  };

  // Get current type config
  const currentType = identifierTypes.find(t => t.value === formData.identifierType);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* -----------------------------------------------------------------
       * Identifier Type Selector
       * ----------------------------------------------------------------- */}
      <div>
        <label className="form-label mb-3">
          What are you searching with?
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {identifierTypes.map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => handleTypeChange(type.value)}
              disabled={isLoading}
              className={`
                p-3 rounded-xl border-2 transition-all duration-200
                flex flex-col items-center justify-center space-y-1
                ${formData.identifierType === type.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                }
                ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <span className="text-2xl">{type.icon}</span>
              <span className="text-sm font-medium">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* -----------------------------------------------------------------
       * Identifier Input Field
       * ----------------------------------------------------------------- */}
      <div>
        <label htmlFor="identifier" className="form-label">
          Enter your {currentType?.label.toLowerCase()} <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl">
            {currentType?.icon}
          </span>
          <input
            type={formData.identifierType === 'email' ? 'email' : formData.identifierType === 'phone' ? 'tel' : 'text'}
            id="identifier"
            name="identifier"
            value={formData.identifier}
            onChange={handleChange}
            placeholder={currentType?.placeholder}
            className={`form-input pl-12 ${errors.identifier ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''}`}
            disabled={isLoading}
            autoComplete="off"
          />
        </div>
        {errors.identifier ? (
          <p className="mt-2 text-sm text-red-500 flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {errors.identifier}
          </p>
        ) : (
          <p className="mt-2 text-sm text-gray-500">
            {formData.identifierType === 'username' && 'Enter the username you want to analyze across social platforms'}
            {formData.identifierType === 'email' && 'We\'ll check for potential exposure and linked accounts'}
            {formData.identifierType === 'phone' && 'Sri Lankan formats supported (07X-XXXXXXX or +94)'}
            {formData.identifierType === 'name' && 'Enter your full name for identity-based searches'}
          </p>
        )}
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
          <span className="flex items-center justify-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Start Analysis</span>
          </span>
        )}
      </button>
    </form>
  );
}

export default InputForm;
