from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import email_model
from flask import flash
from flask_app import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Emails:

    DB = 'login_and_registration'
    tables = 'emails'

    def __init__(self, data) -> None:
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_all(cls):
        query = f'SELECT * FROM {cls.tables};'
        results = connectToMySQL(cls.DB).query_db(query)
        users = []
        if results:
            for user in results:
                users.append( cls(user) )
        return users
    
    @classmethod
    def get_one(cls, data):
        query = f'SELECT * FROM {cls.tables} WHERE id = %(id)s;'
        results = connectToMySQL(cls.DB).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def save(cls, form):
        query = f'''INSERT INTO {cls.tables} (first_name, last_name, email, password) 
                VALUES (  %(first_name)s, %(last_name)s, %(email)s, %(password)s  );'''
        
        pw_hash = bcrypt.generate_password_hash(form['password']).decode('utf-8')
        data = {
            'first_name' : form['first_name'],
            'last_name' : form['last_name'],
            'email' : form['email'],
            'password' : pw_hash
        }

        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def update(cls, data):
        query = f'''UPDATE {cls.tables} 
                SET first_name = %(first_name), last_name = %(last_name)s, email = %(email)s, password = %(password)s
                WHERE id = %(id)s;'''
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete(cls, id):
        query = f'DELETE FROM {cls.tables} WHERE id = %(id)s;'
        data = {'id' : id}
        return connectToMySQL(cls.DB).query_db(query, data)
    

    @classmethod
    def get_one_email(cls, data):
        query = f'SELECT * FROM {cls.tables} WHERE email = %(email)s;'
        results = connectToMySQL(cls.DB).query_db(query, data)
        return cls(results[0])

    #working on, wait on checking
    @classmethod
    def password_check(cls, data):
        print('get user info?')
        user = cls.get_one_email(data)
        print(user.id)
        # check if user password matches
        if bcrypt.check_password_hash(user.password, data['password']):
            print('password match')
            return True
        print('password does not match')
        return False
    
    @classmethod
    def registration_check(cls, data):
        is_valid = True
        if len(data['first_name']) < 3:
            flash('First name must be at least 3 character long', 'registration')
            is_valid = False
        if any(char.isdigit() for char in data['first_name']):
            flash('First name cannot contain numbers', 'registration')
            is_valid = False
        if any(char.isdigit() for char in data['last_name']):
            flash('Last name cannot contain numbers', 'registration')
            is_valid = False
        if len(data['last_name']) < 3:
            flash('Last name must be at least 3 character long', 'registration')
            is_valid = False
        if not cls.validate_email(data):
            flash('Invalid email address!', 'registration')
            is_valid = False
        if len(data['password']) < 6:
            flash('Password must be between 6 and 16 characters long', 'registration')
            is_valid = False
        if len(data['password']) > 16:
            flash('Password must be between 6 and 16 characters long', 'registration')
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash('Password does not match', 'registration')
            is_valid = False
        # password check to have 1 number and 1 uppercase letter
        upper = False
        digit = False
        for i in data['password']:
            if i.isupper():
                upper = True
            elif i.isdigit():
                digit = True
        if not upper:
            flash('Password should include one upper-case letter', 'registration')
            is_valid = False
        if not digit:
            flash('Password should include one number', 'registration')
            is_valid = False
        return is_valid

    @classmethod
    def email_DB_check(cls, email):
        query = f'SELECT * FROM {cls.tables} WHERE email = %(email)s;'
        results = connectToMySQL(cls.DB).query_db(query, email)
        if results:
            return True
        return False
        # check if we return a match from db
        if len(results)< 1:
            # if no match, result len is < 1, return false
            return False
        # else we return the cls(returned user info)
        return cls(result[0])

    @staticmethod
    def validate_email( email ):
        is_valid = True
        if not EMAIL_REGEX.match(email['email']):
            is_valid = False
        return is_valid