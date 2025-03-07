import os
import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

class YouTubeBrowserHelper:
    def __init__(self):
        self.display = Display(visible=0, size=(1280, 1024))
        self.display.start()
        
        # Configure Firefox options
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--window-size=1280,1024")
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        # Initialize the driver
        self.driver = webdriver.Firefox(options=self.options)
        
    def __del__(self):
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
            if hasattr(self, 'display'):
                self.display.stop()
        except:
            pass
    
    def get_cookies_for_url(self, url):
        """
        Visit a YouTube URL and extract cookies to bypass bot detection
        """
        try:
            print(f"Visiting URL to get cookies: {url}")
            self.driver.get(url)
            
            # Wait for the page to load (look for video player or consent dialog)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "movie_player")) or
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Accept')]"))
                )
            except:
                # Continue even if specific elements aren't found
                pass
            
            # If consent dialog appears, accept it
            try:
                consent_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Accept')]")
                consent_button.click()
                time.sleep(2)  # Wait for the action to complete
            except:
                # No consent dialog appeared
                pass
                
            # Get all cookies
            cookies = self.driver.get_cookies()
            
            # Convert to Netscape cookie format that yt-dlp can use
            cookie_file_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
            with open(cookie_file_path, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for cookie in cookies:
                    domain = cookie['domain']
                    flag = "TRUE"
                    path = cookie['path']
                    secure = "TRUE" if cookie.get('secure', False) else "FALSE"
                    expiry = cookie.get('expiry', 0)
                    name = cookie['name']
                    value = cookie['value']
                    f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
            
            print(f"Cookies saved to {cookie_file_path}")
            return cookie_file_path
        except Exception as e:
            print(f"Error getting cookies: {str(e)}")
            return None

# Helper function to get fresh cookies or use cached ones
def get_youtube_cookies(url, force_refresh=False):
    cookie_file_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
    
    # Check if cookie file exists and is less than 6 hours old
    if not force_refresh and os.path.exists(cookie_file_path):
        file_age = time.time() - os.path.getmtime(cookie_file_path)
        if file_age < 21600:  # 6 hours in seconds
            print("Using existing cookie file")
            return cookie_file_path
    
    # Get fresh cookies
    helper = YouTubeBrowserHelper()
    try:
        return helper.get_cookies_for_url(url)
    finally:
        del helper  # Ensure browser is properly closed
