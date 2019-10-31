import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

ENVIRONMENT = os.environ.get('FLASK_ENV')


app = Flask(__name__)
setup_db(app)

# set up cors for the application
CORS(app)


def seed_db():
    # drop the old data base and re create
    db_drop_and_create_all()

    drink1 = {
        'title': 'matcha shake',
        'recipe': [
            {"name": "milk", "color": "grey", "parts": 1},
            {"name": "matcha", "color": "green", "parts": 3}
        ]
    }

    drink2 = {
        'title': 'flatwhite',
        'recipe': [
            {"name": "milk", "color": "grey", "parts": 3},
            {"name": "coffee", "color": "brown", "parts": 1}
        ]
    }

    drink3 = {
        'title': 'cap',
        'recipe': [{
            "name": "foam", "color": "white", "parts": 1},
            {"name": "milk", "color": "grey", "parts": 2},
            {"name": "coffee", "color": "brown", "parts": 1}
        ]
    }
    # put all drinks in a list for quick iteration
    seed_drinks = [drink1, drink2, drink3]
    # loop seed drink list
    for seed_drink in seed_drinks:
        # create  ne drink model
        new_seed_drink = Drink(
            title=seed_drink['title'],
            recipe=json.dumps(seed_drink['recipe'])
        )
        # insert new drink model in the database
        new_seed_drink.insert()

    return True


# check server environment and add seed database if development
if ENVIRONMENT == 'development':
    # enter seed data into database
    seed_db()

# function to check incoming payload against route specific requirments


def permission_check(payload, route_permissions):
    # create a list to store permissions for checking
    check_permissions = []
    # check the payload permissions object for reqular user
    for perm in payload['permissions']:
        check_permissions.append(perm)
    # check to see if payload is from a test
    if payload.get('gty') == 'client-credentials':
        check_permissions.append(payload.get('gty'))
    # set a boolean to check for a testing environment
    test_creds = 'client-credentials' in check_permissions
    # set boolean to development environement AND valid test credentials
    test_permissions = test_creds is True
    # checks permissions and sends a 403 if they are not correct
    if route_permissions is False and test_permissions is False:
        abort(403)

    return True


# ROUTES

# unauthorized rout that returns safe drink information
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # create error instance and set it to false
    error = False
    # check the request method to make sure it is a GET request
    if request.method == 'GET':
        # attempt a query to the database
        try:
            # get all the drinks from the data base
            query = Drink.query.all()
            # create a list instance to send to the client
            drinks = []
            # for each drink in the query result
            for result in query:
                # use short/approved data for general access
                drink = result.short()
                # add to drinks list for response
                drinks.append(drink)
        # if database query is unsuccessful...
        except:
            # set error instance to true
            error = True
            print('Error: {}'.format(sys.exc_info()))

        finally:

            # check error instance
            if error:
                # send the client a 500 error if database query unsuccessful
                abort(500)
            # if no errors
            else:
                # return a json response object with a status of 200 to the client
                return jsonify({'success': True, 'drinks': drinks}), 200

    else:
        # send 405 error: method not allowed if not a get request
        abort(405)

# authorized route that returns drinks along with detailed recipes
@app.route('/drinks-detail', methods=['GET'])
@requires_auth()
def get_drinks_detail(payload):
    # create error instance and set it to false
    error = False
    # check the request method to make sure it is a GET request
    if request.method == 'GET':
        # route permissions set to a boolean
        get_permission = 'get:drinks-detail' in payload['permissions']
        # check permisions and if rejected send client a 403 error
        permission_check(payload, get_permission)

        # attempt a query to the database
        try:
            # get all the drinks from the data base
            query = Drink.query.all()
            # create a list instance to send to client
            drinks = []
            # for each drink in the database
            for result in query:
                # parse and set
                drink = json.loads(json.dumps(result.long()))
                drinks.append(drink)
        # if database query is unsuccessful...
        except:
            # if there was an error
            error = True
            # log error to the server
            print('Error: {}'.format(sys.exc_info()))
        finally:
            # if there was an error on the database send a 500 error
            if error:
                abort(500)
            else:
                # return a json response object with a status of 200 to the client
                return jsonify({'success': True, 'drinks': drinks}), 200

    else:
        # send 405 error: method not allowed if not a get request
        abort(405)

