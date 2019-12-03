#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    CORS(app, resources={r"*": {'origins': r"*"}})

    # CORS Headers

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = [category.format() for category in
                                    categories]

            return jsonify({'success': True,
                           'categories': formatted_categories})
        except:
            abort(422)

    def paginate_questions(request, selection):
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            current_questions = [question.format() for question in
                                 selection]
            return current_questions[start:end]
        except:
            abort(422)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            categories = Category.query.order_by(Category.id).all()
            formatted_categories = [category.format() for category in
                                    categories]

            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'questions': current_questions,
                'total_questions': len(selection),
                })
        except:
            abort(422)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            q = Question.query.filter(Question.id == question_id)
            question = q.one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            categories = Category.query.all()
            formatted_categories = [category.format() for category in
                                    categories]

            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'questions': current_questions,
                'total_questions': len(selection),
                })
        except:

            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)

        if search:
            try:
                s = Question.query.order_by(Question.id)
                s_ = s.filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, s_.all())

                return jsonify(
                    {
                        'success': True, 'questions': current_questions,
                        'total_questions': len(s_.all())
                    })
            except:
                abort(422)
        else:

            try:

                if None in (new_question, new_answer, new_difficulty,
                            new_category):
                    abort(400)

                question = Question(question=new_question,
                                    answer=new_answer,
                                    difficulty=new_difficulty,
                                    category=new_category)
                question.insert()

                return jsonify({'success': True})
            except:
                abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            s = Question.query.order_by(Question.id)
            selection = s.filter(Question.category == category_id).all()

            if selection is None:
                abort(404)

            current_questions = paginate_questions(request, selection)

            cat = Category.query.filter(Category.id == category_id)
            current_category = cat.one_or_none().format()

            return jsonify({
                'success': True,
                'current_category': current_category,
                'questions': current_questions,
                'total_questions': len(selection),
                })
        except:

            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def set_quiz():

        try:
            body = request.get_json()

            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            if quiz_category != 0:
                q = Question.query.order_by(func.random())
                q_f = q.filter(
                    Question.category == quiz_category, Question.id.notin_(
                        previous_questions))
                question = q_f.first()
            else:
                question = Question.query.order_by(func.random()).filter(
                    Question.id.notin_(previous_questions)).first()

            if question:
                return jsonify({'success': True,
                               'question': question.format()})

            return jsonify({'success': True})
        except:

            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': 'resources not found'}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unprocessable'}), 422)

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({'success': False, 'error': 400,
                'message': 'Bad Request'}), 400)

    @app.errorhandler(405)
    def not_allowed(error):
        return (jsonify({'success': False, 'error': 405,
                'message': 'method not allowed'}), 405)

    @app.errorhandler(500)
    def internal_server_error(error):
        return (jsonify({'success': False, 'error': 500,
                'message': 'internal server error'}), 500)

    return app
