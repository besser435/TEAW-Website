import os
import sys
import json
import zipfile
from config import log


DISCARDED_KEYS = {"nbt", "category"}
_RECIPES = {}


def remove_unwanted_keys(obj):
    """
    Recursively remove keys listed in DISCARDED_KEYS
    from dictionaries inside the recipe JSON.
    """
    if isinstance(obj, dict):
        return {
            key: remove_unwanted_keys(value)
            for key, value in obj.items()
            if key not in DISCARDED_KEYS
        }
    elif isinstance(obj, list):
        return [remove_unwanted_keys(item) for item in obj]
    else:
        return obj



def load_recipes():
    global _RECIPES

    datapack_path = os.path.join("../db", "datapack.zip")   # TODO: move to config file
    log.info(f"Loading recipes from datapack: {datapack_path}")

    if not os.path.isfile(datapack_path):
        log.critical("Datapack for recipes not found")
        _RECIPES = {}
        return

    recipes_grouped = {}

    try:
        with zipfile.ZipFile(datapack_path, "r") as z:
            for file_info in z.infolist():

                if not file_info.filename.startswith("data/teaw_recipes/recipe/"):
                    continue

                if not file_info.filename.endswith(".json"):
                    continue

                # Extract folder name
                parts = file_info.filename.split("/")
                # data / teaw_recipes / recipe / <folder> / file.json
                if len(parts) < 5:
                    continue

                folder_name = parts[3]
                file_name = parts[-1]

                if folder_name not in recipes_grouped:
                    recipes_grouped[folder_name] = {}

                try:
                    with z.open(file_info) as f:
                        data = json.load(f)

                    cleaned_recipe = remove_unwanted_keys(data)

                    recipe_key = os.path.splitext(file_name)[0]  # remove .json

                    recipes_grouped[folder_name][recipe_key] = cleaned_recipe

                except Exception as e:
                    log.error(f"Failed loading recipe {file_info.filename}: {e}")

        _RECIPES = recipes_grouped

        total_recipes = sum(len(recipes) for recipes in _RECIPES.values())  
        size_kb = sys.getsizeof(_RECIPES) / 1024
        log.info(f"Total recipes loaded: {total_recipes}")
        log.info(f"Size of loaded recipes: {size_kb:.2f} KB")


    except Exception as e:
        log.error(f"Failed opening datapack zip: {e}")
        _RECIPES = {}


def get_recipes():
    return _RECIPES