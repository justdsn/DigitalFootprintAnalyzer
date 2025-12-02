/**
 * Extension Bridge - Handles communication between web app and Chrome extension
 */

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
    const isInstalled = await checkExtensionById(storedId);
    if (isInstalled) {
      EXTENSION_ID = storedId;
      return true;
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
  EXTENSION_ID = id;
  localStorage.setItem('dfa_extension_id', id);
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
