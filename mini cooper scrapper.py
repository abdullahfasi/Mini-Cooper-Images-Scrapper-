import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import urllib.parse
import time

DESTINATION_FOLDER = r"E:\Data Science Internship\Images folder" # Set the destination folder

def sanitize_filename(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

def download_image(url, folder):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            if 'image' in content_type:
                filename = sanitize_filename(os.path.basename(urllib.parse.urlparse(url).path))
                if not filename or '.' not in filename:
                    ext = content_type.split('/')[-1]
                    filename = f'image_{str(hash(url))}.{ext}'
                file_path = os.path.join(folder, filename)
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(8192):
                        file.write(chunk)
                print(f"Downloaded: {filename}")
                return True
            else:
                print(f"Not an image: {url}")
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def scrape_bing_images(driver, num_images=100):
    """Scrapes image URLs from Bing image search."""
    image_urls = set()
    try:
        for _ in range(5):  # Adjust the number of scrolls as needed
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(2)

        images = driver.find_elements(By.CSS_SELECTOR, "img.mimg")  # Check this selector in browser  # Find image elements
        for img in images:
            src = img.get_attribute('src')
            if src and src.startswith('http'):
                image_urls.add(src)

        if len(image_urls) >= num_images:
            image_urls = list(image_urls)[:num_images]

        print(f"Found {len(image_urls)} image URLs.")
    except Exception as e:
        print(f"Error scraping images: {e}")

    return list(image_urls)

def extract_section_links(driver):
    """Extracts section URLs from the main page."""
    section_links = []
    try:
        
        sections = driver.find_elements(By.CSS_SELECTOR, "a.suggestion-item.has-foreground-img") # Find all section links
        print(f"Found {len(sections)} sections")  # Print number of sections found
        for section in sections:
            link = section.get_attribute('href')
            if link:
                if not link.startswith('http'): # Ensure the link is fully qualified
                    link = "https://www.bing.com" + link
                section_links.append(link)
                print(f"Extracted link: {link}")  # Print each extracted link
    except Exception as e:
        print(f"Error extracting section links: {e}")
    return section_links


def download_images_from_sections(driver, download_image_func):
    """Downloads images by visiting each section link and scraping images from those pages."""
    section_links = extract_section_links(driver)  # Extract section links
    for link in section_links:# Visit each section link and scrape images
        print(f"Visiting section: {link}")
        driver.get(link)  # Navigate to the section page
        image_urls = scrape_bing_images(driver)
        for url in image_urls: # Download images from the section
            download_image_func(url, DESTINATION_FOLDER)

def main():
    search_query = "mini cooper"
    os.makedirs(DESTINATION_FOLDER, exist_ok=True) # Ensure the destination folder exists
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(search_query)}" # 1. Get the initial search results page
        driver.get(url)
        print("Page loaded, starting to extract section links and images...")
        download_images_from_sections(driver, download_image)# 5. Download images from sections

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
