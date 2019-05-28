from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.route('/blog', methods = ['GET'])
def blog():
    user_get = request.args.get('user')
    blog_id = request.args.get('id')
    listing = Blog.query.all()
    if blog_id != None:
        post = Blog.query.get(blog_id)
        return render_template("blog.html", posting = post, id=blog_id)
    if user_get != None:
        listing = Blog.query.filter_by(owner_id = user_get).all()
        return render_template('blog.html', id=blog_id, user=user_get, user_listing = listing)
    return render_template('blog.html', listing = listing, id=blog_id)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    title_error = ""
    body_error = ''
    error = False

    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        blog_body = request.form['blog-body']
        blog_title = request.form['blog-title']
        if blog_body == "":
            body_error = 'Please fill in body'
            error = True
        if blog_title == '':
            title_error = 'Please fill in title'
            error = True
        if error:
            return render_template('newpost.html', body_error = body_error, title_error = title_error)
        else:
            blog = Blog(blog_title, blog_body, logged_in_user())
            db.session.add(blog)
            db.session.commit()
            blog_id = blog.id
            post = Blog.query.get(blog_id)
            return render_template("blog.html", posting = post, id=blog_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        error = False
        password_error =''
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                return redirect("/blog")
            else:
                error = True
                password_error = "wrong password"
                return redirect('/login')
        else:
            error = True
            username_error = "User doesn't exist"
            return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username == "" or password == "":
            username_error = 'Please fill in body'
            error = True
        if not is_valid(username) or not is_valid(password):
            error = True
            username_error = "BAD USERNAME OR PASSWORD"
        if verify != password:
            error = True
            verify_error = "BAD VERIFY"
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            error = True
            username_error='already exists'
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect('/blog')
    return render_template('signup.html')

def is_valid(string):
    space_index = string.find(' ')
    space_present = space_index >= 0
    if space_present:
            return False
    else:
        length = len(string)
        correct_length = length >=3 and length <= 20
        return correct_length    

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')

@app.route("/")
def index():
    user_list = User.query.all()
    return render_template('index.html', list=user_list)

def logged_in_user():
    owner = User.query.filter_by(username=session['user']).first()
    return owner


endpoints_without_login = ['login', 'signup', 'blog', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")




app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()   