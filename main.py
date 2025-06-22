#imports
from flask import render_template,url_for,flash,redirect,request,send_file
from forms import RegistrationForm,LoginForm
from models import app,db,User
from flask_login import LoginManager,login_user, login_required, logout_user, current_user
from downloader import ddl,downloader
with app.app_context():
	db.create_all() 


#vars
ddl_response=None



# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects to login page if user is not logged in

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


#home route
@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

#register
@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		# Check if user already exists
		existing_user = User.query.filter_by(email=form.email.data).first()
		if existing_user:
			flash("Email is already registered. Please log in or use a different email.", "danger")
			return redirect(url_for("register"))  # Redirect back to registration page
		
		# Create and save new user
		new_user = User(email=form.email.data, password=form.password.data)
		db.session.add(new_user)
		db.session.commit()
		flash("Registration successful! You can now log in.", "success")
		return redirect(url_for("login"))
	
	return render_template("register.html", title="Register", form=form)

#login
@app.route("/login", methods=["GET", "POST"])
def login():

	if current_user.is_authenticated:  # Check if user is already logged in
		flash("You are already logged in.", "info")
		return redirect(url_for("home"))  # Redirect to home instead of showing login page

	form = LoginForm()
	next_page = request.args.get("next")  # Get the 'next' parameter from the URL

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and user.check_password(form.password.data):
			login_user(user)
			flash("Login successful!", "success")
			return redirect(next_page) if next_page else redirect(url_for("home"))  # Redirect to next or home
		else:
			flash("Invalid email or password", "danger")

	return render_template("login.html", form=form)

#BUResult
@app.route("/BUResults")
@login_required  # Ensures only logged-in users can access this route
def BUResults():
	global ddl_response
	ddl_response=ddl.func()
	return render_template("BUjhansi.html",resultType=ddl_response[1],courses=ddl_response[0])

@app.route("/BUResultsubmit", methods=["POST"])
def submit():
    roll_from = request.form.get("roll_from")
    roll_to = request.form.get("roll_to")
    result_type_label = request.form.get("result_type")
    course_label = request.form.get("course")

    # Convert label to ID
    course_id = ddl_response[0].get(course_label)
    result_id = ddl_response[1].get(result_type_label)

    pdf_stream=downloader.func(roll_from,roll_to,course_id,course_label,result_id)
    return send_file(
        pdf_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{course_label}_merged_results.pdf"
    )




#logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash("You have been logged out.", "info")
	return redirect(url_for("home"))


if __name__=="__main__":
	with app.app_context():
		db.create_all()
	app.run()


