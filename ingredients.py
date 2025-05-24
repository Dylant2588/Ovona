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
    # No URL persistence; use session state only

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
            st.set_query_params(user=name)  
