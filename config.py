import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env (для локальной работы)
load_dotenv()

class Config:
    # Секретный ключ для сессий. Если не задан в переменных, берем запасной вариант
    SECRET_KEY = os.environ.get('SECRET_KEY', 'percepta-secret-key-2024')
    
    # === САМОЕ ВАЖНОЕ: Строка подключения к базе данных ===
    # Если переменная DATABASE_URL задана (на сервере) — используем её.
    # Если нет (локально) — используем SQLite (файл в папке проекта).
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///percepta.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки SMTP для почты (тоже берем из переменных окружения)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')