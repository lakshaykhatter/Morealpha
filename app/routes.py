from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post, Ticker
from app import db
from werkzeug.urls import url_parse
import secrets
from PIL import Image
import os


@app.route('/')
@app.route('/index')
def index():
	posts = Post.query.order_by('timestamp').limit(10)
	sectors = Ticker.query.with_entities(Ticker.sector).distinct().all()

	return render_template("index.html", posts=posts, sectors=sectors )

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


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, 
				first_name=form.first_name.data, last_name=form.last_name.data)
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			user.image_file = picture_file
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
	posts = Post.query.filter_by(user_id=user.id).limit(5).all()
	posts = None if posts == [] else posts
	tickers = user.tickers

	if user.image_file:
		image_file = url_for('static', filename='profile_pics/' + user.image_file)
	else:
		image_file = url_for('static', filename='profile_pics/default.png')
	return render_template('user.html', user=user, posts=posts, tickers=tickers, image_file=image_file)

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


@app.route('/ticker/<ticker>')
def ticker(ticker):
	ticker = ticker.upper()
	ticker = Ticker.query.filter_by(symbol=ticker).first_or_404()
	posts = ticker.posts
	return render_template('ticker.html', ticker=ticker, posts=posts)


def checkTickers(tickers):
	tickerObjects = []
	for ticker in tickers:
		tick = Ticker.query.filter_by(symbol=ticker.upper()).first()
		if tick != None:
			tickerObjects.append(tick)
	return tickerObjects



@app.route('/post', methods=["GET", "POST"])
@login_required
def createpost():
	if request.method == "POST":
		
		title = request.form['title']
		body = request.form['post']
		ticker1 = request.form['ticker1']
		ticker2 = request.form['ticker2']
		ticker3 = request.form['ticker3']
		ticker4 = request.form['ticker4']
		ticker5 = request.form['ticker5']

		tickers = [ticker1, ticker2, ticker3, ticker4, ticker5]
		tickers = checkTickers(tickers)
		if title == "":
			return jsonify({'error': "Please add a title"}) 
		elif ticker1 == "" or tickers==[]:
			return jsonify({'error': "Please enter a valid ticker at the first input"})
		elif body == "":
			return jsonify({'error': "Please create a post"})

		p = Post()
		p.title = title
		p.body = body
		p.user_id = current_user.id

		for tick in tickers:
			p.tickers.append(tick)
		db.session.add(p)
		db.session.commit()


		return jsonify({'success': "Congratulations you've created a post"})

	return render_template('createpost.html')

@app.route('/post/<post>')
def post(post):
	post = Post.query.get(post)
	return render_template("post.html", post=post)


@app.route('/follow/<ticker>')
@login_required
def followTicker(ticker):
	ticker = Ticker.query.filter_by(symbol=ticker).first()
	current_user.followTicker(ticker)
	db.session.commit()	
	return redirect(url_for('ticker', ticker=ticker.symbol))

@app.route('/unfollow/<ticker>')
@login_required
def unfollowTicker(ticker):
	ticker = Ticker.query.filter_by(symbol=ticker).first()
	current_user.unfollowTicker(ticker)
	db.session.commit()
	return redirect(url_for('ticker', ticker=ticker.symbol))


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

