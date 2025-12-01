// =============================================================================
// X (TWITTER) CONTENT SCRIPT
// =============================================================================
// Extracts profile information from X/Twitter search results and profile pages.
// =============================================================================

(() => {
  'use strict';
  
  const PLATFORM = 'x';
  
  // X/Twitter-specific CSS selectors
  const SELECTORS = {
    // Search results page
    searchResults: '[data-testid="primaryColumn"]',
    searchResultItem: '[data-testid="UserCell"]',
    searchResultName: '[data-testid="UserCell"] div[dir="ltr"] > span',
    searchResultUsername: '[data-testid="UserCell"] div[dir="ltr"]',
    searchResultLink: 'a[role="link"]',
    searchResultImage: 'img[src*="profile_images"]',
    searchResultBio: '[data-testid="UserCell"] div[dir="auto"]',
    
    // Profile page
    profileHeader: '[data-testid="UserName"]',
    profileName: '[data-testid="UserName"] span',
    profileUsername: '[data-testid="UserName"] div[dir="ltr"]',
    profileImage: 'a[href$="/photo"] img, [data-testid="UserAvatar-Container"] img',
    profileBio: '[data-testid="UserDescription"]',
    profileLocation: '[data-testid="UserProfileHeader_Items"] span[data-testid="UserLocation"]',
    profileWebsite: '[data-testid="UserProfileHeader_Items"] a[href]:not([href*="x.com"]):not([href*="twitter.com"])',
    profileJoinDate: '[data-testid="UserJoinDate"]',
    profileStats: '[data-testid="UserProfileHeader_Items"]',
    
    // Tweet content (for additional data)
    tweetContainer: '[data-testid="tweet"]',
    tweetText: '[data-testid="tweetText"]'
  };
  
  /**
   * Extract profiles from X/Twitter search results
   * @returns {Array} Array of profile objects
   */
  function extractSearchResults() {
    const profiles = [];
    
    try {
      // Find all user cells in search results
      const items = document.querySelectorAll(SELECTORS.searchResultItem);
      
      items.forEach((item, index) => {
        try {
          const profile = {
            index: index + 1,
            platform: 'X (Twitter)',
            platformKey: PLATFORM,
            name: null,
            username: null,
            profileUrl: null,
            profileImage: null,
            bio: null,
            isVerified: false,
            extractedPII: {}
          };
          
          // Extract profile link and username
          const links = item.querySelectorAll(SELECTORS.searchResultLink);
          for (const link of links) {
            const href = link.href;
            if (href && (href.includes('x.com/') || href.includes('twitter.com/')) &&
                !href.includes('/status/') && !href.includes('/search')) {
              profile.profileUrl = href;
              
              // Extract username from URL
              const urlMatch = href.match(/(?:x\.com|twitter\.com)\/([a-zA-Z0-9_]+)/);
              if (urlMatch && !['search', 'explore', 'home', 'notifications', 'messages'].includes(urlMatch[1])) {
                profile.username = urlMatch[1];
                break;
              }
            }
          }
          
          // Extract name and username from text
          const textContent = item.textContent || '';
          const usernameMatch = textContent.match(/@([a-zA-Z0-9_]+)/);
          if (usernameMatch) {
            profile.username = profile.username || usernameMatch[1];
          }
          
          // Try to get display name
          const spans = item.querySelectorAll('span');
          for (const span of spans) {
            const text = span.textContent?.trim();
            if (text && !text.startsWith('@') && text.length > 1 && 
                text.length < 50 && !text.match(/^\d+[KMB]?$/)) {
              if (!profile.name) {
                profile.name = text;
              }
            }
          }
          
          // Extract profile image
          const img = item.querySelector(SELECTORS.searchResultImage);
          if (img && img.src) {
            profile.profileImage = img.src;
          }
          
          // Extract bio
          const bioEl = item.querySelector(SELECTORS.searchResultBio);
          if (bioEl) {
            const bioText = bioEl.textContent?.trim();
            if (bioText && bioText !== profile.name && !bioText.startsWith('@')) {
              profile.bio = bioText;
            }
          }
          
          // Check for verified badge
          const verifiedSvg = item.querySelector('svg[aria-label*="Verified"], svg[data-testid="icon-verified"]');
          if (verifiedSvg) {
            profile.isVerified = true;
          }
          
          // Extract PII from visible text
          profile.extractedPII = extractPII(textContent);
          
          // Only add if we have username
          if (profile.username) {
            profiles.push(profile);
          }
          
        } catch (itemError) {
          console.error('Error extracting X search result:', itemError);
        }
      });
      
    } catch (error) {
      console.error('Error extracting X search results:', error);
    }
    
    return profiles;
  }
  
  /**
   * Extract data from an X/Twitter profile page
   * @returns {Object} Profile data
   */
  function extractProfileData() {
    const profile = {
      platform: 'X (Twitter)',
      platformKey: PLATFORM,
      profileUrl: window.location.href,
      name: null,
      username: null,
      profileImage: null,
      bio: null,
      location: null,
      website: null,
      joinDate: null,
      isVerified: false,
      followers: null,
      following: null,
      tweets: null,
      extractedPII: {}
    };
    
    try {
      // Extract username from URL
      const urlMatch = window.location.pathname.match(/^\/([a-zA-Z0-9_]+)/);
      if (urlMatch && !['search', 'explore', 'home', 'notifications', 'messages', 'settings', 'i'].includes(urlMatch[1])) {
        profile.username = urlMatch[1];
      }
      
      // Extract profile image
      const profileImg = document.querySelector(SELECTORS.profileImage);
      if (profileImg && profileImg.src) {
        profile.profileImage = profileImg.src;
      }
      
      // Extract name from profile header
      const headerEl = document.querySelector(SELECTORS.profileHeader);
      if (headerEl) {
        const spans = headerEl.querySelectorAll('span');
        for (const span of spans) {
          const text = span.textContent?.trim();
          if (text && !text.startsWith('@') && text.length > 1) {
            if (!profile.name) {
              profile.name = text;
              break;
            }
          }
        }
      }
      
      // Fallback: try page title
      if (!profile.name) {
        const title = document.title;
        if (title) {
          const titleMatch = title.match(/^(.+?)\s*(?:\(@|\(|on X|on Twitter)/);
          if (titleMatch) {
            profile.name = titleMatch[1].trim();
          }
        }
      }
      
      // Extract bio
      const bioEl = document.querySelector(SELECTORS.profileBio);
      if (bioEl) {
        profile.bio = bioEl.textContent?.trim();
      }
      
      // Extract location
      const locationEl = document.querySelector(SELECTORS.profileLocation);
      if (locationEl) {
        profile.location = locationEl.textContent?.trim();
      } else {
        // Try to find location in profile header items
        const headerItems = document.querySelector(SELECTORS.profileStats);
        if (headerItems) {
          const spans = headerItems.querySelectorAll('span');
          for (const span of spans) {
            const text = span.textContent?.trim();
            // Location patterns for Sri Lanka
            if (text && (text.includes('Sri Lanka') || text.includes('Colombo') || 
                        text.includes('Kandy') || text.includes('Galle'))) {
              profile.location = text;
              break;
            }
          }
        }
      }
      
      // Extract website
      const websiteEl = document.querySelector(SELECTORS.profileWebsite);
      if (websiteEl) {
        profile.website = websiteEl.href;
      }
      
      // Extract join date
      const joinDateEl = document.querySelector(SELECTORS.profileJoinDate);
      if (joinDateEl) {
        profile.joinDate = joinDateEl.textContent?.trim();
      }
      
      // Check for verified badge
      const verifiedSvg = document.querySelector('[data-testid="UserName"] svg[aria-label*="Verified"]');
      if (verifiedSvg) {
        profile.isVerified = true;
      }
      
      // Extract stats from page
      const pageText = document.body.textContent || '';
      
      const followersMatch = pageText.match(/(\d+[\d,]*[KMB]?)\s*Followers/i);
      if (followersMatch) {
        profile.followers = followersMatch[1];
      }
      
      const followingMatch = pageText.match(/(\d+[\d,]*)\s*Following/i);
      if (followingMatch) {
        profile.following = followingMatch[1];
      }
      
      // Extract PII from bio and visible content
      profile.extractedPII = extractPII(profile.bio || pageText);
      
    } catch (error) {
      console.error('Error extracting X profile data:', error);
    }
    
    return profile;
  }
  
  /**
   * Handle messages from background script
   */
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'extractSearchResults') {
      const results = extractSearchResults();
      sendToBackground('searchResultsExtracted', {
        platform: PLATFORM,
        results: results,
        query: message.query,
        url: window.location.href
      });
      sendResponse({ success: true, count: results.length });
    } else if (message.action === 'extractProfileData') {
      const profile = extractProfileData();
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
