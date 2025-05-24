import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Fifth-9 Meal Planner", layout="centered")
st.title("🥗 AI-Powered Meal Planner (MVP)")
st.caption("From your lifestyle to your weekly meals — personalized by AI")

# --- Simulated Login ---
with st.expander("🔐 Login (Simulated)", expanded=True):
    user = st.selectbox("Select your profile", ["Select user", "Dylan", "Guest"])

if user and user != "Select user":
    st.success(f"Logged in as {user}")

    # --- Step 1: Personal Data ---
    st.header("Step 1: Your Info")
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=75)
        lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Lightly Active", "Active", "Athlete"])
    with col2:
        goal = st.selectbox("Goal", ["Lose fat", "Maintain weight", "Build muscle"])
        allergies = st.text_input("Allergies (comma-separated)")

    # --- Step 2: Preferences ---
    st.header("Step 2: Preferences")
    diet_type = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Vegan", "Keto", "High Protein"])
    dislikes = st.text_input("Dislikes or ingredients to avoid")

    # --- Step 3: Meal Plan ---
    st.header("Step 3: Generate Your Meal Plan")
    days = st.slider("How many days?", min_value=1, max_value=7, value=5)
    if st.button("Generate Plan"):
        with st.spinner("Planning your meals..."):
            prompt = f"""
You are a nutrition coach. Generate a meal plan for a person with the following:
- Weight: {weight}kg
- Lifestyle: {lifestyle}
- Goal: {goal}
- Allergies: {allergies}
- Diet Type: {diet_type}
- Dislikes: {dislikes}

Create a meal plan for {days} days, with breakfast, lunch, and dinner.
Each meal should include a calorie estimate. Keep it simple and repeatable when possible.
Output in a clear, easy-to-read format. I also need you to think of things like, when last did this person have Fish? Etc, and rotate that into their diet for micro nutrients.
"""
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            plan = response.choices[0].message.content
            st.success("Done! Here's your plan:")
            st.markdown(plan)
            st.download_button("📄 Download Plan", plan, file_name="meal_plan.txt")
else:
    st.warning("Please log in to continue.")
