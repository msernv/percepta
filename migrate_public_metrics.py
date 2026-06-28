from app import app, db
import sqlalchemy as sa

with app.app_context():
    inspector = sa.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('custom_metrics')]
    
    if 'is_public' not in columns:
        print("🔄 Добавляем колонку 'is_public' в таблицу custom_metrics...")
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE custom_metrics ADD COLUMN is_public BOOLEAN DEFAULT FALSE"))
            conn.commit()
        print("✅ Колонка добавлена!")
    else:
        print("ℹ️ Колонка 'is_public' уже существует.")