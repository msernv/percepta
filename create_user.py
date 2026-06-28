from app import app
from database import db
from models import User

print("🔄 Проверка пользователей...")

with app.app_context():
    existing = User.query.filter_by(email='test@percepta.com').first()
    if existing:
        print("Пользователь уже существует!")
        print(f"Email: {existing.email}")
        print(f"Компания: {existing.company_name}")
    else:
        user = User(
            email='test@percepta.com',
            company_name='Тестовая компания',
            vertical='saas',
            custom_metrics=[]
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("✅ Пользователь создан!")
        print("📧 Email: test@percepta.com")
        print("🔑 Пароль: password123")
        print("🏢 Компания: Тестовая компания")