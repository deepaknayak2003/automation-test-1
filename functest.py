import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
import cv2
import numpy as np
from mss import mss
import threading

# Configuration
URL = "https://demo.dealsdray.com/"
USERNAME = "prexo.mis@dealsdray.com"
PASSWORD = "prexo.mis@dealsdray.com"
XLS_FILE_PATH = r"D:\demo-data.xlsx"  # Update this with the actual path
VIDEO_OUTPUT_PATH = "test_run_video.avi"
SCREENSHOT_OUTPUT_PATH = "final_output_screenshot.png"

# Global flag to stop recording
recording = True

def record_screen(output_video_path, duration):
    sct = mss()
    monitor = sct.monitors[0]
    width, height = monitor["width"], monitor["height"]
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (width, height))

    start_time = time.time()
    while recording and (time.time() - start_time < duration):
        img = sct.grab(monitor)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
        out.write(frame)

    out.release()
    print(f"Screen recording saved: {output_video_path}")

def main():
    global recording
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Maximize the browser window
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 60)  # Increased wait time to 60 seconds

    try:
        # Start the screen recording in a separate thread
        video_thread = threading.Thread(target=record_screen, args=(VIDEO_OUTPUT_PATH, 300))
        video_thread.start()

        # Step 1: Log in
        driver.get(URL)
        print("Navigated to the login page")

        # Check if the username field is present
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        print("Username field found")

        # Check if the password field is present
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        print("Password field found")

        # Check if the login button is clickable
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]")))
        print("Login button found and clickable")

        # Enter credentials and login
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        login_button.click()
        print("Credentials entered and login button clicked")

        # Ensure that the login was successful by checking if the next page loads
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Order']")))
        print("Logged in successfully")

        # Step 2: Click on "Order" in the left menu
        order_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Order']")))
        order_menu.click()
        print("Clicked on 'Order' in the left menu")

        # Step 3: Click on "Orders"
        orders_submenu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Orders']")))
        orders_submenu.click()
        print("Clicked on 'Orders' under 'Order'")

        # Step 4: Click on "Add Bulk Orders"
        add_bulk_orders_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Bulk Orders')]")))
        add_bulk_orders_button.click()
        print("Clicked on 'Add Bulk Orders'")

        # Step 5: Upload the file
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        file_input.send_keys(XLS_FILE_PATH)
        print("File uploaded")

        # Step 6: Click the 'Import' button
        import_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Import']")))
        import_button.click()
        print("Clicked on 'Import' button")

        # Step 7: Click the 'Validate Data' button
        validate_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Validate Data']")))
        validate_button.click()
        print("Clicked on 'Validate Data' button")

        # Handle alert
        try:
            alert = wait.until(EC.alert_is_present())
            alert.accept()
            print("Alert accepted")
        except Exception as e:
            print(f"Exception while handling alert: {e}")

        # Wait for validation to complete (adjust XPath if needed)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Validation completed')]")))
            print("Validation completed message found")
        except Exception as e:
            print(f"Exception while waiting for validation: {e}")

        # Step 8: Take a screenshot of the visible part of the page
        screenshot = driver.get_screenshot_as_png()
        with open(SCREENSHOT_OUTPUT_PATH, 'wb') as file:
            file.write(screenshot)
        print(f"Screenshot of visible page saved: {SCREENSHOT_OUTPUT_PATH}")

    finally:
        # Stop the recording
        recording = False
        video_thread.join()
        driver.quit()

if __name__ == "__main__":
    main()
