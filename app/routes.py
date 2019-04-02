from flask import render_template, flash, redirect, url_for, request
from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Post, Ticker
from app import db
from werkzeug.urls import url_parse



@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/ticker/<ticker>')
def ticker(ticker):
	ticker = ticker.upper()
	ticker = Ticker.query.filter_by(symbol=ticker).first_or_404()
	posts = ticker.posts
	return render_template('ticker.html', ticker=ticker, posts=posts)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(user_id=user.id)
	tickers = Ticker.query.get(1)
	return render_template('user.html', user=user, posts=posts, tickers=tickers)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.about_me = form.about_me.data
		current_user.first_name = form.first_name.data
		current_user.last_name = form.last_name.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.about_me.data = current_user.about_me
		form.first_name.data = current_user.first_name
		form.last_name.data = current_user.last_name

	return render_template('edit_profile.html', title='Edit Profile', form=form)

