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
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'Is This A Test Question?',
            'answer': 'Yes',
            'difficulty': 1,
            'category': 5
        }

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
    2 Tests Cases for the get_categories
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['categories'])
        
    def test_get_categories_method_not_allowed(self):
        res = self.client().post('/categories' )
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        
    """
    2 Tests Cases for the get_paginated_questions
    The first test for the expected behavior
    The second test shows how the response would be in case of the page prameter being beyond the valid number
    """    
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
        
    def test_get_paginated_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']),0)
     
     """
    2 Tests Cases for the delete_question
    The first test for the expected behavior
    The second test for handling one kind of error (422: request unprocessable - when the question_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """   
        
    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id==2).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(question,None)
        
    def test_delete_question_if_not_exist(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    """   
    2 Tests Cases for the create_question
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    """     
    def test_create_question(self):
        res = self.client().post('/questions' , json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1' , json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        
     """
    2 Tests Cases for the search_question
    The first test for the expected behavior (with a valid searchTerm)
    The second test shows how the response would be in case of no matches with the provided searchTerm
    """    
    def test_search_question_with_results(self):
        res = self.client().post('/questions' , json={'searchTerm':'title'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 2)
        
    def test_search_question_with_no_results(self):
        res = self.client().post('/questions' , json={'searchTerm':'faltimah'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        
     """
    2 Tests Cases for the get_questions_by_category
    The first test for the expected behavior
    The second test for handling one kind of error (422: request unprocessable - when the category_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """
        
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 2)
        
    def test_get_questions_by_category_with_invalid_categoryId(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
     
     """
    2 Tests Cases for the set_quiz
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    """   
        
    def test_set_quiz(self):
        res = self.client().post('/quizzes', json={'quiz_category':'6','previous_questions':['10']})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], 11)
        
    def test_set_quiz_method_not_allowed(self):
        res = self.client().get('/quizzes', json={'quiz_category':'6','previous_questions':['10']})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()