// =============================================================================
// BACKGROUND SERVICE WORKER
// =============================================================================
// Orchestrates deep scan operations across multiple social media platforms.
// Handles communication between content scripts, popup, and backend API.
// =============================================================================

// =============================================================================
// API UTILITIES (inlined to avoid import issues)
// =============================================================================

/**
 * Get the API base URL from storage or use default
 */
async function getApiUrl() {
  try {
    // Try to get from Chrome storage first
    const result = await chrome.storage.sync.get(['apiUrl']);
    if (result.apiUrl) {
      return result.apiUrl;
    }
  } catch (error) {
    console.warn('[API] Failed to get API URL from storage:', error);
  }

  // Default to localhost
  return 'http://localhost:8000';
}

/**
 * Send data to backend API
 */
async function sendToBackend(endpoint, data) {
  const baseUrl = await getApiUrl();
  const url = `${baseUrl}${endpoint}`;

  console.log(`[API] Sending request to: ${url}`, data);

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('[API] Response received:', result);
    return result;

  } catch (error) {
    console.error('[API] Request failed:', error);
    throw error;
  }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

console.log('[Service Worker] Initializing...');

// Wait for chrome APIs to be available
function initializeServiceWorker() {
  if (typeof chrome === 'undefined') {
    console.error('[Service Worker] Chrome APIs not available!');
    return;
  }

  console.log('[Service Worker] Chrome APIs available');

  if (chrome.tabs) {
    console.log('[Service Worker] chrome.tabs API available');
  } else {
    console.error('[Service Worker] chrome.tabs API not available!');
  }

  if (chrome.runtime) {
    console.log('[Service Worker] chrome.runtime API available');
  } else {
    console.error('[Service Worker] chrome.runtime API not available!');
  }

  if (chrome.storage) {
    console.log('[Service Worker] chrome.storage API available');
  } else {
    console.error('[Service Worker] chrome.storage API not available!');
  }
}

// Initialize immediately or wait for chrome to be ready
console.log('[Service Worker] Starting...');

// =============================================================================
// CONSTANTS
// =============================================================================

const SUPPORTED_PLATFORMS = {
  facebook: {
    name: 'Facebook',
    emoji: '📘',
    searchUrlPattern: 'https://www.facebook.com/search/people/?q=',
    profileUrlPattern: /facebook\.com\/(?!search|login|help|groups|pages|marketplace|watch|gaming|events)([a-zA-Z0-9.]+)/
  },
  instagram: {
    name: 'Instagram',
    emoji: '📷',
    // Instagram search requires login - use web search interface
    searchUrlPattern: 'https://www.instagram.com/web/search/topsearch/?query=',
    profileUrlPattern: /instagram\.com\/([a-zA-Z0-9._]+)/
  },
  linkedin: {
    name: 'LinkedIn',
    emoji: '💼',
    searchUrlPattern: 'https://www.linkedin.com/search/results/people/?keywords=',
    profileUrlPattern: /linkedin\.com\/in\/([a-zA-Z0-9-]+)/
  },
  x: {
    name: 'X (Twitter)',
    emoji: '𝕏',
    // Use x.com without www
    searchUrlPattern: 'https://x.com/search?q=',
    searchSuffix: '&f=user',  // Filter to show users only
    profileUrlPattern: /(?:x\.com|twitter\.com)\/([a-zA-Z0-9_]+)/
  }
};

// Timeout constants - increased for SPA page loads
const PAGE_LOAD_TIMEOUT = 5000;   // 5 seconds for page to load
const EXTRACTION_TIMEOUT = 15000; // 15 seconds for content extraction

// Scan state management
let currentScan = null;
let scanResults = {};

// Keep-alive mechanism to prevent service worker from going inactive
let keepAliveInterval = null;

function startKeepAlive() {
  if (keepAliveInterval) return; // Already running

  console.log('[Service Worker] Starting keep-alive');
  keepAliveInterval = setInterval(() => {
    // Ping runtime to keep worker alive
    chrome.runtime.getPlatformInfo(() => {
      console.log('[Service Worker] Keep-alive ping');
      if (chrome.runtime.lastError) {
        console.error('[Service Worker] Keep-alive error:', chrome.runtime.lastError);
      }
    });
  }, 20000); // Every 20 seconds
}

