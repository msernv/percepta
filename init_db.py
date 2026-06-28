from app import app, db
from models import User, Upload, CustomMetric

print("🔄 Создание всех таблиц...")

with app.app_context():
    db.create_all()
    print("✅ Все таблицы созданы")
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📋 Таблицы в базе данных: {', '.join(tables)}")
    
    if 'custom_metrics' in tables:
        print("✅ Таблица custom_metrics существует!")
    else:
        print("❌ Таблица custom_metrics НЕ существует!")