# Архитектура Percepta

## Общая структура

Frontend (HTML + Bootstrap + Plotly)
        ↓
Flask Application (app.py)
        ↓
Core Modules (calculations, metrics_engine, predictor)
        ↓
Database (PostgreSQL)

## Модули

### core/calculations.py
Главный модуль расчёта метрик. Содержит функции для:
- Загрузки данных из CSV/Excel
- Расчёта MRR, NRR, Churn, LTV, CAC и других метрик
- Построения когорт
- Поиска рискованных клиентов

### core/metrics_engine.py
Реестр всех метрик с метаданными (название, описание, категория, иконка).

### core/predictor.py
Модуль AI-прогнозирования оттока на основе:
- Активности пользователя
- Истории платежей
- Обращений в поддержку

### core/verticals.py
Вертикали бизнеса (SaaS, E-commerce, FinTech, Retail) с набором метрик для каждой.

## Модели данных

### User
- id, email, password_hash, company_name, vertical
- selected_metrics (JSON)
- custom_metrics (JSON)
- subscription_plan, upload_count, monthly_reset_date

### Upload
- id, user_id, filename, processed_data (JSON)

## Интеграции

### Google Sheets
- Чтение данных через API
- Требуется service_account.json

### Robokassa
- Приём платежей
- Используется Password #1 и Password #2

## Деплой

### Локальный запуск
python app.py

### GitHub Pages
Статическая демо-версия в папке docs/