function stopKeepAlive() {
  if (keepAliveInterval) {
    console.log('[Service Worker] Stopping keep-alive');
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

// =============================================================================
// MESSAGE HANDLERS
// =============================================================================

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  try {
    // Check if chrome APIs are available
    if (!chrome || !chrome.runtime) {
      console.error('[Service Worker] Chrome runtime not available');
      sendResponse({ success: false, error: 'Extension context not available' });
      return true;
    }

    // Use async wrapper for proper response handling
    handleMessage(message, sender).then(sendResponse).catch(error => {
      console.error('Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    });

    // Return true to indicate async response
    return true;
  } catch (error) {
    console.error('[Service Worker] Error in message listener:', error);
    sendResponse({ success: false, error: 'Internal extension error' });
    return true;
  }
});

/**
 * Handle messages from web app (external)
 */
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  try {
    console.log('[Extension] Received message from web app:', message);

    if (message.action === 'checkExtension') {
      // Web app checking if extension is installed
      sendResponse({
        installed: true,
        version: chrome.runtime.getManifest().version,
        ready: true
      });
      return true;
    }

    if (message.action === 'startDeepScan') {
      // Web app requesting a deep scan
      handleMessage(message, sender)
        .then(result => {
          sendResponse({ success: true, data: result });
        })
        .catch(error => {
          sendResponse({ success: false, error: error.message });
        });
      return true; // Will respond asynchronously
    }

    return false;
  } catch (error) {
    console.error('[Service Worker] Error in external message listener:', error);
    sendResponse({ success: false, error: 'Internal extension error' });
    return true;
  }
});

/**
 * Async message handler
 */
async function handleMessage(message, sender) {
  switch (message.action) {
    case 'startDeepScan':
      return await startDeepScan(message.data);

    case 'getScanStatus':
      return getScanStatus();

    case 'cancelScan':
      return cancelScan();

    case 'profileDataExtracted':
      console.log('[Background] Received profile data:', message.data);
      return handleProfileData(message.data, sender);

    case 'searchResultsExtracted':
      console.log('[Background] Received search results:', message.data);
      return handleSearchResults(message.data, sender);

    case 'getApiUrl':
      return { success: true, url: await getApiUrl() };

    case 'sendToBackend':
      return await sendToBackend(message.endpoint, message.data);

    // Guided Login Flow Actions
    case 'checkAuthStatus':
      return { success: true, authStatus: await checkAuthStatus(message.data?.platforms) };

    case 'openLoginTab':
      return await openLoginTab(message.data?.platform);

    case 'startGuidedLogin':
      return await startGuidedLogin(message.data?.platforms);

    case 'waitForLogin':
      return await waitForLogin(message.data?.platform, message.data?.timeout);

    case 'authStatusUpdate':
      return handleAuthStatusUpdate(message.data);

    default:
      return { success: false, error: 'Unknown action' };
  }
}

// =============================================================================
// DEEP SCAN ORCHESTRATION
// =============================================================================

/**
 * Start a deep scan for the given identifier
 * @param {Object} data - Scan parameters
 * @param {string} data.identifierType - Type of identifier (name, email, username)
 * @param {string} data.identifierValue - The identifier value to search
 * @param {string[]} data.platforms - Platforms to scan
 * @returns {Object} Scan initiation result
 */
async function startDeepScan(data) {
  const { identifierType, identifierValue, platforms } = data;

  if (!identifierValue) {
    return { success: false, error: 'Identifier value is required' };
  }

  if (currentScan && currentScan.status === 'in_progress') {
    return { success: false, error: 'A scan is already in progress' };
  }

  // Initialize scan state
  currentScan = {
    id: generateScanId(),
    identifierType: identifierType || 'username',
    identifierValue,
    platforms: platforms || Object.keys(SUPPORTED_PLATFORMS),
    status: 'in_progress',
    startTime: Date.now(),
    progress: 0,
    currentPlatform: null,
    completedPlatforms: [],
    results: {}
  };

  scanResults = {};

  // Start keep-alive mechanism
  startKeepAlive();

  try {
    // Notify popup of scan start
    notifyPopup('scanStarted', { scanId: currentScan.id });

    // Start scanning platforms in parallel for faster results
    const scanPromises = currentScan.platforms.map(async (platform) => {
      try {
        await scanPlatform(platform, identifierValue, identifierType);
        return { platform, success: true };
      } catch (error) {
        console.error(`[Scan] Platform ${platform} failed:`, error);
        return { platform, success: false, error: error.message };
      }
    });

    // Wait for all platforms to complete (with individual timeouts)
    const results = await Promise.allSettled(scanPromises);

    // Log any failures
    results.forEach((result, index) => {
      if (result.status === 'rejected' || (result.value && !result.value.success)) {
        console.warn(`[Scan] Platform ${currentScan.platforms[index]} encountered issues`);
      }
    });

    // Mark all platforms as completed
    currentScan.completedPlatforms = [...currentScan.platforms];
    currentScan.progress = 100;

    // Finalize scan
    if (currentScan.status === 'in_progress') {
      currentScan.status = 'completed';
      currentScan.endTime = Date.now();
      currentScan.results = scanResults;

      // Send results to backend
      try {
        const backendResponse = await sendToBackend('/api/deep-scan/analyze', {
          scan_id: currentScan.id,
          identifier_type: currentScan.identifierType,
          identifier_value: currentScan.identifierValue,
          platforms_scanned: currentScan.completedPlatforms,
          results: scanResults,
          scan_duration_ms: currentScan.endTime - currentScan.startTime
        });

        currentScan.backendAnalysis = backendResponse;
      } catch (error) {
        console.error('Failed to send results to backend:', error);
        currentScan.backendError = error.message;
      }

      // Notify popup of completion
      notifyPopup('scanCompleted', {
        scanId: currentScan.id,
        results: currentScan.results,
        analysis: currentScan.backendAnalysis
      });

      // Notify web app of completion
      notifyWebApp('scanCompleted', {
        results: currentScan.backendAnalysis || currentScan.results
      });
    }

  } finally {
    // Always stop keep-alive when scan ends
    stopKeepAlive();
  }

  return { success: true, scanId: currentScan.id };
}

/**
 * Scan a specific platform for the identifier
 * @param {string} platform - Platform key
 * @param {string} identifier - Value to search
 * @param {string} identifierType - Type of identifier
 */
async function scanPlatform(platform, identifier, identifierType) {
  const platformConfig = SUPPORTED_PLATFORMS[platform];
  if (!platformConfig) return;

  console.log(`[Scan] Starting scan for ${platform} with identifier: ${identifier}`);

  // Build search query based on identifier type
  let searchQuery = identifier;
  if (identifierType === 'email') {
    // Extract username part of email for searching
    searchQuery = identifier.split('@')[0];
  }
  // Note: Names will be URL-encoded when building the search URL

  // Initialize platform results
  scanResults[platform] = {
    platform: platformConfig.name,
    emoji: platformConfig.emoji,
    status: 'scanning',
    profiles: [],
    searchResults: [],
    errors: [],
    startTime: Date.now()
  };

  // Notify web app that platform scan started
  notifyWebApp('platformStarted', {
    platform: platformConfig.name,
    platformKey: platform,
    emoji: platformConfig.emoji
  });

  // Notify popup about platform scan start
  notifyPopup('platformScanStarted', {
    platform,
    platformName: platformConfig.name,
    emoji: platformConfig.emoji
  });

  let tab = null;

  try {
    // Always use search URLs for reliable results
    // Direct profile URLs often fail due to authentication or redirects
    let searchUrl = platformConfig.searchUrlPattern + encodeURIComponent(searchQuery);

    // Add platform-specific search suffixes (e.g., X user filter)
    if (platformConfig.searchSuffix) {
      searchUrl += platformConfig.searchSuffix;
    }

    console.log(`[Scan] Using search URL for ${platform}: ${searchUrl}`);

    // Create new tab in background (not active)
    if (!chrome.tabs || !chrome.tabs.create) {
      throw new Error('chrome.tabs.create API not available');
    }

    tab = await chrome.tabs.create({
      url: searchUrl,
      active: false
    });

    console.log(`[Scan] Tab created for ${platform}, ID: ${tab.id}`);

    // Wait for page to fully load (SPAs need more time)
    await new Promise(resolve => setTimeout(resolve, PAGE_LOAD_TIMEOUT));

    // Inject content scripts dynamically for reliable execution
    // This ensures scripts run even when tabs are created programmatically
    try {
      if (chrome.scripting && chrome.scripting.executeScript) {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content/shared.js']
        });
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: [`content/${platform}.js`]
        });
        console.log(`[Scan] Injected content scripts for ${platform}`);

        // Give scripts time to initialize
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } catch (injectError) {
      console.warn(`[Scan] Could not inject scripts for ${platform}:`, injectError.message);
      // Continue anyway - manifest content scripts may have loaded
    }

    // Send extraction message to content script
    const messageAction = 'extractSearchResults';
    console.log(`[Scan] Sending ${messageAction} message to tab ${tab.id}`);

    if (!chrome.tabs || !chrome.tabs.sendMessage) {
      throw new Error('chrome.tabs.sendMessage API not available');
    }

    try {
      await chrome.tabs.sendMessage(tab.id, {
        action: messageAction,
        query: identifier,
        identifierType
      });
    } catch (msgError) {
      console.warn(`[Scan] Message failed for ${platform}:`, msgError.message);

      // Notify web app about the issue
      notifyWebApp('platformError', {
        platform: platformConfig.name,
        platformKey: platform,
        error: `Content script not responding. Please ensure you are logged into ${platformConfig.name}.`,
        requiresAuth: true
      });
    }

    // Wait for content script to extract and send results
    await waitForPlatformResults(platform, EXTRACTION_TIMEOUT);

  } catch (error) {
    console.error(`[Scan] Error scanning ${platform}:`, error);
    scanResults[platform].status = 'error';
    scanResults[platform].errors.push(error.message);

    // Notify web app of the error
    notifyWebApp('platformError', {
      platform: platformConfig.name,
      platformKey: platform,
      error: error.message
    });
  } finally {
    // Always close the tab after extraction, even if there was an error
    if (tab && tab.id) {
      try {
        await chrome.tabs.remove(tab.id);
        console.log(`[Scan] Closed tab for ${platform}`);
      } catch (closeError) {
        console.warn(`[Scan] Could not close tab for ${platform}:`, closeError);
      }
    }
  }

  // Mark as completed if still scanning
  if (scanResults[platform].status === 'scanning') {
    scanResults[platform].status = 'completed';
  }

  // Calculate duration
  scanResults[platform].endTime = Date.now();
  scanResults[platform].duration = scanResults[platform].endTime - scanResults[platform].startTime;

  // Notify web app that platform scan completed
  notifyWebApp('platformCompleted', {
    platform: platformConfig.name,
    platformKey: platform,
    emoji: platformConfig.emoji,
    count: scanResults[platform].profiles.length + scanResults[platform].searchResults.length,
    duration: scanResults[platform].duration,
    status: scanResults[platform].status
  });

  // Notify popup about platform scan completion
  notifyPopup('platformScanCompleted', {
    platform,
    platformName: platformConfig.name,
    emoji: platformConfig.emoji,
    status: scanResults[platform].status,
    profilesFound: scanResults[platform].profiles.length,
    searchResultsFound: scanResults[platform].searchResults.length
  });

  // Update global scan progress for parallel execution
  if (currentScan) {
    currentScan.completedPlatforms = Object.keys(scanResults).filter(p =>
      scanResults[p].status === 'completed' || scanResults[p].status === 'timeout'
    );
    currentScan.progress = (currentScan.completedPlatforms.length / currentScan.platforms.length) * 100;

    // Notify popup of overall progress
    notifyPopup('scanProgress', {
      platform,
      progress: currentScan.progress,
      completedPlatforms: currentScan.completedPlatforms
    });
  }

  console.log(`[Scan] Completed ${platform} scan in ${scanResults[platform].duration}ms`);
}

