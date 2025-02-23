from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: Dict[str, CookbookEntry] = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	# TODO: implement me
	recipeName = recipeName.replace("_", " ")
	recipeName = recipeName.replace("-", " ")
	recipeName = recipeName.lower()

	recipeNameWithOnlyAlphaCharacters = ""

	for char in recipeName:
		if char.isalpha() or char == ' ':
			recipeNameWithOnlyAlphaCharacters += char
	
	recipeName = recipeNameWithOnlyAlphaCharacters

	everyWord = recipeName.split()
	everyWordCapitalised = []

	for word in everyWord:
		everyWordCapitalised.append(word[0].upper() + word[1:])

	recipeName = " ".join(everyWordCapitalised)

	return recipeName if len(recipeName) > 0 else None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():

	content = request.json
	current_entry:CookbookEntry = None
	if (content == None):
		return 'Recieved request must be valid json!',400

	if (content['type'] == "recipe"):
		try:
			current_entry = Recipe(content['name'], [RequiredItem(x['name'], x['quantity']) for x in content['requiredItems']])
		except:
			return 'request does not contain the required fields', 400
		
		for item in current_entry.required_items:
			if current_entry.required_items.count(item) > 1:
				return 'Request cannot have repeated entries in required items',400
			
	elif (content['type'] == "ingredient"):
		try:
			current_entry = Ingredient(content['name'], content['cookTime'])
		except:
			return 'request does not contain the required fields',400

		if (current_entry.cook_time < 0):
			return 'cooking time must be greater than or equal to 0!',400
	else:
		return 'given type is not valid!',400

	if (cookbook.get(current_entry.name) == None):
		cookbook.update({current_entry.name : current_entry})
	else:
		return 'entry already exists in the cookbook!',400


	return '', 200


def splitRecipeIntoIngredients(recipe: Recipe) -> List[RequiredItem]:
	output: List[RequiredItem] = []

	for item in recipe.required_items:
		if (isinstance(cookbook.get(item.name), Ingredient)):
			if (output.count(item) > 0):
				output[output.index(item)].quantity += item.quantity
			else:
				output.append(item)
		else:
			for nested_item in splitRecipeIntoIngredients(item):
				if (output.count(nested_item) > 0):
					output[output.index(nested_item)].quantity += nested_item.quantity
				else:
					output.append(nested_item)

	return output 

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name: str = None
	listOfIngredients: List[RequiredItem] = None
	cookTime = 0

	try:
		name = request.args.get("name")
	except:
		return 'Must have \'name\' in the query arguments!', 400
	
	currentRecipe = cookbook.get(name) 

	if currentRecipe == None:
		return f'{name} is not in the cookbook!', 400
	elif isinstance(currentRecipe, Ingredient):
		return f'{name} is an ingredient not a recipe!', 400
	
	try:
		listOfIngredients = splitRecipeIntoIngredients(currentRecipe)
	except:
		return 'Invalid ingredients within the recipe!', 400

	# now i know this is a bit slower because iterating multiple times over the same dataset
	# but i think the structure readability improvements it provides is worth 
	# if it becomes a bottleneck or we're prioritising speed (clearly not we're using python) then a refactor wouldn't be too hard
	for item in listOfIngredients:
		try:
			ingredient: Ingredient = cookbook.get(item.name)
			cookTime += ingredient.cook_time * item.quantity
		except:
			return f'{item.name} is not a valid ingredient in the cookbook!', 400

	data = {
		"name": name,
		"cookTime": cookTime,
		"ingredients": listOfIngredients
	}

	return data, 200


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
