import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

INGREDIENTS = [
    "chicken breast", "brown rice", "broccoli", "salmon", "oats", "eggs",
    "greek yogurt", "banana", "almonds", "avocado", "spinach", "sweet potato"
]

BASE_URL = "https://www.tesco.com/groceries/en-GB/search?query={}"  # URL-encoded ingredient name

results = {}

for ingredient in INGREDIENTS:
    print(f"Scraping: {ingredient}")
    search_url = BASE_URL.format(ingredient.replace(" ", "%20"))
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch {ingredient}")
            results[ingredient] = {
                "product": "Unavailable",
                "price": 2.00,
                "unit": "",
                "url": None
            }
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        product_card = soup.find("div", class_="product-list--list-item")

        if product_card:
            name_tag = product_card.find("a", class_="styled__Anchor-sc-1xbujuz-0")
            price_tag = product_card.find("span", class_="value")
            unit_tag = product_card.find("span", class_="weight")

            if name_tag and price_tag:
                name = name_tag.text.strip()
                price = float(price_tag.text.strip())
                url = "https://www.tesco.com" + name_tag.get("href")
                unit = unit_tag.text.strip() if unit_tag else ""
                results[ingredient] = {
                    "product": name,
                    "price": price,
                    "unit": unit,
                    "url": url
                }
            else:
                print(f"⚠️ Missing tags for {ingredient}")
                results[ingredient] = {
                    "product": "Not found",
                    "price": 2.00,
                    "unit": "",
                    "url": None
                }
        else:
            print(f"⚠️ No product card found for {ingredient}")
            results[ingredient] = {
                "product": "Not found",
                "price": 2.00,
                "unit": "",
                "url": None
            }

        time.sleep(1.5)  # be nice to Tesco

    except Exception as e:
        print(f"❌ Error fetching {ingredient}: {e}")
        results[ingredient] = {
            "product": "Error",
            "price": 2.00,
            "unit": "",
            "url": None
        }

with open("tesco_prices.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("✅ Finished scraping Tesco prices!")