/**
 * Wait for platform results with timeout
 */
function waitForPlatformResults(platform, timeout) {
  return new Promise((resolve) => {
    const startTime = Date.now();

    const checkResults = () => {
      const elapsed = Date.now() - startTime;

      if (scanResults[platform]?.status !== 'scanning') {
        console.log(`[Scan] ${platform} results received after ${elapsed}ms`);
        resolve();
        return;
      }

      if (elapsed > timeout) {
        console.warn(`[Scan] ${platform} timed out after ${elapsed}ms`);
        scanResults[platform].status = 'timeout';
        scanResults[platform].errors.push(`Extraction timed out after ${Math.round(timeout / 1000)}s`);
        resolve();
        return;
      }

      setTimeout(checkResults, 200);
    };

    checkResults();
  });
}

/**
 * Handle extracted profile data from content scripts
 */
function handleProfileData(data, sender) {
  const { platform, profile } = data;

  if (!scanResults[platform]) {
    scanResults[platform] = {
      platform: SUPPORTED_PLATFORMS[platform]?.name || platform,
      emoji: SUPPORTED_PLATFORMS[platform]?.emoji || '🔍',
      status: 'completed',
      profiles: [],
      searchResults: [],
      errors: []
    };
  }

  scanResults[platform].profiles.push(profile);
  scanResults[platform].status = 'completed';

  return { success: true };
}

