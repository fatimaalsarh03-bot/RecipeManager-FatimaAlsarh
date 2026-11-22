
import pandas as pd
import random

# Columns used in the recipe database
COLUMNS = [
    "name",
    "ingredients",
    "instructions",
    "prep_time",
    "level",
    "category",
    "rating"
]


def load_recipes(file):
    """Load recipes from a CSV file."""

    df = pd.read_csv(file)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col == "rating" else ""

    return df[COLUMNS]


def search_recipes(df, query):
    """Search recipes by name or ingredients."""

    if not query.strip():
        return df.copy()

    mask = (
        df["name"].astype(str).str.contains(
            query, case=False, na=False
        )
        |
        df["ingredients"].astype(str).str.contains(
            query, case=False, na=False
        )
    )

    return df[mask]


def get_random_recipe(df):
    """Select one random recipe."""

    if df.empty:
        return None

    return df.sample(n=1).iloc[0]


def validate_recipe(name, ingredients, instructions, prep_time):
    """Check that required recipe fields are completed."""

    if not name.strip():
        return False

    if not ingredients.strip():
        return False

    if not instructions.strip():
        return False

    if prep_time < 1:
        return False

    return True


def make_shopping_list(df, selected_recipes):
    """Combine ingredients from selected recipes."""

    ingredients = []

    for name in selected_recipes:
        recipe = df[df["name"] == name]

        if not recipe.empty:
            items = str(
                recipe.iloc[0]["ingredients"]
            ).split(",")

            for item in items:
                item = item.strip()

                if item and item not in ingredients:
                    ingredients.append(item)

    return ingredients
