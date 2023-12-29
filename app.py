
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import qrcode
from urllib.parse import quote_plus
from datetime import datetime
from faker import Faker
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from datetime import timedelta
import os
from flask import session
import sqlite3
from flask import jsonify
from flask_restful import Resource, Api ## I Imported for Learning purpose only
from socketserver import ThreadingMixIn

class ThreadedServer(ThreadingMixIn, Flask):
    pass
#config
fake = Faker()
# app = Flask(__name__)
app = ThreadedServer(__name__) #TRY THIS
app.config['SECRET_KEY'] = 'mforce.com.my'
login_manager = LoginManager(app) # This one Is for restricting the route
login_manager.login_view = 'index'
login_manager.session_protection = 'strong'
app.permanent_session_lifetime = timedelta(seconds=240*60) # Session time
#config

# MongoDB connection API
# username = "juinnlau"
# password = "kl@123456"
# cluster_url = "cluster0.2j2j5zx.mongodb.net"
# database_name = "QR_CHECKER"
# escaped_username = quote_plus(username)
# escaped_password = quote_plus(password)
# uri = f"mongodb+srv://{escaped_username}:{escaped_password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"
# client = MongoClient(uri)
# MongoDB connection API

# SQLite database file
sqlite_db_file = 'qr_database.db'
# Function to establish SQLite connection
def get_db_connection():
    return sqlite3.connect(sqlite_db_file)

def authenticate_user(username, password):
    # SQLite query to check if the user exists and the password is correct
    query = f"SELECT * FROM admin WHERE username = ? AND password = ?"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    user_data = cursor.fetchone()
    conn.close()

    return user_data is not None


# UNIT TESTING
database_name = "qr_database.db"  
username_to_authenticate = "mforce_admin"  
password = "mforce_admin"  
if authenticate_user(username_to_authenticate,  password):
    print(f"User '{username_to_authenticate}' authenticated successfully.")
else:
    print(f"User '{username_to_authenticate}' not found.")

# try:
#     if client:
#         webhookurl = 'https://discord.com/api/webhooks/1169521777588838410/eR43wgZsZ89ezUQK1mkJ1VzVxX-lEcrKk9_IS4Yj6sXPoVYKDFzwjHBLvGPyh7W5i8PA'
#         response = requests.post(webhookurl, json={"content": "Ping from Python script. Connection Establish!"})
#         response.raise_for_status()  # Raise an exception for HTTP errors

#         print("Webhook ping successful")
# except requests.exceptions.RequestException as e:
#     print(f"Error: {e}")


# # Function to establish MongoDB connection
# def get_db_connection():
#     return client[database_name]

# def authenticate_user(username):
#     mydb = get_db_connection()
#     mycol = mydb["customers"]
    
#     user_data = mycol.find_one({"name": username})

#     if user_data:
#         return True
#     else:
#         return False

## Forms Input Validator !!! USEFUL
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

## This I also dunno define for what, but necessary
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    # Assuming your user_id is the username
    return User(user_id)

@app.route('/dashboard')
@login_required
def dashboard():


    return render_template('dashboard.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate_user(username, password):
            user_obj = User(username)
            login_user(user_obj)
            
            print(f'Login successful for user: {username}', 'success')
            session['username'] = username
            return redirect(url_for('dashboard'))
      
    return render_template('home.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.clear()  
    return redirect(url_for('index'))


# Helper function to check if the name already exists
def is_name_duplicate(name):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM customers WHERE name = ?', (name,))
        existing_name = cursor.fetchone()
        return existing_name is not None




@app.route('/register_user', methods=['POST'])
def user_registration():

    try:
        name = request.form.get('name')
        seat = request.form.get('seat')
        role = request.form.get('role')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = name.lower()
        role = role.lower()

        # Check if the name already exists in the database
        if is_name_duplicate(name):
            flash('Name already exists in the database. Please try a different name.')


        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    name TEXT,
                    registerdate TEXT,
                    role TEXT,
                    checkin1 TEXT,
                    checkin2 TEXT,
                    checkin3 TEXT,
                    seat TEXT
                )
            ''')
            user_data = {
                "name": name,
                "registerdate": current_time,
                "checkin1": "null",
                "checkin2": "null",
                "checkin3": "null",
                "seat": seat,
                "role": role
            }
            cursor.execute('''
                INSERT INTO customers (name, registerdate, checkin1, checkin2, checkin3, seat, role)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_data['name'], user_data['registerdate'], user_data['checkin1'], user_data['checkin2'], user_data['checkin3'], user_data['seat'], user_data['role']))

            connection.commit()
            print("User registered successfully")
            flash("User registered successfully")
            return redirect(url_for('dashboard'))

    except Exception:
        flash('An error occurred during registration. Please try again.')
        return redirect(url_for('dashboard'))
  

