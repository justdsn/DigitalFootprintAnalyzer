// =============================================================================
// FOOTER COMPONENT - Modern Minimal Design
// =============================================================================

import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="font-bold text-white">FootprintLK</span>
            </div>
            <p className="text-sm text-slate-500 leading-relaxed max-w-sm">
              A free OSINT tool to help Sri Lankans understand and protect their digital identity across social platforms.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-semibold mb-4 text-sm">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-sm hover:text-white transition-colors">Home</Link>
              </li>
              <li>
                <Link to="/analyze" className="text-sm hover:text-white transition-colors">Analyze</Link>
              </li>
              <li>
                <Link to="/privacy" className="text-sm hover:text-white transition-colors">Privacy Policy</Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm hover:text-white transition-colors">Terms of Service</Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4 text-sm">Contact</h4>
            <a 
              href="mailto:contact@footprintlk.com" 
              className="text-sm hover:text-white transition-colors"
            >
              contact@footprintlk.com
            </a>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">
            © {new Date().getFullYear()} FootprintLK. Made with ❤️ in Sri Lanka.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-600">
              Your data is never stored
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
