import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

'''Pagination function'''
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    currentQuestion = questions[start:end]
    return currentQuestion

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources = {r"*/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Method', 'GET, PUT, POST, DELETE, PATCH')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories", methods=["GET"])
  def all_categories():
    list_categories = Category.query.order_by(Category.type).all()

    if len(list_categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {categories.id: categories.type for categories in list_categories}
    })
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
  @app.route("/questions")
  def get_questions():
    questionList = Question.query.all()
    questionTotal = len(questionList)
    current_Question = paginate_questions(request, selection)

    if questionTotal == 0:
      abort(404)
    
    categoryList = Category.query.all()
    categoryDict = {}
    for category in categoryList:
      categoryDict[category.id] = category.type

    return jsonify ({
      'success': True,
      'questions': current_Question,
      'total_questions': questionTotal,
      'categories': categoryDict
    })    

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int: questions_id>", methods-["DELETE"])
  def delete_question(question_id):
    try:
      selectedQuestion = Question.query.get(question_id)
      selectedQuestion.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
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
  @app.route("/questions", methods=["POST"])
  def addQuestion():
    questionText = body.get_json()
    if questionText.get('searchTerm'):
      searchText = questionText.get('searchTerm')
      searchResult = Question.query.filter(Question.question.ilike(f'%{questionText}%')).all()

      #Abort if no results are found
      if len(searchResult) == 0:
        abort(404)
      
      paginate = paginate_questions(request, selection)
      totalCount = len(Question.query.all())
      return jsonify({
        'success': True,
        'question': paginate,
        'total_questions': totalCount
      })

    else:
      #Get the data for the new question
      newQuestion = body.get('question')
      newAnswer = body.get('answer')
      newDifficulty = body.get('difficulty')
      newCateogry = body.get('category')

      if ((newQuestion is None) or (newAnswer is None) or (newDifficulty is None) or (newCategory is None)):
        abort(422)

      try:
        questionToLoad = Question(question=newQuestion, answer=newAnswer, difficulty=newDifficulty, category=newCategory)
        questionToLoad.insert()

        #setup all questions
        selection = Question.query.order_by(Question.id).all()
        questionList = paginate_questions(request, selection)
        questionCount = len(Question.query.all())

        #send the questions back
        return jsonify({
          'success': True,
          'created': question_id,
          'question': questionToLoad.question,
          'questions': questionList,
          'total_questions': questionCount
        })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
#See above
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id')
  def get_questions_category(categoryID):
    try:
      questionList = Question.query.filter(Question.category == str(categoryID)).all()
      questionCount = len(questionList)
      return jsonify ({
        'success': True,
        'questions': [question.format() for question in questionList],
        'total_questions': questionCount,
        'current_category': categoryID
      })
    except:
      abort(404)

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
  def take_quiz():
    body = request.get_json()
    questionsAsked = body.get('previous_questions')
    currentCategory = body.get('quiz_category')

    #if cateogry or question isn't found, abort
    if ((questionsAsked is None) or (currentCategory is None)):
      abort(400)

    if(currentCategory == 0):
      questionsList = Question.query.all()
    else:
      questionsList = Question.query.filter_by(cateogry = currentCategory['id']).all()
    
    questionCount = len(questionsList)

    #Select a random question from the questions list pulled earlier
    def pick_Random_Question():
      return questionsList[random.randrange(0, questionCount, 1)]

    #Make sure that a question doesn't get asked twice
    def question_Used(questionToCheck):
      questionCheck = False
      for each in questionsAsked:
        if (each == questionsAsked.id):
          questionCheck = True
      return questionCheck

    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    