# udacity-coffeeShop

# Welcome to Udacity Coffee Shop
Welcome to udacity coffee shop! This is a simple and fun full stack application that I used to learn and improve my skills at User Authentication and Authorization.
In addtion, I got some hands-on practice at setting up and implementing a code review infrastructure. 

This application is separated into two major components: the front-end/client facing application and the back-end/server application. Below are section that contain and describe all the detail for setting up and running eiter application. 

## Virtual Environments

Use of a virtual environment is highly recommended and this application takes that into consideration.
Please name your virtual environment: <strong>venv</strong>
If for some reason you must name your virtual environment something other than venv 
please make sure to add the directory to the .gitignore file or your changes will be rejected in review.

## Back End Application

The Backend portion of this application runs on a Stack composed of the following technologies.

<ul>
 <li>Python3</li>
 <li>Flask</li>
 <li>SQLAlchemy</li>
 <li>SQLite</li>
</ul>

If you do not have it already... you will need to install Python3 to get started on this project.

You can download Python3 <a href="https://www.python.org/downloads/">here</a>

### Development Set Up Instructions

Open up your terminal or command line application in your root directory start your virtual environment and enter the following commands:

```
cd backend
pip install -r requirements.txt
cd src
export FLASK_APP=api.py
export FLASK_ENV=development
export FLASK_DEBUG=true
flask run --reload
```

### Auth0 Setup

If you have not already  create an Auth0 account <a>here</a>

Create a new application for udacity-coffee this is where you will get the tenant domain required by your ionic application environment file.

Create a new API for storing and manging drinks this will be the 'AUDIENCE' in your ionic application environment file.

Add the folllowing permissions to your drinks API:
<ul>
 <li>get:drinks-detail</li>
 <li>post:drinks</li>
 <li>patch:drinks</li>
 <li>delete:drinks</li>
</ul>

Then navigate to the User&Roles Heading of your Auth0 account and create the following roles with the following permissions:

<ul>
 <li>
  Barista
  <ul>
   <li>get:drinks-detail</li>
  </ul>
 </li>
 <li>
 Manager
  <ul>
   <li>get:drinks-detail</li>
   <li>post:drinks</li>
   <li>patch:drinks</li>
   <li>delete:drinks</li>
  </ul>
 </li>
</ul>

Once your testing API is set up you will need to update the variable 'AUTH0_DOMAIN' to the tenant domain of your udacity-coffee application.

From the root directory this file can be found at ```/backend/src/auth/auth.py```

If you named your test api something other than drinks you will also need to update the 'API_AUDIENCE' varible as well.

### Development Testing

This application actually has two means of testing:

Postman and test_auth_api.py

The post man suite is recommended but if you would like to run test without using postman or just want to work on the API withou dealing with all the permission levels feel free to use test_auth_api.py

If you are not familiar with postman feel free to download it <a href="https://www.getpostman.com/">here</a> and check out the <a href="https://learning.getpostman.com/docs/postman/launching_postman/installation_and_updates/">PostMan Docementation</a>

Open up your terminal or command line application in your root directory start your virtual environment and enter the following commands:

```
cd backend
export AUTH_CLIENT_ID='Your auth0 client ID formatted as a string'
export AUTH_CLIENT_SECRET='auth0 client secret formatted as a string'
python test_auth_api.py
```

## Front End Application

First things first!

If you do not have it already... you will need to install NodeJS to get started on this project.

You can download NodeJS <a href="https://nodejs.org/en/download/">here</a>


The Frontend portion of this application is an Ionic Freamework Application.

Check out the documentation here -- <a href="https://ionicframework.com/docs">Iocnic Documentation</a>


You will need the ionic framework CLI which you can download with following command via npm:

```
npm install -g ionic
```

With the exception of a few minor changes this portion of the application is largely unchanged.

### Development Set Up Instructions

Once you are done configuring your environemntal variables open up your terminal or command line application in your root directory and enter the following commands:

```
cd frontend
npm i
ionic serve
```

NOTE: Do NOT use ionic serve for production pruposes. In order to get the full benefits and functionality you should create a production build as detailed in the <a href="https://ionicframework.com/docs">Ionic Documentation</a>

## API DOCUMENTATION

