import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.seeds import seed_drinks
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)

# set up cors for the application
CORS(app, resources={r'/': {'origins': '*'}})

# to set Access-Control-Allow Headers and Methods
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, PATCH,PUT,POST, DELETE, OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

for seed_drink in seed_drinks:
    new_seed_drink = Drink(
        title=seed_drink['title'],
        recipe=seed_drink['recipe']
    )
    Drink.insert(new_seed_drink)

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():

    query = Drink.query.all()
    drinks = []

    for result in query:
        drink = {
            'title': result.title,
            'recipe': json.loads(json.dumps(result.short()))
        }
        drinks.append(drink)

    return jsonify({'success':True , 'drinks': drinks}),200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth()
def get_drinks_detail(payload):

    query = Drink.query.all()
    drinks = []

    for result in query:
        drink = {
            'title': result.title,
            'recipe': json.loads(json.dumps(result.long()))
        }
        drinks.append(drink)

    return jsonify({'success':True , 'drinks': drinks}),200



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth()
def create_drink(payload):
    return jsonify({'success':True})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth()
def edit_drink(payload, drink_id):
    return jsonify({'success':True})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth()
def delete_drink(payload, drink_id):
    return jsonify({'success':True})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(401)
def unathorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "code": error.description['code'],
                    "description": error.description['description'],
                    }), 401

# Default port:
if __name__ == '__main__':
    app.run()