def authenticate_customer(name):
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT name FROM customers
                WHERE name = ?
            ''', (name,))
            result = cursor.fetchone()
            if result:
                print("User Found successfully")
                
                return True
            else:
                return False
    except Exception as e:
        print(e)
        return False
    
@app.route('/delete_qrcode/<qr_type>', methods=['POST'])
def delete_qrcode(qr_type):
    try:
        # Delete the QR code file
        os.remove(f'./static/{qr_type.upper()}.png')
    except Exception:
        pass

    # Redirect to qrcode_list route
    response = make_response(redirect(url_for('qrcode_list')))

    # Add cache-related headers to prevent caching of the redirected page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.route('/generate_qr', methods=['POST'])
def qrgenerator():
    action = request.form.get('action')


    if action in ['QRCODE-1', 'QRCODE-2' ,'QRCODE-3']:
        print(f"QR CODE GENERATED for {action.upper()}")
        login_url = url_for('qrlogin', action=action.lower(), _external=True)
        #please be NTOED _external=True is importatn because it use to To generate an absolute URL 
        img_qr = qrcode.make(login_url)
        print(login_url)
        img_qr.save(f'./static/{action.upper()}.png')
        return redirect(url_for('qrcode_list'))
    else:
        return "INVALID ACTION, PLEASE CONTACT MIS"


# Route to Redirectly based on which qrcode Scanned
@app.route('/scan_qr/<qr_type>', methods=['GET'])
def scan_qr(qr_type=None):  

    if qr_type:
        return redirect(url_for('qrlogin', qr_type=qr_type))
    else:
        return "Invalid QR type"
    

@app.route('/qrlogin/<action>', methods=['GET', 'POST'])
def qrlogin(action, qr_type=None):
    if request.method == 'POST':
        name = request.form.get('name')
        name = name.lower()
        if authenticate_customer(name):
            try:
                with get_db_connection() as connection:
                    cursor = connection.cursor()
                    cursor.execute('''
                        SELECT * FROM customers
                        WHERE name = ?
                    ''', (name,))
                    user_data = cursor.fetchone()

                    if user_data:
                        seat_number = user_data[1]  # 1 means second column @@@!!!! important!!
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Determine the column to update based on the action value
                        if action == 'qrcode-1':
                            column_to_update = 'checkin1'
                        elif action == 'qrcode-2':
                            column_to_update = 'checkin2'
                        elif action == 'qrcode-3':
                            column_to_update = 'checkin3'
                        else:
                            flash("Invalid action parameter in the URL.")
                            return redirect(url_for('qrlogin', qr_type=qr_type))  

                        cursor.execute(f'''
                            UPDATE customers
                            SET {column_to_update} = ?
                            WHERE name = ?
                        ''', (current_time, name))
                        connection.commit()

                        print(f"Welcome {name}! CHECKIN SUCCESSFUL")
                        flash(f"Welcome {name}! CHECKIN SUCCESSFUL")
                        flash(f"Your Seat is: {seat_number}")

                        try:
                            seat_image_src = url_for('static', filename=f'seat{seat_number}.gif')
                            print(seat_image_src)
                            return render_template('qrlogin.html', seat_image_src=seat_image_src)
                        except:
                            return "No Seats Assigned"

                    else:
                        flash("User data not found.")

            except Exception as e:
                print(e)
                return "Error accessing the database."

        else:
            return render_template('qrlogin.html', error='Invalid username!! You may not be registered. Please Contact Person In Charge')

    return render_template('qrlogin.html', error=None)


@app.route('/checklist', methods=['GET','POST'])
def checklist():  
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Noble Seasons QRCODE is checkin1 ( WHICH IS USE IN LUCKY DRAW)
        cursor.execute('''
            SELECT name FROM customers WHERE checkin1 IS NOT NULL AND checkin1 != ''
        ''')
        checkin1_result = cursor.fetchall()

        cursor.execute('''SELECT COUNT(name) FROM customers WHERE checkin1 IS NOT NULL AND checkin1 != '' ''')
        count1 = cursor.fetchone()[0]


        # checkin2 is HOTEL QRCODE
        cursor.execute('''
            SELECT name FROM customers WHERE checkin2 IS NOT NULL AND checkin2 != ''
        ''')
        checkin2_result = cursor.fetchall()
        cursor.execute('''SELECT COUNT(name) FROM customers WHERE checkin2 IS NOT NULL AND checkin2 != '' ''')
        count2 = cursor.fetchone()[0]


        # checkin3 is HOTEL QRCODE
        cursor.execute('''
            SELECT name FROM customers WHERE checkin3 IS NOT NULL AND checkin3 != ''
        ''')
        checkin3_result = cursor.fetchall()
        cursor.execute('''SELECT COUNT(name) FROM customers WHERE checkin3 IS NOT NULL AND checkin3 != '' ''')
        count3 = cursor.fetchone()[0]
    return render_template('dashboard.html', checkin1_attendees=checkin1_result, checkin2_attendees=checkin2_result, checkin3_attendees=checkin3_result, checkin_count1=count1,checkin_count2=count2,checkin_count3=count3)

@app.route('/get_checkin3_attendees')
def get_checkin3_attendees():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT name FROM customers WHERE checkin2 IS NOT NULL AND checkin2 != '' AND checkin1 IS NOT NULL AND checkin1 != ''
        ''')
        checkin3_attendees = cursor.fetchall()
    return jsonify(checkin3_attendees)


