# app.py
import os
import secrets
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))  # Add secret key for sessions

# Import and register the routes blueprint
from routes import routes
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
