from selenium import webdriver  # automates the chrome browser using selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # automatically downloads the correct ChromeDriver
import time  # add delays during scrolling
import requests  # for downloading media
from urllib.parse import urlparse  # to clean up and extract filenames from URLs
from bs4 import BeautifulSoup
import re  # regex to find video URLs
from selenium.webdriver.chrome.options import Options  # headless mode

def extract_facebook_ad_data(url):
    print("[STEP] Starting ChromeDriver setup...")
    driver = None  # Initialize driver variable to ensure it's defined
    try:
        # Set up options for headless mode
        options = Options()
        options.add_argument('--headless')  # Run in headless mode (no UI)
        options.add_argument('--no-sandbox')  # Fix for running in Docker/CI environments
        options.add_argument('--disable-dev-shm-usage')  # Disable shared memory usage

        # Start ChromeDriver service with headless options
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)  # Initialize driver with options
        driver.set_window_size(1200, 800)
        driver.get(url)

        print("[STEP] Waiting for ad cards...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'xh8yej3'))
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

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    ads = soup.find_all('div', class_='xh8yej3')
    print(f"[INFO] Found {len(ads)} ad(s).")

    ad_data = []

    # Extract ad data
    for index, ad in enumerate(ads):
        ad_info = {}

        # Extract Library ID
        try:
            library_id = ad.find('div', class_='xt0e3qv')
            if library_id:
                ad_info['Library ID'] = library_id.get_text(strip=True)
        except: pass

        # Extract Description
        try:
            description = ad.find('div', class_='x6ikm8r x10wlt62')
            if description:
                ad_info['Description'] = description.get_text(strip=True)
        except: pass

        # Extract Image URL
        try:
            image_container = ad.find('div', class_='x1ywc1zp x78zum5 xl56j7k x1e56ztr x1277o0a')
            if image_container:
                img_tag = image_container.find('img', src=True)
                if img_tag and img_tag['src']:
                    image_url = img_tag['src']
                    print(f"[DATA] Image URL: {image_url}")
                    ad_info['Image URL'] = image_url
                else:
                    print("[WARN] <img> tag found but no src attribute.")
            else:
                print("[WARN] Image container div not found.")
        except Exception as e:
            print(f"[ERROR] Exception while extracting image URL: {e}")

        # Extract Video URL
        try:
            video_tag = ad.find('video', src=re.compile(r"^https://video\.fde"))
            if video_tag:
                video_url = video_tag['src']
                ad_info['Video URL'] = video_url
        except: pass

        # Extract Backlink URL
        try:
            container = ad.find('div', class_='x6ikm8r x10wlt62')
            a_tag = container.find('a', href=True)
            if a_tag and a_tag['href']:
                ad_info['Backlink URL'] = a_tag['href']
        except: pass

        if any(ad_info.values()):  # Append valid ad data
            ad_data.append(ad_info)

    return ad_data  # Return the complete list
