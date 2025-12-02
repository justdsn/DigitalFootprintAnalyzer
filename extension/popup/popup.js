// =============================================================================
// POPUP SCRIPT
// =============================================================================
// Main JavaScript for the extension popup UI.
// Handles user interactions and communicates with the background service worker.
// =============================================================================

// =============================================================================
// CONSTANTS
// =============================================================================

const PLATFORMS = {
  facebook: { name: 'Facebook', emoji: '📘' },
  instagram: { name: 'Instagram', emoji: '📷' },
  linkedin: { name: 'LinkedIn', emoji: '💼' },
  x: { name: 'X (Twitter)', emoji: '𝕏' }
};

// Configuration URLs
const HELP_URL = 'https://github.com/justdsn/DigitalFootprintAnalyzer#readme';
const DEFAULT_API_PORT = 8000;
const DEFAULT_FRONTEND_PORT = 3000;

// =============================================================================
// DOM ELEMENTS
// =============================================================================

const elements = {
  // Status
  statusIndicator: document.getElementById('statusIndicator'),
  apiStatus: document.getElementById('apiStatus'),
  
  // Form
  scanForm: document.getElementById('scanForm'),
  identifierType: document.getElementById('identifierType'),
  identifierValue: document.getElementById('identifierValue'),
  startScanBtn: document.getElementById('startScanBtn'),
  
  // Progress
  scanProgress: document.getElementById('scanProgress'),
  progressFill: document.getElementById('progressFill'),
  progressText: document.getElementById('progressText'),
  platformStatus: document.getElementById('platformStatus'),
  cancelScanBtn: document.getElementById('cancelScanBtn'),
  
  // Results
  scanResults: document.getElementById('scanResults'),
  resultsSummary: document.getElementById('resultsSummary'),
  resultsDetails: document.getElementById('resultsDetails'),
  newScanBtn: document.getElementById('newScanBtn'),
  viewReportBtn: document.getElementById('viewReportBtn'),
  downloadReportBtn: document.getElementById('downloadReportBtn'),
  
  // Error
  scanError: document.getElementById('scanError'),
  errorTitle: document.getElementById('errorTitle'),
  errorMessage: document.getElementById('errorMessage'),
  retryBtn: document.getElementById('retryBtn'),
  
  // Settings Modal
  settingsLink: document.getElementById('settingsLink'),
  settingsModal: document.getElementById('settingsModal'),
  closeSettingsBtn: document.getElementById('closeSettingsBtn'),
  apiUrl: document.getElementById('apiUrl'),
  enableNotifications: document.getElementById('enableNotifications'),
  saveSettingsBtn: document.getElementById('saveSettingsBtn'),
  
  // Help
  helpLink: document.getElementById('helpLink')
};

// =============================================================================
// STATE
// =============================================================================

let currentScan = null;
let lastResults = null;

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', async () => {
  // Display extension ID
  const extensionId = chrome.runtime.id;
  document.getElementById('extensionId').textContent = extensionId;
  
  // Copy extension ID button
  document.getElementById('copyIdBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(extensionId).then(() => {
      const btn = document.getElementById('copyIdBtn');
      const originalText = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('copied');
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy:', err);
      alert('Failed to copy. Please select and copy manually.');
    });
  });
  
  // Load settings
  await loadSettings();
  
  // Check API status
  await checkApiStatus();
  
  // Check for existing scan
  await checkExistingScan();
  
  // Set up event listeners
  setupEventListeners();
  
  // Update placeholder based on identifier type
  updatePlaceholder();
});

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
  // Form events
  elements.identifierType.addEventListener('change', updatePlaceholder);
  elements.startScanBtn.addEventListener('click', startScan);
  
  // Progress events
  elements.cancelScanBtn.addEventListener('click', cancelScan);
  
  // Results events
  elements.newScanBtn.addEventListener('click', showScanForm);
  elements.viewReportBtn.addEventListener('click', viewFullReport);
  elements.downloadReportBtn.addEventListener('click', downloadReport);
  
  // Error events
  elements.retryBtn.addEventListener('click', showScanForm);
  
  // Settings events
  elements.settingsLink.addEventListener('click', (e) => {
    e.preventDefault();
    showSettingsModal();
  });
  elements.closeSettingsBtn.addEventListener('click', hideSettingsModal);
  elements.saveSettingsBtn.addEventListener('click', saveSettings);
  
  // Help link
  elements.helpLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: HELP_URL });
  });
  
  // Listen for messages from background
  chrome.runtime.onMessage.addListener(handleBackgroundMessage);
}

