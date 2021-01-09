from flask_sqlalchemy import SQLAlchemy
from SeMalZip_web import db

UPLOAD_DIR = "\static\profile_image"

class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(100), default=os.path.join(UPLOAD_DIR, 'default.png'))

    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, email, password, profile_image, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        self.profile_image = profile_image

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email}')>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Review(db.Model):
    __table_name__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique = True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    radial_data = db.Column(db.String(120))
    image_data = db.Column(db.String(256))

    def __init__(self, title, content, data_posted, user_id, radial_data, image_data, **kwargs):
        self.title = title
        self.content = content
        self.data_posted = data_posted
        self.user_id = user_id
        self.radial_data = radial_data
        self.image_data = image_data

    def __repr__(self):
        return f"<Review('{self.id}', '{self.title}')>"