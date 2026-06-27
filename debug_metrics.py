from init_app import app, db
from models import Upload
from core.calculations import calculate_all_metrics
import json

with app.app_context():
    # Находим последнюю загрузку
    upload = Upload.query.order_by(Upload.uploaded_at.desc()).first()
    if upload and upload.processed_data:
        print("✅ Данные найдены")
        metrics = upload.processed_data.get('metrics', {})
        print(f"📊 Найдено метрик: {len(metrics)}")
        print("Первые 5 метрик:")
        for key, value in list(metrics.items())[:5]:
            print(f"  {key}: {value}")
    else:
        print("❌ Данные не найдены. Загрузите файл.")