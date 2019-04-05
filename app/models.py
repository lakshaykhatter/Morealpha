from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

users_tickers = db.Table('users_tickers',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('ticker_id', db.Integer, db.ForeignKey('ticker.id'))
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

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def __repr__(self):
		return "<User {}>".format(self.username)

posts_tickers = db.Table('posts_tickers',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('ticker_id', db.Integer, db.ForeignKey('ticker.id'))
)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(200), index=True)
	tickers = db.relationship("Ticker",secondary=posts_tickers, backref="posts")
	
	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Ticker(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(5), index=True)
	name = db.Column(db.String(200), index=True)
	sector = db.Column(db.String(200),index=True)

	def __repr__(self):
		return '<Ticker: {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))