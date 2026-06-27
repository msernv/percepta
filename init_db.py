from init_app import app, db
from models import User, Upload

print("🔄 Создание всех таблиц...")

with app.app_context():
    db.drop_all()
    print("🗑️ Все таблицы удалены")
    
    db.create_all()
    print("✅ Все таблицы созданы")
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📋 Таблицы в базе данных: {', '.join(tables)}")