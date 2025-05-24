import re

ESTIMATED_PRICES = {
    "chicken breast": 5.50,
    "broccoli": 1.20,
    "brown rice": 1.00,
    "eggs": 2.00,
    "oats": 1.80,
    "banana": 0.20,
    "greek yogurt": 1.50,
    "almonds": 2.50,
    "salmon": 6.00,
    "avocado": 1.20,
}

def extract_ingredients(text):
    return re.findall(r"- ([A-Za-z0-9 ,()]+)\\n", text)

def estimate_costs(ingredients):
    shopping_list = []
    total = 0.0
    for item in ingredients:
        item_lower = item.lower()
        price = next((ESTIMATED_PRICES[p] for p in ESTIMATED_PRICES if p in item_lower), 2.00)
        shopping_list.append(f"{item} – ~£{price:.2f}")
        total += price
    return shopping_list, total