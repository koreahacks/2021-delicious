from flask import Flask, render_template, url_for, request, redirect, session
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from SeMalZip_web import namespace

import datetime, base64
import sys, os, shutil
from urllib.parse import unquote

# 웹 서버 생성하기
app = Flask(__name__)

UPLOAD_DIR = "\static\profile_image"
app.config['SECRET_KEY'] = 'delicious_flask'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_DIR'] = UPLOAD_DIR



db = SQLAlchemy(app)



class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    # profile_image = db.Column(db.String(100), default=os.path.join(UPLOAD_DIR, 'default.png'))

    posts = db.relationship('Review', backref='author', lazy=True)

    def __init__(self, username, email, password, nickname, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nickname = nickname

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}', '{self.password}',' '{self.nickname}')>"

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



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else :
        print(request)
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username).first()
        print(data, User.check_password(data, data.password))
        if User.check_password(data, password) is True:
            session['logged_in'] = True
            print('login success')
            return redirect(url_for('home'))
        else:
            print('login fail', username, password)
            return redirect(url_for('login'))
    # email = request.form['email']
    # passw = request.form['password']
    # login_success = False

    # data = User.query.filter_by(email=email)
    # for user in data:
    #     if user.check_password(passw) is True:
    #         login_success = True
    #         current_user = user

    # if login_success is True : 
    #     session['logged_in'] = True
    #     session['user_email'] = email
    #     session['username'] = current_user.username
    #     return redirect(url_for('home'))
    # else :
    #     return "<div>"+email+"</div>"+"<div>"+passw+"</div>"

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/edit_post', methods=['GET','POST'])
def edit_post():
    user_email = session['user_email']
    title = request.form['title']
    article = request.form['article']

    author = User.query.filter_by(email=user_email).first()
    
    new_post = Review(title=title, content=article, author=author)

    try: 
        db.session.add(new_post)
        db.session.commit()
    except:
        db.session().rollback()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else :
        name = request.form['username']
        email = request.form['email']
        passw = request.form['password']
        nickname = request.form['nickname']
        print(name, email, passw, nickname)
        # is_profile_set = request.form.get('is_profile_set')
        # if is_profile_set is None :
        #     profile_image = "default.png"
            
        # else :
        #     profile_image = name + ".png"

        # path = os.path.join("static/profile_image/", profile_image)

        # if is_profile_set is not None :
        #     shutil.copyfile(
        #     os.path.join("flask_study/static/profile_image/", "temp_profile.png"),  
        #     "flask_study/" + path)
        
        

        new_user = User(username=name, email=email, password=passw, nickname=nickname)
        try:
            db.session.add(new_user)
            db.session.commit()
        except :
            db.session.rollback()
        return redirect(url_for('home'))