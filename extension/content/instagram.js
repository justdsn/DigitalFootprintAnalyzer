// =============================================================================
// INSTAGRAM CONTENT SCRIPT
// =============================================================================
// Extracts profile information from Instagram search results and profile pages.
// =============================================================================

(() => {
  'use strict';
  
  const PLATFORM = 'instagram';
  
  /**
   * Check if user is authenticated on Instagram
   * @returns {boolean} True if logged in
   */
  function isAuthenticated() {
    // Check for logged-in navigation elements
    const authIndicators = [
      'svg[aria-label="Home" i]',
      'svg[aria-label="New post" i]',
      'a[href*="/direct/"]',  // Direct messages
      'a[href="/"]>svg[aria-label="Home"]',
      'nav a[href*="/accounts/activity/"]',  // Activity link
      'img[alt*="profile picture" i]'
    ];
    
    for (const selector of authIndicators) {
      if (document.querySelector(selector)) {
        return true;
      }
    }
    
    // Check if we're on login page (indicates NOT authenticated)
    if (window.location.pathname.includes('/accounts/login')) {
      return false;
    }
    
    // Additional check: look for common unauthenticated elements
    const unauthElements = [
      'input[name="username"]',
      'form[action*="/accounts/login/"]'
    ];
    
    for (const selector of unauthElements) {
      const el = document.querySelector(selector);
      if (el && el.offsetParent !== null) { // Check if visible
        return false;
      }
    }
    
    // Check for login button text
    const buttons = document.querySelectorAll('button[type="submit"]');
    for (const button of buttons) {
      if (button.textContent.toLowerCase().includes('log in')) {
        return false;
      }
    }
    
    return true;
  }
  
  // Instagram-specific CSS selectors
  const SELECTORS = {
    // Search results (in search dropdown)
    searchInput: 'input[placeholder="Search"]',
    searchResults: '[role="dialog"] a, [role="listbox"] a',
    searchResultName: 'span, div',
    searchResultUsername: 'span',
    searchResultImage: 'img, canvas',
    
    // Profile page
    profileHeader: 'header',
    profileName: 'header h2, header span',
    profileUsername: 'header h2',
    profileBio: 'header section > div > span, header section div[dir="auto"]',
    profileImage: 'header img',
    profileStats: 'header ul li, header section ul li',
    profileWebsite: 'header a[href]:not([href*="instagram.com"])',
    
    // Posts section
    postsContainer: 'article',
    postLink: 'a[href*="/p/"]'
  };
  
  /**
   * Extract profiles from Instagram search results
   * @returns {Array} Array of profile objects
   */
  function extractSearchResults() {
    const profiles = [];
    
    try {
      // Find search result links
      const resultLinks = document.querySelectorAll(SELECTORS.searchResults);
      
      resultLinks.forEach((link, index) => {
        try {
          const href = link.href;
          if (!href) return;
          
          let parsedUrl;
          try {
            parsedUrl = new URL(href);
          } catch {
            return; // Invalid URL
          }
          
          const hostname = parsedUrl.hostname.toLowerCase();
          const pathname = parsedUrl.pathname;
          
          // Verify it's Instagram and not a non-profile page
          if (!(hostname === 'instagram.com' || hostname.endsWith('.instagram.com'))) {
            return;
          }
          
          if (pathname.includes('/p/') || pathname.includes('/explore/') ||
              pathname.includes('/reel/')) {
            return;
          }
          
          const profile = {
            index: index + 1,
            platform: 'Instagram',
            platformKey: PLATFORM,
            name: null,
            username: null,
            profileUrl: href,
            profileImage: null,
            isVerified: false,
            extractedPII: {}
          };
          
          // Extract username from pathname
          const usernameMatch = pathname.match(/^\/([a-zA-Z0-9._]+)/);
          if (usernameMatch) {
            profile.username = usernameMatch[1];
          }
          
          // Extract name and username from text content
          const spans = link.querySelectorAll('span');
          if (spans.length >= 2) {
            profile.username = spans[0]?.textContent?.trim() || profile.username;
            profile.name = spans[1]?.textContent?.trim();
          } else if (spans.length === 1) {
            profile.name = spans[0]?.textContent?.trim();
          }
          
          // Extract profile image
          const img = link.querySelector(SELECTORS.searchResultImage);
          if (img && img.src) {
            profile.profileImage = img.src;
          }
          
          // Check for verified badge
          const svg = link.querySelector('svg[aria-label*="Verified"]');
          if (svg) {
            profile.isVerified = true;
          }
          
          // Only add if we have username
          if (profile.username) {
            profiles.push(profile);
          }
          
        } catch (itemError) {
          console.error('Error extracting Instagram search result:', itemError);
        }
      });
      
    } catch (error) {
      console.error('Error extracting Instagram search results:', error);
    }
    
    return profiles;
  }
  
  /**
   * Extract data from an Instagram profile page
   * @returns {Object} Profile data
   */
  function extractProfileData() {
    const profile = {
      platform: 'Instagram',
      platformKey: PLATFORM,
      profileUrl: window.location.href,
      name: null,
      username: null,
      profileImage: null,
      bio: null,
      website: null,
      isVerified: false,
      isPrivate: false,
      posts: null,
      followers: null,
      following: null,
      extractedPII: {}
    };
    
    try {
      // Extract username from URL
      const urlMatch = window.location.pathname.match(/^\/([a-zA-Z0-9._]+)/);
      if (urlMatch) {
        profile.username = urlMatch[1];
      }
      
      // Find the header section
      const header = document.querySelector(SELECTORS.profileHeader);
      
      if (header) {
        // Extract profile image
        const profileImg = header.querySelector('img');
        if (profileImg && profileImg.src) {
          profile.profileImage = profileImg.src;
          // Try to get name from alt text
          if (profileImg.alt) {
            const altMatch = profileImg.alt.match(/(.+?)['']s profile picture/i);
            if (altMatch) {
              profile.name = altMatch[1].trim();
            }
          }
        }
        
        // Extract name from page
        const nameElements = header.querySelectorAll('span');
        for (const el of nameElements) {
          const text = el.textContent?.trim();
          // Name is usually not the username and not a number
          if (text && text !== profile.username && 
              !text.match(/^[\d,]+$/) && 
              !['posts', 'followers', 'following', 'Post', 'Follower', 'Following'].includes(text)) {
            if (!profile.name && text.length > 1) {
              profile.name = text;
            }
          }
        }
        
        // Extract bio
        const bioSelectors = [
          'header section > div > span',
          'header section div[dir="auto"] span',
          'header h1 + div span'
        ];
        
        for (const selector of bioSelectors) {
          const bioEl = document.querySelector(selector);
          if (bioEl) {
            const bioText = bioEl.textContent?.trim();
            if (bioText && bioText.length > 5 && bioText !== profile.name) {
              profile.bio = bioText;
              break;
            }
          }
        }
        
        // Extract website link
        const websiteLink = header.querySelector('a[href]:not([href*="instagram.com"])');
        if (websiteLink) {
          profile.website = websiteLink.href;
        }
        
        // Extract stats (posts, followers, following)
        const statsText = header.textContent || '';
        
        const postsMatch = statsText.match(/(\d+[\d,]*)\s*posts?/i);
        if (postsMatch) {
          profile.posts = postsMatch[1].replace(/,/g, '');
        }
        
        const followersMatch = statsText.match(/(\d+[\d,]*[KM]?)\s*followers?/i);
        if (followersMatch) {
          profile.followers = followersMatch[1];
        }
        
        const followingMatch = statsText.match(/(\d+[\d,]*)\s*following/i);
        if (followingMatch) {
          profile.following = followingMatch[1].replace(/,/g, '');
        }
        
        // Check for verified badge
        const verifiedSvg = header.querySelector('svg[aria-label*="Verified"]');
        if (verifiedSvg) {
          profile.isVerified = true;
        }
        
        // Check if account is private
        if (statsText.toLowerCase().includes('private')) {
          profile.isPrivate = true;
        }
      }
      
      // Fallback: try to get name from page title
      if (!profile.name) {
        const title = document.title;
        if (title) {
          const titleMatch = title.match(/^(.+?)\s*(?:\(@|•|on Instagram)/);
          if (titleMatch) {
            profile.name = titleMatch[1].trim();
          }
        }
      }
      
      // Extract PII from bio and visible content
      const visibleText = document.body.textContent || '';
      profile.extractedPII = extractPII(profile.bio || visibleText);
      
    } catch (error) {
      console.error('Error extracting Instagram profile data:', error);
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
          platformName: 'Instagram',
          loginUrl: 'https://www.instagram.com/accounts/login/',
          message: 'Please log into Instagram to enable deep scanning'
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
          platformName: 'Instagram',
          loginUrl: 'https://www.instagram.com/accounts/login/',
          message: 'Please log into Instagram to enable deep scanning'
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
        loginUrl: authenticated ? null : 'https://www.instagram.com/accounts/login/'
      });
    } else if (message.action === 'performSearch') {
      // Instagram-specific: programmatically perform search
      performInstagramSearch(message.query).then(() => {
        sendResponse({ success: true });
      }).catch(error => {
        sendResponse({ success: false, error: error.message });
      });
      return true; // Will respond asynchronously
    }
    return true;
  });
  
  /**
   * Programmatically perform Instagram search
   * @param {string} query - Search query
   */
  async function performInstagramSearch(query) {
    console.log(`[${PLATFORM}] Performing search for: ${query}`);
    
    // Find search input (reduced timeout for better UX)
    const searchInput = await waitForElement('input[placeholder*="Search" i]', 5000);
    if (!searchInput) {
      throw new Error('Search input not found');
    }
    
    // Click on search input to open search panel
    searchInput.click();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Type the query
    searchInput.value = query;
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    searchInput.dispatchEvent(new Event('change', { bubbles: true }));
    
    console.log(`[${PLATFORM}] Search query entered, waiting for results...`);
    
    // Wait for search results to appear
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Extract search results
    const results = extractSearchResults();
    
    if (results.length > 0) {
      sendToBackground('searchResultsExtracted', {
        platform: PLATFORM,
        results: results,
        query: query,
        url: window.location.href
      });
    }
  }
  
  // Send content script readiness signal
  setTimeout(() => {
    const authenticated = isAuthenticated();
    sendToBackground('contentScriptReady', {
      platform: PLATFORM,
      platformName: 'Instagram',
      authenticated: authenticated,
      url: window.location.href,
      loginUrl: authenticated ? null : 'https://www.instagram.com/accounts/login/'
    });
  }, 1000);
  
  // Auto-extract on profile page load
  if (document.readyState === 'complete') {
    setTimeout(() => {
      if (isProfilePage() && isAuthenticated()) {
        const profile = extractProfileData();
        sendToBackground('profileDataExtracted', {
          platform: PLATFORM,
          profile: profile
        });
      }
    }, 2000);
  }
  
})();
