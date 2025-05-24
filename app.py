import streamlit as st
import os
import json
from meal_plan import generate_meal_plan
from ingredients import extract_ingredients, estimate_costs

PROFILE_DB = "profiles.json"

# --- Load or initialize session profile ---
if "profile" not in st.session_state:
    st.session_state.profile = {}

# Auto-load single saved profile if exists
if not st.session_state.profile and os.path.exists(PROFILE_DB):
    with open(PROFILE_DB, "r") as f:
        stored = json.load(f)
    if len(stored) == 1:
        _, prof = next(iter(stored.items()))
        st.session_state.profile = prof

# --- Profile Setup ---
if not st.session_state.profile:
    st.title("👋 Welcome to Ovona AI Meal Planner")
    st.write("Let's set up your profile (we'll remember you next time).")

    with st.form("profile_form"):
        name = st.text_input("Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
        lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Lightly Active", "Active", "Athlete"])
        goal = st.selectbox("Goal", ["Lose fat", "Maintain weight", "Build muscle"])
        allergies = st.text_input("Allergies (comma-separated)")
        diet_type = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Vegan", "Keto", "High Protein"])
        dislikes = st.text_input("Dislikes or ingredients to avoid")
        submitted = st.form_submit_button("Save Profile")
        if submitted and name:
            profile = {
                "name": name,
                "gender": gender,
                "weight": weight,
                "lifestyle": lifestyle,
                "goal": goal,
                "allergies": allergies,
                "diet_type": diet_type,
                "dislikes": dislikes
            }
            st.session_state.profile = profile
            # Save to disk
            db = {}
            if os.path.exists(PROFILE_DB):
                with open(PROFILE_DB, "r") as f:
                    db = json.load(f)
            db[name] = profile
            with open(PROFILE_DB, "w") as f:
                json.dump(db, f)
            st.experimental_rerun()
    st.stop()

# --- Main Planner ---
st.set_page_config(page_title="Ovona AI Meal Planner")
st.title("🍽️ Ovona AI Meal Planner")

profile = st.session_state.profile
st.success(f"Hello {profile['name']}! Profile loaded: {profile['gender']}, {profile['weight']}kg, {profile['goal']}")

days = st.slider("Number of days", 1, 7, 5)

if st.button("Generate Plan"):
    with st.spinner("Generating your plan..."):
        # Calculate maintenance calories
        maint = (24 if profile["gender"] == "Male" else 22) * profile["weight"]
        mult_map = {"Sedentary": 1.2, "Lightly Active": 1.375, "Active": 1.55, "Athlete": 1.725}
        mult = mult_map.get(profile["lifestyle"], 1.2)
        daily_maint = int(maint * mult)
        # Adjust target based on goal
        if profile["goal"] == "Lose fat":
            target = daily_maint - 500
        elif profile["goal"] == "Build muscle":
            target = daily_maint + 300
        else:
            target = daily_maint

        # Build the prompt
        prompt = f"""
Generate a {days}-day meal plan for a {profile['gender']} named {profile['name']} who weighs {profile['weight']} kg, lives a {profile['lifestyle']} lifestyle, and wants to {profile['goal']}.
Allergies: {profile['allergies']}. Diet type: {profile['diet_type']}. Avoid: {profile['dislikes']}.

Use approximately {target} kcal per day (±100 kcal), not exceeding 2800 kcal. Keep meals simple, affordable, and nutrient-dense for an active UK adult.

Prefer affordable ingredients: chicken, turkey, tuna, eggs, oats, lentils, beans, rice, veg.
Avoid: luxury meats (steak, salmon), excessive snacks, duplicate high-calorie items.

Quantities must reflect **weekly totals**. Use UK-friendly shopping formats like:
- Chicken breast – 1.2 kg
- Eggs – 12
- Brown rice – 1 kg
- Milk – 2L semi-skimmed

For each day, use exactly this structure:

Day X
  Breakfast (YYY kcal): Meal description
  Lunch (YYY kcal): Meal description
  Dinner (YYY kcal): Meal description
  Total: ZZZ kcal
  Ingredients: item1 (qty), item2 (qty), …

At the end, include a Weekly Shopping List grouped by category, e.g.:

Meat
  - Chicken breast – 1 kg
  - Turkey mince – 500g

Vegetables
  - Carrots – 1 kg
  - Broccoli – 500g

Ensure realistic servings, precise quantities, and simple cooking methods.
"""
        plan = generate_meal_plan(prompt, st.secrets["OPENAI_API_KEY"])

    # Display plan
    st.markdown("---")
    st.subheader("📋 Meal Plan")
    st.code(plan)

    # Parse ingredients & calories
    try:
        result = extract_ingredients(plan)
        if isinstance(result, tuple) and len(result) == 2:
            ingredients, calories = result
        else:
            ingredients = result if isinstance(result, list) else []
            calories = {}
    except Exception as e:
        st.error(f"Failed to parse meal plan: {e}")
        ingredients, calories = [], {}

    # Show calories per day
    st.subheader("🔥 Calories Per Day")
    if calories:
        for day, cals in sorted(calories.items()):
            st.write(f"Day {day}: {cals} kcal")
    else:
        st.write("No calorie data available.")

    # Shopping list & cost
    shopping_list, total_cost = estimate_costs(ingredients)
    st.subheader("🛒 Weekly Shopping List & Estimated Cost")
    st.markdown("\n".join(shopping_list))
    st.markdown(f"**Estimated Total Cost: ~£{total_cost:.2f}**")
    st.download_button("📥 Download Shopping List", "\n".join(shopping_list), file_name="shopping_list.txt")

    # Raw output
    st.subheader("🧾 Raw Plan Output")
    st.code(plan)
