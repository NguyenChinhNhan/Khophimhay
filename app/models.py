from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
db = SQLAlchemy()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    filename = db.Column(db.String(255))  # lưu tên file video .mp4
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))

    def __repr__(self):
        return f'<Movie {self.title}>'
#model user
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verify_code = db.Column(db.String(6))
    posts = db.relationship('Post', backref='author', lazy=True)
    avatar = db.Column(db.String(255))
    group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), nullable=True)
    role = db.Column(db.String(20), default='user')  # admin, user, vip1, vip2, ...

    def __repr__(self):
        return f"<User {self.username}>"
#model admin
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password_plain):
        self.password = generate_password_hash(password_plain)

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    def __repr__(self):
        return f'<Admin {self.username}>'
#model report
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Ví dụ: "phim", "bình luận"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Report {self.id} - {self.type}>"
#model post
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Quan hệ với người dùng
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)  # 👉 Thêm trường ảnh đại diện

    def __repr__(self):
        return f"<Actor {self.name}>"
class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(255))  # Tên file ảnh đại diện
class UserGroup(db.Model):
        __tablename__ = 'user_groups'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64), nullable=False)
        users = db.relationship('User', backref='group', lazy=True)
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    movies = db.relationship('Movie', backref='genre', lazy=True)