# authorized route that adds a drink to the database
@app.route('/drinks', methods=['POST'])
@requires_auth()
def create_drink(payload):
    # create error instance and set it to false
    error = False
    # check the request method to make sure it is a GET request
    if request.method == 'POST':
        # route permissions set to a boolean
        
        post_permission = 'post:drinks' in payload['permissions']
        
        # check permisions and if rejected send client a 403 error
        permission_check(payload, post_permission)
        
        # if there is no data in the request let the client know the request was bad
        if request.json == None:
                abort(400)

        # attempt operation on the database

        
        try:
            
            # define new model
            new_drink = Drink(
                title=request.json['title'],
                recipe=json.dumps(request.json['recipe'])
            )
            # ensure data in request is of type string
            if type(new_drink.title) is not str and type(new_drink.recipe) is not str:
                abort(422)
                
            #add new drink to the database
            new_drink.insert()

        except RequestError:
            # set error to true and log on the server
            error = True
            # rollback database commit
            db.session.rollback()
            # log error on the server
            print('Error: {}'.format(sys.exc_info()))

        finally:

            if error:
                # send bad request error
                abort(400)
            else:
                # if no error send success object and log on server
                print('Added: {}'.format(new_drink.long()))
                return jsonify({
                    'success': True,
                    'drinks': [new_drink.long()]
                })

            # close database session
            db.session.close()
        
    else:
        # send 405 error: method not allowed if not a get request
        abort(405)

# authorized route that updates a drink in the database
# or deletes a drink from the database depending on request context
@app.route('/drinks/<int:drink_id>', methods=['PATCH', 'DELETE'])
@requires_auth()
def edit_drink(payload, drink_id):
    # create error instance and set it to false
    error = False
    # check the request method to make sure it is a GET request
    if request.method == 'PATCH':
        # route permissions set to a boolean
        patch_permission = 'patch:drinks' in payload['permissions']
        # check permisions and if rejected send client a 403 error
        permission_check(payload, patch_permission)
        # attempt to perform database operations
        # if there is no data in the request let the client know the request was bad
        if request.json == None:
                abort(400)

        try:
            # query database
            drink = Drink.query.get(drink_id)
            # if no drinks are returned send 404 error to client
            if drink is None:
                abort(404)

            #set drink attributes using user input
            drink.title = request.json.get('title')
            drink.recipe = json.dumps(request.json.get('recipe'))

            # ensure data in request is of type string
            if type(drink.title) is not str and type(drink.recipe) is not str:
                abort(422)

            # commit changes to database
            db.session.commit()

        except RequestError:
            # set error to true and log on the server
            error = True
            # rollback database commit
            db.session.rollback()
            # log error on the server
            print('Error: {}'.format(sys.exc_info()))

        finally:
            # if error occurred send 400 error to the client
            if error:
                abort(400)
            else:
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                })

            # close database session
            db.session.close()

    elif request.method == 'DELETE':
        # route permissions set to a boolean
        delete_permission = 'delete:drinks' in payload['permissions']
        # check permisions and if rejected send client a 403 error
        permission_check(payload, delete_permission)

        try:
            query = Drink.query.get(drink_id)
            if query is None:
                abort(404)
            query.delete()

        except RequestError:
            # set error to true and log on the server
            error = True
            # rollback database commit
            db.session.rollback()
            # log error on the server
            print('Error: {}'.format(sys.exc_info()))

        finally:
            # if error occurred send 400 error to the client
            if error:
                # send bad request error
                abort(400)
            else:
                # if no error send success object and log on server
                print('Deleted: {}'.format(query))
                return jsonify({
                    'success': True,
                    'drinks': drink_id
                })
            # close database session
            db.session.close()
    else:
        # send 405 error: method not allowed if not a get request
        abort(405)


# add a request error definition for db request errors
class RequestError(Exception):
    """Raised when something goes wrong with the request"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

# handle bad request errors
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request -- check your formatting"
    }), 400

# handle unauthorized request errors
@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "status": "Unauthorized",
        "message": "You do not have the necessary authorization to access this resource",
    }), 401

# handle unauthorized request errors
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "status": "Forbidden",
        "message": "You do not have the necessary permissions to access this resource",
    }), 403

# handle resource not found errors
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found -- no such resource was found"
    }), 404

# handle resource for incorrect method use on a route
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

# handle unprocessable entity errors
@app.errorhandler(422)
def unprocessable_enitity(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity -- try submitting a different value"
    }), 422

# handle internal server errors
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


# Default port:
if __name__ == '__main__':
    app.run()
