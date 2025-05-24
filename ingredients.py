import re
import json
from collections import defaultdict

# Load Tesco prices from JSON
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

def extract_ingredients(text):
    ingredients = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("- "):
            ingredients.append(line[2:])
        elif "Ingredients:" in line:
            parts = line.split("Ingredients:")[-1]
            items = [i.strip() for i in parts.split(",") if i.strip()]
            ingredients.extend(items)
    return ingredients

def estimate_costs(ingredients):
    totals = defaultdict(lambda: {"quantity": 0.0, "unit": "", "price": 0.0, "url": None})
    for item in ingredients:
        item_lower = item.lower()
        match = next((key for key in TESCO_PRICES if key in item_lower), None)

        if match:
            data = TESCO_PRICES[match]
            # Try to extract quantity if it exists (e.g., "200g chicken breast")
            quantity_match = re.search(r"(\d+)(g|kg|ml|l)?", item_lower)
            qty = float(quantity_match.group(1)) if quantity_match else 1.0
            unit = quantity_match.group(2) if quantity_match else ""

            # Use match key as the canonical name
            totals[match]["quantity"] += qty
            totals[match]["unit"] = unit or data.get("unit", "")
            totals[match]["price"] = data["price"]
            totals[match]["url"] = data["url"]
        else:
            totals[item]["quantity"] += 1.0
            totals[item]["unit"] = ""
            totals[item]["price"] = 2.00
            totals[item]["url"] = None

    shopping_list = []
    total = 0.0
    for item, info in totals.items():
        line = f"{item} – {info['quantity']:.0f}{info['unit']} – ~£{info['price']:.2f}"
        if info["url"]:
            line += f" ([View]({info['url']}))"
        shopping_list.append(line)
        total += info["price"]

    return shopping_list, total
