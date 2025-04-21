import chromedriver_autoinstaller  # Automatically installs chromedriver
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
    try:
        # Automatically install the appropriate chromedriver
        chromedriver_autoinstaller.install()  # This will automatically download and install the correct chromedriver

        # Set up options for headless mode
        options = Options()
        options.add_argument('--headless')  # Run in headless mode (no UI)
        options.add_argument('--no-sandbox')  # Fix for running in Docker/CI environments
        options.add_argument('--disable-dev-shm-usage')  # Disable shared memory usage

        # Start ChromeDriver service with headless options
        driver = webdriver.Chrome(options=options)  # Use the installed chromedriver
        driver.set_window_size(1200, 800)
        driver.get(url)

        print("[STEP] Waiting for ad cards...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'xh8yej3'))  # Modify this if needed after inspecting the page
        )

        print("[STEP] Scrolling to load more ads...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("[STEP] Finalizing page load...")
        time.sleep(5)
        page_source = driver.page_source  # Save HTML

    except Exception as e:
        print(f"[ERROR] Selenium error: {e}")

    finally:
        if driver:
            driver.quit()  # Quit browser only if driver was created

    # Check if the page_source has been assigned, and only proceed if it is not empty
    if not page_source:
        print("[ERROR] No page source was retrieved.")
        return []

    # Debug: Print page_source length
    print(f"[DEBUG] Length of page source: {len(page_source)} characters.")
    
    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    ads = soup.find_all('div', class_='xh8yej3')  # Modify this if needed after inspecting the page

    # Debug: Check if ads were found
    print(f"[DEBUG] Found {len(ads)} ad(s).")

    ad_data = []

    # Extract ad data
    for index, ad in enumerate(ads):
        ad_info = {}

        try:
            library_id = ad.find('div', class_='xt0e3qv')  # Modify this if needed
            if library_id:
                ad_info['Library ID'] = library_id.get_text(strip=True)
        except Exception as e:
            print(f"[ERROR] Exception while extracting Library ID: {e}")

        try:
            description = ad.find('div', class_='x6ikm8r x10wlt62')  # Modify this if needed
            if description:
                ad_info['Description'] = description.get_text(strip=True)
        except Exception as e:
            print(f"[ERROR] Exception while extracting Description: {e}")

        try:
            image_container = ad.find('div', class_='x1ywc1zp x78zum5 xl56j7k x1e56ztr x1277o0a')  # Modify this if needed
            if image_container:
                img_tag = image_container.find('img', src=True)
                if img_tag and img_tag['src']:
                    image_url = img_tag['src']
                    ad_info['Image URL'] = image_url
        except Exception as e:
            print(f"[ERROR] Exception while extracting Image URL: {e}")

        try:
            video_tag = ad.find('video', src=re.compile(r"^https://video\.fde"))
            if video_tag:
                video_url = video_tag['src']
                ad_info['Video URL'] = video_url
        except Exception as e:
            print(f"[ERROR] Exception while extracting Video URL: {e}")

        try:
            container = ad.find('div', class_='x6ikm8r x10wlt62')  # Modify this if needed
            a_tag = container.find('a', href=True)
            if a_tag and a_tag['href']:
                ad_info['Backlink URL'] = a_tag['href']
        except Exception as e:
            print(f"[ERROR] Exception while extracting Backlink URL: {e}")

        if any(ad_info.values()):
            ad_data.append(ad_info)

    if not ad_data:
        print("[ERROR] No valid ad data found.")
        return []

    return ad_data  # Return the complete list