/**
 * Handle extracted search results from content scripts
 */
function handleSearchResults(data, sender) {
  const { platform, results } = data;

  if (!scanResults[platform]) {
    scanResults[platform] = {
      platform: SUPPORTED_PLATFORMS[platform]?.name || platform,
      emoji: SUPPORTED_PLATFORMS[platform]?.emoji || '🔍',
      status: 'completed',
      profiles: [],
      searchResults: [],
      errors: []
    };
  }

  scanResults[platform].searchResults = results;
  scanResults[platform].status = 'completed';

  return { success: true };
}

// =============================================================================
// SCAN STATUS & CONTROL
// =============================================================================

/**
 * Get current scan status
 */
function getScanStatus() {
  if (!currentScan) {
    return { success: true, status: 'idle', scan: null };
  }

  return {
    success: true,
    status: currentScan.status,
    scan: {
      id: currentScan.id,
      identifierType: currentScan.identifierType,
      identifierValue: currentScan.identifierValue,
      platforms: currentScan.platforms,
      progress: currentScan.progress,
      currentPlatform: currentScan.currentPlatform,
      completedPlatforms: currentScan.completedPlatforms,
      results: currentScan.status === 'completed' ? currentScan.results : null,
      analysis: currentScan.backendAnalysis
    }
  };
}

