from init_app import app, db
from models import User, Upload
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

from forms import LoginForm, RegistrationForm
from core.calculations import calculate_all_metrics
from core.metrics_engine import get_metric_metadata
from core.verticals import get_all_verticals, get_vertical, get_metrics_for_vertical
from core.ai_metric_generator import create_metric_from_query

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    
    # Получаем ВСЕ категории из регистра
    categories = get_all_metric_categories()
    
    categories_metrics = {}
    for category in categories:
        metrics = get_metrics_by_category(category)
        # Фильтруем только доступные для вертикали
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
                'is_active': True
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Все таблицы созданы")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Таблицы в базе данных: {', '.join(tables)}")
    app.run(debug=True)