// =============================================================================
// AUTH DETECTOR CONTENT SCRIPT
// =============================================================================
// Detects login status on social media platforms.
// Uses multiple methods: cookies, DOM elements, and page content.
// =============================================================================

(function () {
    'use strict';

    // Platform-specific auth detection configurations
    const AUTH_CONFIG = {
        facebook: {
            // Cookies that indicate logged-in state
            authCookies: ['c_user', 'xs'],
            // DOM elements present when logged in
            loggedInSelectors: [
                '[role="banner"]',
                '[aria-label="Facebook"]',
                '[data-pagelet="RightRail"]',
                '[data-pagelet="LeftRail"]',
                'div[role="main"]',
                'a[href*="/friends"]',
                'a[href*="/messages"]'
            ],
            // Elements that indicate NOT logged in (login page)
            loginPageSelectors: [
                'input[name="email"]',
                'input[name="pass"]',
                'button[name="login"]',
                '#login_form',
                'form[action*="login"]'
            ],
            // Check if URL indicates logged in
            checkUrl: (url) => !url.includes('/login') && !url.includes('/recover')
        },
        instagram: {
            authCookies: ['sessionid', 'ds_user_id'],
            loggedInSelectors: [
                'svg[aria-label="Home"]',
                'svg[aria-label="Search"]',
                'svg[aria-label="New post"]',
                'a[href="/direct/inbox/"]',
                'span[role="link"]',
                'nav a[href*="/accounts/activity"]'
            ],
            loginPageSelectors: [
                'input[name="username"]',
                'input[name="password"]',
                'button[type="submit"]',
                'form[id="loginForm"]'
            ],
            checkUrl: (url) => !url.includes('/accounts/login')
        },
        linkedin: {
            authCookies: ['li_at', 'JSESSIONID'],
            loggedInSelectors: [
                '.global-nav',
                '.feed-identity-module',
                'nav[aria-label="Primary"]',
                'button[aria-label*="menu"]',
                'a[href*="/feed"]',
                'div[data-test-id="navigation"]',
                '.scaffold-layout'
            ],
            loginPageSelectors: [
                'input[id="session_key"]',
                'input[id="session_password"]',
                'button[type="submit"]',
                '.login__form'
            ],
            checkUrl: (url) => !url.includes('/login') && !url.includes('/checkpoint')
        },
        x: {
            authCookies: ['auth_token', 'ct0'],
            loggedInSelectors: [
                '[data-testid="SideNav_AccountSwitcher_Button"]',
                '[data-testid="AppTabBar_Home_Link"]',
                'nav[aria-label="Primary"]',
                'a[href="/home"]',
                '[data-testid="primaryColumn"]'
            ],
            loginPageSelectors: [
                'input[autocomplete="username"]',
                'input[name="password"]',
                '[data-testid="LoginForm_Login_Button"]',
                'a[href="/login"]'
            ],
            checkUrl: (url) => !url.includes('/login') && !url.includes('/i/flow/login')
        }
    };

    // Detect current platform from URL
    function detectPlatform() {
        const host = window.location.hostname.toLowerCase();

        if (host.includes('facebook.com')) return 'facebook';
        if (host.includes('instagram.com')) return 'instagram';
        if (host.includes('linkedin.com')) return 'linkedin';
        if (host.includes('x.com') || host.includes('twitter.com')) return 'x';

        return null;
    }

    // Check if a cookie exists
    function hasCookie(name) {
        return document.cookie.split(';').some(cookie =>
            cookie.trim().startsWith(name + '=')
        );
    }

    // Check if any auth cookies exist for platform
    function hasAuthCookies(cookies) {
        for (const cookieName of cookies) {
            if (hasCookie(cookieName)) {
                console.log(`[Auth Detector] Found auth cookie: ${cookieName}`);
                return true;
            }
        }
        return false;
    }

    // Check if any selector matches
    function hasAnySelector(selectors) {
        for (const selector of selectors) {
            try {
                const element = document.querySelector(selector);
                if (element) {
                    console.log(`[Auth Detector] Found element: ${selector}`);
                    return true;
                }
            } catch (e) {
                // Invalid selector, skip
            }
        }
        return false;
    }

    // Detect login status using multiple methods
    function detectAuthStatus() {
        const platform = detectPlatform();

        if (!platform) {
            return { platform: null, isLoggedIn: false, error: 'Unknown platform' };
        }

        const config = AUTH_CONFIG[platform];
        const url = window.location.href;

        // Method 1: Check cookies (most reliable)
        const hasCookies = hasAuthCookies(config.authCookies);

        // Method 2: Check if on login page
        const isLoginPage = hasAnySelector(config.loginPageSelectors);

        // Method 3: Check URL
        const urlIndicatesLoggedIn = config.checkUrl(url);

        // Method 4: Check for logged-in UI elements (wait needed for SPAs)
        const hasLoggedInUI = hasAnySelector(config.loggedInSelectors);

        // Determine final status
        // User is logged in if:
        // - Has auth cookies AND not on login page
        // - OR has logged-in UI elements AND URL doesn't indicate login page
        const isLoggedIn = (hasCookies && !isLoginPage) ||
            (hasLoggedInUI && urlIndicatesLoggedIn && !isLoginPage);

        console.log(`[Auth Detector] ${platform}: isLoggedIn=${isLoggedIn}`, {
            hasCookies,
            hasLoggedInUI,
            isLoginPage,
            urlIndicatesLoggedIn,
            url
        });

        return {
            platform,
            isLoggedIn,
            hasCookies,
            hasLoggedInUI,
            isLoginPage,
            url
        };
    }

    // Listen for auth check requests
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'checkAuth' || message.action === 'getAuthStatus') {
            // Wait a bit for page to fully render (SPAs)
            setTimeout(() => {
                const status = detectAuthStatus();
                console.log('[Auth Detector] Responding with:', status);
                sendResponse(status);
            }, message.action === 'checkAuth' ? 1000 : 100);
            return true; // Will respond asynchronously
        }
    });

    // Notify service worker when page loads
    function notifyPageLoad() {
        const platform = detectPlatform();
        if (!platform) return;

        // Wait for page to settle
        setTimeout(() => {
            const status = detectAuthStatus();

            // Send auth status to service worker
            chrome.runtime.sendMessage({
                action: 'authStatusUpdate',
                data: status
            }).catch(() => {
                // Extension context may not be ready
            });
        }, 2000);
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', notifyPageLoad);
    } else {
        notifyPageLoad();
    }

    console.log(`[Auth Detector] Loaded for ${detectPlatform() || 'unknown platform'}`);
})();
