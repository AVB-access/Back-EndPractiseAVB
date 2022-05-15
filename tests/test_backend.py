import pytest
import sys
sys.path.append('../test')
from backend import create_app
import json

#Reset data to default
with open('backup_data.json', 'r') as bckup:
	with open('data.json', 'w') as f:
		f.write(bckup.read())

@pytest.fixture
def client():
	app = create_app()
	app.config["TESTING"] = True
	with app.test_client() as client:
		yield client

def details_checker(client, recipe_name, expected):
	rv = client.get("/recipes/details/" + recipe_name)
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected

def test_get_recipes(client):
	rv = client.get("/recipes")
	expected = {"recipeNames":["scrambledEggs","garlicPasta","chai"]}
	
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected
	
def test_get_recipe_details(client):
	#Test all default recipes
	names_to_test = ["garlicPasta", "scrambledEggs", "chai", "NOTEXISTS"]
	expected = [{"details":{ #garlicPasta details
					"ingredients": 
						["500mL water","100g spaghetti","25mL olive oil","4 cloves garlic","Salt"],
					"numSteps":5}},
				 {"details":{#scrambledEggs details
    			"ingredients": 
    				["1 tsp oil","2 eggs","salt"],
    			"numSteps":5}},
    			{"details":{ #chai details
    			"ingredients": 
    				["400mL water","100mL milk","5g chai masala","2 tea bags or 20 g loose tea leaves"],
    			"numSteps":4}}, {}]
	for i, name in enumerate(names_to_test):
		details_checker(client, name, expected[i])
		
def test_post_recipe(client):
	#Bad JSON input
	rv = client.post('/recipes', data="{{'test':'test'}")
	assert rv.status_code == 400
	
	#Valid JSON bad input
	rv = client.post('/recipes', data="{'test':'test'}")
	assert rv.status_code == 400
	
	#Valid input
	rv = client.post('/recipes', data='{"name":"butteredBagel", \
					"ingredients":["1 bagel","butter"], \
					"instructions":["cut the bagel","spread butter on bagel"]}')
	assert rv.status_code == 201
	
	#Test the new recipe in the other requests
	rv = client.get('/recipes')
	expected = {"recipeNames":["scrambledEggs","garlicPasta","chai","butteredBagel"]}
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected
	
	rv = client.get("/recipes/details/" + 'butteredBagel')
	expected = {"details":{
					"ingredients":
						["1 bagel","butter"],
					"numSteps":2}}
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected
    
	#Repeat valid input
	rv = client.post('/recipes', data='{"name":"butteredBagel", \
					"ingredients":["1 bagel","butter"], \
					"instructions":["cut the bagel","spread butter on bagel"]}')
	assert rv.status_code == 400
	assert json.loads(rv.data) == {'error':'Recipe already exists'}
	
def test_put_request(client):
	#Bad JSON input
	rv = client.put('/recipes', data="{{'test':'test'}")
	assert rv.status_code == 400
	
	#Valid JSON bad input
	rv = client.put('/recipes', data="{'test':'test'}")
	assert rv.status_code == 400
	
	#Valid input
	rv = client.put('/recipes', data='{"name": "butteredBagel",\
								"ingredients": [\
									"1 bagel", \
									"2 tbsp butter"], \
								"instructions": [ \
									"cut the bagel", \
									"spread butter on bagel"]}')
	assert rv.status_code == 204
	
	#Test the new recipe in the other requests
	rv = client.get('/recipes')
	expected = {"recipeNames":["scrambledEggs","garlicPasta","chai","butteredBagel"]}
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected
	
	rv = client.get("/recipes/details/" + 'butteredBagel')
	expected = {"details":{
					"ingredients":
						["1 bagel","2 tbsp butter"],
					"numSteps":2}}
	assert rv.status_code == 200
	assert json.loads(rv.data) == expected
	
