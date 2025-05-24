import re
import json
from collections import defaultdict

# Load data at top-level (no indent)
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

def extract_ingredients(text):
    # 4 spaces indent for function body
    ingredients = []
    lines = text.splitlines()
    for line in lines:
        # another 4 spaces for loop body
        line = line.strip()
        if line.startswith("- "):
            ingredients.append(line[2:])
    return ingredients

def estimate_costs(ingredients):
    # 4 spaces indent again
    totals = defaultdict(int)
    for item in ingredients:
        totals[item] += 1
    shopping_list = [f"{k}: {v}" for k, v in totals.items()]
    total_cost = sum(totals.values()) * 2.0
    return shopping_list, total_cost