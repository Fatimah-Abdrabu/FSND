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
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE') #Though no need for PUT now #
    return response
  
  '''
  PURPOSE: To get all available categories
  URL: {BaseURL}/categories
  HTTP METHOD: GET
  REQUEST ARGUMENTS: none
  RETURNS: A formatted Json string contains a list of category objects and the success value
   
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
  A helper method to return a paginated questions list, so we don't need to repeat it once it's needed
   
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
  

  '''
  PURPOSE: To get a list of paginated questions
  URL: {BaseURL}/questions
  HTTP METHOD: GET
  REQUEST ARGUMENTS: page (optional)
  RETURNS: A formatted Json string contains a list of paginated questions, 
  number of total questions,  categories and the success value.
   
  '''
  
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
  PURPOSE: To delete a specific question By its ID
  URL: {BaseURL}/questions/<question_id>
  HTTP METHOD: DELETE
  REQUEST ARGUMENTS: question_id (Mandatory)
  RETURNS: A formatted Json string contains a list of paginated questions, 
  number of total questions,  categories and the success value.
   
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
  PURPOSE: This endpoint compine two functions: Creating a question Or Searching for questions based on a search term
  URL: {BaseURL}/questions
  HTTP METHOD: POST
  REQUEST ARGUMENTS: 
    - For searching: the searchTerm string is required, page is optional
    - To Add a new question: question, answer, difficulty and the category are all required
  RETURNS: 
    - For the search function: It will return a formatted Json string contains a list of paginated questions (only question objects that include that string within their question), 
      number of total questionsand the success value.
    - For a question creation: the success value will be returned. 
   
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
  PURPOSE: To get a list of paginated questions based on category
  URL: {BaseURL}/categories/<category_id>/questions
  HTTP METHOD: GET
  REQUEST ARGUMENTS: page (optional)
  RETURNS: A formatted Json string contains a list of paginated questions, 
  number of total questions,  current category and the success value.
   
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
  PURPOSE: To get a random questions to play the quiza
  URL: {BaseURL}/quizzes
  HTTP METHOD: POST
  REQUEST ARGUMENTS: category (it could be 0), array of previous_questions (it could be empty)
  RETURNS: A formatted Json string contains a selected random question and the success value.
           If No questions found, the success value will only get returned
   
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
  A list of error handlers for the common expected errors 
  including 400, 404, 422 and 500. 
  All are returned as JSON objects in the following format: success value (always False), error code and the error message
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

    