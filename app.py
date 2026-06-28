from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

# Импортируем db из database.py
from database import db

# Импорт моделей (после создания db)
from models import User, Upload

# Импорт остальных модулей
from forms import LoginForm, RegistrationForm
from core.calculations import calculate_all_metrics
from core.metrics_engine import get_metric_metadata
from core.verticals import get_all_verticals, get_vertical, get_metrics_for_vertical
from core.ai_metric_generator import create_metric_from_query

# ============================================================
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# ============================================================
app = Flask(__name__)
app.config.from_object('config.Config')

# Привязываем db к приложению
db.init_app(app)

# Добавляем функции для шаблонов
app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(get_metric_metadata=get_metric_metadata)

def get_custom_metric(metric_id):
    try:
        if not current_user.is_authenticated:
            return None
        custom_metrics = current_user.custom_metrics or []
        for metric in custom_metrics:
            if str(metric.get('id')) == str(metric_id):
                return metric
        return None
    except:
        return None

app.jinja_env.globals.update(get_custom_metric=get_custom_metric)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Настройка загрузки файлов
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================
# ФУНКЦИЯ ГЕНЕРАЦИИ PDF-ОТЧЕТА
# ============================================================
def generate_pdf_report(company_name, metrics, mrr_history, cohort, risky_clients):
    """Генерирует PDF-отчет с метриками и графиками"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#6f42c1'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=10
    )
    normal_style = styles['Normal']
    center_style = ParagraphStyle(
        'Center',
        parent=normal_style,
        alignment=TA_CENTER
    )
    
    # Заголовок
    story.append(Paragraph("📊 Percepta — Отчет по метрикам", title_style))
    story.append(Paragraph(f"<b>{company_name}</b>", normal_style))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Метрики (таблица)
    metrics_data = [
        [Paragraph("Выручка", center_style), Paragraph(f"${metrics.get('revenue', 0):.0f}", center_style)],
        [Paragraph("MRR", center_style), Paragraph(f"${metrics.get('mrr', 0):.0f}", center_style)],
        [Paragraph("NRR", center_style), Paragraph(f"{metrics.get('nrr', 0):.1f}%", center_style)],
        [Paragraph("Churn", center_style), Paragraph(f"{metrics.get('customer_churn_rate', 0):.1f}%", center_style)],
        [Paragraph("ARPU", center_style), Paragraph(f"${metrics.get('arpu', 0):.1f}", center_style)],
        [Paragraph("Активные", center_style), Paragraph(str(metrics.get('active_users', 0)), center_style)],
        [Paragraph("Ушедшие", center_style), Paragraph(str(metrics.get('churned_users', 0)), center_style)],
        [Paragraph("LTV", center_style), Paragraph(f"${metrics.get('ltv', 0):.0f}", center_style)]
    ]
    
    # Создаем таблицу метрик 4 колонки x 4 строки
    metric_table = Table([metrics_data[i:i+4] for i in range(0, len(metrics_data), 4)], colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    metric_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (1,0), (1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 20))
    
    # График MRR
    if mrr_history and len(mrr_history) > 0:
        story.append(Paragraph("📈 Динамика MRR", heading_style))
        
        fig, ax = plt.subplots(figsize=(6, 3))
        months = [d.get('month', '') for d in mrr_history]
        values = [d.get('value', 0) for d in mrr_history]
        ax.plot(months, values, marker='o', color='#6f42c1', linewidth=2)
        ax.set_ylabel('MRR, $')
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        plt.close()
        
        img = Image(img_buffer, width=6*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 15))
    
    # Когорты
    if isinstance(cohort, dict):
        cohort_list = cohort.get('data', [])
    elif isinstance(cohort, list):
        cohort_list = cohort
    else:
        cohort_list = []

    if cohort_list and len(cohort_list) > 0:
        story.append(Paragraph("🔥 Когортное удержание", heading_style))
        cohort_data = []
        cohort_data.append([Paragraph("Месяц", center_style), Paragraph("Удержание, %", center_style)])
        
        for c in cohort_list[:10]:
            if isinstance(c, dict):
                month = c.get('month', '')
                retention = c.get('retention', 0)
            elif isinstance(c, (list, tuple)):
                month = c[0] if len(c) > 0 else ''
                retention = c[1] if len(c) > 1 else 0
            else:
                month = str(c)
                retention = 0
            cohort_data.append([Paragraph(str(month), center_style), Paragraph(f"{retention}%", center_style)])
        
        cohort_table = Table(cohort_data, colWidths=[2.5*inch, 2.5*inch])
        cohort_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(cohort_table)
        story.append(Spacer(1, 15))
    
    # Рискованные клиенты
    story.append(Paragraph("⚠️ Клиенты в зоне риска", heading_style))
    if risky_clients and len(risky_clients) > 0:
        risk_data = []
        risk_data.append([Paragraph("ID", center_style), Paragraph("Выручка", center_style), 
                         Paragraph("Риск", center_style), Paragraph("Причины", center_style)])
        
        for c in risky_clients[:5]:
            reasons_text = ', '.join(c.get('reasons', []))[:50]
            risk_data.append([
                Paragraph(f"#{c.get('user_id', '')}", center_style),
                Paragraph(f"${c.get('revenue', 0):.2f}", center_style),
                Paragraph(f"{c.get('risk', 0)}%", center_style),
                Paragraph(reasons_text, normal_style)
            ])
        
        risk_table = Table(risk_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 2.5*inch])
        risk_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(risk_table)
    else:
        story.append(Paragraph("✅ Отлично! Клиенты в зоне риска не найдены.", normal_style))
    
    # Футер
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.grey
    )
    story.append(Paragraph("Сгенерировано в Percepta — AI-аналитика для вашего бизнеса", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================
# МАРШРУТЫ
# ============================================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            email=form.email.data,
            company_name=form.company_name.data,
            vertical=form.vertical.data,
            custom_metrics=[]
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    last_upload = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).first()
    
    if not last_upload or not last_upload.processed_data:
        flash('Загрузите данные, чтобы увидеть дашборд', 'info')
        return render_template('dashboard.html', has_data=False, enumerate=enumerate)
    
    data = last_upload.processed_data
    return render_template('dashboard.html', has_data=True, data=data, enumerate=enumerate)

@app.route('/download_report')
@login_required
def download_report():
    """Генерирует и скачивает PDF-отчет"""
    last_upload = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).first()
    
    if not last_upload or not last_upload.processed_data:
        flash('Нет данных для отчета. Загрузите файл.', 'warning')
        return redirect(url_for('dashboard'))
    
    data = last_upload.processed_data
    metrics = data.get('metrics', {})
    cohort = data.get('cohort', [])
    risky = data.get('risky_clients', [])
    mrr_history = data.get('mrr_history', [])
    
    company_name = current_user.company_name or 'Моя компания'
    
    pdf_buffer = generate_pdf_report(company_name, metrics, mrr_history, cohort, risky)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'percepta_report_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Файл не выбран', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Неподдерживаемый формат. Используйте CSV или Excel.', 'danger')
            return redirect(request.url)
        
        # ===== ПРОВЕРКА ЛИМИТОВ ЗАГРУЗКИ =====
        today = datetime.utcnow()
        if current_user.monthly_reset_date and (today - current_user.monthly_reset_date) > timedelta(days=30):
            current_user.upload_count = 0
            current_user.monthly_reset_date = today
            db.session.commit()
        
        if current_user.subscription_plan == 'free' and current_user.upload_count >= 5:
            flash('Вы исчерпали лимит загрузок (5 в месяц). Перейдите на PRO тариф для безлимита.', 'warning')
            return redirect(url_for('pricing'))
        
        try:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)
            
            custom_metrics = current_user.custom_metrics or []
            result = calculate_all_metrics(filepath, current_user.vertical, custom_metrics)
            
            upload = Upload(
                user_id=current_user.id,
                filename=filename,
                processed_data=result
            )
            db.session.add(upload)
            db.session.commit()
            
            # Увеличиваем счётчик загрузок
            current_user.upload_count += 1
            db.session.commit()
            
            flash('Данные успешно загружены и обработаны!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Ошибка при обработке файла: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/api/metrics')
@login_required
def get_metrics():
    last_upload = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.uploaded_at.desc()).first()
    
    if not last_upload or not last_upload.processed_data:
        return jsonify({'error': 'Нет данных'}), 404
    
    return jsonify(last_upload.processed_data)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    from core.metrics_engine import get_metrics_by_category, get_all_metric_categories, METRICS_REGISTRY
    from core.verticals import get_all_verticals, get_vertical, get_metrics_for_vertical
    
    new_vertical = request.args.get('vertical')
    if new_vertical and new_vertical != current_user.vertical:
        if get_vertical(new_vertical):
            current_user.vertical = new_vertical
            current_user.selected_metrics = []
            db.session.commit()
            flash(f'Вертикаль изменена на "{get_vertical(new_vertical).name}"', 'info')
            return redirect(url_for('settings'))
    
    vertical = get_vertical(current_user.vertical)
    if not vertical:
        flash('Вертикаль не найдена, установлена SaaS', 'warning')
        current_user.vertical = 'saas'
        db.session.commit()
        vertical = get_vertical('saas')
    
    available_metric_ids = get_metrics_for_vertical(current_user.vertical)
    categories = get_all_metric_categories()
    
    categories_metrics = {}
    for category in categories:
        metrics = get_metrics_by_category(category)
        filtered = [m for m in metrics if m['id'] in available_metric_ids]
        if filtered:
            categories_metrics[category] = filtered
    
    selected_ids = current_user.selected_metrics or []
    all_verticals = get_all_verticals()
    all_metrics_count = len(METRICS_REGISTRY)
    
    return render_template(
        'settings.html',
        categories=categories,
        categories_metrics=categories_metrics,
        selected_ids=selected_ids,
        vertical=vertical,
        all_verticals=all_verticals,
        all_metrics_count=all_metrics_count
    )

@app.route('/save_settings', methods=['POST'])
@login_required
def save_settings():
    new_vertical = request.form.get('vertical')
    if new_vertical and get_vertical(new_vertical):
        current_user.vertical = new_vertical
    
    selected_metrics = request.form.getlist('metrics')
    
    available_metric_ids = get_metrics_for_vertical(current_user.vertical)
    valid_metrics = [m for m in selected_metrics if m in available_metric_ids]
    
    current_user.selected_metrics = valid_metrics
    db.session.commit()
    
    flash('Настройки успешно сохранены!', 'success')
    return redirect(url_for('settings'))

@app.route('/create_metric', methods=['GET', 'POST'])
@login_required
def create_metric():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        custom_name = request.form.get('custom_name', '').strip()
        
        if not query:
            flash('Пожалуйста, опишите, что вы хотите измерить', 'danger')
            return redirect(url_for('create_metric'))
        
        try:
            parsed, code = create_metric_from_query(query)
            
            name = custom_name if custom_name else parsed['name']
            
            custom_metrics = current_user.custom_metrics or []
            metric_id = len(custom_metrics) + 1
            
            new_metric = {
                'id': metric_id,
                'name': name,
                'description': parsed['description'],
                'query': query,
                'code': code,
                'created_at': datetime.now().isoformat(),
                'is_active': True,
                'is_public': request.form.get('is_public') == 'true'
            }
            
            custom_metrics.append(new_metric)
            current_user.custom_metrics = custom_metrics
            
            if current_user.vertical == 'custom':
                selected = current_user.selected_metrics or []
                metric_id_str = f"custom_{metric_id}"
                if metric_id_str not in selected:
                    selected.append(metric_id_str)
                    current_user.selected_metrics = selected
            
            db.session.commit()
            
            flash(f'✅ Метрика "{name}" успешно создана!', 'success')
            return redirect(url_for('settings'))
            
        except Exception as e:
            flash(f'Ошибка при создании метрики: {str(e)}', 'danger')
            return redirect(url_for('create_metric'))
    
    custom_metrics = current_user.custom_metrics or []
    return render_template('create_metric.html', custom_metrics=custom_metrics)

@app.route('/delete_metric/<int:metric_id>', methods=['POST'])
@login_required
def delete_metric(metric_id):
    custom_metrics = current_user.custom_metrics or []
    new_metrics = [m for m in custom_metrics if m.get('id') != metric_id]
    
    if len(new_metrics) == len(custom_metrics):
        flash('Метрика не найдена', 'danger')
        return redirect(url_for('create_metric'))
    
    current_user.custom_metrics = new_metrics
    
    metric_id_str = f"custom_{metric_id}"
    if current_user.selected_metrics and metric_id_str in current_user.selected_metrics:
        current_user.selected_metrics.remove(metric_id_str)
    
    db.session.commit()
    
    flash('Метрика удалена', 'success')
    return redirect(url_for('create_metric'))

# ============================================================
# МАРКЕТПЛЕЙС МЕТРИК
# ============================================================

@app.route('/marketplace')
@login_required
def marketplace():
    """Страница маркетплейса"""
    all_users = User.query.all()
    public_metrics = []
    
    for user in all_users:
        if user.id == current_user.id:
            continue
        user_metrics = user.custom_metrics or []
        for metric in user_metrics:
            if metric.get('is_public', False):
                metric_copy = metric.copy()
                metric_copy['owner_email'] = user.email
                metric_copy['owner_id'] = user.id
                public_metrics.append(metric_copy)
    
    installed_ids = [str(m.get('id')) for m in (current_user.custom_metrics or [])]
    
    return render_template(
        'marketplace.html',
        public_metrics=public_metrics,
        installed_ids=installed_ids
    )

@app.route('/install_metric/<int:metric_id>', methods=['POST'])
@login_required
def install_metric(metric_id):
    """Устанавливает публичную метрику в аккаунт пользователя"""
    all_users = User.query.all()
    found_metric = None
    
    for user in all_users:
        if user.id == current_user.id:
            continue
        user_metrics = user.custom_metrics or []
        for metric in user_metrics:
            if metric.get('id') == metric_id and metric.get('is_public', False):
                found_metric = metric
                break
        if found_metric:
            break
    
    if not found_metric:
        flash('Метрика не найдена или не является публичной', 'danger')
        return redirect(url_for('marketplace'))
    
    installed = current_user.custom_metrics or []
    for m in installed:
        if m.get('name') == found_metric.get('name'):
            flash('Эта метрика уже установлена', 'info')
            return redirect(url_for('marketplace'))
    
    new_metric = {
        'id': len(installed) + 1,
        'name': found_metric.get('name'),
        'description': found_metric.get('description'),
        'query': found_metric.get('query'),
        'code': found_metric.get('code'),
        'created_at': datetime.now().isoformat(),
        'is_active': True,
        'is_public': False
    }
    
    installed.append(new_metric)
    current_user.custom_metrics = installed
    
    if current_user.selected_metrics is None:
        current_user.selected_metrics = []
    metric_id_str = f"custom_{new_metric['id']}"
    if metric_id_str not in current_user.selected_metrics:
        current_user.selected_metrics.append(metric_id_str)
    
    db.session.commit()
    
    flash(f'✅ Метрика "{found_metric.get("name")}" успешно установлена!', 'success')
    return redirect(url_for('marketplace'))

# ============================================================
# GOOGLE SHEETS INTEGRATION
# ============================================================

@app.route('/google/setup', methods=['GET', 'POST'])
@login_required
def google_setup():
    """Настройка подключения к Google Sheets"""
    if request.method == 'POST':
        spreadsheet_id = request.form.get('spreadsheet_id', '').strip()
        range_name = request.form.get('range_name', 'Лист1').strip()
        
        if not spreadsheet_id:
            flash('Введите ID таблицы', 'danger')
            return redirect(url_for('google_setup'))
        
        if not os.path.exists('service_account.json'):
            flash('Файл service_account.json не найден. Скачайте его из Google Cloud Console.', 'danger')
            return redirect(url_for('google_setup'))
        
        session['google_spreadsheet_id'] = spreadsheet_id
        session['google_range_name'] = range_name
        
        flash('Таблица подключена!', 'success')
        return redirect(url_for('google_import'))
    
    return render_template('google_setup.html')

@app.route('/google/import')
@login_required
def google_import():
    """Импортирует данные из Google Sheets"""
    from google_sheets_integration import get_sheet_data, process_sheet_data
    
    spreadsheet_id = session.get('google_spreadsheet_id')
    range_name = session.get('google_range_name', 'Лист1')
    
    if not spreadsheet_id:
        flash('Сначала настройте таблицу', 'warning')
        return redirect(url_for('google_setup'))
    
    try:
        df = get_sheet_data(spreadsheet_id, range_name)
        if df is None or df.empty:
            flash('Нет данных в таблице', 'info')
            return redirect(url_for('dashboard'))
        
        df = process_sheet_data(df)
        if df.empty:
            flash('Нет данных после обработки', 'danger')
            return redirect(url_for('dashboard'))
        
        result = calculate_all_metrics(df, current_user.vertical, current_user.custom_metrics or [])
        upload = Upload(
            user_id=current_user.id,
            filename=f'google_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            processed_data=result
        )
        db.session.add(upload)
        db.session.commit()
        
        flash(f'Данные импортированы ({len(df)} записей)!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Ошибка импорта: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ============================================================
# ПОДПИСКИ И МОНЕТИЗАЦИЯ
# ============================================================

@app.route('/pricing')
def pricing():
    """Страница с тарифами"""
    return render_template('pricing.html')

@app.route('/upgrade_to_pro')
@login_required
def upgrade_to_pro():
    """Обновляет тариф пользователя до PRO"""
    current_user.subscription_plan = 'pro'
    db.session.commit()
    flash('🎉 Вы перешли на тариф PRO!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/downgrade_to_free')
@login_required
def downgrade_to_free():
    """Возвращает пользователя на бесплатный тариф"""
    current_user.subscription_plan = 'free'
    current_user.upload_count = 0
    current_user.monthly_reset_date = datetime.utcnow()
    db.session.commit()
    flash('Вы вернулись на бесплатный тариф', 'info')
    return redirect(url_for('dashboard'))

# ============================================================
# ПЛАТЕЖИ ЧЕРЕЗ ROBOKASSA
# ============================================================

@app.route('/payment/create')
@login_required
def create_payment_route():
    from robokassa_integration import get_payment_url
    
    amount = 990
    description = 'Подписка Percepta PRO (1 месяц)'
    inv_id = current_user.id * 1000 + int(datetime.now().timestamp()) % 1000
    
    payment_url = get_payment_url(amount, description, current_user.email, inv_id)
    
    session['payment_inv_id'] = inv_id
    session['payment_amount'] = amount
    
    return redirect(payment_url)

@app.route('/payment/success')
@login_required
def payment_success():
    """Страница успешной оплаты"""
    inv_id = request.args.get('InvId')
    out_sum = request.args.get('OutSum')
    
    if not inv_id or not out_sum:
        flash('Ошибка: не получены данные о платеже', 'danger')
        return redirect(url_for('dashboard'))
    
    from robokassa_integration import check_payment
    
    if check_payment(inv_id, out_sum):
        current_user.subscription_plan = 'pro'
        db.session.commit()
        flash('🎉 Оплата прошла успешно! Вы на тарифе PRO!', 'success')
    else:
        flash('Оплата не подтверждена. Попробуйте еще раз.', 'warning')
    
    return redirect(url_for('dashboard'))

@app.route('/payment/cancel')
@login_required
def payment_cancel():
    """Страница отмены оплаты"""
    flash('Вы отменили оплату', 'info')
    return redirect(url_for('pricing'))

# ============================================================
# ОБРАТНАЯ СВЯЗЬ И О ПРОЕКТЕ
# ============================================================

@app.route('/about')
def about():
    """Страница 'О проекте'"""
    return render_template('about.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    """Страница обратной связи"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', 'general')
        message = request.form.get('message', '').strip()
        
        if not message:
            flash('Пожалуйста, напишите сообщение', 'danger')
            return redirect(url_for('feedback'))
        
        # Сохраняем в базу данных (можно добавить модель позже)
        # Пока просто показываем сообщение
        flash('✅ Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('feedback.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Все таблицы созданы")
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Таблицы в базе данных: {', '.join(tables)}")
    
    app.run(debug=True)