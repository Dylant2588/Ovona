
import re
import json
from collections import defaultdict
from typing import Tuple, Dict, List

# Load Tesco prices
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

PANTRY_STAPLES = {"olive oil", "salt", "pepper", "soy sauce", "vinegar", "lemon juice", "spices"}

# Normalize units and amounts
def parse_ingredient_line(line: str) -> Tuple[str, str, float]:
    match = re.match(r"^(.*)\((\d+)([a-zA-Z]+)\)$", line.strip())
    if match:
        name = match.group(1).strip().lower()
        amount = float(match.group(2))
        unit = match.group(3).lower()
        return name, unit, amount
    else:
        return line.strip().lower(), "", 1.0

def extract_ingredients(text: str) -> Tuple[Dict[str, Dict[str, float]], Dict[str, int]]:
    ingredients = defaultdict(lambda: defaultdict(float))
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
            name, unit, amount = parse_ingredient_line(stripped[2:])
            ingredients[name][unit] += amount

    return ingredients, calories_by_day

def estimate_costs(grouped_ingredients: Dict[str, Dict[str, float]]) -> Tuple[List[str], float]:
    total_cost = 0.0
    shopping_list = []
    fallback_cost = 2.5  # fallback cap

    for item, unit_map in grouped_ingredients.items():
        if item in PANTRY_STAPLES:
            continue  # skip pantry items

        for unit, quantity in unit_map.items():
            display_qty = f"{quantity:.0f}{unit}" if unit else f"{int(quantity)}"
            price = TESCO_PRICES.get(item, fallback_cost)
            if item not in TESCO_PRICES:
                shopping_list.append(f"{item.title()} – {display_qty}  *")
            else:
                shopping_list.append(f"{item.title()} – {display_qty}")
            total_cost += price * quantity

    return shopping_list, total_cost
