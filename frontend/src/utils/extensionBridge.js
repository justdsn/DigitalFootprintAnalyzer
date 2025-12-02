/**
 * Extension Bridge - Handles communication between web app and Chrome extension
 */

/* global chrome */

// Extension ID (will be set after extension is loaded)
let EXTENSION_ID = null;

/**
 * Detect and connect to the extension
 * @returns {Promise<boolean>} Whether extension is installed
 */
export async function detectExtension() {
  // Try to get extension ID from storage
  const storedId = localStorage.getItem('dfa_extension_id');
  
  if (storedId) {
    // Validate stored ID format
    const trimmedId = storedId.trim();
    if (trimmedId.length === 32 && /^[a-z]{32}$/.test(trimmedId)) {
      const isInstalled = await checkExtensionById(trimmedId);
      if (isInstalled) {
        EXTENSION_ID = trimmedId;
        return true;
      }
    } else {
      // Invalid format, clear from storage
      localStorage.removeItem('dfa_extension_id');
    }
  }
  
  // Extension ID not found or invalid, need user to provide it
  return false;
}

/**
 * Check if extension with given ID is installed
 */
async function checkExtensionById(extensionId) {
  try {
    const response = await chrome.runtime.sendMessage(
      extensionId,
      { action: 'checkExtension' }
    );
    return response?.installed === true;
  } catch (error) {
    return false;
  }
}

/**
 * Set the extension ID manually (user provides after installation)
 */
export function setExtensionId(id) {
  // Validate extension ID format (32 characters, alphanumeric)
  if (!id || typeof id !== 'string') {
    throw new Error('Invalid extension ID: must be a non-empty string');
  }
  
  const trimmedId = id.trim();
  if (trimmedId.length !== 32 || !/^[a-z]{32}$/.test(trimmedId)) {
    console.warn('Extension ID format may be incorrect. Expected 32 lowercase letters.');
  }
  
  EXTENSION_ID = trimmedId;
  localStorage.setItem('dfa_extension_id', trimmedId);
}

/**
 * Get current extension ID
 */
export function getExtensionId() {
  return EXTENSION_ID;
}

/**
 * Send deep scan request to extension
 * @param {Object} scanData - Scan parameters
 * @returns {Promise<Object>} Scan results
 */
export async function startDeepScanViaExtension(scanData) {
  if (!EXTENSION_ID) {
    throw new Error('Extension not connected. Please install and configure the extension first.');
  }
  
  try {
    // Send message to extension
    const response = await chrome.runtime.sendMessage(
      EXTENSION_ID,
      {
        action: 'startDeepScan',
        data: {
          identifierType: scanData.identifierType,
          identifierValue: scanData.identifierValue,
          platforms: scanData.platforms || ['facebook', 'instagram', 'linkedin', 'x']
        }
      }
    );
    
    if (!response.success) {
      throw new Error(response.error || 'Extension scan failed');
    }
    
    return response.data;
    
  } catch (error) {
    console.error('[Web App] Extension communication error:', error);
    throw new Error('Failed to communicate with extension. Make sure it is installed and enabled.');
  }
}

/**
 * Check extension status
 */
export async function getExtensionStatus() {
  if (!EXTENSION_ID) {
    return { installed: false, ready: false };
  }
  
  try {
    const response = await chrome.runtime.sendMessage(
      EXTENSION_ID,
      { action: 'checkExtension' }
    );
    return {
      installed: true,
      ready: response?.ready === true,
      version: response?.version
    };
  } catch (error) {
    return { installed: false, ready: false };
  }
}
