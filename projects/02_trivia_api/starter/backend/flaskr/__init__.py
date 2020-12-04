import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"localhost:5000/*": {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Acces-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
    

  @app.route('/categories', methods=['GET'])
  def get_categories():
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    all_categories= Category.query.all()
    all_categories = [category.format() for category in all_categories]
    return jsonify({
      'success': True,
      'categories': all_categories,
      'count': len(all_categories)
    }) 


  def paginate_questions(page):
    page_start = (page - 1) * QUESTIONS_PER_PAGE
    page_end = page_start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    questions_count = len(questions)
    page_questions = []
    
    # Handle case if the last page has less than 10 questions
    # no need for the 'Anded' condition but added as further explanation
    if page_end > questions_count and page_start < questions_count:
        page_end = questions_count

    page_questions = questions[page_start: page_end]
    # if page_start and page_end are out of range the page_question will be an empty list
    # and it's length will be 0
    if len(page_questions) == 0:
      abort(404)

    return page_questions

  @app.route('/questions', methods=['GET'])
  def get_questions():
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
    # get a page number if any from request
    page = request.args.get('page', 1, type=int)
    
    # if a page number is out range  paginate_questions it will abort to 404
    questions = paginate_questions(page)
    formatted_questions = [question.format() for question in questions]    

    questions_count = Question.query.count()
    categories = [Category.query.get(q['category']) for q in formatted_questions]
    categories = [q['category'] for q in formatted_questions]

    #categories = [c.format() for c in categories]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': questions_count,
      'categories': categories,
      'current_category': 'Science'
    })

    @app.route('questions/<int: question_id>')
    def delete_question(question_id):
      '''
      @TODO: 
      Create an endpoint to DELETE question using a question ID. 

      TEST: When you click the trash icon next to a question, the question will be removed.
      This removal will persist in the database and when you refresh the page. 
      '''
      not_found = False
      try:
        question_to_delete = Question.query.get(question_id)
        if question_to_delete is None:
          not_found = True
        
        question_to_delete.delete()
        
      except:
        db.session.rollback()
        db.session.close()
        if not_found:
          abort(404)
        else:
          # TODO
          ## handle some error in case of a fail to commit
          pass
      
      return jsonify({
        'success': True,
        'id': question_id
      })

  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    '''
    This endpoints is responsible for handling get requests on the given route.
    The response is a json object including the success, list of formatted questions,
    total_questions which is the count of the questions, and the category of queried question.
    In case of an error it responds with 404
    '''
    try:
      questions = Question.query.filter_by(category=category_id).all()
      total_questions = len(questions)
      questions = [q.format() for q in questions]
    except Exception as e:
      print(e)
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'current_category': category_id,
      'total_questions': total_questions
    })
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

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404
  
  @app.errorhandler(422)
  def cannot_be_processed(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
    }), 405

  return app

    