// =============================================================================
// SCAN FUNCTIONS
// =============================================================================

async function startScan() {
  const identifierType = elements.identifierType.value;
  const identifierValue = elements.identifierValue.value.trim();
  
  // Validate input
  if (!identifierValue) {
    showError('Input Required', 'Please enter a value to search for.');
    return;
  }
  
  // Get selected platforms
  const platforms = Array.from(document.querySelectorAll('input[name="platform"]:checked'))
    .map(cb => cb.value);
  
  if (platforms.length === 0) {
    showError('No Platforms Selected', 'Please select at least one platform to scan.');
    return;
  }
  
  // Show progress section
  showProgress();
  
  // Initialize platform status
  initializePlatformStatus(platforms);
  
  // Send scan request to background
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'startDeepScan',
      data: {
        identifierType,
        identifierValue,
        platforms
      }
    });
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to start scan');
    }
    
    currentScan = {
      id: response.scanId,
      identifierType,
      identifierValue,
      platforms
    };
    
  } catch (error) {
    console.error('Error starting scan:', error);
    showError('Scan Failed', error.message);
  }
}

async function cancelScan() {
  try {
    await chrome.runtime.sendMessage({ action: 'cancelScan' });
    showScanForm();
  } catch (error) {
    console.error('Error cancelling scan:', error);
  }
}

async function checkExistingScan() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getScanStatus' });
    
    if (response.success && response.status === 'in_progress') {
      // Resume showing progress for existing scan
      currentScan = response.scan;
      showProgress();
      initializePlatformStatus(response.scan.platforms);
      updateProgress(response.scan.progress, `Scanning ${response.scan.currentPlatform}...`);
      
      // Update completed platforms
      response.scan.completedPlatforms.forEach(platform => {
        updatePlatformStatus(platform, 'completed');
      });
      
      if (response.scan.currentPlatform) {
        updatePlatformStatus(response.scan.currentPlatform, 'scanning');
      }
      
    } else if (response.success && response.status === 'completed' && response.scan?.results) {
      // Show results from completed scan
      lastResults = response.scan.results;
      showResults(response.scan.results, response.scan.analysis);
    }
  } catch (error) {
    console.error('Error checking existing scan:', error);
  }
}

// =============================================================================
// UI FUNCTIONS
// =============================================================================

function showScanForm() {
  elements.scanForm.classList.remove('hidden');
  elements.scanProgress.classList.add('hidden');
  elements.scanResults.classList.add('hidden');
  elements.scanError.classList.add('hidden');
  updateStatusIndicator('Ready', 'ready');
}

function showProgress() {
  elements.scanForm.classList.add('hidden');
  elements.scanProgress.classList.remove('hidden');
  elements.scanResults.classList.add('hidden');
  elements.scanError.classList.add('hidden');
  updateStatusIndicator('Scanning...', 'scanning');
}

function showResults(results, analysis) {
  elements.scanForm.classList.add('hidden');
  elements.scanProgress.classList.add('hidden');
  elements.scanResults.classList.remove('hidden');
  elements.scanError.classList.add('hidden');
  updateStatusIndicator('Complete', 'ready');
  
  renderResults(results, analysis);
}

function showError(title, message) {
  elements.scanForm.classList.add('hidden');
  elements.scanProgress.classList.add('hidden');
  elements.scanResults.classList.add('hidden');
  elements.scanError.classList.remove('hidden');
  
  elements.errorTitle.textContent = title;
  elements.errorMessage.textContent = message;
  
  updateStatusIndicator('Error', 'error');
}

function updateStatusIndicator(text, state) {
  const dot = elements.statusIndicator.querySelector('.status-dot');
  const textEl = elements.statusIndicator.querySelector('.status-text');
  
  dot.classList.remove('scanning', 'error');
  if (state === 'scanning') dot.classList.add('scanning');
  if (state === 'error') dot.classList.add('error');
  
  textEl.textContent = text;
}

