import sqlite3, os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin 
from admin.admin import admin

# Configuration
DATABASE = '/tmp/flsite.db'
DEBUG = True 
SECRET_KEY = "bbdbsuyfbdt32t411!@3218"
MAX_CONTENT_LENGTH = 1024 * 1024

# Create app
app = Flask(__name__)
# Push configuration in App
app.config.from_object(__name__)
# Connecto to DB
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

# Register Blueprint
app.register_blueprint(admin, url_prefix='/admin') #/domaine/<url_prefix>/<URL-bleuprint>

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Sign In is required"
login_manager.login_message_category = "success"

# Login
@login_manager.user_loader
def laod_user(user_id):
    return UserLogin().fromDB(user_id, dbase)

# Connect to DB
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Create DB
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

# Get DB
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    """ Встановлення з'єднання з БД перед виконуванням запиту """
    global dbase
    db = get_db()
    dbase = FDataBase(db)

# Close connect with DB
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route("/home")
@app.route("/")
def index():
    return render_template('index.html', posts=dbase.getPostsAnonce())

# Add post
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def addPost():
    if request.method == 'POST':
        if len(request.form['title']) > 4 and len(request.form['text']) > 10:
            user = current_user.getName()
            res = dbase.addPost(request.form['title'], request.form['text'], request.form['url'], author=user)
            if not res:
                flash('An error while adding the post', 'error')
            else:
                flash('The post added successfully', 'success')
                return redirect(f"/post/{request.form['url']}")
        else:
            flash('An error while adding the post!', 'error')

    return render_template('add_post.html', title='Add post')

@app.route("/userava")
@login_required   
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
    
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

# Upload
@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Uploading image error", "error")
                flash("Uploading image is successfully!", 'success')
            except FileNotFoundError as e:
                flash("Uploading image error", "error")
        else:
            flash("Uploading image error", "error")

    return redirect(url_for('profile'))

@app.route("/uploadata", methods=['GET', 'POST'])
@login_required
def uploadData():
    name = current_user.getName()
    email = current_user.getEmail()
    psw = current_user.getPassword()
    if request.method == "POST":
        if request.form['name'] != name or request.form['email'] != email or request.form['psw'] != psw and request.form['psw'].strip() != '':
            try:
                if request.form['psw'] == request.form['psw2']:
                    hash = generate_password_hash(request.form['psw'])
                    res = dbase.updateUserData(request.form['name'], request.form['email'], hash, current_user.get_id())
                    if not res:
                        flash("Uploading data error", "error")
                    flash("Uploading data is successfully!", 'success')
                else:
                    flash('Password is not correct', 'error')
            except FileNotFoundError as e:
                flash("Uploading error", "error")
        else:
            res = dbase.updateUserData(name, email, psw, current_user.get_id())
            flash('The information has not been changed', 'error')
            return redirect(url_for('profile'))
        
    return redirect(url_for('profile'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for('login'))
        
        flash('Login or password is not correct', 'error')

    return render_template("login.html")

# User's profile
@app.route('/profile')
@login_required
def profile():
    user = dbase.getUser(current_user.get_id())
    return render_template("profile.html", u=user)

@app.route('/profile/<path:email>/delete')
@login_required
def deleteProfile(email):
    try:
        dbase.deleteUser(email=email)
        logout_user()
        redirect('/register')
    except:
        print("Maybe Error")

    return redirect('/register')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are logged out", "success")
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 2 and len(request.form['email']) > 4 and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Registration was successful", "success")
                return redirect(url_for('login'))
            else:
                flash("Registration error", "error")
        else:
            flash("The fields are not filled in correctly", "error")
    
    return render_template('register2.html')

# Get All Posts
@app.route("/post/<alias>")
@login_required
@admin.route("/pubs/<alias>")
def showPost(alias):
    title, post, author = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', title=title, post=post, author=author)


if __name__ == "__main__":
    app.run(debug=True)