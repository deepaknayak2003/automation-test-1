import os
import time
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import numpy as np

# ADD YOUR WEBSITE LINKS HERE
urls_to_test = [
    "https://www.getcalley.com/",
    "https://www.getcalley.com/calley-lifetime-offer/",
    "https://www.getcalley.com/see-a-demo/",
    "https://www.getcalley.com/calley-teams-features/",
    "https://www.getcalley.com/calley-pro-features/"
    # Add more URLs as needed
]

def take_full_page_screenshot(driver, url, output_path):
    try:
        driver.get(url)
        time.sleep(2)
        
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        slices = []
        
        for i in range(0, total_height, viewport_height):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.5)
            slices.append(np.array(Image.open(BytesIO(driver.get_screenshot_as_png()))))
        
        full_image = np.vstack(slices)
        Image.fromarray(full_image).save(output_path)
        print(f"Screenshot saved: {output_path}")
    except Exception as e:
        print(f"Error taking screenshot for {url}: {e}")

def validate_page(driver, url):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "Error" not in driver.title
        print(f"Page validated successfully: {url}")
    except Exception as e:
        print(f"Validation failed for {url}: {str(e)}")

def main():
    browsers = ["Chrome", "Firefox"]
    resolutions = {
        "Desktop": ["1920x1080", "1366x768", "1536x864"],
        "Mobile": ["360x640", "414x896", "375x667"]
    }
    
    for browser in browsers:
        if browser == "Chrome":
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
        elif browser == "Firefox":
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service)
        
        try:
            for device, res_list in resolutions.items():
                for resolution in res_list:
                    width, height = map(int, resolution.split("x"))
                    driver.set_window_size(width, height)
                    
                    for url in urls_to_test:
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        folder_path = os.path.join(browser, device, resolution)
                        os.makedirs(folder_path, exist_ok=True)
                        file_name = f"Screenshot-{timestamp}.png"
                        output_path = os.path.join(folder_path, file_name)
                        
                        take_full_page_screenshot(driver, url, output_path)
                        validate_page(driver, url)
        finally:
            driver.quit()

if __name__ == "__main__":
    main()