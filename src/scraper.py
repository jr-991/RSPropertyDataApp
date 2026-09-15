import tkinter as tk
import scraper
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright
from enum import Enum
from typing import Optional
import json
import os
import random
import time

# Constants for handling HTTP 429 responses and request delays
MAX_RETRIES_ON_429 = 3
DEFAULT_RETRY_AFTER = 5
REQUEST_DELAY_RANGE = (1, 3)

class State(Enum):
    New_York = "New-York"
    Nevada = "Nevada"
    Idaho = "Idaho"
    Texas = "Texas"
    Arizona = "Arizona"
    Illinois = "Illinois"
    California = "California"
    Washington = "Washington"
    North_Carolina = "North-Carolina"
    Florida = "Florida"

def fetch(state: Optional[State] = None, pgLow: int = 1, pgHigh: Optional[int] = None):
    properties = []

    # Initialize Playwright and launch a headless browser 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(pgLow, (pgHigh or pgLow) + 1):
            if not state:
                url = f"https://www.realtor.com/realestateforsale"
            else:
                url = f"https://www.realtor.com/realestateandhomes-search/{state.value}/pg-{page_num}"

            if page_num > pgLow:
                time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

            # Retry / delay logic to prevent or handle HTTP 429 responses (Too Many Requests)
            nav_response = None
            for attempt in range(MAX_RETRIES_ON_429 + 1):
                nav_response = page.goto(url, wait_until="domcontentloaded", timeout=20000)

                if nav_response is not None and nav_response.status == 429:
                    if attempt == MAX_RETRIES_ON_429:
                        print(f"Giving up on {url} after repeated 429 responses.")
                        break

                    retry_after = nav_response.headers.get("retry-after")
                    wait_seconds = float(retry_after) if retry_after and retry_after.isdigit() else DEFAULT_RETRY_AFTER
                    print(f"Got 429 for {url}, waiting {wait_seconds}s before retry {attempt + 1}/{MAX_RETRIES_ON_429}")
                    time.sleep(wait_seconds)
                    continue

                break

            if nav_response is not None and nav_response.status == 429:
                continue

            response = page.content()

            soup = BeautifulSoup(response, "html.parser")

            json_script = soup.find_all("script", type="application/ld+json")

            # Debug information
            print("HTML length:", len(response)) # Print the length of the HTML response
            print("Listings found:", len(json_script)) # Print the number of listings found
            print("Fetching properties from:", url) # Log the URL being fetched / debug information

            # Iterate through each JSON script block found in the HTML response
            for script in json_script:

                try: 
                    data = json.loads(script.string)

                except (json.JSONDecodeError, TypeError) as e:
                    print("Error parsing JSON:", e)
                    continue

                if not isinstance(data, dict):
                    continue
                
                main_entity = data.get("mainEntity", {}) # Get the main entity from the JSON data

                if not isinstance(main_entity, dict):
                    continue

                if main_entity.get("@type") != "ItemList": # Skip if the main entity is not an item list
                    continue

                listings = main_entity.get("itemListElement", []) # Get the list of item list elements from the main entity

                # Iterate through each listing in the item list element
                for listing in listings:
                    entity = listing.get("mainEntity", {})
                    address = entity.get("address", {})

                    property_data = {
                        "price": listing.get("offers", {}).get("price"),
                        "address": address.get("streetAddress"),
                        "city": address.get("addressLocality"),
                        "state": address.get("addressRegion"),
                        "postal_code": address.get("postalCode"),
                        "bedrooms": entity.get("numberOfBedrooms"),
                        "floor_size": entity.get("floorSize", {}).get("value"),
                        "latitude": entity.get("geo", {}).get("latitude"),
                        "longitude": entity.get("geo", {}).get("longitude"),
                        "url": listing.get("url"),
                    }
                    properties.append(property_data)
                    print("Fetched property:", property_data)

                    # Log the fetched property to a file for debugging purposes
                    with open(os.path.join(os.path.dirname(__file__), "data", "fetched_properties.txt"), "a", encoding="utf-8") as file:
                        file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M")) + ", " + json.dumps(property_data) + "\n")

                break

    return properties
