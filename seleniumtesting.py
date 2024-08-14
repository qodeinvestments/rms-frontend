from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Set up the web driver (Make sure to have the appropriate driver installed, e.g., chromedriver)
driver = webdriver.Chrome()

# Open the website in the first tab
driver.get('https://swandashboard.vercel.app/')

# Open multiple tabs
for i in range(50):  # Change the range to open more or fewer tabs
    driver.execute_script("window.open('https://swandashboard.vercel.app/', '_blank');")

# Keep the browser open for a while
import time
time.sleep(60)  # Keeps the browser open for 60 seconds
driver.quit()
