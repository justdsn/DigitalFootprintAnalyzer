// =============================================================================
// PRIVACY POLICY PAGE
// =============================================================================
// Privacy Policy page for the Digital Footprint Analyzer.
// =============================================================================

import React from 'react';
import { Link } from 'react-router-dom';

function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-display font-bold text-gray-900 mb-4">
            Privacy Policy
          </h1>
          <p className="text-gray-500">Last updated: November 28, 2025</p>
        </div>

        {/* Content Card */}
        <div className="bg-white rounded-2xl shadow-card p-8 md:p-10 space-y-8">
          {/* Introduction */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-gray-600 leading-relaxed">
              Welcome to Digital Footprint Analyzer ("we," "our," or "us"). We are committed to protecting 
              your privacy and ensuring the security of your personal information. This Privacy Policy 
              explains how we collect, use, disclose, and safeguard your information when you use our 
              digital footprint analysis service.
            </p>
          </section>

          {/* Information We Collect */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              When you use our service, we may collect the following types of information:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li><strong>Identifiers:</strong> Usernames, email addresses, phone numbers, or names that you voluntarily provide for analysis.</li>
              <li><strong>Usage Data:</strong> Information about how you interact with our service, including timestamps and features used.</li>
              <li><strong>Technical Data:</strong> Browser type, device information, and IP address for security and service improvement purposes.</li>
            </ul>
          </section>

          {/* How We Use Your Information */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              We use the information you provide solely for the following purposes:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>To perform digital footprint analysis based on your request</li>
              <li>To generate platform URLs and identify potential exposure</li>
              <li>To provide personalized privacy recommendations</li>
              <li>To improve and optimize our service</li>
              <li>To ensure the security and integrity of our platform</li>
            </ul>
          </section>

          {/* Data Retention */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">4. Data Retention</h2>
            <p className="text-gray-600 leading-relaxed">
              <strong>We do not store your personal identifiers.</strong> The information you enter for 
              analysis (usernames, emails, phone numbers, names) is processed in real-time and is not 
              saved to our databases. Once your analysis is complete, we do not retain any of your 
              submitted identifiers. Only anonymized, aggregated usage statistics may be retained for 
              service improvement purposes.
            </p>
          </section>

          {/* Data Security */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">5. Data Security</h2>
            <p className="text-gray-600 leading-relaxed">
              We implement appropriate technical and organizational security measures to protect your 
              information during transmission and processing. All data transfers are encrypted using 
              industry-standard SSL/TLS protocols. However, no method of transmission over the Internet 
              is 100% secure, and we cannot guarantee absolute security.
            </p>
          </section>

          {/* Third-Party Services */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">6. Third-Party Services</h2>
            <p className="text-gray-600 leading-relaxed">
              Our service generates links to third-party social media platforms (Facebook, Instagram, 
              X/Twitter, LinkedIn) based on the identifiers you provide. We are not responsible for the 
              privacy practices of these external platforms. We encourage you to review their respective 
              privacy policies.
            </p>
          </section>

          {/* Your Rights */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">7. Your Rights</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              As a user of our service, you have the right to:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>Choose what information you provide for analysis</li>
              <li>Use the service without creating an account</li>
              <li>Request information about how your data is processed</li>
              <li>Contact us with any privacy-related concerns</li>
            </ul>
          </section>

          {/* Children's Privacy */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">8. Children's Privacy</h2>
            <p className="text-gray-600 leading-relaxed">
              Our service is not intended for individuals under the age of 13. We do not knowingly 
              collect personal information from children under 13. If you believe we have inadvertently 
              collected such information, please contact us immediately.
            </p>
          </section>

          {/* Changes to This Policy */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">9. Changes to This Policy</h2>
            <p className="text-gray-600 leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of any changes by 
              posting the new Privacy Policy on this page and updating the "Last updated" date. You are 
              advised to review this Privacy Policy periodically for any changes.
            </p>
          </section>

          {/* Contact Us */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">10. Contact Us</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have any questions about this Privacy Policy or our privacy practices, please 
              contact us at:
            </p>
            <p className="text-gray-600 mt-2">
              <strong>Email:</strong> privacy@digitalfootprint.lk
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

export default PrivacyPolicyPage;
