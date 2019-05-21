from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods = ['GET'])
def blog():
    blog_id = request.args.get('id')
    listing = Blog.query.all()
    if blog_id != None:
        post = Blog.query.get(blog_id)
        return render_template("blog.html", posting = post, id=blog_id)
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
            blog = Blog(blog_title, blog_body)
            db.session.add(blog)
            db.session.commit()
            blog_id = blog.id
            post = Blog.query.get(blog_id)
            return render_template("blog.html", posting = post, id=blog_id)

if __name__ == '__main__':
    app.run()   