from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(100))
    vertical = db.Column(db.String(50), default='saas')
    selected_metrics = db.Column(db.JSON, default=list)
    custom_metrics = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Поля для подписок
    subscription_plan = db.Column(db.String(20), default='free')  # 'free' или 'pro'
    upload_count = db.Column(db.Integer, default=0)  # Счётчик загрузок в текущем месяце
    monthly_reset_date = db.Column(db.DateTime, default=datetime.utcnow)  # Дата сброса счётчика
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    raw_data = db.Column(db.JSON)
    processed_data = db.Column(db.JSON)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='uploads')
    
    def __repr__(self):
        return f'<Upload {self.filename}>'