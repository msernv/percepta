from init_app import app, db
from models import Upload

with app.app_context():
    count = Upload.query.count()
    Upload.query.delete()
    db.session.commit()
    print(f"🗑️ Удалено {count} старых записей из таблицы uploads")