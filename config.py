import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'percepta-secret-key-2024'
    
    # База данных PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:#si-World1@localhost:5432/percepta_db?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SMTP
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    
    # ROBOKASSA
    ROBOKASSA_MERCHANT_LOGIN = os.getenv('ROBOKASSA_MERCHANT_LOGIN', '')
    ROBOKASSA_PASSWORD_1 = os.getenv('ROBOKASSA_PASSWORD_1', '')
    ROBOKASSA_PASSWORD_2 = os.getenv('ROBOKASSA_PASSWORD_2', '')