from app import app, db
import sqlalchemy as sa
from datetime import datetime

with app.app_context():
    inspector = sa.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'subscription_plan' not in columns:
        print("🔄 Добавляем колонку subscription_plan...")
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(20) DEFAULT 'free'"))
            conn.commit()
        print("✅ Колонка subscription_plan добавлена!")
    else:
        print("ℹ️ Колонка subscription_plan уже существует.")
    
    if 'upload_count' not in columns:
        print("🔄 Добавляем колонку upload_count...")
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN upload_count INTEGER DEFAULT 0"))
            conn.commit()
        print("✅ Колонка upload_count добавлена!")
    else:
        print("ℹ️ Колонка upload_count уже существует.")
    
    if 'monthly_reset_date' not in columns:
        print("🔄 Добавляем колонку monthly_reset_date...")
        # Создаем колонку без DEFAULT, чтобы избежать ошибки SQLite
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN monthly_reset_date TIMESTAMP"))
            conn.commit()
        print("✅ Колонка monthly_reset_date добавлена (без DEFAULT)!")
        
        # Обновляем существующие записи через Python
        print("🔄 Устанавливаем CURRENT_TIMESTAMP для существующих пользователей...")
        from models import User
        users = User.query.all()
        for user in users:
            user.monthly_reset_date = datetime.utcnow()
        db.session.commit()
        print(f"✅ Обновлено {len(users)} пользователей")
    else:
        print("ℹ️ Колонка monthly_reset_date уже существует.")
    
    # Обновляем существующих пользователей (если поля не были заполнены)
    print("🔄 Проверяем существующих пользователей...")
    from models import User
    users = User.query.all()
    updated = 0
    for user in users:
        if not user.subscription_plan:
            user.subscription_plan = 'free'
            updated += 1
        if user.upload_count is None:
            user.upload_count = 0
            updated += 1
        if not user.monthly_reset_date:
            user.monthly_reset_date = datetime.utcnow()
            updated += 1
    db.session.commit()
    print(f"✅ Обновлено {updated} полей у пользователей")