/**
 * Cancel the current scan
 */
function cancelScan() {
  if (!currentScan || currentScan.status !== 'in_progress') {
    return { success: false, error: 'No scan in progress' };
  }

  currentScan.status = 'cancelled';
  currentScan.endTime = Date.now();

  // Stop keep-alive when scan is cancelled
  stopKeepAlive();

  notifyPopup('scanCancelled', { scanId: currentScan.id });

  return { success: true };
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Generate a unique scan ID
 */
function generateScanId() {
  return 'DS-' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substring(2, 7).toUpperCase();
}

/**
 * Send notification to popup and web app
 */
function notifyPopup(event, data) {
  // Send to extension popup
  if (chrome.runtime && chrome.runtime.sendMessage) {
    chrome.runtime.sendMessage({ event, data }).catch(() => {
      // Popup might be closed, ignore error
    });
  }

  // Send to web app content script
  if (chrome.tabs && chrome.tabs.query && chrome.tabs.sendMessage) {
    chrome.tabs.query({ url: ['http://localhost:3000/*', 'http://localhost:*/*'] }).then(tabs => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, { event, data }).catch(() => {
          // Content script might not be loaded, ignore error
        });
      });
    }).catch(err => {
      console.warn('Could not query web app tabs:', err);
    });
  }
}

/**
 * Send notification specifically to web app
 */
