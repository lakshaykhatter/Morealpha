from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CommentForm
from app.models import User, Post, Ticker, Comment
from app import db
from werkzeug.urls import url_parse
import secrets
from PIL import Image
import os
import bleach


@app.route('/')
@app.route('/index')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by('timestamp').paginate(page, 3, False)
	next_url = url_for('index', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
	return render_template("index.html", posts=posts.items, next_url=next_url, prev_url=prev_url)

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
	posts = Post.query.filter_by(user_id=user.id).all()
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
		tickers = request.form.getlist('tickers[]')
		tickers = checkTickers(tickers)

		if title == "":
			return jsonify({'error': "Please add a title"}) 
		elif tickers == []:
			return jsonify({'error': "Please enter a valid ticker"})
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

	tickerList = [ {"title":str(ticker.symbol)} for ticker in Ticker.query.all()]
	return render_template('createpost.html', tickers=tickerList)

@app.route('/post/<post>', methods=["GET", "POST"])
@login_required
def post(post):
	post = Post.query.filter_by(id=post).first_or_404()
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		redirect(request.referrer)
	return render_template("post.html", post=post, form=form)



@app.route('/editpost/<int:id>', methods=["GET", "POST"])
def editPost(id):
	p = Post.query.filter_by(id=id).first_or_404()
	
	if request.method == "GET":
		
		if current_user.id == p.author.id:
			title = p.title
			body = p.body
			tickerList = [ {"title":str(ticker.symbol)} for ticker in Ticker.query.all()]
			postTickers = [str(ticker.symbol) for ticker in p.tickers]
			return render_template("editpost.html", title=title, body=body, tickers=tickerList, postTickers=postTickers)
	
	elif request.method == "POST":
		title = request.form['title']
		body = request.form['post']
		tickers = request.form.getlist('tickers[]')
		tickers = checkTickers(tickers)

		if title == "":
			return jsonify({'error': "Please add a title"}) 
		elif tickers == []:
			return jsonify({'error': "Please enter a valid ticker"})
		elif body == "":
			return jsonify({'error': "Please create a post"})

		p.title = title
		p.body = body
		p.user_id = current_user.id
		p.tickers = [] 
		
		for tick in tickers:
			p.tickers.append(tick)

		db.session.add(p)
		db.session.commit()


		return jsonify({'success': "Congratulations you've updated your post"})

	return redirect(url_for('user', username=current_user.username))


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

@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
	post = Post.query.filter_by(id=post_id).first_or_404()
	if action == 'like':
		current_user.like_post(post)
		db.session.commit()
	if action == 'unlike':
		current_user.unlike_post(post)
		db.session.commit()
	return redirect(request.referrer)


@app.route('/followuser/<username>')
@login_required
def followuser(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('index'))
    if user == current_user:
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('user', username=username))

@app.route('/unfollowuser/<username>')
@login_required
def unfollowuser(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('index'))
    if user == current_user:
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/user/<username>/<action>')
@login_required
def followLookup(username, action):
	user = User.query.filter_by(username=username).first_or_404()
	if action == "following":
		return render_template('follow.html', action=action, user=user)
	elif action == "followers":
		return render_template('follow.html', action=action, user=user)


