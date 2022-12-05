import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from flaskr import create_app
from models import setup_db, Question, Category
from urllib import response

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres','abc','localhost:5432', self.database_name)
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


    def test_get_all_categories(self):
        response = self.client().get('/categories')
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['categories'])

    def test_get_all_categories_error(self):
        response = self.client().get('/categories/1')
        body = json.loads(response.data)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], "Not found!")

    def test_get_all_questions(self):
        response = self.client().get('/questions')
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['questions'])

    def test_get_all_questions_error(self):
        response = self.client().get('/questions/1')
        body = json.loads(response.data)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error'], 405)
        self.assertEqual(body['message'], "Thats Not Allowed!")

    def test_delete_individual_question(self):
        response = self.client().delete('/questions/5')
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertEqual(body['deleted'], 5)

    def test_delete_individual_question_error(self):
        response = self.client().delete('/questions/1000')
        body = json.loads(response.data)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], 'Not found!')

    def test_create_individual_question(self):
        test_question = {
            "question": "What is life?",
            "answer": "24.",
            "category": "1",
            "difficulty": "1"

        }
        response = self.client().post('/questions', json=test_question)
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['created'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()



