import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import re

def extract_facebook_ad_data(url):
    print("[STEP] Starting ChromeDriver setup...")

    driver = None
    page_source = ""

    # Initialize sets to track seen values for each element and avoid duplicates
    seen_library_ids = set()
    seen_descriptions = set()
    seen_image_urls = set()
    seen_video_urls = set()
    seen_backlink_urls = set()

    try:
        # Automatically install the appropriate chromedriver
        chromedriver_autoinstaller.install()

        # Set up options for headless mode
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Start ChromeDriver service with headless options
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1200, 800)
        driver.get(url)

        print("[STEP] Waiting for initial page load...")
        # Wait for initial page load (up to 30 seconds)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'xh8yej3'))
            )
            print("[INFO] Initial ad elements found, beginning timed scrolling...")
        except:
            print("[WARN] Initial elements not found within 30s, will continue with scrolling anyway")

        # Set up timing for the full 160-second scrolling session
        start_time = time.time()
        scroll_duration = 160  # seconds
        scroll_interval = 2  # seconds between scrolls
        
        print(f"[STEP] Starting {scroll_duration}s scrolling session to load all ads...")
        
        # Continuously scroll until time is up
        while time.time() - start_time < scroll_duration:
            # Get current scroll position and page height
            current_position = driver.execute_script("return window.pageYOffset;")
            page_height = driver.execute_script("return document.body.scrollHeight;")
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            remaining = scroll_duration - elapsed
            
            # Log progress every ~10 seconds
            if int(elapsed) % 10 == 0:
                print(f"[INFO] Scrolling in progress: {int(elapsed)}s elapsed, {int(remaining)}s remaining")
            
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_interval)
            
            # Every ~20 seconds, scroll back up a bit and then down again to trigger loading of potentially missed content
            if int(elapsed) % 20 < 2:
                up_position = max(0, current_position - 1000)
                driver.execute_script(f"window.scrollTo(0, {up_position});")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
        print(f"[STEP] Completed {int(time.time() - start_time)}s of scrolling")
        
        # Save the final page source after the full scrolling session
        page_source = driver.page_source

    except Exception as e:
        print(f"[ERROR] Selenium error: {e}")

    finally:
        if driver:
            driver.quit()

    if not page_source:
        print("[ERROR] No page source was retrieved.")
        return []

    # Debug: Print page_source length
    print(f"[DEBUG] Length of page source: {len(page_source)} characters.")
    
    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    ads = soup.find_all('div', class_='xh8yej3')

    # Debug: Check if ads were found
    print(f"[DEBUG] Found {len(ads)} ad(s).")

    ad_data = []

    # Extract ad data
    for index, ad in enumerate(ads):
        ad_info = {}

        try:
            library_id = ad.find('div', class_='xt0e3qv')
            if library_id:
                ad_info['Library ID'] = library_id.get_text(strip=True)

                # Skip the ad if its Library ID has already been seen
                if ad_info['Library ID'] in seen_library_ids:
                    continue
                seen_library_ids.add(ad_info['Library ID'])

        except Exception as e:
            print(f"[ERROR] Exception while extracting Library ID: {e}")

        try:
            description = ad.find('div', class_='x6ikm8r x10wlt62')
            if description:
                ad_info['Description'] = description.get_text(strip=True)

                # Skip the ad if its Description has already been seen
                if ad_info['Description'] in seen_descriptions:
                    continue
                seen_descriptions.add(ad_info['Description'])

        except Exception as e:
            print(f"[ERROR] Exception while extracting Description: {e}")

        try:
            image_container = ad.find('div', class_='x1ywc1zp x78zum5 xl56j7k x1e56ztr x1277o0a')
            if image_container:
                img_tag = image_container.find('img', src=True)
                if img_tag and img_tag['src']:
                    image_url = img_tag['src']
                    ad_info['Image URL'] = image_url

                    # Skip the ad if its Image URL has already been seen
                    if ad_info['Image URL'] in seen_image_urls:
                        continue
                    seen_image_urls.add(ad_info['Image URL'])

        except Exception as e:
            print(f"[ERROR] Exception while extracting Image URL: {e}")

        try:
            video_tag = ad.find('video', src=re.compile(r"^https://video\.fde"))
            if video_tag:
                video_url = video_tag['src']
                ad_info['Video URL'] = video_url

                # Skip the ad if its Video URL has already been seen
                if ad_info['Video URL'] in seen_video_urls:
                    continue
                seen_video_urls.add(ad_info['Video URL'])

        except Exception as e:
            print(f"[ERROR] Exception while extracting Video URL: {e}")

        try:
            container = ad.find('div', class_='x6ikm8r x10wlt62')
            a_tag = container.find('a', href=True)
            if a_tag and a_tag['href']:
                ad_info['Backlink URL'] = a_tag['href']

                # Skip the ad if its Backlink URL has already been seen
                if ad_info['Backlink URL'] in seen_backlink_urls:
                    continue
                seen_backlink_urls.add(ad_info['Backlink URL'])

        except Exception as e:
            print(f"[ERROR] Exception while extracting Backlink URL: {e}")

        if any(ad_info.values()):
            ad_data.append(ad_info)

    if not ad_data:
        print("[ERROR] No valid ad data found.")
        return []

    return ad_data