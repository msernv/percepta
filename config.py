import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'percepta-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:%23si-World1@localhost:5432/percepta_db?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')