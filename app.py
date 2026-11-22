
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from myutils import (
    COLUMNS,
    load_recipes,
    search_recipes,
    get_random_recipe,
    validate_recipe,
    make_shopping_list
)

st.set_page_config(page_title="RecipeManager", page_icon="🍳")

# Load recipes when the application starts
if "recipes" not in st.session_state:
    if os.path.exists("recipes.csv"):
        try:
            st.session_state.recipes = load_recipes("recipes.csv")
        except Exception:
            st.session_state.recipes = pd.DataFrame(columns=COLUMNS)
            st.error("Could not load recipes.csv.")
    else:
        st.session_state.recipes = pd.DataFrame(columns=COLUMNS)

if "random_recipe" not in st.session_state:
    st.session_state.random_recipe = None

# Save recipes to the CSV file
def save_recipes():
    st.session_state.recipes.to_csv("recipes.csv", index=False)


# Sidebar navigation and CSV options
with st.sidebar:
    st.title("🍳 RecipeManager")

    page = st.radio(
        "Menu",
        ("Add Recipe", "Search", "View All", "Surprise Me")
    )

    st.divider()
    st.subheader("Recipe Data")

    uploaded_file = st.file_uploader(
        "Upload a recipe CSV",
        type=["csv"]
    )

    if st.button("Load CSV"):
        if uploaded_file is not None:
            try:
                st.session_state.recipes = load_recipes(
                    BytesIO(uploaded_file.getvalue())
                )
                save_recipes()
                st.success("Recipes loaded successfully!")
            except Exception as e:
                st.error(f"Could not load the file: {e}")
        else:
            st.warning("Please upload a CSV file first.")

    csv_data = st.session_state.recipes.to_csv(index=False)

    st.download_button(
        "Download Recipes CSV",
        data=csv_data,
        file_name="recipes.csv",
        mime="text/csv"
    )


# 1. Add Recipe
if page == "Add Recipe":

    st.title("Add a New Recipe")

    with st.form("recipe_form"):

        recipe_name = st.text_input("Recipe Name")

        ingredients = st.text_area(
            "Ingredients (separate with commas)"
        )

        instructions = st.text_area("Cooking Instructions")

        prep_time = st.number_input(
            "Preparation Time (minutes)",
            min_value=1,
            step=1
        )

        level = st.selectbox(
            "Difficulty Level",
            ("Easy", "Medium", "Hard")
        )

        category = st.selectbox(
            "Category",
            ("Breakfast", "Lunch", "Dinner", "Dessert")
        )
        rating = st.select_slider(
            "Rating",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: "⭐" * x
)
        submitted = st.form_submit_button("Save Recipe")

    if submitted:

        if validate_recipe(
            recipe_name,
            ingredients,
            instructions,
            prep_time
        ):

            new_recipe = {
                "name": recipe_name.strip(),
                "ingredients": ", ".join(
                    item.strip()
                    for item in ingredients.split(",")
                    if item.strip()
                ),
                "instructions": instructions.strip(),
                "prep_time": prep_time,
                "level": level,
                "category": category,
                "rating": rating
            }

            st.session_state.recipes = pd.concat(
                [
                    st.session_state.recipes,
                    pd.DataFrame([new_recipe])
                ],
                ignore_index=True
            )

            save_recipes()
            st.success("Recipe saved successfully!")

        else:
            st.warning(
                "Please complete all fields before saving."
            )


# 2. Search
elif page == "Search":

    st.title("Find Your Recipe")

    search_query = st.text_input(
        "Search by recipe name or ingredient"
    )

    category_filter = st.selectbox(
        "Filter by Category",
        ("All", "Breakfast", "Lunch", "Dinner", "Dessert")
    )

    filtered_recipes = search_recipes(
        st.session_state.recipes,
        search_query
    )

    if category_filter != "All":
        filtered_recipes = filtered_recipes[
            filtered_recipes["category"] == category_filter
        ]

    st.subheader("Search Results")

    if not filtered_recipes.empty:

        for _, recipe in filtered_recipes.iterrows():

            with st.expander(recipe["name"]):

                st.write("**Ingredients:**", recipe["ingredients"])
                st.write("**Preparation Time:**", recipe["prep_time"], "minutes")
                st.write("**Difficulty:**", recipe["level"])
                st.write("**Category:**", recipe["category"])

                st.write("**Instructions:**", recipe["instructions"])

                if recipe["rating"] > 0:
                    st.write("**Rating:**", "⭐" * int(recipe["rating"]))
                else:
                    st.write("**Rating:** Not rated yet")

    else:
        st.info("No recipes found. Try another search!")


# 3. View All
elif page == "View All":

    st.title("All Saved Recipes")

    recipes = st.session_state.recipes.copy()

    if not recipes.empty:

        st.write(f"Total Recipes: {len(recipes)}")

        sort_by_rating = st.checkbox("Sort by highest rating")

        if sort_by_rating:
            recipes = recipes.sort_values(
                "rating",
                ascending=False
            )

        st.subheader("Your Recipes")

        edited_recipes = st.data_editor(
    recipes,
    use_container_width=True,
    hide_index=True,
    column_config={
        "rating": st.column_config.NumberColumn(
            "Rating (1-5)",
            min_value=1,
            max_value=5,
            step=1,
            format="%d ⭐"
        )
    }
)
        

        if st.button("Save Changes"):
            st.session_state.recipes = edited_recipes[COLUMNS]
            save_recipes()
            st.success("Changes saved successfully!")

        st.divider()

        # Innovation: Create a shopping list
        st.subheader("Smart Shopping List")
        st.write("Select recipes to combine their ingredients.")

        selected_recipes = st.multiselect(
            "Choose recipes",
            st.session_state.recipes["name"].tolist()
        )

        if st.button("Generate Shopping List"):

            shopping_list = make_shopping_list(
                st.session_state.recipes,
                selected_recipes
            )

            if shopping_list:
                st.write("### Shopping List")

                for item in shopping_list:
                    st.checkbox(item, key=f"shop_{item}")

            else:
                st.info("Select at least one recipe first.")

    else:
        st.info("No recipes saved yet. Add a recipe first!")


# 4. Surprise Me
elif page == "Surprise Me":

    st.title("Surprise Me!")
    st.write("Can't decide what to cook? Let us choose for you!")

    if not st.session_state.recipes.empty:

        if st.button("Pick a Random Recipe"):
            st.session_state.random_recipe = get_random_recipe(
                st.session_state.recipes
            )

        random_recipe = st.session_state.random_recipe

        if random_recipe is not None:

            st.subheader(f"Today's Pick: {random_recipe['name']}")

            st.write("**Category:**", random_recipe["category"])
            st.write("**Difficulty:**", random_recipe["level"])
            st.write(
                "**Preparation Time:**",
                random_recipe["prep_time"],
                "minutes"
            )
            st.write("**Ingredients:**", random_recipe["ingredients"])
            st.write("**Instructions:**", random_recipe["instructions"])

    else:
        st.info("No recipes available yet. Add some recipes first!")
