from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from models import db, User, Student
import os

app = Flask(__name__, instance_relative_config=True)

app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Observation 9 & 10: Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    # Observation 18: Print Form Validation Result to Console
    if form.validate_on_submit():
        print("Form submitted successfully!")

        # Observation 13: Prevent Duplicate Email Registration
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            password=hashed_pw
        )

        db.session.add(user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('login'))
    
    elif request.method == 'POST':
        print("Validation failed.")

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        print("Login attempt for: " + form.email.data)
        
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('students'))
        else:
            flash("Invalid email or password.")

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/students')
@login_required
def students():
    # Observation 6: Sort Students Alphabetically by Full Name
    student_list = Student.query.order_by(Student.full_name).all()

    return render_template(
        'students.html',
        students=student_list
    )

@app.route('/add-student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    email = request.form['email']

    student = Student(
        full_name=name,
        email=email
    )

    db.session.add(student)
    db.session.commit()
    flash(f"Student {name} added successfully!")
    return redirect(url_for('students'))

@app.route('/delete-student/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))

if __name__ == '__main__':
    if not os.path.exists(os.path.join(app.instance_path, 'app.db')):
        os.makedirs(app.instance_path, exist_ok=True)
        with app.app_context():
            db.create_all()

    app.run(debug=True)