@app.route('/spinner', methods=['GET', 'POST'])
@login_required
def spinner():
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Noble Seasons QRCODE is checkin1 (WHICH IS USED IN LUCKY DRAW)
        cursor.execute('''
            SELECT name FROM customers WHERE checkin1 IS NOT NULL AND checkin1 != ''
        ''')
        checkin1_result = cursor.fetchall()
        
        # Join names with '\n' without enclosing them in single quotes
        spinner_list = '\n'.join([name_tuple[0] for name_tuple in checkin1_result])

        print(spinner_list)

    return render_template('spin.html', spinner_list=spinner_list)



@app.route('/table',methods=['POST','GET'])
@login_required
def table():
    return render_template('datatable.html')


@app.route('/qrcode',methods=['POST','GET'])
@login_required
def qrcode_list():
    return render_template('qrcode.html')

@app.route('/testing',methods=['POST','GET'])
def testing():
    return render_template('admin-dashboard.html')


## =======================
## TESTING FOR RESTFUL API
## =======================


def validate_api_key(api_key):
    valid_api_keys = ['mforce']
    return api_key in valid_api_keys

class LicenseResource(Resource):
    def post(self): # POST or GET defined here will determined which REQUESTS FOR THE ENDPOINT
        # Get the API key from the request headers
        api_key = request.headers.get('X-API-Key')

        if validate_api_key(api_key):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                'message': 'Hello, from JIA JUINN!',
                'time': current_time,
            }
            return jsonify(data)
        else:
            return jsonify({'error': 'Invalid API key'})
        
api = Api(app)
api.add_resource(LicenseResource, '/license', methods=['POST'])


@app.route('/api/data', methods=['POST'])
def data():
    # Ensure that the request contains a valid API key
    api_key = request.headers.get('X-API-Key')
    if not validate_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401

    # The rest of your data retrieval logic goes here
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Noble Seasons QRCODE is checkin1 (WHICH IS USED IN LUCKY DRAW)
        cursor.execute('''
            SELECT * FROM customers
        ''')

        Full_Table = cursor.fetchall()
        # Convert datetime objects to strings (assuming the third column is a datetime column)
        Full_Table = [(row[0], str(row[1]), str(row[2]), str(row[3]), row[4], str(row[5]), str(row[6])) for row in Full_Table]

        # Convert the list of tuples to a list of dictionaries
        data = [{'name': row[0], 'seat': row[1], 'role': row[2], 'registerdate': row[3], 'checkin1': row[4], 'checkin2': row[5], 'checkin3': row[6]} for row in Full_Table]

        # Convert the list of dictionaries to JSON using Flask's jsonify
        json_data = jsonify(data)
        print(json_data)

    return jsonify(data)


## =======================
## TESTING FOR RESTFUL API
## =======================

# @app.route('/post-database', methods=['GET'])
# def post_test():
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
#     with get_db_connection() as connection:
#         cursor = connection.cursor()
#         user_data = {
#             "name": "testing",
#             "registerdate": current_time,
#             "checkin1": "null",
#             "checkin2": "null",
#             "checkin3": "null",
#             "seat": 139,
#             "role": "testing_role"
#         }
#         cursor.execute('''
#             INSERT INTO customers (name, registerdate, checkin1, checkin2, checkin3, seat, role)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         ''', (user_data['name'], user_data['registerdate'], user_data['checkin1'], user_data['checkin2'], user_data['checkin3'], user_data['seat'], user_data['role']))

#         connection.commit()
#         print("User registered successfully")
#         flash("User registered successfully")
#         return redirect(url_for('dashboard'))




application = app

if __name__ == "__main__":
    app.run(host='127.0.0.1',debug=True, threaded=True)
