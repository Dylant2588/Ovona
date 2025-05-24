
import re
import json
from collections import defaultdict
from typing import Tuple, Dict, List

# Load Tesco prices
with open("tesco_prices.json", "r") as f:
    TESCO_PRICES = json.load(f)

PANTRY_STAPLES = {"olive oil", "salt", "pepper", "soy sauce", "vinegar", "lemon juice", "spices"}

# Unit mapping for vague terms
UNIT_CONVERSIONS = {
    "handful": ("g", 30),
    "scoop": ("g", 30),
    "cup": ("ml", 240),
    "tbsp": ("ml", 15),
    "tsp": ("ml", 5),
    "slice": ("unit", 1),
    "egg": ("unit", 1),
    "eggs": ("unit", 1),
    "clove": ("unit", 1)
}

def parse_natural_line(line: str) -> Tuple[str, str, float]:
    # Match patterns like: "1 cup spinach", "2 eggs", "30g almonds"
    match = re.match(r"[-*]\s*(\d+(?:\.\d+)?)(\s*[a-zA-Z]+)?\s+(.+)", line.strip())
    if match:
        amount = float(match.group(1))
        raw_unit = (match.group(2) or "").strip().lower()
        name = match.group(3).strip().lower().rstrip(".,")

        # If unit is vague like "handful", convert
        if raw_unit in UNIT_CONVERSIONS:
            unit, factor = UNIT_CONVERSIONS[raw_unit]
            return name, unit, amount * factor
        elif raw_unit in {"g", "kg", "ml", "l", "tbsp", "tsp"}:
            return name, raw_unit, amount
        elif raw_unit:  # catch all as 'unit' for now
            return name, raw_unit, amount
        else:
            return name, "", amount
    return line.strip().lower(), "", 1.0

def is_valid_ingredient_line(line: str) -> bool:
    return bool(re.match(r"[-*]\s*(\d+).*", line.strip()))

def clean_name(raw: str) -> str:
    return raw.lower().split(" with ")[0].split(" and ")[0].strip(" -:")

def extract_ingredients(text: str) -> Tuple[Dict[str, Dict[str, float]], Dict[str, int]]:
    ingredients = defaultdict(lambda: defaultdict(float))
    calories_by_day = {}
    current_day = None

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith("day "):
            match = re.search(r"Day\s+(\d+)", stripped, re.IGNORECASE)
            if match:
                current_day = f"Day {match.group(1)}"

        kcal_match = re.search(r"(\d+)\s*kcal", stripped, re.IGNORECASE)
        if kcal_match and current_day:
            calories_by_day.setdefault(current_day, 0)
            calories_by_day[current_day] += int(kcal_match.group(1))

        if is_valid_ingredient_line(stripped):
            name, unit, amount = parse_natural_line(stripped)
            name = clean_name(name)
            ingredients[name][unit] += amount

    return ingredients, calories_by_day

def estimate_costs(grouped_ingredients: Dict[str, Dict[str, float]]) -> Tuple[List[str], float]:
    total_cost = 0.0
    shopping_list = []
    fallback_cost = 2.5

    for item, unit_map in grouped_ingredients.items():
        is_pantry = any(pantry in item for pantry in PANTRY_STAPLES)
        if is_pantry:
            continue

        for unit, quantity in unit_map.items():
            display_qty = f"{quantity:.0f}{unit}" if unit else f"{int(quantity)}"
            price = TESCO_PRICES.get(item, fallback_cost)
            label = f"{item.title()} – {display_qty}"
            if item not in TESCO_PRICES:
                label += "  *"
            shopping_list.append(label)
            try:
                total_cost += price * float(quantity)
            except (TypeError, ValueError):
                total_cost += price

    return shopping_list, total_cost
