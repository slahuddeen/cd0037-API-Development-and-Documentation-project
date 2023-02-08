import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import desc
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_category():
        try:
            categories = Category.query.all()
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            formatted_categories = [category.format() for category in categories]

            category_list = {}
            for cat in categories:
                category_list[cat.id] = cat.type

            if len(categories) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'categories': category_list,
                'total_categories': len(formatted_categories)
            })
        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            
            category = Category.query.order_by(Category.id).all()
            category_list = {}
            for cat in category:
                category_list[cat.id] = cat.type

            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            return jsonify({
                'success': True,
                "questions": formatted_questions[start:end],
                "categories": category_list,
                "total_questions": len(formatted_questions),
                "current_category": len(category_list)
            })
        except:
            abort(422)

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        selected_question = Question.query.get(question_id)
        if selected_question is None:
            abort(404)
        selected_question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            "deleted": question_id,
        })  


    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_questions():
        body = request.get_json()
        added_category = body.get("category", None)
        added_question = body.get("question", None)
        added_answer = body.get("answer", None)
        added_difficulty = body.get("difficulty", None)

        new_question = Question(question=added_question, answer=added_answer, category=added_category, difficulty=added_difficulty)
        new_question.insert()

        selection = Question.query.order_by(desc(Question.id)).first()
        #current_question = paginate_questions(request, selection)
        
        return jsonify({'success': True,})
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        searchTerm = body.get("searchTerm", None)

        try:
            if searchTerm:
                search = "%{}%".format(searchTerm)
                questions = Question.query.filter(
                    Question.question.ilike(search)).all()
                current_questions = [question.format()
                                     for question in questions]

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(current_questions),
                })

        except:
            abort(422)
 
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_individual_question_by_category(category_id):
        try:
            selected_category = Category.query.get(category_id)
            if selected_category is None:
                abort(404)
            else:
                selection = Question.query.filter_by(
                    category=selected_category.id).order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "current_category": selected_category.type,
                    "total_questions": len(selection)
                })

        except:
            abort(422)

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizes', methods=['POST'])
    def get_individual_question_by_quizes():
        body = request.get_json()
        if body is None:
            abort(400)
        quiz_category = body['quiz_category']
        previous_questions = body['previous_questions']

        try:
            if quiz_category['id'] == 0:
                questions = Question.query.order_by(Question.id).all()
            else:
                questions = Question.query.filter_by(
                    category=quiz_category['id']).order_by(Question.id).all()

            generated_question = random.choice(questions).format()

            is_used = False
            if generated_question['id'] in previous_questions:
                is_used = True

            else:
                return jsonify({
                    "success": True,
                    "question": generated_question})

            while is_used:
                if len(previous_questions) == len(questions):
                    return jsonify({
                        'success': True,
                        'message': "Completed successfully!"
                    })
        except:
            abort(422)

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found!'
        })

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Thats Not Allowed!'
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Thats not processable!'
        })

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error!'
        })

    return app

