import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Setting up CORS. Allow '*' for origins.
  '''
  CORS(app, resources={r"*": {"origins": "*"}})

  '''
  Using after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  '''
  @TODO: 

  PURPOSE: To get all available categories
  URL: {BaseURL}/categories
  HTTP METHOD: GET
  
  
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = [category.format() for category in categories]
      
      return jsonify({
        'success':True,
        'categories': formatted_categories
      })
    except:
     abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def paginate_questions(request, selection):
    try:
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      current_questions = [question.format() for question in selection]
      return current_questions[start:end]
    except:
     abort(422)
  

  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)
      
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = [category.format() for category in categories]
      
      return jsonify({
        'success':True,
        'categories': formatted_categories,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    except:
     abort(422)
    
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

   try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      
      if question is None:
          abort(404)
          
      question.delete()
      
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)
      
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
      
      return jsonify({
        'success':True,
        'categories': formatted_categories,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    
   except:
     abort(422)
    
 
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():

    body = request.get_json()
    
    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_difficulty = body.get('difficulty',None)
    new_category = body.get('category',None)
    search = body.get('searchTerm',None)
    
    if search:
      try:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
        current_questions = paginate_questions(request,selection)    
          
        return jsonify({
        'success':True,
        'questions': current_questions,
        'total_questions': len(selection)
        })
      except:
       abort(422)
      
    else:
      try: 
        
        if None  in (new_question, new_answer, new_difficulty, new_category):
          abort(400)
             
        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
        question.insert()

        return jsonify({
          'success':True
        })
      except:
        abort(422)
    
    
 

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      selection = Question.query.order_by(Question.id).filter(Question.category==category_id).all()
      
      if selection is None:
          abort(404)
            
      current_questions = paginate_questions(request,selection)
      
      category = Category.query.filter(Category.id==category_id).one_or_none()
      current_category = category.format()
      
      return jsonify({
        'success':True,
        'current_category': current_category,
        'questions': current_questions,
        'total_questions': len(selection)
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''


  @app.route('/quizzes', methods=['POST'])
  def set_quiz():

    try:
      body = request.get_json()
      
      previous_questions = body.get('previous_questions',None)
      quiz_category = body.get('quiz_category',None)
      
      if (quiz_category !=0):
        question = Question.query.order_by(func.random()).filter(
                                        Question.category==quiz_category,
                                        Question.id.notin_(previous_questions)
                                      ).first()
      else:
        question = Question.query.order_by(func.random()).filter(
                                        Question.id.notin_(previous_questions)
                                      ).first() 
      
      if(question):
          return jsonify({
          'success':True,
          'question': question.format()
          })
        
      return jsonify({
      'success':True
      })
          
    except:
     abort(422)  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message": "resources not found"
      }), 404
      
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
      }), 422
      
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
      }), 400
 
  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
      }), 405 
      
  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
      }), 500     
  
  return app

    