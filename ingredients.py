import re
import json
from collections import defaultdict

# Load Tesco prices from JSON
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

CATEGORY_MAP = {
    "meat": ["chicken", "beef", "mince", "steak", "pork", "salmon", "turkey"],
    "vegetables": ["carrot", "broccoli", "spinach", "pepper", "lettuce", "onion", "potato", "tomato"],
    "fruit": ["banana", "apple", "orange", "avocado", "berries"],
    "cupboard": ["rice", "pasta", "stock", "oats", "almond", "oil", "spice", "salt", "pepper"],
    "dairy": ["milk", "cheese", "yogurt", "butter", "egg"],
    "other": []
}

def get_category(ingredient):
    for category, keywords in CATEGORY_MAP.items():
        if any(k in ingredient for k in keywords):
            return category
    return "other"

def extract_ingredients(text):
    ingredients = []
    calories_per_day = defaultdict(int)
    current_day = 1
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if re.match(r"(?i)day \d+", line):
            current_day = int(re.findall(r"\d+", line)[0])
        elif line.lower().startswith("calories"):
            cal_match = re.search(r"(\d+)", line)
            if cal_match:
                calories_per_day[current_day] += int(cal_match.group(1))
        elif line.startswith("- "):
            ingredients.append(line[2:])
        elif "Ingredients:" in line:
            parts = line.split("Ingredients:")[-1]
            items = [i.strip() for i in parts.split(",") if i.strip()]
            ingredients.extend(items)
        elif any(kw in line.lower() for kw in ["adjust", "ensure", "incorporate"]):
            continue
        elif any(char.isalpha() for char in line) and any(char.isdigit() for char in line):
            ingredients.append(line)
    return ingredients, dict(calories_per_day)

def estimate_costs(ingredients):
    grouped = defaultdict(lambda: defaultdict(lambda: {"quantity": 0.0, "unit": "", "price": 0.0, "url": None}))
    total = 0.0

    for item in ingredients:
        item_lower = item.lower()
        match = next((key for key in TESCO_PRICES if key in item_lower), None)
        quantity_match = re.search(r"(\d+)(g|kg|ml|l|each|pack|tub|eggs)?", item_lower)
        qty = float(quantity_match.group(1)) if quantity_match else 1.0
        unit = quantity_match.group(2) if quantity_match else ""

        # Clean unit output
        if unit == "each":
            unit = ""
        elif unit in ["tub", "pack"]:
            unit += "s"
        elif unit == "eggs":
            unit = " eggs"

        category = get_category(item_lower)
        key = match if match else item_lower

        if match:
            data = TESCO_PRICES[match]
            grouped[category][key]["quantity"] += qty
            grouped[category][key]["unit"] = unit or data.get("unit", "")
            grouped[category][key]["price"] = data["price"]
            grouped[category][key]["url"] = data["url"]
            total += data["price"]
        else:
            grouped[category][key]["quantity"] += qty
            grouped[category][key]["unit"] = unit
            grouped[category][key]["price"] = 2.00
            grouped[category][key]["url"] = None
            total += 2.00

    shopping_list = []
    for category in sorted(grouped.keys()):
        shopping_list.append(f"**{category.title()}**")
        for item, info in grouped[category].items():
            qty_display = f"{info['quantity']:.0f}{info['unit']}".strip()
            line = f"- {item} – {qty_display}"
            if info["url"]:
                line += f" ([View]({info['url']}))"
            shopping_list.append(line)
        shopping_list.append("")

    return shopping_list, total
