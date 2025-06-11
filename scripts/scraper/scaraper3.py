from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re
import csv

# Chrome headless setup
options = Options()
options.add_argument("--headless=new")  # 新しいヘッドレスモード
options.add_argument("--lang=fr-FR")    # フランス語設定
driver = webdriver.Chrome(service=Service(), options=options)

# Open Google Maps
driver.get("https://www.google.com/maps")

# Handle GDPR popup if present
try:
    accept_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label^='Accepter']"))
    )
    accept_button.click()
except NoSuchElementException:
    print("No GDPR popup detected.")
except:
    pass

# Wait for the search box and search
search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "searchboxinput"))
)
search_input.send_keys("Les parcs autour de l'École Polytechnique de Dakar")

# Submit the search
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "searchbox-searchbutton"))
)
search_button.click()

# Scroll to load more results
scrollable_div_xpath = '//div[@role="feed"]'
scrollable_div = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, scrollable_div_xpath))
)

prev_height = 0
retries = 0
while retries < 5:
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    time.sleep(2)
    new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    if new_height == prev_height:
        retries += 1
    else:
        retries = 0
        prev_height = new_height

# Extract search results
items = []
maps_items = driver.find_elements(By.XPATH, '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]')

for i, maps_item in enumerate(maps_items):
    try:
        link = maps_item.find_element(By.CSS_SELECTOR, "a[jsaction][jslog]").get_attribute("href")
        title = maps_item.find_element(By.CSS_SELECTOR, "div.fontHeadlineSmall").text

        maps_item.click()
        time.sleep(3)

        # Get address
        try:
            address = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Adresse') or contains(@aria-label, 'Address')]"))
            ).text
        except:
            address = ""

        # Extract lat/lng from URL
        current_url = driver.current_url
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
        lat, lng = match.groups() if match else ("", "")

        items.append({
            "title": title,
            "url": link,
            "address": address,
            "latitude": lat,
            "longitude": lng
        })

        driver.back()
        time.sleep(2)
    except Exception as e:
        print(f"Error on item {i}: {e}")
        continue

# Save to CSV
with open("parks_dakar.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["title", "url", "address", "latitude", "longitude"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in items:
        writer.writerow(item)

# Cleanup
driver.quit()