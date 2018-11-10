from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import pymysql
import pymysql.cursors
from datetime import datetime 

app = Flask(__name__)

# Config pyMySQL
db = pymysql.connect(host='localhost',user='root', password='',db='newtry',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def about1():
    return render_template('dashboard.html')




# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    phone = StringField('Phone', [validators.Length(min=10 , max=12)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        phone = form.phone.data
        password = sha256_crypt.encrypt(form.password.data)

        # Create cursor
        cursor=db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", username)
        row=cursor.fetchone()
        if row:
            return redirect(url_for('register'))

        else:

            # Execute query
            cursor.execute("INSERT INTO users(name, email, username, phone, password) VALUES(%s, %s, %s, %s, %s)", (name, email, username, phone, password))

            # Commit to DB
            cursor.connection.commit()

            # Close connection
            cursor.close()

            flash('You are now registered and can log in', 'success')

            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET' , 'POST'])
def profile():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cresha WHERE username = %s", session['username'])
    data = cursor.fetchall()
    cursor.connection.commit()
    return render_template('profile.html' , data=data)


        

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cursor = db.cursor()

        # Get user by username
        result = cursor.execute("SELECT * FROM users WHERE username = %s", username)

        if result >0:
            # Get stored hash
            data = cursor.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['email'] = data['email'] 
                session['phone'] = data['phone']

                flash('You are now logged in', 'success')
                return redirect(url_for('profile'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/cabshare', methods=['GET' , 'POST'])
def search():
    cursor=db.cursor()
    if request.method == 'POST':    
        journeydate = request.form['date']
        time = request.form['time']
        leavingfrom = request.form['leavingfrom']
        goingto = request.form['goingto']
        emptyseats = request.form['numberofseats']
        cursor.execute('INSERT INTO cresha(journeydate, time, leavingfrom, goingto, emptyseats, username, phone) VALUES (%s, %s, %s, %s, %s, %s ,%s)', (journeydate, time, leavingfrom, goingto, emptyseats, session['username'], session['phone']))
        cursor.connection.commit()	
        cursor.close()
    return render_template('dashboard.html')

@app.route('/cabsearch' , methods=['GET' , 'POST'])
def search2():
    cursor=db.cursor()
    if request.method == 'POST':
        journeydate1 = request.form['date']
        leavingfrom1 = request.form['leavingfrom']
        goingto1 = request.form['goingto']

        result = cursor.execute("SELECT * FROM cresha WHERE (leavingfrom,goingto) = (%s,%s)", (leavingfrom1,goingto1))
        data = cursor.fetchall()
        cursor.connection.commit()
        return render_template('profile1.html' , data=data)
    return render_template('cabsearchs.html')
        
     




# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
