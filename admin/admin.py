from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
import sqlite3

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Functions
def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)


# DB
db = None
@admin.before_request
def before_request():
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

# Home
@admin.route('/')
def index():
    if not isLogged:
        return redirect(url_for('.login'))
    
    return render_template('admin/index.html', title="Menu", isLogged=isLogged())

# Login
@admin.route('/login', methods=['GET', 'POST'])
def login():
    if isLogged():
        return redirect(url_for('.index')) # '.' - is important


    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['psw'] == 'admin':
            login_admin()
            session.modified = True
            return redirect(url_for('.index')) # admin.index
        else:
            flash("Login or password is not correct", "error")

    return render_template("admin/login.html")

# Logout 
@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    flash("You are logged out", "success")
    logout_admin()
    session.modified = True

    return redirect(url_for('.login'))

@admin.route("/pubs")
def pubs():
    if not isLogged():
        return redirect(url_for('.login'))
    
    posts = []
    if db:
        try:
            post = db.cursor()
            post.execute(f"SELECT title, text, url, author FROM posts")
            posts = post.fetchall()
        except sqlite3.Error as e:
            print("Error with connect to DB" + str(e))

    return render_template('admin/pubs.html', title='All posts', list=posts, isLogged=isLogged())

@admin.route("/users")
def users():
    if not isLogged():
        return redirect(url_for('.login'))
    
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Error with connect to DB" + str(e))

    return render_template('admin/users.html', title='All users', list=list, isLogged=isLogged())


# Delete Post
@admin.route('/pubs/<path:url>/delete')
def post_delete(url):
    if not isLogged():
        return redirect(url_for('.login'))
    
    if db:
        try:
            post = db.cursor()
            post.execute(f"DELETE FROM posts WHERE url = ?", (url,))
            db.commit()
        except sqlite3.Error as e:
            print("Error with connect to DB " + str(e))

    return redirect("/admin/pubs")
