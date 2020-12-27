import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
    CORS(app, resources={r"*": {"origins": "*"}}, allow_headers="*")

    """
  @TODO: Use the after_request decorator to set Access-Control-Allow
  """

    @app.after_request
    def after_request(response):
        # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add(
            "Acces-Control-Allow-Headers", "content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS"
        )
        # added allow-credentials because i got an error in console when trying to access quiz
        response.headers.add("Access-Control-Allow-Credentials", "true")

        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        """
        @TODO:
        Create an endpoint to handle GET requests
        for all available categories.
        """
        all_categories = Category.query.all()
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type
        return jsonify(
            {"success": True, "categories": categories, "count": len(categories)}
        )

    def paginate_questions(page, questions):
        page_start = (page - 1) * QUESTIONS_PER_PAGE
        page_end = page_start + QUESTIONS_PER_PAGE
        questions_count = len(questions)
        page_questions = []

        # Handle case if the last page has less than 10 questions
        # no need for the 'Anded' condition but added as further explanation
        if page_end > questions_count and page_start < questions_count:
            page_end = questions_count

        page_questions = questions[page_start:page_end]
        # if page_start and page_end are out of range the page_question will be an empty list
        # and it's length will be 0
        page_empty = False
        if len(page_questions) == 0:
            page_empty = True

        return page_questions, page_empty

    @app.route("/questions", methods=["GET"])
    def get_questions():
        """
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.

        TEST: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
        """
        # get a page number if any from request
        page = request.args.get("page", 1, type=int)

        questions, page_empty = paginate_questions(page, Question.query.all())
        ## if the length of requested page is 0, then page_empty will be True
        if page_empty:
            # should I abort or return an empty list?
            return jsonify(
                {
                    "success": True,
                    "questions": [],
                    "total_questions": Question.query.count(),
                    "categories": {},
                    "current_category": None,
                }
            )

        formatted_questions = [question.format() for question in questions]

        questions_count = Question.query.count()

        categories = {}
        all_categories = Category.query.all()
        # create a dictionary (map) with keys as the category id, and values as the category type
        for cat in all_categories:
            categories[cat.id] = cat.type

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": questions_count,
                "categories": categories,
                "current_category": None,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """
        @TODO:
        Create an endpoint to DELETE question using a question ID.

        TEST: When you click the trash icon next to a question, the question will be removed.
        This removal will persist in the database and when you refresh the page.
        """
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
                # todo add some logging

        return jsonify({"success": True, "id": question_id})

    @app.route("/questions", methods=["POST"])
    def create_question():
        """
        @TODO:
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.

        TEST: When you submit a question on the "Add" tab,
        the form will clear and the question will appear at the end of the last page
        of the questions list in the "List" tab.
        """
        body = request.get_json()
        try:
            print(body)
            question = body["question"]
            answer = body["answer"]
            difficulty = body["difficulty"]
            category = body["category"]
            # if any of these keys do not exist in the body
            # then it was a bad requestion
        except KeyError:
            abort(400)

        try:
            new_question = Question(question, answer, difficulty, category)
            new_question.insert()
            id = new_question.id

        except:
            # failure to commit
            db.session.rollback()
            db.session.close()
            abort(500)

        # the try, except blocks will abort in case of an error
        # if there are no errors

        return jsonify({"success": "True", "id": new_question.id})

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        """
        @TODO:
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.

        TEST: Search by any phrase. The questions list will update to include
        only question that include that string within their question.
        Try using the word "title" to start.
        """

        body = request.get_json()

        if body is None:
            abort(400)
        if "searchTerm" not in body:
            ## bad request because searchTerm not present
            abort(400)

        search_term = body.get("searchTerm")

        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        questions = [q.format() for q in questions]
        return jsonify(
            {
                "questions": questions,
                "total_question": len(questions),
                "current_category": None,
            }
        )

    @app.route("/categories/<category_id>/questions", methods=["GET"])
    def get_category_questions(category_id):
        """
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
        """
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

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "current_category": category.format(),  # should current_category be the Category Object
                "total_questions": total_questions,
            }
        )

    def check_out_of_unique_questions(previous_questions, quiz_category):
        category_id = quiz_category["id"]
        questions_in_category_count = Question.query.filter_by(
            category=category_id
        ).count()
        # previous_questions_with_current_category_count = 0
        counter = questions_in_category_count
        out_of_questions = False
        for q in previous_questions:
            if Question.query.get(q).category == int(category_id):
                counter -= 1
                if counter == 0:
                    out_of_questions = True
                    break
        if counter <= 0:
            out_of_questions = True
        return out_of_questions

    def pick_random_category():
        category_count = Category.query.count()
        quiz_category = Category.query.order_by(func.random()).first()
        return quiz_category

    @app.route("/quiz", methods=["POST"])
    def quiz_next_question():
        """
        @TODO:
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not.
        """
        body = request.get_json()

        try:
            previous_questions = body["previous_questions"]
            quiz_category = body["quiz_category"]
        except KeyError:
            # the required fields are not present in the dictionary
            abort(400)

        if "type" not in quiz_category or "id" not in quiz_category:
            abort(400)

        # try:
        try:
            # if all categories is selected
            # then quiz_category= {'type': 'click', 'id': 0}}
            if quiz_category["type"] == "click":
                quiz_category = pick_random_category().format()
            # random_question

            out_of_questions = check_out_of_unique_questions(
                previous_questions, quiz_category
            )
            # if i am out of questions, i will repeat one of the previous questions
            # until i am specified otherwise
            category_id = quiz_category["id"]

            if out_of_questions:
                # send no question and indicate that the quiz has ended
                return jsonify({"success": True, "question": None})

            if Question.query.filter_by(category=category_id).count() == 0:
            # bad request as there is no such category
                abort(400)
            else:
                # i believe this loop takes some time and picking a non repeated question
                # could be done more efficiently
                while True:
                    new_question = (
                        Question.query.filter_by(category=category_id)
                        .order_by(func.random())
                        .first()
                    )
                    if new_question.id not in previous_questions:
                        break
            new_question = new_question.format()

        except Exception as e:
            print(sys.exc_info())
            abort(400)

        return jsonify(
            {"success": True, "quiz_category": quiz_category, "question": new_question}
        )

    """
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not Found"}), 404

    @app.errorhandler(422)
    def cannot_be_processed(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server Error"}
            ),
            500,
        )

    return app
