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
        self.assertTrue(data['categories'])# if the dict is empty assertion will fail
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['count'], count)


        # make sure that each category in the query has all attributes
        for id in data['categories']:
            self.assertIsInstance(id, str)
            self.assertIsInstance(data['categories'][id], str)

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
        categories = [categ.copy() for categ in categories_copy]
        for categ in categories_copy:
            categ.delete()

        res = self.client().get('/categories')
        data = json.loads(res.data)
        count = Category.query.count()

        for categ in categories:
            categ.insert()

        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['categories'], {})
        self.assertIsInstance(data['categories'], dict)

    def test_get_categories_unallowed_method(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')
        self.assertEqual(data['error'], 405)

    def test_get_questions_table_populated(self):
        pass

    def test_get_questions_table_empty(self):
        pass

    def test_post_question(self):
        some_category_types = ['Art', 'Science', 'Language']
        categories = [Category(cat_type) for cat_type in some_category_types]
        for cat in categories:
            cat.insert()

        cat_id = Category.query.first().id
        res = self.client().post('/questions', json={
            'question':'How long is a day?',
            'answer':'24 hours',
            'difficulty':1,
            'category':cat_id
            }
            )

        data = json.loads(res.data)
        id = data['id']
        self.assertEqual(data['success'], True)

        question = Question.query.get(id)

        self.assertTrue(question)
        self.assertEqual(question.question, 'How long is a day?')
        self.assertEqual(question.answer, '24 hours')
        self.assertEqual(question.difficulty, 1)
        self.assertEqual(question.category, cat_id)
        question.delete()

    def test_search_question(self):
        #Create a category so it can be referenced by newly inserted questions
        cat = Category('Mystery')
        cat.insert()
        #prepare Question attributes
        answer= "yes"
        diff = 0
        #prepare a question that should not be in the result
        not_a_target = Question('Will I be found using the chosen search term?', 'No', cat.id, diff).format()
        #prepare questions that are to be expected in the result
        question_strings =['can you this find that?', 'where is THIS?', 'who is tHiS']
        target_questions = [Question(s, answer, cat.id, diff) for s in question_strings]

        for q in target_questions:
            q.insert()
        expected_res = [q.format() for q in target_questions]
        term = "this"
        res = self.client().post('/questions/search', json={
            'searchTerm':term
            }
            )
        data = json.loads(res.data)
        try:
            result_questions = data['questions']
            count = data['total_questions']
            self.assertTrue(result_questions)
            self.assertEqual(count, len(expected_res))

            # assert that resulst are the same as the created questions
            for res_question in result_questions:
                self.assertTrue(res_question in expected_res)

            # assert that the question that does not include the search term is not in the result
            self.assertFalse(not_a_target in result_questions)

            
        except:
            for q in target_questions:
                q.delete()

    def test_delete_question_exists(self):
        # create a new question to be used for the test
        # create a category for it so as not to violate category FK constraint
        cat = Category('Mystery')
        cat.insert()
        diff = 9000
        question_to_delete = Question('Can we be funny while coding?', 'No', cat.id, 0)
        
        question_to_delete.insert()
        question_id = question_to_delete.id

        res = self.client().delete(f'/questions/{question_id}')

        data = json.loads(res.data)
        
        res_status = data.get('success', None)
        res_id =  data.get('id', None)
        self.assertIsNotNone(res_status)
        self.assertIsNotNone(res_id)

        self.assertTrue(res_status)
        self.assertEqual(question_id, res_id)
        self.assertIsNone(Question.query.get(question_id))
    


        



        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()