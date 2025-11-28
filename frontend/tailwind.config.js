/** @type {import('tailwindcss').Config} */

/* =============================================================================
 * TAILWIND CSS CONFIGURATION
 * =============================================================================
 * Custom Tailwind configuration for the Digital Footprint Analyzer.
 * Includes custom colors, fonts, and responsive breakpoints.
 * ============================================================================= */

module.exports = {
  // ---------------------------------------------------------------------------
  // Content Sources
  // ---------------------------------------------------------------------------
  // Specify all files that contain Tailwind classes for proper purging
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],

  // ---------------------------------------------------------------------------
  // Theme Customization
  // ---------------------------------------------------------------------------
  theme: {
    extend: {
      // -----------------------------------------------------------------------
      // Custom Color Palette
      // -----------------------------------------------------------------------
      // Blues and Teals as specified for the project
      colors: {
        // Primary Blues
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Main primary color
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',  // Dark primary
          900: '#1e3a8a',
        },
        // Teals for accents
        accent: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // Main accent color
          600: '#0d9488',  // Dark accent
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        // Risk level colors
        risk: {
          low: '#22c55e',      // Green
          medium: '#f59e0b',   // Amber
          high: '#ef4444',     // Red
        }
      },

      // -----------------------------------------------------------------------
      // Custom Font Families
      // -----------------------------------------------------------------------
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },

      // -----------------------------------------------------------------------
      // Custom Animations
      // -----------------------------------------------------------------------
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },

      // -----------------------------------------------------------------------
      // Custom Spacing
      // -----------------------------------------------------------------------
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },

      // -----------------------------------------------------------------------
      // Box Shadows
      // -----------------------------------------------------------------------
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'card': '0 0 20px rgba(0, 0, 0, 0.08)',
      },
    },
  },

  // ---------------------------------------------------------------------------
  // Plugins
  // ---------------------------------------------------------------------------
  plugins: [],
}
