from flask import Flask, render_template, url_for, redirect, request, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from database import get_db_connection
import bcrypt
import logging
from analyze import predict_disease


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class SymptomAnalysisForm(FlaskForm):
    symptoms = TextAreaField('Symptoms', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserRegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ALoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SymptomForm(FlaskForm):
    symptoms = StringField('Enter Symptoms', validators=[DataRequired()])
    submit = SubmitField('Predict Disease')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            name = form.username.data
            password = form.password.data

            # storing data in database
            conn = get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM users WHERE username=%s", (name,))
            user = my_cursor.fetchone()
            conn.close()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('welcome'))
            else:
                flash("Login failed. Please check your credentials.")
                logging.debug("Login failed. Please check your credentials.")
                return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error: {e}")
            flash("An error occurred during login. Please try again.")
    else:
        logging.debug("Form validation failed")

    return render_template("user_login.html", form=form)

@app.route("/alogin", methods=["GET", "POST"])
def alogin():
    form = ALoginForm()
    if form.validate_on_submit():
        try:
            name = form.username.data
            password = form.password.data
            admi = 1

            # Debugging: Print form data
            print(f"Username: {name}, Password: {password}")

            # Query the database for admin user
            conn = get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM users WHERE username=%s AND is_admin=%s", (name, admi))
            user = my_cursor.fetchone()
            conn.close()

            # Debugging: Print user data
            print(f"User from DB: {user}")

            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                # Set session variables
                session['id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = True  # Explicitly set admin status

                # Debugging: Print session data
                print(f"Session after login: {session}")

                # Redirect to adminboard
                return redirect(url_for('adminboard'))
            else:
                flash("Login failed. Please check your credentials.")
                logging.debug("Login failed. Please check your credentials.")
                return redirect(url_for('alogin'))
        except Exception as e:
            logging.error(f"Error: {e}")
            flash("An error occurred during login. Please try again.")
    else:
        logging.debug("Form validation failed")

    return render_template("admin_login.html", form=form)

@app.route("/user_register", methods=['GET', 'POST'])
def user_register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        try:
            name = form.username.data
            email = form.email.data
            password = form.password.data
            user = 0
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # storing data in database
            conn = get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, user))
            conn.commit()
            conn.close()
            flash("User registered successfully")
            logging.debug("User registered successfully")
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error registering user: {e}")
            flash("An error occurred during registration. Please try again.")
    else:
        logging.debug("Form validation failed")

    return render_template("user_register.html", form=form)

@app.route("/adminboard")
def adminboard():
    # Check if the user is an admin
    if 'is_admin' not in session or not session['is_admin']:
        flash("You do not have permission to access this page.")
        return redirect(url_for('alogin'))
    return render_template("adminboard.html")

@app.route('/userboard', methods=['GET', 'POST'])
def userboard():
    form = SymptomForm()
    if form.validate_on_submit():
        symptoms = form.symptoms.data
        try:
            # Predict the disease
            predicted_disease = predict_disease(symptoms)
            predicted_disease = predicted_disease.strip()  # Remove leading/trailing whitespace
            print("Predicted Disease (After Stripping):", predicted_disease)  # Debugging where to add this

            # Fetch precautions and description from the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Query to fetch precautions from the `diseases` table
            cursor.execute("SELECT prec1, prec2, prec3, prec4 FROM diseases WHERE dname = %s", (predicted_disease,))
            precautions = cursor.fetchone()

            # Query to fetch description from the `disease_descriptions` table
            cursor.execute("SELECT description FROM disease_descriptions WHERE dname = %s", (predicted_disease,))
            description = cursor.fetchone()

            conn.close()
    
            # Prepare data to pass to the template
            disease_data = {
                'name': predicted_disease,
                'precautions': precautions,
                'description': description[0] if description else "No description available."
            }

            # Render the template with the disease data
            return render_template('userboard.html', form=form, disease_data=disease_data)

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('userboard'))

    return render_template('userboard.html', form=form)

@app.route("/userlist")
def userlist():
    # Check if the user is an admin
    if 'is_admin' not in session or not session['is_admin']:
        flash("You do not have permission to access this page.")
        return redirect(url_for('alogin'))

    try:
        # Fetch all users from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    
        conn.close()

        # Render the userlist template with the users data
        return render_template("userlist.html", users=users)
    except Exception as e:
        logging.error(f"Error fetching user list: {e}")
        flash("An error occurred while fetching the user list.")
        return redirect(url_for('adminboard'))

@app.route("/admin/diseases")
def admin_diseases():
    # Check if the user is an admin
    if 'is_admin' not in session or not session['is_admin']:
        flash("You do not have permission to access this page.")
        return redirect(url_for('alogin'))

    try:
        # Fetch all diseases and their details from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch data from the `diseases` and `disease_descriptions` tables
        cursor.execute("""
            SELECT d.dname, d.prec1, d.prec2, d.prec3, d.prec4, dd.description
            FROM diseases d
            LEFT JOIN disease_descriptions dd ON d.dname = dd.dname
        """)
        diseases = cursor.fetchall()
        conn.close()

        # Render the admin diseases template
        return render_template("admin_diseases.html", diseases=diseases)
    except Exception as e:
        logging.error(f"Error fetching disease details: {e}")
        flash("An error occurred while fetching disease details.")
        return redirect(url_for('adminboard'))

@app.route("/welcome")
def welcome():
    # Check if the user is logged in
    if 'username' not in session or 'id' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))

    try:
        # Fetch the user's email from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (session['id'],))
        user = cursor.fetchone()
        conn.close()

        if user:
            email = user[0]
        else:
            flash("User not found.")
            return redirect(url_for('login'))

        # Render the welcome template
        return render_template("welcome.html", username=session['username'], email=email)
    except Exception as e:
        logging.error(f"Error fetching user details: {e}")
        flash("An error occurred while fetching user details.")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Remove the user ID from the session
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Add this import at the top
from analyze1 import analyze_symptoms

# Add this new route (place it with your other routes)
@app.route('/advanced-analysis', methods=['GET', 'POST'])
def advanced_analysis():
    form = SymptomForm()
    
    if form.validate_on_submit():
        symptoms = form.symptoms.data
        analysis_result = analyze_symptoms(symptoms)
        
        if analysis_result['status'] == 'error':
            flash(f'Analysis error: {analysis_result["message"]}', 'danger')
            return redirect(url_for('advanced_analysis'))
            
        return render_template(
            'advanced_analysis.html',
            symptoms=symptoms,
            analysis_result=analysis_result,
            form=form
        )
    
    return render_template('advanced_analysis.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)