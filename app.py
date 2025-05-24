import streamlit as st
from meal_plan import generate_meal_plan
from ingredients import extract_ingredients, estimate_costs

st.set_page_config(page_title="Ovona AI Meal Planner")
st.title("🍽️ Ovona AI Meal Planner")

# --- Simulated Login ---
user = st.selectbox("Select user", ["Select", "Dylan", "Guest"])
if user == "Select":
    st.stop()
st.success(f"Logged in as {user}")

# --- User Input ---
st.header("User Preferences")
weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=75)
lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Lightly Active", "Active", "Athlete"])
goal = st.selectbox("Goal", ["Lose fat", "Maintain weight", "Build muscle"])
allergies = st.text_input("Allergies (comma-separated)")
diet_type = st.selectbox("Diet Type", ["Standard", "Vegetarian", "Vegan", "Keto", "High Protein"])
dislikes = st.text_input("Dislikes or ingredients to avoid")
days = st.slider("Number of days", 1, 7, 5)

if st.button("Generate Plan"):
    with st.spinner("Generating your plan..."):
        prompt = f"""
Generate a {days}-day meal plan for:
- Weight: {weight}kg
- Lifestyle: {lifestyle}
- Goal: {goal}
- Allergies: {allergies}
- Diet type: {diet_type}
- Dislikes: {dislikes}

Each day must include:
1. Breakfast, lunch, dinner
2. Calorie estimates for each meal
3. A bullet-point list of ingredients after each meal, like:
   Ingredients: chicken breast, brown rice, broccoli

Keep meals simple, practical, and varied (include fish for omegas, steak for iron, etc).
"""
        plan = generate_meal_plan(prompt, st.secrets["OPENAI_API_KEY"])
        st.markdown("---")
        st.subheader("📋 Meal Plan")
        st.markdown(plan)

        ingredients = extract_ingredients(plan)
        st.write("🧪 Extracted Ingredients:", ingredients)

        shopping_list, total = estimate_costs(ingredients)
        st.subheader("🛒 Ingredients + Cost Estimate")
        st.markdown("\n".join(shopping_list))
        st.markdown(f"**Estimated Total Cost: ~£{total:.2f}**")
        st.download_button("📥 Download Shopping List", "\n".join(shopping_list), file_name="shopping_list.txt")

        st.subheader("🧾 Raw Plan Output")
        st.code(plan)
