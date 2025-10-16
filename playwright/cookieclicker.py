from playwright.sync_api import sync_playwright
import time

def run_cookie_clicker():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )
        
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(120000)
        
        try:
            page.goto("https://orteil.dashnet.org/cookieclicker/")
            
            # Handle initial consent
            try:
                page.click(".cc_btn_accept_all", timeout=5000)
            except Exception:
                pass
            
            # Handle language selection
            try:
                page.click("#langSelect-EN", timeout=60000)
            except Exception:
                pass
            
            # CAPTCHA handling with detection
            print("Checking for CAPTCHA...")
            
            # Wait for either CAPTCHA to appear or game to load
            captcha_solved = False
            start_time = time.time()
            
            while time.time() - start_time < 60:  # Wait up to 60 seconds
                # Check if CAPTCHA is present (common CAPTCHA indicators)
                captcha_indicators = [
                    "iframe[src*='captcha']",
                    "iframe[src*='recaptcha']",
                    ".g-recaptcha",
                    "#captcha",
                    "text=CAPTCHA",
                    "text=verify",
                    "text=robot"
                ]
                
                captcha_found = False
                for indicator in captcha_indicators:
                    if page.is_visible(indicator, timeout=1000):
                        captcha_found = True
                        break
                
                if captcha_found:
                    print("CAPTCHA detected! Please solve it manually...")
                    print("Press Enter in the console when CAPTCHA is solved.")
                    input("Waiting for CAPTCHA solution...")
                    captcha_solved = True
                    break
                
                # Check if game has loaded (big cookie is visible)
                if page.is_visible("#bigCookie", timeout=1000):
                    print("Game loaded successfully!")
                    break
                
                time.sleep(1)
            
            if not captcha_solved and page.is_visible("#bigCookie"):
                print("No CAPTCHA detected, game loaded successfully!")
            
            # Handle any post-CAPTCHA consent banners
            try:
                consent_selectors = [
                    "#onetrust-accept-btn-handler",
                    "button[aria-label='Accept all']",
                    ".fc-cta-consent",
                    ".cc-btn.cc-allow"
                ]
                for selector in consent_selectors:
                    if page.is_visible(selector, timeout=3000):
                        page.click(selector)
                        break
            except Exception:
                pass
            
            # Wait for and click the big cookie
            cookie_selector = "#bigCookie"
            page.wait_for_selector(cookie_selector, state="visible", timeout=30000)
            page.click(cookie_selector)
            
            print("Bot started! Clicking cookies and buying upgrades...")
            
            # Main game loop
            while True:
                page.click(cookie_selector)
                
                cookies_element = page.query_selector("#cookies")
                if cookies_element:
                    cookies_text = cookies_element.text_content().split(" ")[0].replace(",", "")
                    
                    if cookies_text.isdigit():
                        cookies_count = int(cookies_text)
                        
                        # Buy most expensive affordable product first
                        for i in range(3, -1, -1):
                            price_element = page.query_selector(f"#productPrice{i}")
                            if price_element:
                                price_text = price_element.text_content().replace(",", "")
                                
                                if price_text.isdigit():
                                    price_val = int(price_text)
                                    
                                    if cookies_count >= price_val:
                                        product_element = page.query_selector(f"#product{i}")
                                        if product_element and "enabled" in product_element.get_attribute("class"):
                                            product_element.click()
                                            print(f"Bought product {i} for {price_val} cookies")
                                            break
                
                page.wait_for_timeout(10)
                
        except Exception as e:
            print("ERROR:", e)
        finally:
            print("Bot stopped. Browser will remain open.")

if __name__ == "__main__":
    run_cookie_clicker()