
import streamlit as st
import os
import json
import pandas as pd
import altair as alt
from meal_plan import generate_meal_plan
from ingredients import extract_ingredients, estimate_costs, PANTRY_STAPLES

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
        maint = (24 if profile["gender"] == "Male" else 22) * profile["weight"]
        mult_map = {"Sedentary": 1.2, "Lightly Active": 1.375, "Active": 1.55, "Athlete": 1.725}
        mult = mult_map.get(profile["lifestyle"], 1.2)
        daily_maint = int(maint * mult)
        if profile["goal"] == "Lose fat":
            target = daily_maint - 500
        elif profile["goal"] == "Build muscle":
            target = daily_maint + 300
        else:
            target = daily_maint

        prompt = f'''
Generate a {days}-day meal plan for a {profile['gender']} named {profile['name']} who weighs {profile['weight']} kg, lives a {profile['lifestyle']} lifestyle, and wants to {profile['goal']}.
Allergies: {profile['allergies']}. Diet type: {profile['diet_type']}. Avoid: {profile['dislikes']}.

Use approximately {target} kcal per day (±100 kcal), not exceeding 2800 kcal. Keep meals simple, affordable, and nutrient-dense for an active UK adult.
'''
        plan = generate_meal_plan(prompt, st.secrets["OPENAI_API_KEY"])

    st.markdown("---")
    st.subheader("📋 Meal Plan")
    days_output = plan.split("Day ")
    for day in days_output[1:]:
        header = day.split("\n")[0].strip()
        with st.expander(f"📅 Day {header}"):
            st.markdown(f"```{day}```")

    try:
        ingredients, calories = extract_ingredients(plan)
    except Exception as e:
        st.error(f"Failed to parse meal plan: {e}")
        ingredients, calories = {}, {}

    st.write("🧪 Debug:")
    st.json({"calories": calories, "ingredient_groups": len(ingredients)})

    if calories:
        st.subheader("🔥 Calories Per Day")
        for day, cals in sorted(calories.items()):
            st.write(f"{day}: {cals} kcal")

        cal_df = pd.DataFrame({"Day": list(calories.keys()), "Calories": list(calories.values())})
        target_line = target
        st.subheader("📊 Weekly Calorie Breakdown")
        chart = alt.Chart(cal_df).mark_bar(color="#4CAF50").encode(
            x=alt.X("Day", sort=list(calories.keys())),
            y=alt.Y("Calories")
        ).properties(width=600, height=400)
        line = alt.Chart(pd.DataFrame({"y": [target_line]})).mark_rule(
            color="red", strokeDash=[5, 5]
        ).encode(y="y")
        text = alt.Chart(cal_df).mark_text(
            align="center", dy=-10, size=12
        ).encode(
            x="Day",
            y="Calories",
            text="Calories"
        )
        st.altair_chart(chart + line + text, use_container_width=True)

   try:
    shopping_list, total_cost = estimate_costs(ingredients)
except Exception as e:
    st.error(f"Failed to estimate costs: {e}")
    shopping_list, total_cost = [], 0.0
        st.subheader("🛒 Weekly Shopping List & Estimated Cost")
        st.markdown(f"**Estimated Total Cost: ~£{total_cost:.2f}**")
        st.download_button("📥 Download Shopping List", "\n".join(shopping_list), file_name="shopping_list.txt")

        used_pantry = [item for item in ingredients.keys() if any(x in item for x in PANTRY_STAPLES)]
        if used_pantry:
            emoji_map = {
                "olive oil": "🫒", "salt": "🧂", "pepper": "🌶️", "soy sauce": "🍶",
                "lemon juice": "🍋", "vinegar": "🧴", "spices": "🧂"
            }
            emojis = " ".join(emoji_map.get(item, "🧂") for item in used_pantry)
            st.markdown(f"**Pantry staples used:** {emojis}")
    else:
        st.warning("No ingredients found. No shopping list available.")
