from flask import Flask, flash,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
import json
import pymysql 
from flask_mail import Mail,Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, render_template, flash
import os
import time
import math


local_server=True
pymysql.install_as_MySQLdb()
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,  # Port number for SSL
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail=Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['UPLOAD_FOLDER'] = '/home/to23/Work/Learning/flask_learning/static'

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI']= params['local_uri']
    print("*********dgdgdbhdg***************88")

# else (local_server):
#     app.config['SQLALCHEMY_DATABASE_URI']= params['local_uri']

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://classicmodelsuser:Sydney#58^@110.226.124.45:3306/classicmodels'
db = SQLAlchemy(app)    

##################################### models######################################

class blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tiltle = db.Column(db.String(100),unique=True,nullable=True)
    content = db.Column(db.Text(100),nullable=True)
    date = db.Column(db.DateTime(100),nullable=True)

class contact(db.Model):
    cont_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True,nullable=True)
    email = db.Column(db.String(100),nullable=True)
    phone_number = db.Column(db.String(100),nullable=True)
    message = db.Column(db.Text(100),nullable=True)
    date = db.Column(db.DateTime(100),nullable=True)

class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),unique=True,nullable=True)
    slug = db.Column(db.String(100),unique=True,nullable=True)
    content = db.Column(db.Text(100),nullable=True)
    date = db.Column(db.DateTime(100),nullable=True)
    file_path = db.Column(db.String(255)) 
    

class user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

####################################views###############################################

@app.route("/")
def home():
    posts_data = posts.query.all()
    last=math.ceil(len(posts_data)/2)
    print(last,"********last*********")
    page=request.args.get('number')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)
    posts_data=posts_data[(page-1)*4:(page-1)*4+4]
    #first
    if int(page) ==1:
       prev=""
       next="/?number="+str(page+1)
    #last
    elif(int(page)==last):
       prev="/?number="+str(page-1)
       next=""
    #middle
    else:
        next="/?number="+str(page+1)
        prev="/?number="+str(page-1)
   
    return render_template('index.html',params=params,posts_data=posts_data,prev=prev,next=next)

@app.route("/register",methods=['GET','POST'])
def signin():
    if request.method=="POST":
        name=request.form.get('name')
        password=request.form.get('password')
        auth_data = user.query.filter_by(username=name).first()
        if auth_data:
            flash('Username already exists')
            return render_template('register.html')
        
        if auth_data is None:
            new_user = user(username=name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in
            login_user(new_user)
            return redirect(url_for('home'))
    else:
        return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    # if 'user' in session and session['user'] == ['']
    if request.method == "POST":
        user_data = user.query.filter_by(
            username=request.form.get("name")).first()
        if user_data:
           if user_data and user_data.check_password(request.form.get("password")):
              login_user(user_data)
              return redirect(url_for("home"))
        else:
            render_template("login.html")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template('aboutus.html')

@app.route("/contact", methods=['GET', 'POST'])
def contacts():
    if request.method =="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        phone_number=request.form.get('phone_number')
        message=request.form.get('message')
        date=request.form.get('date')
        entry =contact(name=name,email=email,phone_number=phone_number,message=message,date=date)
        db.session.add(entry)
        db.session.commit()
        import smtplib
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        email = "630786shahidmalik@gmail.com"
        password = "fvue mqlr yice tbni"
        server.login(email, password)
        sender_email = email
        receiver_email = email
        subject = "Test Email"
        body = "This is a test email sent using smtplib in Python."
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        
        return redirect(url_for('contacts'))

    return render_template('contact.html')

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post_data=posts.query.filter_by(slug=post_slug).first()
    return render_template("aboutus.html",params=params,post_data=post_data)


    
@app.route("/blog",methods=['GET','POST'])
def blogs():
    if request.method=="POST":
        title=request.form.get('title')
        slug=request.form.get('slug')
        content=request.form.get('content')
        date=request.form.get('date')
        file = request.files['file']
        print(file,"**************************88888")

        if file:
            filename = str(int(time.time())) + "_" + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(filepath,"8************filepath************")
            file.save(filepath)
            filename = filepath.split('/')[-1]
            data = posts(title=title, slug=slug, content=content, date=date, file_path=filename)
            print(data.file_path,"*************data.filepath***************")
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("blog.html")

@app.route("/admin")
def adminpanel():
    posts_data = posts.query.all()
    return render_template("admin_panel.html",posts_data=posts_data)

@app.route("/edit/<int:id>",methods=['GET','POST'])
def edit(id):
    if request.method=="POST":
        title=request.form.get('title')
        slug=request.form.get('slug')
        content=request.form.get('content')
        date=request.form.get('date')

        data=posts(title=title,slug=slug,content=content,date=date)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("adminpanel"))
    else:
        posts_data = posts.query.filter_by(id=id).first()
        return render_template("blog.html",posts_data=posts_data)

@app.route("/delete/<int:id>")
def delete(id):
    post_data = posts.query.filter_by(id=id).first()
    if post_data:
            db.session.delete(post_data)
            db.session.commit()
    return redirect(url_for("adminpanel"))


if __name__ == "__main__":
    # Explicitly specify host and port (optional)
    app.run(debug=True)
