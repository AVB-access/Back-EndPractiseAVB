import json
from flask import Flask
from flask import request
from flask import Response

"""Custom Exceptions"""
class InvalidInput(Exception):
	pass
class AlreadyExistError(Exception):
	pass
class RecipeNotFound(Exception):
	pass

def create_app():
	app = Flask(__name__)
	
	#Default home page
	@app.route('/')
	def hello_world():
		return 'Hello world!'
	
	#Verify POST request data and input into file
	def handle_recipes_post(data):
		#Attempt to read a JSON from the request
		usr_in = json.loads(request.data)
		
		#Verify there is a name, ingredient list, and steps
		check = ['name','ingredients', 'instructions']
		if ( not list(usr_in.keys()) == check or not usr_in['name'] or
			type(usr_in['name']) != str or 
			len(usr_in['ingredients']) == 0 or 
			len(usr_in['instructions']) == 0):
			raise InvalidInput('Invalid Input for JSON')
		#END input checks

		#Check if recipe already exists
		for recipe in data['recipes']:
			if recipe['name'] == usr_in['name']:
				raise AlreadyExistError
		
		#Add to the file
		data['recipes'].append(usr_in)
		with open('data.json', 'w') as f:
			f.write(json.dumps(data))
		
		#Finished
		return True
	
	#Update an existing recipe if it exists
	#Called on HTTP PUT request
	def handle_recipes_put(data):
		#Attempt to read json from input
		usr_in = json.loads(request.data)
		
		#Verify there is a name, ingredient list, and steps
		check = ['name','ingredients', 'instructions']
		if ( not list(usr_in.keys()) == check or not usr_in['name'] or
			type(usr_in['name']) != str or 
			len(usr_in['ingredients']) == 0 or 
			len(usr_in['instructions']) == 0):
			raise InvalidInput('Invalid Input for JSON')
		#END input checks
		
		#Check if recipe exists at all
		for i, recipe in enumerate(data['recipes']):
			if i >= len(data['recipes']):
				raise RecipeNotFound
			if recipe['name'] == usr_in['name']:
				recipe['ingredients'] = usr_in['ingredients']
				recipe['instructions'] = usr_in['instructions']
				break
		
		with open('data.json', 'w') as f:
			f.write(json.dumps(data))
			
		return 204
		
	#Handle /recipes requests
	#	GET -> return all recipe names in JSON
	#	POST -> add recipe to data unless already exists
	#	PUT -> update existing recipe
	@app.route('/recipes', methods=['GET', 'POST', 'PUT'])
	def get_recipes():
		#Load the file into a variable
		with open('data.json') as f:
			data = json.load(f)
		
		if request.method == 'POST':
			if handle_recipes_post(data):
				return Response(status=201)
		elif request.method == 'PUT':
			status_code = handle_recipes_put(data)
			return Response(status=status_code)
		else:
			#Get the names and place into a json then return
			ret_val = {'recipeNames':[recipe['name'] for recipe in data['recipes']]}
			return ret_val
	
	#Get details of a given recipe
	@app.route('/recipes/details/<string:name>')
	def get_recipe_details(name):
		#Load JSON data into variable
		with open('data.json') as f:
			data = json.load(f)
		ret_val = {}
		
		for recipe in data['recipes']:
			if recipe['name'] == name:
				ret_val = {'details':
							{'ingredients':recipe['ingredients'],
							'numSteps':len(recipe['instructions'])}}
				break
		
		return ret_val
		
	
	"""ERROR HANDLERS"""
	@app.errorhandler(json.JSONDecodeError)
	def handle_badrequest(e):
		return {'error':'Bad Request'}, 400
		
	@app.errorhandler(InvalidInput)
	def handle_badInput(e):
		return {'error':'Bad Input'}, 400
	
	@app.errorhandler(AlreadyExistError)
	def handle_alreadyexist(e):
		return {'error':'Recipe already exists'}, 400
		
	@app.errorhandler(RecipeNotFound)
	def handleNotExist(e):
		return {'error':'Recipe does not exist'},404
	
	return app
	
if __name__ == "__main__":
    app = create_app()
    app.run()
