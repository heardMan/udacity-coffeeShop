
import os
import json
import unittest
import http.client
from src.api import app
from flask import request
from flask_sqlalchemy import SQLAlchemy
from src.database.models import setup_db, database_path, Drink

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
        self.database_path = database_path

        conn = http.client.HTTPSConnection("dev-y5wb70ja.auth0.com")
        payload = "{\"client_id\":\""+CLIENT_ID+"\",\"client_secret\":\""+CLIENT_SECRET+"\",\"audience\":\"drinks\",\"grant_type\":\"client_credentials\"}"
        headers = { 'content-type': "application/json" }
        conn.request("POST", "/oauth/token", payload, headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data)
        token = json_data['access_token']
        token_type = json_data['token_type']
        self.headers = {
            'authorization': '{} {}'.format(token_type, token)
        }
        conn.close()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        

    # test route get drinks
    def test_get_drinks(self):
        """Test the get drinks route"""
        pass

    # test route get drinks-detail
    def test_get_drinks_detail(self):
        """Test the get drinks-detail route"""

        """Test Authorization"""
        #try to get drinks detail data without headers
        res_0 = self.client().get('/drinks-detail')
        #parse data
        data_0 = json.loads(res_0.data)
        #expect a 401 unauthorized status
        self.assertEqual(res_0.status_code, 401)
        #expect the success property to be false
        self.assertEqual(data_0['success'], False)

        """Test Functionality"""
        #get drinks detail data with headers
        res = self.client().get('/drinks-detail', headers=self.headers)
        #parse data
        data = json.loads(res.data)
        #ensure request was good
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # ensure we have at least one category
        self.assertGreater(len(data['drinks']), 0)
    
    # test route post drink
    def test_post_drink(self):
        """Test the post drinks route"""

        # """Test Authorization"""
        # #try to get drinks detail data without headers
        # post = self.client().post('/drink', json={
        #     'title': 'test_one',
        #     'recipe': [
        #         {
        #             'color': 'green',
        #             'name': 'matcha',
        #             'parts': 3
        #         },
        #         {
        #             'color': 'white',
        #             'name': 'milk',
        #             'parts': 1
        #         }
        #     ]
        # })
        # #parse data
        # post_data = json.loads(post.data)
        # #expect a 401 unauthorized status
        # self.assertEqual(post.status_code, 401)
        # #expect the success property to be false
        # self.assertEqual(post_data['success'], False)

        pass

    # test route patch drink
    def test_patch_drink(self):
        """Test the patch drinks route"""
        pass

    # test route delete drink
    def test_delete_drink(self):
        """Test the delete drinks route"""
        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

