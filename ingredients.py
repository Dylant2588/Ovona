import re
import json
from collections import defaultdict

# Load Tesco prices
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

def extract_ingredients(text):
    ingredients = []
    calories_by_day = {}
    current_day = None

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()

        # Detect Day number
        if stripped.startswith("📅 Day") or stripped.startswith("Day "):
            match = re.search(r"Day\s+(\d+)", stripped)
            if match:
                current_day = f"Day {match.group(1)}"

        # Detect total calories (markdown bold optional)
        if "Total:" in stripped:
            kcal_match = re.search(r"Total:\s*(\d+)\s*kcal", stripped)
            if kcal_match and current_day:
                calories_by_day[current_day] = int(kcal_match.group(1))

        # Detect ingredient lines
        if stripped.startswith("- "):
            ingredients.append(stripped[2:])

    return ingredients, calories_by_day