from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import secrets

# Loads environment variables from the .env file
load_dotenv()

# Creates a Flask application
app = Flask(__name__)


app.config['SECRET_KEY'] = secrets.token_hex(16)

# Database configuration
db_uri = os.getenv('DATABASE_URI') or 'postgresql://localhost:5432/churchdb'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Set to False to suppress a warning

# Initializes SQLAlchemy
db = SQLAlchemy(app)

# Load Africa's Talking API credentials
africas_talking_username = os.getenv('AFRICAS_TALKING_USERNAME')
africas_talking_api_key = os.getenv('AFRICAS_TALKING_API_KEY')

# Set the credentials in the Flask app configuration
app.config['AFRICAS_TALKING_USERNAME'] = africas_talking_username
app.config['AFRICAS_TALKING_API_KEY'] = africas_talking_api_key

# Check if the credentials are missing
if not africas_talking_username or not africas_talking_api_key:
    raise ValueError("Africa's Talking API credentials are missing.")


if not africas_talking_username or not africas_talking_api_key:
    raise ValueError("Africas Talking API credentials are not set.")
# Import routes at the end to avoid circular imports
from app import routes


# Error handling for database connection
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Error connecting to the database: {e}")