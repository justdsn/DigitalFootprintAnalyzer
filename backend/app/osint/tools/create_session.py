"""
create_session.py
-----------------
Helper script to create Playwright storageState session files for supported OSINT platforms.

Usage (interactive):
  python create_session.py --platform instagram --headless false

The script opens a Playwright browser (default visible) and navigates to the
platform's login page. Complete a manual login in the opened browser window
and then press ENTER in the console to save the session to the project's
session store (managed by `SessionManager`). The saved session file will be
created with restrictive permissions (0o600) where possible.

Security: This script does not store credentials. It only saves the Playwright
storageState after logging in via the browser.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
import json
import getpass

# Ensure the parent backend directory is on sys.path so `app` imports work
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))

from playwright.sync_api import sync_playwright

from app.osint.session_manager import SessionManager

logger = logging.getLogger(__name__)


LOGIN_PAGES = {
    "instagram": "https://www.instagram.com/accounts/login/",
    "facebook": "https://www.facebook.com/login",
    "linkedin": "https://www.linkedin.com/login/",
    # X/Twitter uses either x.com or twitter.com depending on region
    "twitter": "https://twitter.com/login/",
    "x": "https://x.com/login/",
}

# Best-effort selectors for auto-login. Playwright selectors may change per
# platform version / localization; these are best-effort and may require
# manual login for newer layouts.
LOGIN_SELECTORS = {
    "instagram": {"username": 'input[name="username"]', "password": 'input[name="password"]', "submit": 'button[type="submit"]'},
    "facebook": {"username": 'input#email', "password": 'input#pass', "submit": 'button[name="login"]'},
    "linkedin": {"username": 'input#username', "password": 'input#password', "submit": 'button[type="submit"]'},
    "twitter": {"username": 'input[name="text"]', "password": 'input[name="password"]', "submit": 'div[data-testid="LoginForm_Login_Button"]'},
    "x": {"username": 'input[name="text"]', "password": 'input[name="password"]', "submit": 'div[data-testid="LoginForm_Login_Button"]'},
}


def detect_login_url(platform: str) -> str:
    platform = platform.lower()
    if platform in LOGIN_PAGES:
        return LOGIN_PAGES[platform]
    # Fallback: try to open the platform home
    raise ValueError(f"Unsupported platform for session creation: {platform}")


def create_session(platform: str, headless: bool = False, browser_name: str = "chromium", username: str = None, password: str = None):
    sm = SessionManager()
    platform = platform.lower()

    if platform not in sm.SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}. Supported: {sm.SUPPORTED_PLATFORMS}")

    login_url = detect_login_url(platform)

    print(f"Opening browser for platform: {platform}")
    print("If the login page doesn't appear, ensure Playwright browsers are installed (playwright install chromium)")
    print("A browser window will open. Log in manually and press ENTER in this console to save the session.")

    with sync_playwright() as pw:
        if browser_name == "chromium":
            browser = pw.chromium.launch(headless=headless)
        elif browser_name == "firefox":
            browser = pw.firefox.launch(headless=headless)
        elif browser_name == "webkit":
            browser = pw.webkit.launch(headless=headless)
        else:
            browser = pw.chromium.launch(headless=headless)

        context = browser.new_context()
        page = context.new_page()


        try:
            page.goto(login_url)
        except Exception as e:
            print(f"Warning: could not navigate to {login_url}. Error: {e}")

        # If credentials are provided, attempt an automated login
        username_val = username
        password_val = password

        attempted_auto = False
        if username_val and password_val:
            try:
                selectors = LOGIN_SELECTORS.get(platform, {})
                username_selector = selectors.get("username")
                password_selector = selectors.get("password")
                submit_selector = selectors.get("submit")

                if username_selector and password_selector:
                    attempted_auto = True
                    print("Attempting automated login (one-step) with provided credentials...")
                    page.fill(username_selector, username_val)
                    page.fill(password_selector, password_val)
                    if submit_selector:
                        page.click(submit_selector)
                    else:
                        page.keyboard.press("Enter")
                    # Wait for navigation or small delay for login to complete
                    try:
                        page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Automated login attempt failed: {e}")

        # If automated login wasn't attempted or we cannot detect success, fall back to manual
        if not attempted_auto:
            input("Press ENTER once you have logged in manually (or CTRL+C to abort)...")

        # Grab storage state
        try:
            storage_state = context.storage_state()
        except Exception as e:
            print(f"Failed to get storage state: {e}")
            storage_state = {}
        except Exception as e:
            print(f"Failed to get storage state: {e}")
            storage_state = {}

        # Prompt before saving empty state
        if not storage_state.get('cookies') and not storage_state.get('origins'):
            save_anyway = input("Session appears empty (no cookies/origins found). Save anyway? [y/N]: ")
            if save_anyway.strip().lower() not in ('y', 'yes'):
                print("Skipping save.")
                saved = False
            else:
                saved = sm.save_session(platform, storage_state)
        else:
            # Save with SessionManager helper
            saved = sm.save_session(platform, storage_state)
        if saved:
            path = sm.get_session_path(platform)
            print(f"Session saved to {path}")
        else:
            print(f"Failed to save session for {platform}")

        # Clean up
        try:
            context.close()
            browser.close()
        except Exception:
            pass


def main(argv):
    parser = argparse.ArgumentParser("Create Playwright storageState sessions for OSINT collectors")
    parser.add_argument("--platform", required=True, help="Platform to create session for (instagram, facebook, linkedin, twitter)")
    parser.add_argument("--headless", default="false", choices=["true", "false"], help="Use headless browser. Default false (visible)")
    parser.add_argument("--browser", default="chromium", choices=["chromium", "firefox", "webkit"], help="Which Playwright browser to use")
    parser.add_argument("--username", help="Optional username/email to attempt automated login")
    parser.add_argument("--password", help="Optional password to attempt automated login (use with caution)")

    args = parser.parse_args(argv)
    headless = args.headless.lower() == "true"

    # Get sensitive input if necessary
    password_val = args.password
    if args.username and not password_val:
        password_val = getpass.getpass(prompt=f"Enter password for {args.username}: ")

    try:
        create_session(args.platform, headless=headless, browser_name=args.browser, username=args.username, password=password_val)
    except KeyboardInterrupt:
        print("Aborted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