function notifyWebApp(event, data) {
  // Send to web app content script
  if (chrome.tabs && chrome.tabs.query && chrome.tabs.sendMessage) {
    chrome.tabs.query({ url: ['http://localhost:3000/*', 'http://localhost:*/*'] }).then(tabs => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          action: 'webappEvent',
          event,
          data
        }).catch((error) => {
          console.warn(`Could not send event to web app tab ${tab.id}:`, error.message);
        });
      });
    }).catch(err => {
      console.warn('Could not query web app tabs:', err);
    });
  }
}

// =============================================================================
// GUIDED LOGIN FLOW
// =============================================================================

// Platform login URLs
const PLATFORM_LOGIN_URLS = {
  facebook: 'https://www.facebook.com/',
  instagram: 'https://www.instagram.com/',
  linkedin: 'https://www.linkedin.com/login',
  x: 'https://x.com/'
};

// Track login tabs for guided flow
let loginTabs = {};
let authStatusCache = {};

/**
 * Check auth status for multiple platforms
 * @param {string[]} platforms - List of platforms to check
 * @returns {Object} Auth status for each platform
 */
async function checkAuthStatus(platforms) {
  const platformList = platforms || Object.keys(SUPPORTED_PLATFORMS);
  const results = {};

  console.log('[Auth] Checking auth status for:', platformList);

  for (const platform of platformList) {
    try {
      results[platform] = await checkPlatformAuth(platform);
    } catch (error) {
      console.error(`[Auth] Error checking ${platform}:`, error);
      results[platform] = { isLoggedIn: false, error: error.message };
    }
  }

  console.log('[Auth] Auth status results:', results);
  return results;
}

/**
 * Check if user is logged into a specific platform
 * @param {string} platform - Platform key
 * @returns {Object} Auth status
 */
async function checkPlatformAuth(platform) {
  const loginUrl = PLATFORM_LOGIN_URLS[platform];
  if (!loginUrl) {
    return { isLoggedIn: false, error: 'Unknown platform' };
  }

  // Check cache first (valid for 30 seconds)
  const cached = authStatusCache[platform];
  if (cached && Date.now() - cached.timestamp < 30000) {
    console.log(`[Auth] Using cached status for ${platform}:`, cached.isLoggedIn);
    return cached;
  }

  let tab = null;
  try {
    // Create tab in background to check auth
    tab = await chrome.tabs.create({
      url: loginUrl,
      active: false
    });

    console.log(`[Auth] Created tab ${tab.id} to check ${platform}`);

    // Wait for page to load
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Inject auth detector and check status
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content/auth-detector.js']
      });
    } catch (injectError) {
      console.warn(`[Auth] Could not inject script for ${platform}:`, injectError.message);
    }

    // Give script time to initialize
    await new Promise(resolve => setTimeout(resolve, 500));

    // Request auth status from content script
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'getAuthStatus' });

    const result = {
      platform,
      isLoggedIn: response?.isLoggedIn || false,
      timestamp: Date.now()
    };

    // Cache result
    authStatusCache[platform] = result;

    console.log(`[Auth] ${platform} auth status:`, result.isLoggedIn);
    return result;

  } catch (error) {
    console.error(`[Auth] Error checking ${platform}:`, error);
    return { platform, isLoggedIn: false, error: error.message };
  } finally {
    // Close the check tab
    if (tab?.id) {
      try {
        await chrome.tabs.remove(tab.id);
      } catch (e) {
        // Tab may already be closed
      }
    }
  }
}

/**
 * Open login tab for a specific platform
 * @param {string} platform - Platform key
 * @returns {Object} Tab info
 */
async function openLoginTab(platform) {
  const loginUrl = PLATFORM_LOGIN_URLS[platform];
  if (!loginUrl) {
    return { success: false, error: 'Unknown platform' };
  }

  console.log(`[Auth] Opening login tab for ${platform}`);

  // Close existing login tab for this platform if any
  if (loginTabs[platform]) {
    try {
      await chrome.tabs.remove(loginTabs[platform]);
    } catch (e) {
      // Tab may not exist
    }
  }

  // Open login page in foreground
  const tab = await chrome.tabs.create({
    url: loginUrl,
    active: true  // Make it active so user can log in
  });

  loginTabs[platform] = tab.id;

  // Clear cached auth status for this platform
  delete authStatusCache[platform];

  return {
    success: true,
    tabId: tab.id,
    platform,
    loginUrl
  };
}

