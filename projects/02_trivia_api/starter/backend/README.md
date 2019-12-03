# Full Stack Trivia API Backend

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API Reference

### Getting Started
- Base URL: Currently it will be running locally at the default, `http://127.0.0.1:5000/`.
- Authentication: No authentication or API keys is required. 

### Error Handling

  A list of error handlers have been set for the common expected errors 
  including `400`, `404`, `422` and `500`. 
  All are returned as JSON objects in the following format: success value (always False), error code and the error message
  
```

{
        "success": False,
        "error": 404,
        "message": "resources not found"
}

```

### Endpoints 
#### GET /categories
  - **PURPOSE:** To get all available categories
  
  - **URL:** {BaseURL}/categories
  
  - **HTTP METHOD:** GET
  
  - **REQUEST ARGUMENTS:** none
  
    *Sample Request*: `curl http://127.0.0.1:5000/categories`
    
  - **RETURNS:** A formatted Json string contains a list of category objects and the success value
  ```
  {  
   "categories":[  
      {  
         "id":1,
         "type":"Science"
      },
      {  
         "id":2,
         "type":"Art"
      },
      {  
         "id":3,
         "type":"Geography"
      },
      {  
         "id":4,
         "type":"History"
      },
      {  
         "id":5,
         "type":"Entertainment"
      },
      {  
         "id":6,
         "type":"Sports"
      }
   ],
   "success":true
}
  ```

#### GET /questions

  - **PURPOSE:** To get a list of paginated questions
  
  - **URL:** {BaseURL}/questions
  
  - **HTTP METHOD:** GET
  
  - **REQUEST ARGUMENTS:** page (optional)
  
    *Sample Request*: `curl http://127.0.0.1:5000/questions?page=2`
    
  - **RETURNS:** A formatted Json string contains a list of paginated questions, number of total questions,  categories and the success value.
  ```
  {
    "categories": [
        {
            "id": 1,
            "type": "Science"
        },
        {
            "id": 2,
            "type": "Art"
        },
        {
            "id": 3,
            "type": "Geography"
        }
    ],
    "questions": [
        {
            "answer": "Escher",
            "category": 2,
            "difficulty": 1,
            "id": 16,
            "question": "Which Dutch graphic artist–initials M C was a creator of optical illusions?"
        },
        {
            "answer": "Mona Lisa",
            "category": 2,
            "difficulty": 3,
            "id": 17,
            "question": "La Giaconda is better known as what?"
        }
    ],
    "success": true,
    "total_questions": 19
}
  ```
  
#### DELETE /questions/{question_id}

  - **PURPOSE:** To delete a specific question By its ID
  
  - **URL:** {BaseURL}/questions/{question_id}
  
  - **HTTP METHOD:** DELETE
  
  - **REQUEST ARGUMENTS:** question_id (Mandatory), page (optional)
  
    *Sample Request*: `curl http://127.0.0.1:5000/questions/2?page=2`
    
  - **RETURNS:** A formatted Json string contains a list of paginated questions,after deleting the required ID, 
  number of total questions,  categories and the success value (Same as Above).
  
  
  
  #### POST /questions

  - **PURPOSE:** This endpoint compine two functions: Creating a question Or Searching for questions based on a search term
  
  - **URL:** {BaseURL}/questions
  
  - **HTTP METHOD:** POST
  
  - **REQUEST ARGUMENTS:** 
     - For searching: the searchTerm string is required, page is optional
     
       *Sample Request For Searching*: 
       
       `curl http://127.0.0.1:5000/questions?page=1 -X POST -H "Content-Type: application/json" -d '{"searchTerm":"title"}'`
       
     - To Add a new question: question, answer, difficulty and the category are all required
       
       *Sample Request For Creating a Question*:
       
       `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":"Is It a test Question?", "answer":"Yes", "difficulty":"1", "category":"5"}'`
    
    
  - **RETURNS:** 
    - For the search function: It will return a formatted Json string contains a list of paginated questions (only question objects that include that string within their question),number of total questionsand the success value.
  
    - For a question creation: the success value will be returned.
    
```
    Search Response body

{
    "questions": [
        {
            "answer": "Maya Angelou",
            "category": 4,
            "difficulty": 2,
            "id": 5,
            "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        },
        {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 6,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        }
    ],
    "success": true,
    "total_questions": 2
}

```

    Create a Question Response body
    
    {
    "success": true
    }
    
    ```
  

## Testing The Backend
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
