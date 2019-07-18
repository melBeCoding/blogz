from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Melo1994@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route("/")
def index():
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
    title = request.args['title']
    body = request.args['body']
    return render_template('blogpost.html', title=title, body=body)

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
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return render_template('blogpost.html', title=title, body=body)
            #return render_template('posted.html', title="Content posted")
        else:
            return render_template('post.html', title="Content not posted", error1 = title_error, error2 = body_error)
    return render_template('notposted.html', title="Content not posted")

if __name__ == "__main__":
    app.run()