from app import app, db
from models import CustomMetric

with app.app_context():
    # Создаем все таблицы (если их нет)
    db.create_all()
    print("✅ Все таблицы созданы (или уже существуют)")
    
    # Проверяем, есть ли таблица custom_metrics
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'custom_metrics' in tables:
        print("✅ Таблица custom_metrics существует")
        # Проверяем колонку is_public
        columns = [col['name'] for col in inspector.get_columns('custom_metrics')]
        if 'is_public' not in columns:
            print("🔄 Добавляем колонку is_public...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE custom_metrics ADD COLUMN is_public BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("✅ Колонка is_public добавлена")
    else:
        print("❌ Таблица custom_metrics НЕ создана! Проверьте модели.")