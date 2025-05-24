import streamlit as st
import os
import json
from meal_plan import generate_meal_plan
from ingredients import extract_ingredients, estimate_costs

PROFILE_DB = "profiles.json"

# --- Load profile from session or query params or disk ---
def load_profile():
    # 1. from session
    if "profile" in st.session_state and st.session_state.profile:
        return
    # 2. from query params
    params = st.experimental_get_query_params()
    if "user" in params:
        name = params["user"][0]
        # load from disk
        if os.path.exists(PROFILE_DB):
            with open(PROFILE_DB, "r") as f:
                db = json.load(f)
            if name in db:
                st.session_state.profile = db[name]
                return
    # 3. no profile yet
    st.session_state.profile = {}

load_profile()

# --- Profile Setup ---
if not st.session_state.profile:
    st.title("👋 Welcome to Ovona AI Meal Planner")
    st.write("Let's set up your profile (we'll remember you next time).")
    with st.form(key="profile_form"):
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
            # save to session
            st.session_state.profile = {
                "name": name,
                "gender": gender,
                "weight": weight,
                "lifestyle": lifestyle,
                "goal": goal,
                "allergies": allergies,
                "diet_type": diet_type,
                "dislikes": dislikes
            }
            # save to disk
            db = {}
            if os.path.exists(PROFILE_DB):
                with open(PROFILE_DB, "r") as f:
                    db = json.load(f)
            db[name] = st.session_state.profile
            with open(PROFILE_DB, "w") as f:
                json.dump(db, f)
            # set query param for persistent recall
            st.experimental_set_query_params(user=name)
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
        prompt = f"""
Generate a {days}-day meal plan for a {profile['gender']} named {profile['name']} who weighs {profile['weight']}kg, lives a {profile['lifestyle']} lifestyle, and wants to {profile['goal']}.
Allergies: {profile['allergies']}. Diet type: {profile['diet_type']}. Avoid: {profile['dislikes']}.

Each day must include:
1. Breakfast, lunch, and dinner with calorie estimates in parentheses.
2. Total calories for the day as 'Total: X kcal'.
3. A bullet-point list of ingredients after each day, formatted 'Ingredients: chicken breast, carrots, ...'.
Ensure the plan is varied—include fish for omegas, steak for iron, etc.
"""
        plan = generate_meal_plan(prompt, st.secrets["OPENAI_API_KEY"])

    st.markdown("---")
    st.subheader("📋 Meal Plan")
    st.code(plan)

    # Parse
    ingredients, calories = extract_ingredients(plan)

    # Calories per day
    st.subheader("🔥 Calories Per Day")
    for day, cals in calories.items():
        st.write(f"**Day {day}** – {cals} kcal")

    # Shopping list & cost
    shopping_list, total_cost = estimate_costs(ingredients)
    st.subheader("🛒 Shopping List & Estimated Cost")
    st.markdown("\n".join(shopping_list))
    st.markdown(f"**Estimated Total Cost: ~£{total_cost:.2f}**")
    st.download_button("📥 Download Shopping List", "\n".join(shopping_list), file_name="shopping_list.txt")

    st.subheader("🧾 Raw Plan Output")
    st.code(plan)
