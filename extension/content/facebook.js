// =============================================================================
// FACEBOOK CONTENT SCRIPT
// =============================================================================
// Extracts profile information from Facebook search results and profile pages.
// =============================================================================

(() => {
  'use strict';

  const PLATFORM = 'facebook';

  /**
   * Check if user is authenticated on Facebook
   * @returns {boolean} True if logged in
   */
  function isAuthenticated() {
    // Check for user menu/profile icon which indicates logged-in state
    const authIndicators = [
      '[aria-label*="profile" i]',
      '[aria-label*="account" i]',
      '[data-click="profile_icon"]',
      'div[role="banner"] img[referrerpolicy="origin-when-cross-origin"]', // Profile picture in header
      'a[href*="/me/"]',
      'a[href*="/profile.php"]'
    ];

    for (const selector of authIndicators) {
      if (document.querySelector(selector)) {
        return true;
      }
    }

    // Check if we're on login page (indicates NOT authenticated)
    if (window.location.pathname.includes('/login')) {
      return false;
    }

    // Additional check: look for common unauthenticated elements
    const unauthElements = [
      'form[action*="/login"]',
      'input[name="email"][placeholder*="Email" i]'
    ];

    for (const selector of unauthElements) {
      if (document.querySelector(selector)) {
        return false;
      }
    }

    return true;
  }

  // Facebook-specific CSS selectors (with fallbacks for DOM changes)
  // Updated December 2024 - Facebook's DOM changes frequently
  const SELECTORS = {
    // Search results page - multiple selectors for resilience
    searchResults: '[data-pagelet="SearchResults"], [role="feed"], [role="main"] > div > div',
    searchResultItem: '[data-visualcompletion="ignore-dynamic"], [role="article"], div[data-testid="search-result"]',
    searchResultName: 'a[role="link"] span, a span[dir="auto"]',
    searchResultLink: 'a[role="link"][href*="facebook.com"]',
    searchResultImage: 'image, img[data-visualcompletion="media-vc-image"], svg image, img[alt]',

    // Profile page selectors with fallbacks
    profileName: 'h1, [data-pagelet="ProfileActions"] h1',
    profileUsername: '[data-pagelet="ProfileActions"] + div span, span[dir="auto"]',
    profileBio: '[data-pagelet="ProfileTileCollection"] span, div[data-pagelet*="Profile"] span',
    profileImage: '[data-pagelet="ProfileTileCollection"] image, [data-pagelet="ProfileTileCollection"] img, img[data-imgperflogname="profileCoverPhoto"]',
    profileInfo: '[data-pagelet="ProfileTileCollection"], [data-pagelet*="ProfileAppSection"]',

    // About section with fallbacks
    aboutSection: '[data-pagelet="ProfileAppSection_0"], [data-pagelet*="About"]',
    aboutItem: '[role="listitem"], div[class*="about"]',
    workEducation: '[data-pagelet="ProfileAppSection_1"]',
    placesLived: '[data-pagelet="ProfileAppSection_2"]',
    contactInfo: '[data-pagelet="ProfileAppSection_3"]'
  };

  /**
   * Extract profiles from Facebook search results
   * @returns {Array} Array of profile objects
   */
  function extractSearchResults() {
    const profiles = [];

    try {
      // Try multiple selectors for search results container
      const selectors = SELECTORS.searchResults.split(', ');
      let resultsContainer = null;

      for (const selector of selectors) {
        resultsContainer = document.querySelector(selector.trim());
        if (resultsContainer) {
          console.log(`[Facebook] Found results container with selector: ${selector}`);
          break;
        }
      }

      // Fallback: scan the entire main content area
      if (!resultsContainer) {
        console.log('[Facebook] Primary container not found, falling back to body scan');
        resultsContainer = document.querySelector('[role="main"]') || document.body;
      }

      // Find all result items using multiple selectors
      const itemSelectors = SELECTORS.searchResultItem.split(', ');
      let items = [];

      for (const selector of itemSelectors) {
        const found = resultsContainer.querySelectorAll(selector.trim());
        if (found.length > 0) {
          items = found;
          console.log(`[Facebook] Found ${found.length} items with selector: ${selector}`);
          break;
        }
      }

      // Fallback: find all links that look like profile links
      if (items.length === 0) {
        console.log('[Facebook] No items found, scanning for profile links directly');
        items = document.querySelectorAll('a[href*="facebook.com/"][role="link"]');
      }

      items.forEach((item, index) => {
        try {
          const profile = {
            index: index + 1,
            platform: 'Facebook',
            platformKey: PLATFORM,
            name: null,
            username: null,
            profileUrl: null,
            profileImage: null,
            snippet: null,
            mutualFriends: null,
            extractedPII: {}
          };

          // Extract name and profile URL
          const linkElements = item.querySelectorAll('a[role="link"]');
          for (const link of linkElements) {
            const href = link.href;
            if (!href) continue;

            try {
              const parsedUrl = new URL(href);
              const hostname = parsedUrl.hostname.toLowerCase();
              const pathname = parsedUrl.pathname;

              // Verify it's a Facebook domain and a profile URL
              if ((hostname === 'facebook.com' || hostname.endsWith('.facebook.com')) &&
                !pathname.includes('/search') &&
                !pathname.includes('/groups') &&
                !pathname.includes('/pages')) {
                profile.profileUrl = href;

                // Extract username from pathname
                const usernameMatch = pathname.match(/^\/([a-zA-Z0-9.]+)/);
                if (usernameMatch) {
                  profile.username = usernameMatch[1];
                }

                // Try to get name from link text
                const nameSpan = link.querySelector('span');
                if (nameSpan && nameSpan.textContent) {
                  profile.name = nameSpan.textContent.trim();
                }

                break;
              }
            } catch {
              // Invalid URL, skip
              continue;
            }
          }

          // Extract profile image
          const imgElement = item.querySelector(SELECTORS.searchResultImage);
          if (imgElement) {
            // Handle SVG image element
            if (imgElement.tagName.toLowerCase() === 'image') {
              profile.profileImage = imgElement.getAttribute('xlink:href') || imgElement.getAttribute('href');
            } else {
              profile.profileImage = imgElement.src;
            }
          }

          // Extract snippet/description
          const textContent = item.textContent;
          if (textContent) {
            // Look for mutual friends info
            const mutualMatch = textContent.match(/(\d+)\s*mutual\s*friends?/i);
            if (mutualMatch) {
              profile.mutualFriends = parseInt(mutualMatch[1], 10);
            }

            // Extract PII from visible text
            profile.extractedPII = extractPII(textContent);
          }

          // Only add if we have at least a name or URL
          if (profile.name || profile.profileUrl) {
            profiles.push(profile);
          }

        } catch (itemError) {
          console.error('Error extracting Facebook search result item:', itemError);
        }
      });

    } catch (error) {
      console.error('Error extracting Facebook search results:', error);
    }

    return profiles;
  }

  /**
   * Extract data from a Facebook profile page
   * @returns {Object} Profile data
   */
  function extractProfileData() {
    const profile = {
      platform: 'Facebook',
      platformKey: PLATFORM,
      profileUrl: window.location.href,
      name: null,
      username: null,
      profileImage: null,
      bio: null,
      location: null,
      workplace: null,
      education: null,
      email: null,
      phone: null,
      website: null,
      relationshipStatus: null,
      followers: null,
      friends: null,
      extractedPII: {}
    };

    try {
      // Extract username from URL
      const urlMatch = window.location.pathname.match(/^\/([a-zA-Z0-9.]+)/);
      if (urlMatch && !['search', 'groups', 'pages', 'watch', 'marketplace'].includes(urlMatch[1])) {
        profile.username = urlMatch[1];
      }

      // Extract name from page title or h1
      const h1 = document.querySelector('h1');
      if (h1) {
        profile.name = h1.textContent.trim();
      } else {
        // Fallback to page title
        const title = document.title;
        if (title) {
          profile.name = title.replace(/\s*[\|–-]\s*Facebook.*$/i, '').trim();
        }
      }

      // Extract profile image
      const profileImage = document.querySelector(SELECTORS.profileImage);
      if (profileImage) {
        if (profileImage.tagName.toLowerCase() === 'image') {
          profile.profileImage = profileImage.getAttribute('xlink:href') || profileImage.getAttribute('href');
        } else {
          profile.profileImage = profileImage.src;
        }
      }

      // Extract bio/intro
      const bioElement = document.querySelector(SELECTORS.profileBio);
      if (bioElement) {
        profile.bio = bioElement.textContent.trim();
      }

      // Extract all visible text for PII analysis
      const pageText = document.body.textContent || '';
      profile.extractedPII = extractPII(pageText);

      // Try to extract structured info from About section
      const aboutSection = document.querySelector(SELECTORS.aboutSection);
      if (aboutSection) {
        const aboutText = aboutSection.textContent;

        // Look for location patterns
        const locationPatterns = [
          /(?:Lives in|From|Located in)\s+([^·\n]+)/i,
          /(?:Colombo|Kandy|Galle|Jaffna|Kurunegala|Negombo|Sri Lanka)/i
        ];

        for (const pattern of locationPatterns) {
          const match = aboutText.match(pattern);
          if (match) {
            profile.location = match[1] || match[0];
            break;
          }
        }

        // Look for workplace
        const workMatch = aboutText.match(/(?:Works at|Worked at)\s+([^·\n]+)/i);
        if (workMatch) {
          profile.workplace = workMatch[1].trim();
        }

        // Look for education
        const eduMatch = aboutText.match(/(?:Studied at|Goes to|Went to)\s+([^·\n]+)/i);
        if (eduMatch) {
          profile.education = eduMatch[1].trim();
        }
      }

      // Extract friends count if visible
      const statsText = document.body.textContent;
      const friendsMatch = statsText.match(/(\d+[\d,]*)\s*friends?/i);
      if (friendsMatch) {
        profile.friends = friendsMatch[1].replace(/,/g, '');
      }

      const followersMatch = statsText.match(/(\d+[\d,]*)\s*followers?/i);
      if (followersMatch) {
        profile.followers = followersMatch[1].replace(/,/g, '');
      }

    } catch (error) {
      console.error('Error extracting Facebook profile data:', error);
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

      // Check authentication before extraction
      if (!isAuthenticated()) {
        console.log(`[${PLATFORM}] User is not authenticated`);
        sendToBackground('authenticationRequired', {
          platform: PLATFORM,
          platformName: 'Facebook',
          loginUrl: 'https://www.facebook.com/login',
          message: 'Please log into Facebook to enable deep scanning'
        });
        sendResponse({ success: false, error: 'authentication_required' });
        return true;
      }

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

      // Check authentication before extraction
      if (!isAuthenticated()) {
        console.log(`[${PLATFORM}] User is not authenticated`);
        sendToBackground('authenticationRequired', {
          platform: PLATFORM,
          platformName: 'Facebook',
          loginUrl: 'https://www.facebook.com/login',
          message: 'Please log into Facebook to enable deep scanning'
        });
        sendResponse({ success: false, error: 'authentication_required' });
        return true;
      }

      const profile = extractProfileData();

      console.log(`[${PLATFORM}] Profile data extracted`);

      sendToBackground('profileDataExtracted', {
        platform: PLATFORM,
        profile: profile
      });
      sendResponse({ success: true });
    } else if (message.action === 'checkAuthentication') {
      const authenticated = isAuthenticated();
      sendResponse({
        success: true,
        authenticated: authenticated,
        loginUrl: authenticated ? null : 'https://www.facebook.com/login'
      });
    }
    return true;
  });

  // Send content script readiness signal
  setTimeout(() => {
    const authenticated = isAuthenticated();
    sendToBackground('contentScriptReady', {
      platform: PLATFORM,
      platformName: 'Facebook',
      authenticated: authenticated,
      url: window.location.href,
      loginUrl: authenticated ? null : 'https://www.facebook.com/login'
    });
  }, 1000);

  // Auto-extract on page load if on search or profile page
  if (document.readyState === 'complete') {
    setTimeout(() => {
      if (isSearchPage() && isAuthenticated()) {
        const results = extractSearchResults();
        if (results.length > 0) {
          sendToBackground('searchResultsExtracted', {
            platform: PLATFORM,
            results: results,
            url: window.location.href
          });
        }
      } else if (isProfilePage() && isAuthenticated()) {
        const profile = extractProfileData();
        sendToBackground('profileDataExtracted', {
          platform: PLATFORM,
          profile: profile
        });
      }
    }, 2000);
  }

})();