function updateProgress(percent, text) {
  elements.progressFill.style.width = `${percent}%`;
  elements.progressText.textContent = text;
}

function initializePlatformStatus(platforms) {
  elements.platformStatus.innerHTML = platforms.map(platform => `
    <div class="platform-status-item" data-platform="${platform}">
      <span class="emoji">${PLATFORMS[platform]?.emoji || '🔍'}</span>
      <span class="name">${PLATFORMS[platform]?.name || platform}</span>
      <span class="status pending">Pending</span>
    </div>
  `).join('');
}

function updatePlatformStatus(platform, status) {
  const item = elements.platformStatus.querySelector(`[data-platform="${platform}"]`);
  if (item) {
    const statusEl = item.querySelector('.status');
    statusEl.className = `status ${status}`;
    statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
  }
}

function updatePlaceholder() {
  const type = elements.identifierType.value;
  const placeholders = {
    username: 'e.g., john_doe',
    name: 'e.g., John Perera',
    email: 'e.g., john@example.com'
  };
  elements.identifierValue.placeholder = placeholders[type] || 'Enter value';
}

function renderResults(results, analysis) {
  // Calculate summary
  let totalProfiles = 0;
  let totalPII = 0;
  let platformsWithResults = 0;
  
  Object.values(results).forEach(platformResult => {
    if (platformResult.profiles?.length > 0 || platformResult.searchResults?.length > 0) {
      platformsWithResults++;
      totalProfiles += (platformResult.profiles?.length || 0) + (platformResult.searchResults?.length || 0);
    }
    if (platformResult.profiles) {
      platformResult.profiles.forEach(profile => {
        const pii = profile.extractedPII || {};
        totalPII += (pii.emails?.length || 0) + (pii.phones?.length || 0);
      });
    }
  });
  
  // Render summary
  elements.resultsSummary.innerHTML = `
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-value">${totalProfiles}</div>
        <div class="summary-label">Profiles Found</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">${platformsWithResults}</div>
        <div class="summary-label">Platforms</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">${totalPII}</div>
        <div class="summary-label">PII Items</div>
      </div>
      <div class="summary-item">
        <div class="summary-value">${analysis?.risk_score || '-'}</div>
        <div class="summary-label">Risk Score</div>
      </div>
    </div>
  `;
  
  // Render detailed results
  let detailsHtml = '';
  
  Object.entries(results).forEach(([platformKey, platformResult]) => {
    const profiles = [...(platformResult.profiles || []), ...(platformResult.searchResults || [])];
    if (profiles.length === 0) return;
    
    detailsHtml += `
      <div class="result-platform">
        <div class="result-platform-header">
          <span class="emoji">${platformResult.emoji || PLATFORMS[platformKey]?.emoji || '🔍'}</span>
          <span class="name">${platformResult.platform || PLATFORMS[platformKey]?.name || platformKey}</span>
          <span class="count">${profiles.length} found</span>
        </div>
        <div class="result-profiles">
          ${profiles.slice(0, 5).map(profile => `
            <div class="result-profile">
              ${profile.profileImage 
                ? `<img src="${profile.profileImage}" class="result-profile-image" alt="">`
                : '<div class="result-profile-image"></div>'
              }
              <div class="result-profile-info">
                <div class="result-profile-name">${profile.name || 'Unknown'}</div>
                <div class="result-profile-username">@${profile.username || '-'}</div>
              </div>
            </div>
          `).join('')}
          ${profiles.length > 5 ? `<div style="padding: 8px 0; color: var(--text-secondary); font-size: 12px;">+${profiles.length - 5} more</div>` : ''}
        </div>
      </div>
    `;
  });
  
  elements.resultsDetails.innerHTML = detailsHtml || '<p style="color: var(--text-secondary); text-align: center;">No profiles found</p>';
}

// =============================================================================
// MESSAGE HANDLERS
// =============================================================================

