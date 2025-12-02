// =============================================================================
// LINKEDIN CONTENT SCRIPT
// =============================================================================
// Extracts profile information from LinkedIn search results and profile pages.
// =============================================================================

(() => {
  'use strict';
  
  const PLATFORM = 'linkedin';
  
  // LinkedIn-specific CSS selectors
  const SELECTORS = {
    // Search results page
    searchResults: '.search-results-container',
    searchResultItem: '.reusable-search__result-container',
    searchResultName: '.entity-result__title-text a span[aria-hidden="true"]',
    searchResultLink: '.entity-result__title-text a',
    searchResultImage: '.entity-result__universal-image img',
    searchResultHeadline: '.entity-result__primary-subtitle',
    searchResultLocation: '.entity-result__secondary-subtitle',
    
    // Profile page
    profileSection: '.pv-top-card',
    profileName: '.pv-top-card--list h1, .text-heading-xlarge',
    profileHeadline: '.pv-top-card--list .text-body-medium',
    profileLocation: '.pv-top-card--list .text-body-small',
    profileImage: '.pv-top-card__photo img, .pv-top-card-profile-picture__image',
    profileAbout: '#about ~ .display-flex .pv-shared-text-with-see-more span',
    profileConnections: '.pv-top-card--list .t-bold',
    
    // Experience section
    experienceSection: '#experience',
    experienceItem: '.artdeco-list__item',
    experienceTitle: '.t-bold span[aria-hidden="true"]',
    experienceCompany: '.t-normal span[aria-hidden="true"]',
    
    // Education section
    educationSection: '#education',
    educationItem: '.artdeco-list__item',
    educationSchool: '.t-bold span[aria-hidden="true"]',
    educationDegree: '.t-normal span[aria-hidden="true"]',
    
    // Contact info (when expanded)
    contactSection: '.pv-contact-info',
    contactEmail: 'a[href^="mailto:"]',
    contactPhone: '.pv-contact-info__ci-container',
    contactWebsite: 'a[href]:not([href*="linkedin.com"])'
  };
  
  /**
   * Extract profiles from LinkedIn search results
   * @returns {Array} Array of profile objects
   */
  function extractSearchResults() {
    const profiles = [];
    
    try {
      // Find all search result items
      const items = document.querySelectorAll(SELECTORS.searchResultItem);
      
      items.forEach((item, index) => {
        try {
          const profile = {
            index: index + 1,
            platform: 'LinkedIn',
            platformKey: PLATFORM,
            name: null,
            username: null,
            profileUrl: null,
            profileImage: null,
            headline: null,
            location: null,
            connectionDegree: null,
            extractedPII: {}
          };
          
          // Extract name and profile URL
          const nameLink = item.querySelector(SELECTORS.searchResultName);
          const profileLink = item.querySelector(SELECTORS.searchResultLink);
          
          if (nameLink) {
            profile.name = nameLink.textContent?.trim();
          }
          
          if (profileLink && profileLink.href) {
            profile.profileUrl = profileLink.href.split('?')[0]; // Remove query params
            
            // Extract username/slug from URL
            const urlMatch = profile.profileUrl.match(/linkedin\.com\/in\/([a-zA-Z0-9-]+)/);
            if (urlMatch) {
              profile.username = urlMatch[1];
            }
          }
          
          // Extract profile image
          const img = item.querySelector(SELECTORS.searchResultImage);
          if (img && img.src && !img.src.includes('ghost')) {
            profile.profileImage = img.src;
          }
          
          // Extract headline (job title)
          const headline = item.querySelector(SELECTORS.searchResultHeadline);
          if (headline) {
            profile.headline = headline.textContent?.trim();
          }
          
          // Extract location
          const location = item.querySelector(SELECTORS.searchResultLocation);
          if (location) {
            profile.location = location.textContent?.trim();
          }
          
          // Check for connection degree
          const itemText = item.textContent || '';
          const degreeMatch = itemText.match(/(\d+)(?:st|nd|rd|th)\s*degree/i);
          if (degreeMatch) {
            profile.connectionDegree = degreeMatch[1];
          }
          
          // Extract PII from visible text
          profile.extractedPII = extractPII(itemText);
          
          // Only add if we have at least a name or URL
          if (profile.name || profile.profileUrl) {
            profiles.push(profile);
          }
          
        } catch (itemError) {
          console.error('Error extracting LinkedIn search result:', itemError);
        }
      });
      
    } catch (error) {
      console.error('Error extracting LinkedIn search results:', error);
    }
    
    return profiles;
  }
  
  /**
   * Extract data from a LinkedIn profile page
   * @returns {Object} Profile data
   */
  function extractProfileData() {
    const profile = {
      platform: 'LinkedIn',
      platformKey: PLATFORM,
      profileUrl: window.location.href.split('?')[0],
      name: null,
      username: null,
      profileImage: null,
      headline: null,
      location: null,
      about: null,
      connections: null,
      experience: [],
      education: [],
      email: null,
      phone: null,
      website: null,
      extractedPII: {}
    };
    
    try {
      // Extract username from URL
      const urlMatch = window.location.pathname.match(/\/in\/([a-zA-Z0-9-]+)/);
      if (urlMatch) {
        profile.username = urlMatch[1];
      }
      
      // Extract name
      const nameEl = document.querySelector(SELECTORS.profileName);
      if (nameEl) {
        profile.name = nameEl.textContent?.trim();
      }
      
      // Fallback: try page title
      if (!profile.name) {
        const title = document.title;
        if (title) {
          const titleMatch = title.match(/^(.+?)\s*(?:\||–|-|•)/);
          if (titleMatch) {
            profile.name = titleMatch[1].trim();
          }
        }
      }
      
      // Extract profile image
      const imgEl = document.querySelector(SELECTORS.profileImage);
      if (imgEl && imgEl.src && !imgEl.src.includes('ghost')) {
        profile.profileImage = imgEl.src;
      }
      
      // Extract headline
      const headlineEl = document.querySelector(SELECTORS.profileHeadline);
      if (headlineEl) {
        profile.headline = headlineEl.textContent?.trim();
      }
      
      // Extract location
      const locationEl = document.querySelector(SELECTORS.profileLocation);
      if (locationEl) {
        profile.location = locationEl.textContent?.trim();
      }
      
      // Extract about section
      const aboutEl = document.querySelector(SELECTORS.profileAbout);
      if (aboutEl) {
        profile.about = aboutEl.textContent?.trim();
      }
      
      // Extract connections count
      const pageText = document.body.textContent || '';
      const connectionsMatch = pageText.match(/(\d+[\d,]*)\+?\s*connections?/i);
      if (connectionsMatch) {
        profile.connections = connectionsMatch[1].replace(/,/g, '');
      }
      
      // Extract experience
      const experienceSection = document.querySelector(SELECTORS.experienceSection);
      if (experienceSection) {
        const experienceItems = experienceSection.querySelectorAll(SELECTORS.experienceItem);
        experienceItems.forEach((item, idx) => {
          if (idx < 3) { // Limit to first 3
            const title = item.querySelector(SELECTORS.experienceTitle)?.textContent?.trim();
            const company = item.querySelector(SELECTORS.experienceCompany)?.textContent?.trim();
            if (title || company) {
              profile.experience.push({ title, company });
            }
          }
        });
      }
      
      // Extract education
      const educationSection = document.querySelector(SELECTORS.educationSection);
      if (educationSection) {
        const educationItems = educationSection.querySelectorAll(SELECTORS.educationItem);
        educationItems.forEach((item, idx) => {
          if (idx < 3) { // Limit to first 3
            const school = item.querySelector(SELECTORS.educationSchool)?.textContent?.trim();
            const degree = item.querySelector(SELECTORS.educationDegree)?.textContent?.trim();
            if (school || degree) {
              profile.education.push({ school, degree });
            }
          }
        });
      }
      
      // Extract contact info if visible
      const contactSection = document.querySelector(SELECTORS.contactSection);
      if (contactSection) {
        const emailLink = contactSection.querySelector(SELECTORS.contactEmail);
        if (emailLink) {
          profile.email = emailLink.href?.replace('mailto:', '');
        }
        
        const websiteLink = contactSection.querySelector(SELECTORS.contactWebsite);
        if (websiteLink) {
          profile.website = websiteLink.href;
        }
      }
      
      // Extract PII from all visible content
      profile.extractedPII = extractPII(pageText);
      
      // Also look for email in about section
      if (profile.about) {
        const emailMatch = profile.about.match(/[\w.-]+@[\w.-]+\.\w+/);
        if (emailMatch && !profile.email) {
          profile.email = emailMatch[0];
        }
      }
      
    } catch (error) {
      console.error('Error extracting LinkedIn profile data:', error);
    }
    
    return profile;
  }
  
  /**
   * Handle messages from background script
   */
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log(`[${PLATFORM} Content Script] Received message:`, message.action);
    
    if (message.action === 'extractSearchResults') {
      console.log(`[${PLATFORM}] Starting extraction for query:`, message.query);
      
      const results = extractSearchResults();
      
      console.log(`[${PLATFORM}] Extracted ${results.length} results`);
      
      sendToBackground('searchResultsExtracted', {
        platform: PLATFORM,
        results: results,
        query: message.query,
        url: window.location.href
      });
      sendResponse({ success: true, count: results.length });
    } else if (message.action === 'extractProfileData') {
      console.log(`[${PLATFORM}] Starting profile data extraction`);
      
      const profile = extractProfileData();
      
      console.log(`[${PLATFORM}] Profile data extracted`);
      
      sendToBackground('profileDataExtracted', {
        platform: PLATFORM,
        profile: profile
      });
      sendResponse({ success: true });
    }
    return true;
  });
  
  // Auto-extract on page load
  if (document.readyState === 'complete') {
    setTimeout(() => {
      if (isSearchPage()) {
        const results = extractSearchResults();
        if (results.length > 0) {
          sendToBackground('searchResultsExtracted', {
            platform: PLATFORM,
            results: results,
            url: window.location.href
          });
        }
      } else if (isProfilePage()) {
        const profile = extractProfileData();
        sendToBackground('profileDataExtracted', {
          platform: PLATFORM,
          profile: profile
        });
      }
    }, 2000);
  }
  
})();
