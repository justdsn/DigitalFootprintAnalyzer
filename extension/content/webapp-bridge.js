// =============================================================================
// WEB APP BRIDGE CONTENT SCRIPT
// =============================================================================
// Injects into the web app and facilitates communication with extension
// =============================================================================

console.log('[DFA Extension] Web app bridge loaded');

// Listen for messages from web app (page script)
window.addEventListener('message', async (event) => {
  // Only accept messages from same origin
  if (event.source !== window) return;
  
  const message = event.data;
  
  // Only handle DFA messages
  if (!message || message.source !== 'dfa-webapp') return;
  
  console.log('[DFA Extension] Received message from web app:', message);
  
  try {
    let response;
    
    switch (message.action) {
      case 'checkExtension':
        // Extension is installed if this script is running
        response = {
          success: true,
          installed: true,
          version: chrome.runtime.getManifest().version,
          ready: true,
          extensionId: chrome.runtime.id
        };
        break;
        
      case 'startDeepScan':
        // Forward to background service worker
        response = await chrome.runtime.sendMessage({
          action: 'startDeepScan',
          data: message.data
        });
        break;
        
      case 'getScanStatus':
        response = await chrome.runtime.sendMessage({
          action: 'getScanStatus'
        });
        break;
        
      case 'cancelScan':
        response = await chrome.runtime.sendMessage({
          action: 'cancelScan'
        });
        break;
        
      default:
        response = {
          success: false,
          error: `Unknown action: ${message.action}`
        };
    }
    
    // Send response back to web app
    window.postMessage({
      source: 'dfa-extension',
      requestId: message.requestId,
      action: message.action,
      response: response
    }, '*');
    
  } catch (error) {
    console.error('[DFA Extension] Error handling message:', error);
    
    // Send error response
    window.postMessage({
      source: 'dfa-extension',
      requestId: message.requestId,
      action: message.action,
      response: {
        success: false,
        error: error.message
      }
    }, '*');
  }
});

// Listen for messages from background (scan progress updates)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.event) {
    // Forward progress/completion events to web app
    window.postMessage({
      source: 'dfa-extension',
      event: message.event,
      data: message.data
    }, '*');
  }
  return false;
});

// Notify web app that extension is ready
window.postMessage({
  source: 'dfa-extension',
  event: 'extensionReady',
  data: {
    version: chrome.runtime.getManifest().version,
    extensionId: chrome.runtime.id
  }
}, '*');
