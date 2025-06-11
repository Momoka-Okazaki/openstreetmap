from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import csv

# to launch Chrome in headless mode
options = Options()
options.add_argument("--headless") # comment it while developing

# create a Chrome web driver instance with the
# specified options
driver = webdriver.Chrome(
    service=Service(),
    options=options
)

# connect to the Google Maps home page
driver.get("https://www.google.com/maps")

# to deal with the option GDPR options
try:
     # select the "Accept all" button from the GDPR cookie option page
    accept_button = driver.find_element(By.CSS_SELECTOR, "[aria-label=\"Accept all\"]")
    # click it
    accept_button.click()
except NoSuchElementException:
    print("No GDPR requirenments")

# select the search input and fill it in
search_input = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#searchboxinput"))
)
from selenium.webdriver.common.keys import Keys
search_query = "italian restaurants"
search_input.send_keys(search_query + Keys.ENTER)

# where to store the scraped data
items = []

# select the Google Maps items
maps_items = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//div[@role="feed"]//div[contains(@jsaction, "mouseover:pane")]'))
)

# iterate over the Google Maps items and
# perform the scraping logic
for maps_item in maps_items:
    link_element = maps_item.find_element(By.CSS_SELECTOR, "a[jsaction][jslog]")
    url = link_element.get_attribute("href")

    title_element = maps_item.find_element(By.CSS_SELECTOR, "div.fontHeadlineSmall")
    title = title_element.text

    reviews_element = maps_item.find_element(By.CSS_SELECTOR, "span[role=\"img\"]")
    reviews_string = reviews_element.get_attribute("aria-label")

    # define a regular expression pattern to extract the stars and reviews count
    reviews_string_pattern = r"(\d+\.\d+) stars (\d+[,]*\d+) Reviews"

    # use re.match to find the matching groups
    reviews_string_match = re.match(reviews_string_pattern, reviews_string)

    reviews_stars = None
    reviews_count = None

    # if a match is found, extract the data
    if reviews_string_match:
        # convert stars to float
        reviews_stars = float(reviews_string_match.group(1))
        # convert reviews count to integer
        reviews_count = int(reviews_string_match.group(2).replace(",", ""))

    # select the Google Maps item <div> with most info
    # and extract data from it
    info_div = maps_item.find_element(By.CSS_SELECTOR, ".fontBodyMedium")

    # scrape the price, if present
    try:
        price_element = info_div.find_element(By.XPATH, ".//*[@aria-label[contains(., 'Price')]]")
        price = price_element.text
    except NoSuchElementException:
        price = None

    info = []
    # select all <span> elements with no attributes or the @style attribute
    # and descendant of a <span>
    span_elements = info_div.find_elements(By.XPATH, ".//span[not(@*) or @style][not(descendant::span)]")
    for span_element in span_elements:
      info.append(span_element.text.replace("⋅", "").strip())

    # to remove any duplicate info and empty strings
    info = list(filter(None, list(set(info))))

    img_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img[decoding=\"async\"][aria-hidden=\"true\"]"))
    )
    image = img_element.get_attribute("src")

    # select the tag <div> element and extract data from it
    tags_div = maps_item.find_elements(By.CSS_SELECTOR, ".fontBodyMedium")[-1]
    tags = []
    tag_elements = tags_div.find_elements(By.CSS_SELECTOR, "span[style]")
    for tag_element in tag_elements:
      tags.append(tag_element.text)

    # populate a new item with the scraped data
    item = {
      "url": url,
      "image": image,
      "title": title,
      "reviews": {
        "stars": reviews_stars,
        "count": reviews_count
      },
      "price": price,
      "info": info,
      "tags": tags
    }
    # add it to the list of scraped data
    items.append(item)

# output CSV file path
output_file = "items.csv"

# flatten and export to CSV
with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
    # define the CSV field names
    fieldnames = ["url", "image", "title", "reviews_stars", "reviews_count", "price", "info", "tags"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # write the header
    writer.writeheader()

    # write each item, flattening info and tags
    for item in items:
        writer.writerow({
            "url": item["url"],
            "image": item["image"],
            "title": item["title"],
            "reviews_stars": item["reviews"]["stars"],
            "reviews_count": item["reviews"]["count"],
            "price": item["price"],
            "info": "; ".join(item["info"]),
            "tags": "; ".join(item["tags"])
        })

# close the web browser
driver.quit()