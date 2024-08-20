from flask import Flask, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient
from processing import *

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'your_secret_key'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['ielts_db']
users_collection = db['users']

@app.route("/", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Incorrect username or password', 'error')
    return render_template('login.html', title="Login")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        if users_collection.find_one({"username": username}):
            flash('Username already exists', 'error')
        else:
            users_collection.insert_one({"username": username, "password": password})
            flash('Successfully Registered!', 'success')
            return redirect(url_for('login_page'))
    return render_template('register.html', title="Register")

@app.route("/home", methods=["GET", "POST"])
def home_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    errors = ""
    text = None
    english = None
    print('rendering home page')
    if request.method == "POST":
        print('post request hit')
        text = request.form.get("text")
        english = request.form.get("language")

        if not text or not english:
            errors = "Text and language selection are required."
            return render_template('home.html', title="IELTS Reviewer", errors=errors)

        text_split = text.split('\r\n')
        results = main(text_split, english)
        print('results obtained is ', results)
        return render_template('result.html', title="IELTS Reviewer", results=results)
    
    return render_template('home.html', title="IELTS Reviewer", errors=errors)




@app.route("/rules")
def rules_page():
    return render_template('rules.html', title='Rules')

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run()
