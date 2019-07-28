from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345678@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'key'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'home', 'about']
    if 'username' not in session and request.endpoint not in allowed_routes:
        return redirect('/login')


@app.route("/")
def index():
    allposts = Blog.query.all()
    return render_template('home.html',title="Blog posts", posts=allposts)

@app.route("/users")
def users():
    allusers = User.query.all()
    return render_template('users.html',title="All users", users=allusers)

@app.route("/home")
def home():
    allposts = Blog.query.all()
    return render_template('home.html',title="Blog posts", posts=allposts)

@app.route("/post")
def blog():
    return render_template('post.html',title="Create new post")

@app.route("/about")
def about():
    return render_template('about.html',title="About page")

@app.route("/blogpost", methods=['GET'])
def blogpost():
    tid = request.args.get('id')
    post = Blog.query.filter_by(id=tid).first()
    #title = request.args.get('title')
    #body = request.args.get('body')
    return render_template('blogpost.html', title=post.title, body=post.body)

@app.route("/bloguser", methods=['GET'])
def bloguser():
    tid = request.args.get('id')
    owner = User.query.filter_by(id=tid).first()
    posts = owner.blogs
    #title = request.args.get('title')
    #body = request.args.get('body')
    return render_template('bloguser.html', title=("Posts by " + owner.username), posts=posts)

@app.route("/posted", methods=['POST', 'GET'])
def posted():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error = ""
        body_error = ""
        if not (title):
            title_error="Title is required!"
        if not (body):
            body_error="Body is required!"

        if not title_error and not body_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/blogpost?id=" + str(new_post.id))
            #return render_template('blogpost.html', id=str(new_post.id), title=title, body=body)
            #return render_template('posted.html', title="Content posted")
        else:
            return render_template('post.html', title="Content not posted", error1 = title_error, error2 = body_error, stitle=title, sbody=body)
    return render_template('notposted.html', title="Content not posted")



@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        pass1 = request.form['pass1']

        name_error = ""
        pass1_error = ""

        existing_user = User.query.filter_by(username=name).first()
        if not existing_user:
            name_error = "Username not found!"
        else:
            if not existing_user.password == pass1:
                pass1_error = "Password incorrect!"

        if not (name):
            name_error = "Name can't be empty!"

        if not (pass1):
            pass1_error = "Password can't be empty!"

        if not name_error and not pass1_error and existing_user:
            session['username'] = existing_user.username
            return redirect("/post")
        else:
            return render_template("login.html", name_error = name_error, pass1_error = pass1_error, name = name, pass1 = '')
    else:
        return render_template("login.html", name_error = "", pass1_error = "", name = "", pass1 = '')

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        email = request.form['email']

        name_error = ""
        pass1_error = ""
        pass2_error = ""
        email_error = ""

        existing_user = User.query.filter_by(username=name).first()
        if existing_user:
            name_error = "Account name taken!"

        if not (name):
            name_error = "Name can't be empty!"

        if not (pass1):
            pass1_error = "Password can't be empty!"

        if not (pass2):
            pass2_error = "Password can't be empty!"
        elif (pass2 != pass1):
            pass2_error = "Password does not match!"

        if not (email):
            email_error = "Email can't be empty!"
        


        if not name_error and not pass1_error and not pass2_error and not email_error and not existing_user:
            new_user = User(name, pass1)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = name
            return redirect("/post")
        else:
            return render_template("register.html", name_error = name_error, pass1_error = pass1_error, pass2_error = pass2_error, email_error = email_error,
         name = name, pass1 = '', pass2 = '', email = email)
    else:
        return render_template("register.html", name_error = "", pass1_error = "", pass2_error = "", email_error = "",
     name = "", pass1 = '', pass2 = '', email = "")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/home')








if (__name__ == '__main__'):
    app.run(port=(1234))
