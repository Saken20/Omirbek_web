from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = '228'  # Замените на реальный секретный ключ

# Настройка SQLite базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    profile_photo = db.Column(db.String(255), default='/static/images/profile_photo.jpg')

    def __repr__(self):
        return f'<User {self.email}>'

# Создание базы данных при первом запуске
with app.app_context():
    db.create_all()
    # Добавление тестового пользователя, если он еще не существует
    if not User.query.filter_by(email='user@example.com').first():
        test_user = User(
            email='user@example.com',
            password=generate_password_hash('password123'),
            first_name='Иван',
            last_name='Иванов',
            profile_photo='/static/images/profile_photo.jpg'
        )
        db.session.add(test_user)
        db.session.commit()

# Дефолтная страница (/)
@app.route('/')
def index():
    return render_template('index.html', logged_in='user' in session)

# Страница услуг
@app.route('/services')
def services():
    return render_template('services.html', logged_in='user' in session)

# Страница профиля (только для авторизованных)
@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Пожалуйста, войдите в аккаунт для просмотра профиля.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=session['user']).first()
    return render_template('profile.html', user=user)

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = email
            flash('Успешный вход!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'error')
    
    return render_template('login.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Проверка, существует ли пользователь
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован.', 'error')
            return redirect(url_for('register'))
        
        # Создание нового пользователя
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            profile_photo='/static/images/profile_photo.jpg'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Пожалуйста, войдите.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)