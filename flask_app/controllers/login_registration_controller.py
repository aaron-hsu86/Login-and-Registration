from flask_app import app, bcrypt
from flask import render_template, redirect, request, session, flash
from flask_app.models import email_model
app.secret_key = "secret-key"

@app.route('/')
def main_page():
    return render_template('login-registration.html')

# success page
@app.route('/dashboard/<int:id>')
def dashboard(id):
    if 'id' not in session:
        flash('Please log in page', 'user')
        return redirect('/')
    user = email_model.Emails.get_one({'id':id})
    print(user)
    return render_template('dashboard.html', user = user)

@app.route('/register', methods=['post'])
def registration():
    # check if info in form is valid
    if not email_model.Emails.registration_check(request.form):
        return redirect('/')
    # check if email is in database
    if email_model.Emails.email_DB_check(request.form):
        flash('Email is already registered', 'registration')
        return redirect('/')
    id = email_model.Emails.save(request.form)
    session['id'] = id
    return redirect(f'/dashboard/{id}')

@app.route('/login', methods=['post'])
def login_check():
    if not email_model.Emails.validate_email(request.form):
        flash('Invalid email address, check your spelling', 'login')
        return redirect('/')
    elif email_model.Emails.email_DB_check(request.form):
        # email is in database
        if email_model.Emails.password_check(request.form):
            # if password check passed
            id = email_model.Emails.get_one_email(request.form).id
        else: # password did not match
            flash('Invalid email/password combination', 'login')
            return redirect('/')
    else:
        flash('Invalid email/password combination', 'login')
        return redirect('/')
    
    session['id'] = id
    return redirect(f'/dashboard/{id}')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')