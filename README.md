# 📊 Percepta — AI-аналитика для B2B SaaS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Deploy](https://img.shields.io/badge/GitHub_Pages-Live-purple.svg)](https://msernv.github.io/percepta)

**Percepta** — это AI-платформа для аналитики и прогнозирования в B2B SaaS. Помогает компаниям отслеживать ключевые метрики, находить утечки в доходах и прогнозировать отток клиентов с точностью до 90%.

🔗 **Демо-версия:** [msernv.github.io/percepta](https://msernv.github.io/percepta)  
📧 **Тестовый доступ:** `test@percepta.com` / `password123`

---

## 🚀 Ключевые возможности

- 📊 **70+ метрик** — от MRR и NRR до LTV и CAC
- 🤖 **AI-прогнозирование** — предсказываем отток на основе поведения
- 📱 **PWA-приложение** — работайте с телефона и планшетов
- 🔗 **Интеграции** — Google Sheets, CSV, Excel
- 🛒 **Маркетплейс метрик** — делитесь и устанавливайте метрики
- 💰 **Монетизация** — подписки (Free / PRO) + Robokassa
- 🌗 **Тёмная тема** — комфортная работа в любое время

---

## 📊 Метрики

| Категория | Метрики |
| :--- | :--- |
| **Финансы** | Выручка, MRR, ARR, NRR, GRR, LTV, CAC, LTV/CAC, Payback Period, Expansion Revenue, Downgrade Revenue, Churned Revenue, ARPU, ARPPU, Monthly Growth Rate |
| **Отток** | Customer Churn, Revenue Churn, Net Churn, Retention Rate, Downgrade Rate, Upgrade Rate, Reactivation Rate |
| **Активность** | DAU, WAU, MAU, Stickiness Ratio, Active Users, Churned Users, Trial Users, New Users |
| **Воронка** | Trial Conversion, Lead → MQL, MQL → SQL, SQL → Closed-Won, Time to Value |
| **Продукт** | Feature Adoption, Session Duration, Sessions per User, Bounce Rate |
| **E-commerce** | AOV, Conversion Rate, Cart Abandonment, Return Rate, CLV, Repurchase Rate |
| **FinTech** | Transaction Volume, Average Transaction, Fraud Rate, Net Interest Margin |
| **Подписки** | Average Subscription Length, Payment Failure Rate, Dunning Success Rate |
| **Операционные** | Inventory Turnover, Staff Efficiency, Footfall, Average Check, Loyalty Rate, NPS |
| **Качество сервиса** | Support Ticket Volume, Response Time, Resolution Time, CSAT |

---

## 🛠 Технологии

- **Backend:** Python 3.11, Flask, SQLAlchemy
- **Frontend:** Bootstrap 5, Plotly, Chart.js
- **Database:** PostgreSQL
- **PDF:** ReportLab
- **Payments:** Robokassa
- **Deploy:** GitHub Pages, Docker-ready

---

## 📂 Структура проекта

percepta/
├── core/ # Ядро приложения
│ ├── calculations.py # Расчёт метрик
│ ├── metrics_engine.py # Реестр метрик
│ ├── predictor.py # AI-прогнозирование
│ ├── verticals.py # Вертикали бизнеса
│ └── ai_metric_generator.py # Генератор метрик через AI
├── templates/ # HTML-шаблоны
│ ├── base.html # Базовый шаблон
│ ├── dashboard.html # Дашборд
│ ├── upload.html # Загрузка данных
│ ├── settings.html # Настройки
│ ├── marketplace.html # Маркетплейс
│ ├── pricing.html # Тарифы
│ ├── about.html # О проекте
│ └── feedback.html # Обратная связь
├── static/ # CSS, JS, иконки
│ ├── icons/ # PWA иконки
│ ├── sw.js # Service Worker
│ └── manifest.json # PWA манифест
├── docs/ # GitHub Pages
│ └── index.html # Демо-версия
├── app.py # Главный файл приложения
├── config.py # Настройки
├── models.py # Модели базы данных
├── database.py # Инициализация БД
├── forms.py # Формы авторизации
├── requirements.txt # Зависимости
├── Procfile # Для деплоя
├── runtime.txt # Версия Python
└── README.md # Этот файл


---

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Клонируй репозиторий
git clone https://github.com/msernv/percepta.git
cd percepta

# Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate

# Установи зависимости
pip install -r requirements.txt

# Настрой базу данных PostgreSQL
# Создай файл .env с переменными окружения

# Запусти приложение
python app.py

Демо-доступ
GitHub Pages: msernv.github.io/percepta
Тестовый пользователь: test@percepta.com / password123

🐳 Docker

docker build -t percepta .
docker run -p 5000:5000 percepta

🤝 Вклад в проект
Форкни репозиторий

Создай ветку для фичи (git checkout -b feature/amazing-feature)

Закоммить изменения (git commit -m 'Add amazing feature')

Запушь (git push origin feature/amazing-feature)

Открой Pull Request

Подробнее: CONTRIBUTING.md

📄 Лицензия
Распространяется под лицензией MIT. Подробности в файле LICENSE.

📬 Контакты
Email: msernv@gmail.com
Telegram: @mkhlsmirnov
GitHub: msernv/percepta

⭐ Если проект полезен — поставь звезду!