from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import bleach
from markdown import markdown

users_tickers = db.Table('users_tickers',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('ticker_id', db.Integer, db.ForeignKey('ticker.id'))
	)

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	first_name = db.Column(db.String(120), index=True)
	last_name = db.Column(db.String(120), index=True)
	about_me = db.Column(db.String(1000))
	image_file = db.Column(db.String(200), default='default.png')
	tickers = db.relationship("Ticker", secondary=users_tickers, backref="users")
	liked = db.relationship('PostLike',foreign_keys='PostLike.user_id',backref='user', lazy='dynamic')
	followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def followTicker(self, ticker):
		if ticker not in self.tickers:
			self.tickers.append(ticker)

	def unfollowTicker(self, ticker):
		if ticker in self.tickers:
			self.tickers.remove(ticker)

	def like_post(self, post):
		if not self.has_liked_post(post):
			like = PostLike(user_id=self.id, post_id=post.id)
			db.session.add(like)

	def unlike_post(self, post):
		if self.has_liked_post(post):
			PostLike.query.filter_by(
				user_id=self.id,
				post_id=post.id).delete()

	def has_liked_post(self, post):
		return PostLike.query.filter(
			PostLike.user_id == self.id,
			PostLike.post_id == post.id).count() > 0
	
	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())


	def __repr__(self):
		return "<User {}>".format(self.username)

class PostLike(db.Model):
	__tablename__ = 'post_like'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


posts_tickers = db.Table('posts_tickers',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
	db.Column('ticker_id', db.Integer, db.ForeignKey('ticker.id'))
)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.Text, index=True)
	tickers = db.relationship("Ticker",secondary=posts_tickers, backref="posts")
	likes = db.relationship('PostLike', backref='post', lazy='dynamic')
	comments = db.relationship('Comment', backref='post', lazy='dynamic')
	
	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Ticker(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(5), index=True)
	name = db.Column(db.String(200), index=True)
	sector = db.Column(db.String(200),index=True)
	exchange = db.Column(db.String(200), index=True)

	def __repr__(self):
		return '<Ticker: {}>'.format(self.name)

class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) 
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator): 
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
		target.body_html = bleach.linkify(bleach.clean( markdown(value, output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))