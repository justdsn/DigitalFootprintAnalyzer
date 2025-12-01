// =============================================================================
// SHARED CONTENT SCRIPT UTILITIES
// =============================================================================
// Common utilities and functions used by all platform-specific content scripts.
// =============================================================================

/**
 * Extract profile information from a profile card/element
 * @param {Element} element - DOM element containing profile info
 * @param {Object} selectors - Platform-specific CSS selectors
 * @returns {Object} Extracted profile data
 */
function extractProfileFromElement(element, selectors) {
  const profile = {
    name: null,
    username: null,
    profileUrl: null,
    profileImage: null,
    bio: null,
    location: null,
    email: null,
    phone: null,
    website: null,
    followers: null,
    following: null,
    metadata: {}
  };
  
  try {
    // Extract name
    if (selectors.name) {
      const nameEl = element.querySelector(selectors.name);
      if (nameEl) {
        profile.name = nameEl.textContent.trim();
      }
    }
    
    // Extract username
    if (selectors.username) {
      const usernameEl = element.querySelector(selectors.username);
      if (usernameEl) {
        profile.username = usernameEl.textContent.trim().replace('@', '');
      }
    }
    
    // Extract profile URL
    if (selectors.profileUrl) {
      const linkEl = element.querySelector(selectors.profileUrl);
      if (linkEl && linkEl.href) {
        profile.profileUrl = linkEl.href;
      }
    }
    
    // Extract profile image
    if (selectors.profileImage) {
      const imgEl = element.querySelector(selectors.profileImage);
      if (imgEl && imgEl.src) {
        profile.profileImage = imgEl.src;
      }
    }
    
    // Extract bio
    if (selectors.bio) {
      const bioEl = element.querySelector(selectors.bio);
      if (bioEl) {
        profile.bio = bioEl.textContent.trim();
      }
    }
    
    // Extract additional PII if visible
    const text = element.textContent || '';
    
    // Extract emails
    const emailMatch = text.match(/[\w.-]+@[\w.-]+\.\w+/g);
    if (emailMatch && emailMatch.length > 0) {
      profile.email = emailMatch[0];
    }
    
    // Extract phone numbers (Sri Lankan formats)
    const phoneMatch = text.match(/(?:\+94|0)?7[0-9]{8}|(?:\+94|0)?[1-9][0-9]{7}/g);
    if (phoneMatch && phoneMatch.length > 0) {
      profile.phone = phoneMatch[0];
    }
    
    // Extract URLs - filter out social media platform URLs
    const urlMatch = text.match(/https?:\/\/[^\s]+/g);
    if (urlMatch && urlMatch.length > 0) {
      const socialDomains = ['facebook.com', 'instagram.com', 'linkedin.com', 'x.com', 'twitter.com'];
      profile.website = urlMatch.find(urlStr => {
        try {
          const parsedUrl = new URL(urlStr);
          const hostname = parsedUrl.hostname.toLowerCase();
          // Check if URL is NOT from a social media platform
          return !socialDomains.some(domain => 
            hostname === domain || hostname.endsWith('.' + domain)
          );
        } catch {
          return false; // Invalid URL
        }
      });
    }
    
  } catch (error) {
    console.error('Error extracting profile data:', error);
  }
  
  return profile;
}

/**
 * Extract text content safely
 * @param {Element} element - DOM element
 * @param {string} selector - CSS selector
 * @returns {string|null} Text content or null
 */
function safeGetText(element, selector) {
  try {
    const el = element.querySelector(selector);
    return el ? el.textContent.trim() : null;
  } catch {
    return null;
  }
}

/**
 * Extract attribute value safely
 * @param {Element} element - DOM element
 * @param {string} selector - CSS selector
 * @param {string} attribute - Attribute name
 * @returns {string|null} Attribute value or null
 */
function safeGetAttribute(element, selector, attribute) {
  try {
    const el = element.querySelector(selector);
    return el ? el.getAttribute(attribute) : null;
  } catch {
    return null;
  }
}

/**
 * Wait for an element to appear in the DOM
 * @param {string} selector - CSS selector
 * @param {number} timeout - Maximum wait time in ms
 * @returns {Promise<Element|null>} The element or null if timeout
 */
