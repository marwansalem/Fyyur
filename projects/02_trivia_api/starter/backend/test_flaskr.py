import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_TEST_NAME = os.getenv('DB_TEST_NAME', 'trivia_test') 
        #TODO should I use a different database for testing?
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '1234') 
        self.database_path = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DB_TEST_NAME}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_table_populated(self):
        '''
        This function inserts dummy values in 
        Category relation, it makes a post request
        then it tests the success of the response,
        whether the categories is not an empty list,
        count of categories in response,
        it finally checks whether each category
        has the correct format of an 'id' and a
        type.
        All the dummy data are deleted before
        the assertions are made.
        '''
        count = Category.query.count()
        delete_created_categories = False
        if count == 0:
            delete_created_categories = True
            for i in range(100):
                cat = Category('test_type' )
                cat.insert()
        res = self.client().get('/categories')
        data = json.loads(res.data)
        count = Category.query.count()
            
        if delete_created_categories:
            Categories = Category.query.all()
            for categ in Categories:
                categ.delete()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # assert it is not an empty list
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], list)
        self.assertEqual(data['count'], count)


        # make sure that each category in the query has all attributes
        for categ in data['categories']:
            self.assertTrue(categ['id'])
            self.assertIsInstance(categ['id'], int)
            self.assertTrue(categ['type'])
            self.assertIsInstance(categ['type'], str)

    def test_get_categories_table_empty(self):
        '''
        This function empties deletes all rows in Category relation
        and then makes a post request and tests whether the response will be 
        will have correct count as 0, and whether the 
        categories in the response is an empty list.
        The function reinserts the deleted categories before asserting
        in case the assertions fail.
        '''
        categories_copy = Category.query.all()
        #emot
        for categ in categories_copy:
            categ.delete()

        res = self.client().get('/categories')
        data = json.loads(res.data)
        count = Category.query.count()

        for categ in categories_copy:
            categ.insert()

        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['categories'], [])
        self.assertIsInstance(data['categories'], list)

        
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()