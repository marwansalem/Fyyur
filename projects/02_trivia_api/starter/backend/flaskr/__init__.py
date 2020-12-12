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
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
    

  @app.route('/categories', methods=['GET'])
  def get_categories():
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    print(Category.query.all())
    all_categories= Category.query.all()
    categories = {}
    for category in all_categories:
      categories[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': categories,
      'count': len(all_categories)
    }) 


  def paginate_questions(page, questions):
    page_start = (page - 1) * QUESTIONS_PER_PAGE
    page_end = page_start + QUESTIONS_PER_PAGE
    questions_count = len(questions)
    page_questions = []
    
    # Handle case if the last page has less than 10 questions
    # no need for the 'Anded' condition but added as further explanation
    if page_end > questions_count and page_start < questions_count:
        page_end = questions_count

    page_questions = questions[page_start: page_end]
    # if page_start and page_end are out of range the page_question will be an empty list
    # and it's length will be 0
    page_empty = False
    if len(page_questions) == 0:
      page_empty = True

    return page_questions, page_empty


    
  @app.route('/questions', methods=['GET'])
  def get_questions():
    ''' 
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
    page= request.args.get('page', 1, type=int)
    

    questions, page_empty = paginate_questions(page, Question.query.all())
    ## if the length of requested page is 0, then page_empty will be True
    if page_empty:
      # should I abort or return an empty list?
      return jsonify({
      'success': True,
      'questions': [],
      'total_questions': Questions.query.count(),
      'categories': {},
      'current_category': None
      })
      
    formatted_questions = [question.format() for question in questions]    

    questions_count = Question.query.count()
    categories = []
    category_set = set()
    
    # for q in formatted_questions:
    #   cat = Category.query.get(q['category'])
    #   if (cat.id in category_set) is False:
    #     category_set.add(cat.id)
    #     categories.append(cat.type)
    #categories = [Category.query.get(q['category']).type for q in formatted_questions]
    #for cc in categories:
    #  print(cc, Category.query.filter_by(type=cc).first().id)
    #categories = Category.query.filter(Category.type in [ Category.query.get(q['category']).type for q in formatted_questions] )
    
    
    categories = {}
    # create a dictionary (map) with keys as the category id, and values as the category type

    for q in formatted_questions:
      categories[q['category']] = Category.query.get(q['category']).type
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': questions_count,
      'categories': categories,
      'current_category': None
    })

  @app.route('questions/<int: question_id>')
  def delete_question(question_id):
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    question_not_found = False
    try:
      question_to_delete = Question.query.get(question_id)
      if question_to_delete is None:
        question_not_found = True
      
      question_to_delete.delete()
      
    except:
      db.session.rollback()
      db.session.close()
      if question_not_found:
        abort(404)
      else:
        ## handle some error in case of a fail to commit
        abort(500)
        #todo add some logging
    
    return jsonify({
      'success': True,
      'id': question_id
    })


  @app.route('/questions', methods=['POST'])
  def create_question():
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    body = request.get_json()
    try:
      question = body['question']
      answer = body['answer']
      difficulty = body['difficulty']
      category = body['category']
      # if any of these keys do not exist in the body
      # then it was a bad requestion
    except KeyError:
      abort(400)
    
    try:
      new_question = Question(question, answer, difficulty, category)
      new_question.insert()
      id = new_question.id

    except:
      #failure to commit
      db.session.rollback()
      db.session.close()
      abort(500)
    
    # the try, except blocks will abort in case of an error
    # if there are no errors

    return jsonify({
      'success': 'True',
      'id': new_question.id
    })

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    body = request.get_json()
    print(body)
    if 'searchTerm' not in body:
      ## bad request because searchTerm not present
      abort(400)
    
    search_term = body.get('searchTerm')

    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    questions = [q.format() for q in questions]
    return jsonify({
      'questions': questions,
      'total_question': len(questions),
      'current_category': None
    })

  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 

    This endpoints is responsible for handling get requests on the given route.
    The response is a json object including the success, list of formatted questions having
    category = category_id,
    total_questions which is the count of the questions  of queried question.
    In case of an error it responds with 404
    '''
    category = Category.query.get(category_id)
    if category is None:
      abort(404)

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
      'current_category': category.format(), #should current_category be the Category Object
      'total_questions': total_questions
    })



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

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500

  return app

    