function handleBackgroundMessage(message) {
  switch (message.event) {
    case 'scanStarted':
      console.log('Scan started:', message.data.scanId);
      break;
      
    case 'scanProgress':
      updateProgress(message.data.progress, `Scanning ${PLATFORMS[message.data.platform]?.name || message.data.platform}...`);
      message.data.completedPlatforms.forEach(p => updatePlatformStatus(p, 'completed'));
      if (message.data.platform && !message.data.completedPlatforms.includes(message.data.platform)) {
        updatePlatformStatus(message.data.platform, 'scanning');
      }
      break;
      
    case 'scanCompleted':
      lastResults = message.data.results;
      showResults(message.data.results, message.data.analysis);
      break;
      
    case 'scanCancelled':
      showScanForm();
      break;
      
    case 'scanError':
      showError('Scan Error', message.data.error);
      break;
  }
}

// =============================================================================
// SETTINGS FUNCTIONS
// =============================================================================

async function loadSettings() {
  try {
    const settings = await chrome.storage.local.get(['apiUrl', 'enableNotifications']);
    elements.apiUrl.value = settings.apiUrl || 'http://localhost:8000';
    elements.enableNotifications.checked = settings.enableNotifications !== false;
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

async function saveSettings() {
  try {
    await chrome.storage.local.set({
      apiUrl: elements.apiUrl.value || 'http://localhost:8000',
      enableNotifications: elements.enableNotifications.checked
    });
    hideSettingsModal();
    await checkApiStatus();
  } catch (error) {
    console.error('Error saving settings:', error);
  }
}

function showSettingsModal() {
  elements.settingsModal.classList.remove('hidden');
}

function hideSettingsModal() {
  elements.settingsModal.classList.add('hidden');
}

async function checkApiStatus() {
  const statusEl = elements.apiStatus;
  const dot = statusEl.querySelector('.status-dot');
  const text = statusEl.querySelector('span:last-child');
  
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getApiUrl' });
    const apiUrl = response.url || 'http://localhost:8000';
    
    const healthResponse = await fetch(`${apiUrl}/api/health`);
    const health = await healthResponse.json();
    
    if (health.status === 'healthy') {
      dot.classList.remove('offline');
      text.textContent = 'API: Connected';
    } else {
      dot.classList.add('offline');
      text.textContent = 'API: Unhealthy';
    }
  } catch {
    dot.classList.add('offline');
    text.textContent = 'API: Offline';
  }
}

// =============================================================================
// REPORT FUNCTIONS
// =============================================================================

/**
 * Construct frontend URL from API URL
 * @param {string} apiUrl - The API URL
 * @returns {string} The frontend URL
 */
function getFrontendUrl(apiUrl) {
  try {
    const url = new URL(apiUrl);
    url.port = DEFAULT_FRONTEND_PORT.toString();
    return url.toString().replace(/\/$/, '');
  } catch {
    // Fallback for invalid URLs
    return `http://localhost:${DEFAULT_FRONTEND_PORT}`;
  }
}

function viewFullReport() {
  if (!lastResults || !currentScan) return;
  
  // Open the web app with results
  chrome.storage.local.get(['apiUrl'], (settings) => {
    const baseUrl = settings.apiUrl || `http://localhost:${DEFAULT_API_PORT}`;
    const webAppUrl = getFrontendUrl(baseUrl);
    
    chrome.tabs.create({
      url: `${webAppUrl}/results?scan=${encodeURIComponent(JSON.stringify({
        identifier: currentScan.identifierValue,
        identifierType: currentScan.identifierType,
        results: lastResults
      }))}`
    });
  });
}

async function downloadReport() {
  if (!lastResults) return;
  
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'sendToBackend',
      endpoint: '/api/deep-scan/analyze',
      data: {
        identifier_type: currentScan?.identifierType || 'username',
        identifier_value: currentScan?.identifierValue || 'unknown',
        results: lastResults,
        generate_pdf: true
      }
    });
    
    if (response.report_id) {
      // Open PDF download link
      const settings = await chrome.storage.local.get(['apiUrl']);
      const apiUrl = settings.apiUrl || `http://localhost:${DEFAULT_API_PORT}`;
      chrome.tabs.create({ url: `${apiUrl}/api/report/${response.report_id}/pdf` });
    } else {
      showError('Report Generation Failed', 'Could not generate report. Please try again.');
    }
  } catch (error) {
    console.error('Error downloading report:', error);
    showError('Report Download Failed', error.message || 'Failed to generate report. Please try again.');
  }
}
