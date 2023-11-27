from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

app = Flask(__name__)

questions = [
        "CON How are you attendisng the the service this Sunday? \n",
        "CON How satisfied are you with your overall experience at church? \n",
        "CON Which communication channel do you prefer for receiving church updates? \n",
        "CON Which of the church's resources do you use the most? \n",
        ""
        ]

answers = [
        ["1. Physically present \n", "2. Online livestream \n"],
        ["1. Not pleased \n", "2. Content \n", "3. Satisfied \n", "4. Happy \n", "5. Highly Blessed \n"],
        ["1. Whatsapp \n", "2. RBC Website \n", "3. Email \n", "4. Other \n"],
        ["1. Weekly Digest \n", "2. Podcast \n", "3. Sermons \n", "4. Cell groups \n"]
    ]

user_responses = {}


class Response(db.Model):
    __tablename__= 'responses'
    response_id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), nullable=False)
    numeric_answer = db.Column(db.Integer, nullable=True)
    submission_timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=True)
    question_text = db.Column(db.Text, nullable=True)


class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)


@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    # Receives data from Africa's Talking API
    data = request.json

    # Extracts relevant info from the request
    session_id = data.get('sessionId')
    phone_number = data.get('phoneNumber')
    text = data.get('text')
    network_code = data.get('networkCode')
    service_code = data.get('serviceCode')

    # TODO: Implement your logic to handle the USSD request
    
    if text == '':
        response = "CON Welcome to Ridgeways Baptist anonymous survey! \n"
        response += "1. Proceed \n"
        response += "2. Cancel"

    elif text == '1':
        response = get_survey_question(session_id, 0)

    elif text.startswith('1*'):
        response = process_survey_response(session_id, text)

    else:
        response = "END Invalid choice"


    #response_text = handle_ussd_request(session_id, phone_number, text)

    # Return a plain text response to Africa's Talking API
    return response, 200, {'Content-Type': 'text/plain'}

def get_survey_question(session_id, question_number):
    question_text = questions[question_number]
    answer_options = answers[question_number]
    
    user_responses[session_id] = {}
    response = f"{question_text}"
    
    for option in answer_options:
        response += f"{option}\n"

    return response

def process_survey_response(session_id, text):
    question_number = int(text.split('*')[1])
    selected_option = int(text.split('*')[2])

    # Store the user's response
    user_responses[session_id][question_number] = selected_option

     # Create a new database entry for the response
    response = Response(
        phone_number=user_responses[session_id]['phone_number'],
        numeric_answer=selected_option,
        question_id=question_number + 1,
        question_text=questions[question_number]
    )
    db.session.add(response)
    db.session.commit()

    next_question_number = question_number + 1

    if next_question_number < len(questions):
        response = get_survey_question(session_id, next_question_number)
    else:
        response = process_final_responses(session_id)

    return response

def process_final_responses(session_id):
    # Process the user's responses (you can customize this part based on your needs)
    final_response = "END Survey completed. Thank you and have a blessed day!\n"
    
    for i, question_text in enumerate(questions):
        answer_options = answers[i]
        selected_option = user_responses[session_id][i + 1]
        final_response += f"{question_text}{answer_options[selected_option - 1]}\n"

    return final_response

if __name__ == '__main__':
    app.run(debug=True)
