from flask import Blueprint, render_template, request, redirect, flash, abort
from .models import Task, User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Task(content=task_content, user_id=current_user.id)

        db.session.add(new_task)
        db.session.commit()
        return redirect('/')

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    total = len(tasks)
    completed = sum(1 for task in tasks if task.completed)

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed
    )


@main.route('/delete/<int:id>')
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@main.route('/toggle/<int:id>')
@login_required
def toggle(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        abort(403)
    task.completed = not task.completed
    db.session.commit()
    return redirect('/')

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        task.content = request.form['content']
        db.session.commit()
        return redirect('/')

    return render_template('edit.html', task=task)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 🔴 CHECK IF USER EXISTS (PUT IT HERE)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return redirect('/register')

        # 🔐 HASH PASSWORD
        hashed_password = generate_password_hash(password)

        # 👤 CREATE USER
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # 🔓 AUTO LOGIN
        login_user(user)

        return redirect('/')

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            return redirect('/')
        else:
            flash("Invalid username or password")

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')