The following example calls will all make the assumption that one is currently running a development server on port 5000.

SAMPLE DRINK

```
model_drink = {
        'title': 'example',
        'recipe': [
            {"name": "ingredient one", "color": "grey", "parts": 1},
            {"name": "ingredient two", "color": "green", "parts": 3}
        ]
    }
```

#### GET /drinks

Acceptable Methods: GET

Parameters: NONE

Sample Request Object: N/A

Sample request endpoint: 

http://localhost:5000/drinks

Sample Response: 

```
{
  "drinks": [
    {
      "id": 1, 
      "recipe": [
        {
          "color": "grey", 
          "parts": 1
        }, 
        {
          "color": "green", 
          "parts": 3
        }
      ], 
      "title": "matcha shake"
    }, 
    
    ... remaining results omitted ...

  ], 
  "success": true
}
```

#### GET /drinks-detail

Acceptable Methods: GET

Parameters: NONE

Sample Request Object: N/A

Sample request endpoint: 

http://localhost:5000/drinks-detail

Sample Response: 

```
{
  "drinks": [
    {
      "id": 1, 
      "recipe": [
        {
          "color": "grey", 
          "name": "ingredient one", 
          "parts": 1
        }, 
        {
          "color": "green", 
          "name": "ingredient two", 
          "parts": 3
        }
      ], 
      "title": "matcha shake"
    }, 
    
    .. remaining results omitted...
  ], 
  "success": true
  ```

#### POST /drinks

Acceptable Methods: GET

Parameters: NONE

Sample Request Object:

```
{
    "title": "Water3",
    "recipe": [{
        "name": "Water",
        "color": "blue",
        "parts": 1
    }]
}
```

Sample request endpoint: 

http://localhost:5000/drinks

Sample Response: !!!!!!!!!!!

#### PATCH /drinks/{id}

Acceptable Methods: GET

Parameters: drink_id

Sample Request Object: 

```
{
    "title": "Water5"
}
```

Sample request endpoint: 

http://localhost:5000/drinks/{drink_id}

Sample Response: 

```
{
  "drinks": [
    {
      "id": 1,
      "recipe": null,
      "title": "Water5"
    }
  ],
  "success": true
}
```

#### DELETE /drniks/{id}

Acceptable Methods: GET

Parameters: drink_id

Sample Request Object: N/A

Sample request endpoint: 

http://localhost:5000/drinks/1

Sample Response: 

```
{
  "drinks": 1,
  "success": true
}
```

#### Sample 400 Error

description: if the request is not formatted properly the following error will be sent

sample response:
```
{

    "success": False,
    "error": 400,
    "message": "Bad Request -- check your formatting"

}, 400
```

#### Sample 401 Error

description: if the user does not have a valid access token the following error will be sent

sample response:
```
{
    
    "success": False,
    "error": 401,
    "message": "You do not have the necessary authorization to access this resource"

}, 401
```

#### Sample 403 Error

description: if the user has a valid access token but does not have the correct permissions the follow error will ber sent

sample response:
```
{
    
    "success": False,
    "error": 403,
    "message": "You do not have the necessary permissions to access this resource"

}, 403
```

#### Sample 404 Error

description: if the requested resouces is not available the following error will be sent

sample response:
```
{
    
    "success": False,
    "error": 404,
    "message": "Resource Not Found -- no such resource was found"

}, 404
```

#### Sample 405 Error

description: if the request attempts to use an unapproved method the following error will be sent

sample response:
```
{
    
    "success": False,
    "error": 405,
    "message": "Method Not Allowed"

}, 405
```

#### Sample 422 Error

description: if the request is not of the appropriate data type the following error will be sent

sample response:
```
{
    
    "success": False,
    "error": 422,
    "message": "Unprocessable Entity -- try submitting a different value"

}, 422
```

#### Sample 500 Error

description: if the application has an internal error not related to user input the following error will be sent

sample response:
```
{
    
    "success": False,
    "error": 500,
    "message": "Internal Server Error"

}, 500
```

### Conclusion

Thank you for your interest in udacity-coffeeShop!

If you have any questions feel free to send me a message here on git hub or leave a comment and I will try to get back to you as soon as possible.