from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re

def extract_facebook_ad_data_selenium(url):
    """Fetch and extract ad data using Selenium to handle dynamic content."""
    
    # Set up Chrome WebDriver
    driver_path = r'C:/DRIVER/chrome-win64/chrome.exe'  # Use your provided ChromeDriver path
    driver = webdriver.Chrome(executable_path=driver_path)
    
    # Open the URL
    driver.get(url)

    # Wait for the page to load (you may need to adjust the wait time depending on the speed)
    time.sleep(5)  # Adjust this based on the complexity of the page and network speed

    # Get the page source after rendering the JavaScript
    page_source = driver.page_source

    # Close the WebDriver
    driver.quit()

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Example: Find all ad cards (this selector may need adjustment based on the page structure)
    ads = soup.find_all('div', class_='AdCard')  # Adjust the class based on the actual HTML

    ad_data = []
    
    # Loop through each ad and extract the necessary data
    for ad in ads:
        ad_info = {}
        
        # Extract Library ID (or any other identifier for the ad)
        library_id = ad.find('div', class_='LibraryID')  # Adjust as needed
        if library_id:
            ad_info['Library ID'] = library_id.get_text(strip=True)
        
        # Extract Description
        description = ad.find('div', style='white-space: pre-wrap;')  # Adjust as needed
        if description:
            ad_info['Description'] = description.get_text(strip=True)
        
        # Extract image URL (match pattern)
        image_url = ad.find('img', src=re.compile(r"^https://scontent.fde"))
        if image_url:
            ad_info['Image URL'] = image_url['src']
        
        # Extract video URL (match pattern)
        video_url = ad.find('video', src=re.compile(r"^https://video.fde"))
        if video_url:
            ad_info['Video URL'] = video_url['src']
        
        ad_data.append(ad_info)
    
    return ad_data