/**
 * Wait for login to complete on a platform
 * @param {string} platform - Platform key
 * @param {number} timeout - Timeout in ms
 * @returns {Promise<boolean>} Whether login completed
 */
function waitForLogin(platform, timeout = 120000) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const checkInterval = 3000; // Check every 3 seconds

    const checkAuth = async () => {
      const elapsed = Date.now() - startTime;

      if (elapsed > timeout) {
        console.log(`[Auth] Login timeout for ${platform}`);
        resolve({ success: false, reason: 'timeout' });
        return;
      }

      // Check if tab still exists
      const tabId = loginTabs[platform];
      if (tabId) {
        try {
          const tab = await chrome.tabs.get(tabId);

          // Try to check auth status
          try {
            const response = await chrome.tabs.sendMessage(tabId, { action: 'getAuthStatus' });
            if (response?.isLoggedIn) {
              console.log(`[Auth] Login completed for ${platform}`);

              // Update cache
              authStatusCache[platform] = {
                platform,
                isLoggedIn: true,
                timestamp: Date.now()
              };

              // Notify web app
              notifyWebApp('authSuccess', { platform, isLoggedIn: true });

              resolve({ success: true, platform });
              return;
            }
          } catch (e) {
            // Content script not ready, will retry
          }
        } catch (e) {
          // Tab closed, user cancelled
          console.log(`[Auth] Login tab closed for ${platform}`);
          delete loginTabs[platform];
          resolve({ success: false, reason: 'cancelled' });
          return;
        }
      }

      // Schedule next check
      setTimeout(checkAuth, checkInterval);
    };

    // Start checking
    checkAuth();
  });
}

/**
 * Start guided login flow for multiple platforms
 * @param {string[]} platforms - Platforms that need login
 * @returns {Object} Result
 */
async function startGuidedLogin(platforms) {
  console.log('[Auth] Starting guided login for:', platforms);

  // Notify web app that guided login is starting
  notifyWebApp('guidedLoginStarted', { platforms });

  // Open first platform
  if (platforms.length > 0) {
    await openLoginTab(platforms[0]);
  }

  return {
    success: true,
    platforms,
    message: 'Please log into the displayed platform(s)'
  };
}

/**
 * Handle auth status update from content script
 */
function handleAuthStatusUpdate(data) {
  const { platform, isLoggedIn } = data;

  if (platform && isLoggedIn) {
    // Update cache
    authStatusCache[platform] = {
      platform,
      isLoggedIn,
      timestamp: Date.now()
    };

    // Notify web app
    notifyWebApp('authSuccess', { platform, isLoggedIn: true });

    console.log(`[Auth] ${platform} login detected`);
  }

  return { success: true };
}

// =============================================================================
// EXTENSION LIFECYCLE
// =============================================================================

/**
 * Handle extension installation/update
 */
chrome.runtime.onInstalled.addListener((details) => {
  try {
    console.log('[Service Worker] Installed, checking APIs...');
    // Simple API check
    if (typeof chrome !== 'undefined') {
      console.log('[Service Worker] Chrome APIs available');
      if (chrome.tabs) console.log('[Service Worker] tabs API available');
      if (chrome.runtime) console.log('[Service Worker] runtime API available');
      if (chrome.storage) console.log('[Service Worker] storage API available');
    }

    if (details.reason === 'install') {
      console.log('Digital Footprint Analyzer extension installed');
      // Set default settings
      if (chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({
          apiUrl: 'http://localhost:8000',
          enableNotifications: true
        });
      }
    } else if (details.reason === 'update') {
      console.log('Digital Footprint Analyzer extension updated to version', chrome.runtime.getManifest().version);
    }
  } catch (error) {
    console.error('[Service Worker] Error in onInstalled listener:', error);
  }
});

/**
 * Keep service worker alive during scans (simplified)
 */
console.log('[Service Worker] Alarm system disabled for stability');
