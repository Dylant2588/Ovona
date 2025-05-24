import streamlit as st
import os
import json
from meal_plan import generate_meal_plan
from ingredients import extract_ingredients, estimate_costs

# Constants
deFAULT_PROFILE_DB = "profiles.json"

# --- Load or initialize profile ---
if "profile" not in st.session_state:
    st.session_state.profile = {}

# Try loading profile from session or disk
if not st.session_state.profile:
    params = st.experimental_get_query_params()
    if "user" in params:
        name = params["user"][0]
        if os.path.exists(deFAULT_PROFILE_DB):
            with open(deFAULT_PROFILE_DB, "r") as f:
                db = json.load(f)
            if name in db:
                st.session_state.profile = db[name]

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
            if os.path.exists(deFAULT_PROFILE_DB):
                with open(deFAULT_PROFILE_DB, "r") as f:
                    db = json.load(f)
            db[name] = profile
            with open(deFAULT_PROFILE_DB, "w") as f:
                json.dump(db, f)
            # Persist query param
            st.set_query_params(user=name)  # persist user in URL
            # st.experimental_rerun()  # Not needed; Streamlit auto-reruns on form submit
    st.stop()

# --- Main Planner ---
st.set_page_config(page_title="Ovona AI Meal Planner")
st.title("🍽️ Ovona AI Meal Planner")
profile = st.session_state.profile
st.success(f"Hello {profile['name']}! Profile loaded: {profile['gender']}, {profile['weight']}kg, {profile['goal']}")

days = st.slider("Number of days", 1, 7, 5)

if st.button("Generate Plan"):
    with st.spinner("Generating your plan..."):
        # Calculate target calories
        if profile["gender"] == "Male":
            maint = 24 * profile["weight"]
        else:
            maint = 22 * profile["weight"]
        mult = {"Sedentary":1.2, "Lightly Active":1.375, "Active":1.55, "Athlete":1.725}[profile["lifestyle"]]
        daily_maint = int(maint * mult)
        if profile["goal"] == "Lose fat":
            target = daily_maint - 500
        elif profile["goal"] == "Build muscle":
            target = daily_maint + 300
        else:
            target = daily_maint

        # Build prompt
        prompt = f"""
Generate a {days}-day meal plan for a {profile['gender']} named {profile['name']} who weighs {profile['weight']} kg, lives a {profile['lifestyle']} lifestyle, and wants to {profile['goal']}.  
Allergies: {profile['allergies']}. Diet type: {profile['diet_type']}. Avoid: {profile['dislikes']}.  

Use approximately **{target}** kcal per day (±100 kcal).  

**For each day**, output exactly this structure:

Day X  
  Breakfast (YYY kcal): Meal description  
  Lunch (YYY kcal): Meal description  
  Dinner (YYY kcal): Meal description  
  **Total: ZZZ kcal**  
  **Ingredients:** item1 (qty), item2 (qty), …  

**At the very end**, after all days, include a single **Weekly Shopping List** section, grouped by category, with each ingredient and total quantity needed for the week, e.g.:

**Meat**  
- Chicken breast – 1 kg  
- Salmon fillets – 2 × 150 g  

**Vegetables**  
- Carrots – 1 kg  
- Broccoli – 500 g  

…and so on.  
Keep servings realistic and quantities precise.  
Ensure variety (fish, steak, legumes, etc.) and simple cooking methods.
"""
        plan = generate_meal_plan(prompt, st.secrets["OPENAI_API_KEY"])

    # Output plan
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
    st.subheader("🛒 Weekly Shopping List & Estimated Cost")
    st.markdown("\n".join(shopping_list))
    st.markdown(f"**Estimated Total Cost: ~£{total_cost:.2f}**")
    st.download_button("📥 Download Shopping List", "\n".join(shopping_list), file_name="shopping_list.txt")

    st.subheader("🧾 Raw Plan Output")
    st.code(plan)
