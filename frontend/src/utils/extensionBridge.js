/**
 * Extension Bridge - Handles communication between web app and Chrome extension
 * Uses window.postMessage for cross-context communication
 */

let requestIdCounter = 0;
const pendingRequests = new Map();

/**
 * Send message to extension via content script
 */
function sendMessageToExtension(action, data = null) {
  return new Promise((resolve, reject) => {
    const requestId = ++requestIdCounter;
    
    // Store resolver
    pendingRequests.set(requestId, { resolve, reject });
    
    // Send message via postMessage
    window.postMessage({
      source: 'dfa-webapp',
      requestId,
      action,
      data
    }, '*');
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (pendingRequests.has(requestId)) {
        pendingRequests.delete(requestId);
        reject(new Error('Extension request timeout'));
      }
    }, 30000);
  });
}

/**
 * Listen for responses from extension
 */
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  
  const message = event.data;
  if (!message || message.source !== 'dfa-extension') return;
  
  // Handle response to a request
  if (message.requestId && pendingRequests.has(message.requestId)) {
    const { resolve, reject } = pendingRequests.get(message.requestId);
    pendingRequests.delete(message.requestId);
    
    if (message.response?.success === false) {
      reject(new Error(message.response.error || 'Extension request failed'));
    } else {
      resolve(message.response);
    }
  }
  
  // Handle events (scanProgress, scanCompleted, etc.)
  if (message.event) {
    const event = new CustomEvent('dfa-extension-event', {
      detail: { event: message.event, data: message.data }
    });
    window.dispatchEvent(event);
  }
});

/**
 * Detect if extension is installed
 */
export async function detectExtension() {
  try {
    const response = await sendMessageToExtension('checkExtension');
    return response.installed === true;
  } catch (error) {
    console.error('[Web App] Extension detection failed:', error);
    return false;
  }
}

/**
 * Get extension info (version, ID)
 */
export async function getExtensionInfo() {
  try {
    const response = await sendMessageToExtension('checkExtension');
    return {
      installed: response.installed,
      version: response.version,
      extensionId: response.extensionId,
      ready: response.ready
    };
  } catch (error) {
    return {
      installed: false,
      version: null,
      extensionId: null,
      ready: false
    };
  }
}

/**
 * Start deep scan via extension
 */
export async function startDeepScanViaExtension(scanData) {
  try {
    const response = await sendMessageToExtension('startDeepScan', {
      identifierType: scanData.identifierType,
      identifierValue: scanData.identifierValue,
      platforms: scanData.platforms || ['facebook', 'instagram', 'linkedin', 'x']
    });
    
    if (!response.success) {
      throw new Error(response.error || 'Scan failed');
    }
    
    return response;
    
  } catch (error) {
    console.error('[Web App] Scan request failed:', error);
    throw new Error(`Failed to start scan: ${error.message}`);
  }
}

/**
 * Get current scan status
 */
export async function getScanStatus() {
  try {
    const response = await sendMessageToExtension('getScanStatus');
    return response;
  } catch (error) {
    console.error('[Web App] Failed to get scan status:', error);
    return { status: 'error', error: error.message };
  }
}

/**
 * Cancel current scan
 */
export async function cancelScan() {
  try {
    await sendMessageToExtension('cancelScan');
  } catch (error) {
    console.error('[Web App] Failed to cancel scan:', error);
  }
}

/**
 * Listen for extension events (progress, completion, etc.)
 */
export function onExtensionEvent(callback) {
  const handler = (event) => {
    callback(event.detail.event, event.detail.data);
  };
  
  window.addEventListener('dfa-extension-event', handler);
  
  // Return cleanup function
  return () => {
    window.removeEventListener('dfa-extension-event', handler);
  };
}
