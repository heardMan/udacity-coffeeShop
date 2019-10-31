import os
import json
import unittest
import http.client
from src.pyenv import TOKEN
from src.api import app, seed_db

from flask import request
from flask_sqlalchemy import SQLAlchemy
from src.database.models import setup_db, test_database_path, Drink, db_drop_and_create_all

CLIENT_ID = os.environ.get('AUTH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('AUTH_CLIENT_SECRET')


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    @classmethod
    def setUpClass(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_name = "drink_test"
        self.database_path = test_database_path

        self.headers = {
            'authorization': TOKEN
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            os.environ['FLASK_ENV'] = 'development'

    def tearDown(self):
        """Executed after reach test"""
        # rest database
        db_drop_and_create_all()
        # add data to database
        seed_db()

    def test_get_drinks(self):
        """Test the get drinks route"""

        """Test Functionality"""
        # test the unauthorized /drinks route
        res = self.client().get('/drinks')
        data = res.json
        # ensure request was good
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        """Test Output"""
        # ensure we have at least one category
        self.assertGreater(len(data['drinks']), 0)

    def test_get_drinks_detail(self):
        """Test the get drinks-detail route"""

        """Test Authorization"""
        # try to get drinks detail data without headers
        res_0 = self.client().get('/drinks-detail')
        # parse data
        data_0 = json.loads(res_0.data)
        # expect a 401 unauthorized status
        self.assertEqual(res_0.status_code, 401)
        # expect the success property to be false
        self.assertEqual(data_0['success'], False)

        """Test Functionality"""
        # get drinks detail data with headers
        res = self.client().get('/drinks-detail', headers=self.headers)
        # parse data
        data = json.loads(res.data)
        # ensure request was good
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        """Test Output"""
        # ensure we have at least one category
        self.assertGreater(len(data['drinks']), 0)

    # test route post drink
    def test_post_drink(self):
        """Test the post drinks route"""

        # sample json object we can post
        sample_post = {
            'title': 'sample_post',
            'recipe': [{"name": "red", "color": "red", "parts": 1}, {"name": "blue", "color": "blue", "parts": 2}, {"name": "green", "color": "green", "parts": 1}]
        }

        """Test Authorization"""
        # try to get drinks detail data without headers
        post_0 = self.client().post('/drinks', json=sample_post)
        # parse data
        post_data_0 = json.loads(post_0.data)
        # expect a 401 unauthorized status
        self.assertEqual(post_0.status_code, 401)
        # expect the success property to be false
        self.assertEqual(post_data_0['success'], False)

        """Test Functionality"""

        # count the number of drinks in data
        intial_drinks = len(Drink.query.all())

        # test post
        post = self.client().post('/drinks', headers=self.headers, json=sample_post)
        # parse data
        post_data = json.loads(post.data)
        # expect a 200 ok status
        self.assertEqual(post.status_code, 200)
        # expect the success property to be true
        self.assertEqual(post_data['success'], True)

        # count drinks in data
        final_drinks = len(Drink.query.all())

        """Test Output"""
        # expect final number of drinks to be greater than initial
        self.assertGreater(final_drinks, intial_drinks)

    # test route patch drink

    def test_patch_drink(self):
        """Test the patch drinks route"""

        # save original drink data
        original_drink = Drink.query.all()[0]
        drink_index = original_drink.id

        sample_patch = {
            'title': 'sample_patch-{}'.format(drink_index+100),
            'recipe': [{"name": "orange", "color": "orange", "parts": 1}, {"name": "green", "color": "green", "parts": 2}, {"name": "yellow", "color": "yellow", "parts": 1}]
        }

        """Test Authorization"""
        # try to get drinks detail data without headers
        res_0 = self.client().patch('/drinks/{}'.format(drink_index))
        # parse data
        data_0 = json.loads(res_0.data)
        # expect a 401 unauthorized status
        self.assertEqual(res_0.status_code, 401)
        # expect the success property to be false
        self.assertEqual(data_0['success'], False)

        """Test Functionality"""
        # test patch
        patch = self.client().patch('/drinks/{}'.format(drink_index),
                                    headers=self.headers, json=sample_patch)
        # parse data
        patch_data = json.loads(patch.data)
        # expect a 200 ok status
        self.assertEqual(patch.status_code, 200)
        # expect the success property to be true
        self.assertEqual(patch_data['success'], True)
        # create a variable for the patched drink
        patched_drink = patch_data['drinks'][0]

        """Test Output"""
        # the titles should be different
        self.assertNotEqual(original_drink.title, patched_drink['title'])
        # the recipes should be different
        self.assertNotEqual(original_drink.recipe, patched_drink['recipe'])

    # test route delete drink

    def test_delete_drink(self):
        """Test the delete drinks route"""
        # get most recently added item
        drink_1 = Drink.query.all()[0]

        """"Test Authorization"""
        # try to get drinks detail data without headers
        post_0 = self.client().delete('/drinks/{}'.format(drink_1.id))
        # parse data
        post_data_0 = json.loads(post_0.data)
        # expect a 401 unauthorized status
        self.assertEqual(post_0.status_code, 401)
        # expect the success property to be false
        self.assertEqual(post_data_0['success'], False)

        """Test Functionality"""
        # first we get a count of the drinks before attempting to post
        get_0 = self.client().get('/drinks')
        # parse data
        data_0 = get_0.json
        # count the number of drinks in data
        intial_drinks = len(data_0['drinks'])
        # test post
        delete = self.client().delete('/drinks/{}'.format(drink_1.id), headers=self.headers)
        # parse data
        delete_data = json.loads(delete.data)
        # expect a 200 ok status
        self.assertEqual(delete.status_code, 200)
        # expect the success property to be true
        self.assertEqual(delete_data['success'], True)
        # get a count of the drinks after we attempt to post
        get_1 = self.client().get('/drinks')
        # parse data
        data_1 = get_1.json
        # count drinks in data
        final_drinks = len(data_1['drinks'])

        """Test Output"""
        # expect final number of drinks to be greater than initial
        self.assertLess(final_drinks, intial_drinks)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