function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }
    
    const observer = new MutationObserver((mutations, obs) => {
      const el = document.querySelector(selector);
      if (el) {
        obs.disconnect();
        resolve(el);
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    setTimeout(() => {
      observer.disconnect();
      resolve(null);
    }, timeout);
  });
}

/**
 * Send extracted data to background service worker
 * @param {string} action - Action type
 * @param {Object} data - Data to send
 */
function sendToBackground(action, data) {
  chrome.runtime.sendMessage({ action, data }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('Error sending to background:', chrome.runtime.lastError);
    }
  });
}

/**
 * Extract PII patterns from text
 * @param {string} text - Text to analyze
 * @returns {Object} Extracted PII
 */
function extractPII(text) {
  const pii = {
    emails: [],
    phones: [],
    urls: [],
    mentions: []
  };
  
  if (!text) return pii;
  
  // Extract emails
  const emailRegex = /[\w.-]+@[\w.-]+\.\w+/g;
  const emails = text.match(emailRegex);
  if (emails) {
    pii.emails = [...new Set(emails)];
  }
  
  // Extract phone numbers (Sri Lankan and international)
  const phoneRegex = /(?:\+94|0)?7[0-9]{8}|(?:\+94|0)?[1-9][0-9]{7}|\+[1-9]\d{6,14}/g;
  const phones = text.match(phoneRegex);
  if (phones) {
    pii.phones = [...new Set(phones)];
  }
  
  // Extract URLs
  const urlRegex = /https?:\/\/[^\s<>"']+/g;
  const urls = text.match(urlRegex);
  if (urls) {
    pii.urls = [...new Set(urls)];
  }
  
  // Extract mentions
  const mentionRegex = /@[a-zA-Z0-9._]+/g;
  const mentions = text.match(mentionRegex);
  if (mentions) {
    pii.mentions = [...new Set(mentions)];
  }
  
  return pii;
}

/**
 * Check if hostname matches a platform domain
 * Uses exact domain matching to prevent subdomain spoofing
 * @param {string} hostname - Hostname to check
 * @param {string} domain - Domain to match against
 * @returns {boolean}
 */
function isValidPlatformDomain(hostname, domain) {
  // Exact match or subdomain match
  return hostname === domain || hostname.endsWith('.' + domain);
}

/**
 * Determine current platform from URL
 * Uses proper hostname validation to prevent spoofing
 * @returns {string|null} Platform name or null
 */
function getCurrentPlatform() {
  const hostname = window.location.hostname.toLowerCase();
  
  if (isValidPlatformDomain(hostname, 'facebook.com')) return 'facebook';
  if (isValidPlatformDomain(hostname, 'instagram.com')) return 'instagram';
  if (isValidPlatformDomain(hostname, 'linkedin.com')) return 'linkedin';
  if (isValidPlatformDomain(hostname, 'x.com') || isValidPlatformDomain(hostname, 'twitter.com')) return 'x';
  
  return null;
}

/**
 * Check if current page is a search results page
 * @returns {boolean}
 */
function isSearchPage() {
  const pathname = window.location.pathname;
  const search = window.location.search;
  return pathname.includes('/search') || search.includes('q=');
}

/**
 * Check if current page is a profile page
 * @returns {boolean}
 */
function isProfilePage() {
  const platform = getCurrentPlatform();
  const pathname = window.location.pathname;
  
  switch (platform) {
    case 'facebook':
      return !pathname.includes('/search') && 
             !pathname.includes('/groups') && 
             !pathname.includes('/pages') &&
             pathname !== '/';
    case 'instagram':
      return pathname.match(/^\/[a-zA-Z0-9._]+\/?$/) !== null;
    case 'linkedin':
      return pathname.startsWith('/in/');
    case 'x':
      return pathname.match(/^\/[a-zA-Z0-9_]+\/?$/) !== null &&
             !pathname.includes('/search') &&
             !pathname.includes('/home');
    default:
      return false;
  }
}

/**
 * Debounce function for performance
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // This will be handled by platform-specific scripts
  return false;
});
