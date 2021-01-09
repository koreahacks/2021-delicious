from flask import Flask, render_template, url_for, request, redirect, session
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
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

    reviews = db.relationship('Review', backref='author', lazy=True)

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
    
    cat_money = db.Column(db.Integer)
    cat_easy = db.Column(db.Integer)
    cat_safe = db.Column(db.Integer)
    cat_space = db.Column(db.Integer)
    cat_facility = db.Column(db.Integer)
    cat_god = db.Column(db.Integer)

    image_data = db.Column(db.String(256))

    def __init__(self, title, content, data_posted, user_id, cat_money, cat_easy, cat_safe, cat_space, cat_facility, cat_god, image_data, **kwargs):
        self.title = title
        self.content = content
        self.data_posted = data_posted
        self.user_id = user_id
        
        self.cat_money = cat_money
        self.cat_easy = cat_easy
        self.cat_safe = cat_safe
        self.cat_space = cat_space
        self.cat_facility = cat_facility
        self.cat_god = cat_god

        self.image_data = image_data

    def __repr__(self):
        return f"<Review('{self.id}', '{self.title}')>"



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search():
    review_list = Review.query.all()
    category = request.args.get("cat", "keyword")
    if category is "money":
        review_list = Review.query.order_by(Review.cat_money.desc())
    elif category is "easy" :
        review_list = Review.query.order_by(Review.cat_easy.desc())
    elif category is "safe" :
        review_list = Review.query.order_by(Review.cat_safe.desc())
    elif category is "space" :
        review_list = Review.query.order_by(Review.cat_space.desc())
    elif category is "facility" :
        review_list = Review.query.order_by(Review.cat_facility.desc())
    elif category is "god" :
        review_list = Review.query.order_by(Review.cat_god.desc())
    return render_template('search.html', list=review_list)

@app.route("/review")
def review():
    review_index = request.args.get('review_num', "0")
    review_article = Review.query.filter_by(id=review_index).first()
    return render_template('review.html', rindex=review_index, rarticle=review_article)

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
            session['username'] = username
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

@app.route('/editpost', methods=['GET','POST'])
def edit_post():
    if request.method == "GET" :
        return render_template('editpost.html')
    else:
        username = session['username']
        title = request.form['title']
        article = request.form['article']

        cat_money = request.form['cat_money']
        cat_easy = request.form['cat_easy']
        cat_safe = request.form['cat_safe']
        cat_facility = request.form['cat_facility']
        cat_space = request.form['cat_space']
        cat_god = request.form['cat_god']

        author = User.query.filter_by(username=username).first()
        image_data=""
        uploaded_image = request.files.getlist("image")
        for image in uploaded_image :
            f = image
            f.save(secure_filename(f.filename))
            image_data += f.filename+", " 
        new_post = Review(title=title, content=article, author=author, cat_money=cat_money, cat_easy=cat_easy, cat_safe=cat_safe, cat_space=cat_space, cat_facility=cat_facility, cat_god=cat_god, image_data=image_data, data_posted=datetime.datetime, user_id=author.id)

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