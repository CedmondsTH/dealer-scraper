#!/usr/bin/env python3
"""
Playwright subprocess wrapper to avoid asyncio conflicts with Streamlit.
Runs Playwright in a separate process to bypass Windows event loop issues.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def fetch_with_playwright_subprocess(url: str, timeout: int = 30000) -> Optional[str]:
    """
    Fetch page content using Playwright in a subprocess to avoid asyncio conflicts.
    
    Args:
        url: URL to fetch
        timeout: Timeout in milliseconds
        
    Returns:
        HTML content or None if failed
    """
    try:
        # Create the Playwright script
        script_content = f'''
import sys
import json
from playwright.sync_api import sync_playwright

def main():
    try:
        with sync_playwright() as p:
            # Launch browser with stealth settings
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                viewport={{'width': 1920, 'height': 1080}},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                extra_http_headers={{
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }}
            )
            
            page = context.new_page()
            
            # Add stealth scripts
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined,
                }});
                
                // Remove automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)
            
            # Navigate with realistic timing
            page.goto("{url}", wait_until="domcontentloaded", timeout={timeout})
            
            # Wait a bit for dynamic content
            page.wait_for_timeout(2000)
            
            # Get content
            html = page.content()
            
            browser.close()
            
            # Output result
            result = {{"success": True, "html": html, "length": len(html)}}
            print(json.dumps(result))
            
    except Exception as e:
        result = {{"success": False, "error": str(e)}}
        print(json.dumps(result))

if __name__ == "__main__":
    main()
'''
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # Run Playwright in subprocess
            logger.info(f"Running Playwright subprocess for: {{url}}")
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout // 1000 + 10,  # Add buffer to subprocess timeout
                cwd=Path(__file__).parent.parent.parent  # Run from project root
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout.strip())
                    if data.get("success"):
                        logger.info(f"Playwright subprocess success: {{data.get('length', 0)}} characters")
                        return data.get("html")
                    else:
                        logger.error(f"Playwright subprocess error: {{data.get('error')}}")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse subprocess output: {{e}}")
                    logger.debug(f"Raw output: {{result.stdout[:500]}}")
                    return None
            else:
                logger.error(f"Playwright subprocess failed with code {{result.returncode}}")
                logger.error(f"Stderr: {{result.stderr}}")
                return None
                
        finally:
            # Clean up temp file
            try:
                Path(script_path).unlink()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Subprocess wrapper failed: {{e}}")
        return None