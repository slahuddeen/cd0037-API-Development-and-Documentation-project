import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from flaskr import create_app
from models import setup_db, Question, Category
from urllib import response

from pathlib import Path
from dotenv import load_dotenv


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        env_path = Path('.')/'.env'
        load_dotenv('.env')
        self.database_name = "trivia"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(os.getenv("USER"),os.getenv("PASSWORD"),'localhost:5432', self.database_name)
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
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_individual_question_by_category(self):
        response = self.client().get('/categories/1/questions')
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['questions'])

    def test_not_found(self):
        response = self.client().get('/question')
        body = json.loads(response.data)

        self.assertEqual(body['error'], 404)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Not found!')

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

    def test_delete_individual_question_error(self):
        response = self.client().delete('/questions/1000')
        body = json.loads(response.data)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], 'Not found!')

    def test_create_individual_question(self):
        test_question = {
            "question": "test: What is life?",
            "answer": "24",
            "category": "1",
            "difficulty": "1"

        }
        response = self.client().post('/questions', json=test_question)
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)

    def test_search_questions(self):
        search = {
            "searchTerm": "clay"
        }
        response = self.client().post('/questions/search', json=search)
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)

    def test_search_questions_failure(self):
        search = {
            "searchTerm": "imnotreal"
        }
        response = self.client().post('/questions/search', json=search)
        body = json.loads(response.data)
        self.assertEqual(body['success'], True)
        self.assertEqual(body['total_questions'], 0)
    
    def test_create_individual_question_failure(self):
        test_question = {
            "question": "test:this should not work",
            "answer": 24,
            "category": 0,
            "difficulty": "1"

        }
        res = self.client().post('/questions/9', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Thats Not Allowed!")
    
    def test_get_next_question_failure(self):
        json_request = {
            'previous_questions': [2], 
            'quiz_category': {'id': 2, 'category': 'Art'}
        }
        res = self.client().post('/quizes', json=json_request)
        data = json.loads(res.data)

        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)

    def test_delete_individual_question(self):
        id = Question.query.first().id
        response = self.client().delete("/questions/" + str(id))
        body = json.loads(response.data)

        self.assertEqual(body['success'], True)
        self.assertEqual(body['deleted'], id)


    def test_get_next_question(self):
        json_request = {
            'previous_questions': [2], 
            'quiz_category': {'id': 1, 'category': 'Science'}
        }

        res = self.client().post('/quizes', json=json_request)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()



