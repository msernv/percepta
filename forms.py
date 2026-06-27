from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    company_name = StringField('Название компании', validators=[DataRequired()])
    vertical = SelectField(
        'Тип бизнеса',
        choices=[
            ('saas', 'SaaS / Подписки'),
            ('ecommerce', 'E-commerce'),
            ('fintech', 'FinTech'),
            ('subscription', 'Подписки (общие)'),
            ('retail', 'Ритейл / Офлайн'),
            ('custom', 'Прочее (Custom) — все метрики')
        ],
        default='saas'
    )
    submit = SubmitField('Зарегистрироваться')