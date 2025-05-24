import re
import json

# Load Tesco prices from JSON
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

def extract_ingredients(text):
    ingredients = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        # Bullet points
        if line.startswith("- "):
            ingredients.append(line[2:])
        # Inline Ingredients: chicken, rice, etc
        elif "Ingredients:" in line:
            parts = line.split("Ingredients:")[-1]
            items = [i.strip() for i in parts.split(",") if i.strip()]
            ingredients.extend(items)
    return ingredients

def estimate_costs(ingredients):
    shopping_list = []
    total = 0.0
    for item in ingredients:
        item_lower = item.lower()
        match = next((TESCO_PRICES[k] for k in TESCO_PRICES if k in item_lower), None)
        if match:
            price = match["price"]
            link = match["url"]
            display = f"{item} – ~£{price:.2f} ([View]({link}))"
        else:
            price = 2.00
            display = f"{item} – ~£2.00"
        shopping_list.append(display)
        total += price
    return shopping_list, total
