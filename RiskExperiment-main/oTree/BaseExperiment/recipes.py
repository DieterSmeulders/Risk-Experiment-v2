"""Sandwich orders factory"""
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from pathlib import Path


datapath = Path(__file__).parent / "datafiles"
recfile = datapath / "recipes.yaml"
ingfile = datapath / "ingredients.yaml"


def load_recipes():
    with open(recfile) as f:
        return yaml.load(f, Loader=Loader)


def load_ingredients():
    with open(ingfile) as f:
        return yaml.load(f, Loader=Loader)


def images_map(ingredients):    
    #from django.templatetags.static import static  # it doesn't work properly in otree

    def image_url(ingredient):
        name = ingredient.lower().replace(' ', '_')
        return f"/static/sandwiches/images/{name}.jpg"

    images = {}
    for category, items in ingredients.items():
        for item in items:
            images[item] = image_url(item)
    return images


RECIPES = load_recipes()

INGREDIENTS = load_ingredients()
