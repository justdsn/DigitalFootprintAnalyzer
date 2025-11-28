// =============================================================================
// TERMS OF SERVICE PAGE
// =============================================================================
// Terms of Service page for the Digital Footprint Analyzer.
// =============================================================================

import React from 'react';
import { Link } from 'react-router-dom';

function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-display font-bold text-gray-900 mb-4">
            Terms of Service
          </h1>
          <p className="text-gray-500">Last updated: November 28, 2025</p>
        </div>

        {/* Content Card */}
        <div className="bg-white rounded-2xl shadow-card p-8 md:p-10 space-y-8">
          {/* Introduction */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-600 leading-relaxed">
              By accessing and using Digital Footprint Analyzer ("the Service"), you accept and agree to 
              be bound by these Terms of Service. If you do not agree to these terms, please do not use 
              our Service. We reserve the right to modify these terms at any time, and your continued use 
              of the Service constitutes acceptance of any modifications.
            </p>
          </section>

          {/* Description of Service */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
            <p className="text-gray-600 leading-relaxed">
              Digital Footprint Analyzer is a free OSINT (Open Source Intelligence) tool designed to help 
              Sri Lankan users understand their digital presence across social media platforms. The Service 
              provides analysis of usernames, emails, phone numbers, and names to identify potential 
              exposure and impersonation risks. Our Service generates links to public social media profiles 
              and provides privacy recommendations.
            </p>
          </section>

          {/* User Responsibilities */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">3. User Responsibilities</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              When using our Service, you agree to:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>Only analyze identifiers that belong to you or for which you have explicit permission</li>
              <li>Not use the Service for stalking, harassment, or any illegal activities</li>
              <li>Not use the Service to collect information about others without their consent</li>
              <li>Not attempt to circumvent, disable, or interfere with security features of the Service</li>
              <li>Not use automated systems or software to access the Service without our permission</li>
              <li>Comply with all applicable laws and regulations in Sri Lanka and your jurisdiction</li>
            </ul>
          </section>

          {/* Acceptable Use */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">4. Acceptable Use</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              The Service is intended for legitimate personal privacy awareness purposes only. 
              Acceptable uses include:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>Checking your own digital footprint and online presence</li>
              <li>Identifying potential impersonation accounts using your identity</li>
              <li>Understanding what information about you may be publicly accessible</li>
              <li>Improving your personal online privacy and security</li>
            </ul>
          </section>

          {/* Prohibited Activities */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">5. Prohibited Activities</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              The following activities are strictly prohibited:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>Using the Service to investigate, stalk, or harass other individuals</li>
              <li>Gathering information to commit fraud, identity theft, or other crimes</li>
              <li>Using the Service for commercial purposes without authorization</li>
              <li>Attempting to access accounts or information that does not belong to you</li>
              <li>Distributing malware or engaging in any activity that harms the Service</li>
              <li>Misrepresenting your identity or affiliation when using the Service</li>
            </ul>
          </section>

          {/* Disclaimer of Warranties */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">6. Disclaimer of Warranties</h2>
            <p className="text-gray-600 leading-relaxed">
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT ANY WARRANTIES OF ANY KIND, 
              EITHER EXPRESS OR IMPLIED. We do not guarantee that the Service will be uninterrupted, 
              secure, or error-free. The analysis results are based on publicly available patterns and 
              may not be 100% accurate. We make no warranties regarding the accuracy, completeness, or 
              reliability of any analysis results or recommendations provided.
            </p>
          </section>

          {/* Limitation of Liability */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">7. Limitation of Liability</h2>
            <p className="text-gray-600 leading-relaxed">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, 
              SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, 
              DATA, OR OTHER INTANGIBLE LOSSES, RESULTING FROM YOUR USE OF THE SERVICE. Our total liability 
              for any claims arising from your use of the Service shall not exceed the amount you paid to 
              use the Service (if any).
            </p>
          </section>

          {/* Intellectual Property */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">8. Intellectual Property</h2>
            <p className="text-gray-600 leading-relaxed">
              The Service, including its original content, features, and functionality, is owned by 
              Digital Footprint Analyzer and is protected by international copyright, trademark, and 
              other intellectual property laws. You may not copy, modify, distribute, or create derivative 
              works based on the Service without our express written permission.
            </p>
          </section>

          {/* Third-Party Links */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">9. Third-Party Links</h2>
            <p className="text-gray-600 leading-relaxed">
              The Service generates links to third-party social media platforms. We have no control over 
              the content, privacy policies, or practices of these third-party sites. We do not endorse or 
              assume any responsibility for any third-party sites, information, materials, products, or 
              services. Your use of third-party websites is at your own risk.
            </p>
          </section>

          {/* Indemnification */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">10. Indemnification</h2>
            <p className="text-gray-600 leading-relaxed">
              You agree to indemnify, defend, and hold harmless Digital Footprint Analyzer and its 
              affiliates, officers, directors, employees, and agents from and against any claims, 
              liabilities, damages, losses, and expenses, including reasonable attorney's fees, arising 
              out of or in any way connected with your access to or use of the Service, your violation 
              of these Terms, or your violation of any third-party rights.
            </p>
          </section>

          {/* Governing Law */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">11. Governing Law</h2>
            <p className="text-gray-600 leading-relaxed">
              These Terms shall be governed by and construed in accordance with the laws of Sri Lanka, 
              without regard to its conflict of law provisions. Any disputes arising under these Terms 
              shall be subject to the exclusive jurisdiction of the courts located in Sri Lanka.
            </p>
          </section>

          {/* Termination */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">12. Termination</h2>
            <p className="text-gray-600 leading-relaxed">
              We reserve the right to terminate or suspend your access to the Service immediately, without 
              prior notice or liability, for any reason whatsoever, including without limitation if you 
              breach these Terms. Upon termination, your right to use the Service will immediately cease.
            </p>
          </section>

          {/* Contact Information */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">13. Contact Information</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <p className="text-gray-600 mt-2">
              <strong>Email:</strong> legal@digitalfootprint.lk
            </p>
          </section>

          {/* Back Link */}
          <div className="pt-6 border-t border-gray-200">
            <Link 
              to="/" 
              className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TermsOfServicePage;
