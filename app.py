from flask import Flask, render_template, request, redirect, session
import mysql.connector
import pymysql
import fitz
import re
app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'


db_host = 'localhost'
db_user = 'nresult'
db_password = '2025'
db_name = 'result2'

app = Flask(__name__)
app.secret_key = "xyz"

def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="aron21",
        password="2025",
        database="register2"
    )

def email_exists(email):
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM reg1 WHERE email = %s", (email,))
    user = mycursor.fetchone()

    mycursor.close()
    mydb.close()
    return user is not None

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        mydb = get_database_connection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM reg1 WHERE email = %s AND pass = %s", (email, password))
        user = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        if user:
            session["useremail"] = user[1]
            return redirect('/home')
        else:
            return "Login Failed"

    return render_template("login.html")

@app.route("/Inlogin", methods=["POST", "GET"])
def insert_institute():
    if request.method == "POST":
        Iname = request.form['Iname']
        password = request.form['password']

        mydb = get_database_connection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM reg4 WHERE Iname = %s AND pass = %s", (Iname, password))
        user = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        if user:
            session["Iname"] = user[1]
            return redirect('/home')
        else:
            return "Login Failed"

    return render_template("ins_login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form['user']
        email = request.form['email']
        password = request.form['password']
        rpassword = request.form['cpassword']

        if password != rpassword:
            return render_template("signup.html", error="Passwords do not match. Please re-enter your passwords.")

        mydb = get_database_connection()
        mycursor = mydb.cursor()

        if email_exists(email):
            mycursor.close()
            mydb.close()
            return render_template("signup.html", error="Email already exists. Please use a different email.")

        try:
            mycursor.execute("INSERT INTO reg1 (user, email, pass,rpass) VALUES (%s, %s, %s,%s)", (username, email, password,rpassword))
            mydb.commit()
            mycursor.close()
            mydb.close()
            return redirect('/')
        except mysql.connector.IntegrityError as e:
            mycursor.close()
            mydb.close()
            return render_template("signup.html", error="Email already exists. Please use a different email.")

    return render_template("signup.html")

@app.route("/home")
def dashboard():
    if "useremail" in session:
        return render_template("home.html", useremail=session["useremail"], user_type="student")
    elif "Iname" in session:
        return render_template("home.html", Iname=session["Iname"], user_type="institute")
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session.pop("useremail", None)
    session.pop("Iname", None)
    return redirect("/")




def get_db_connection():
    return pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)
@app.route("/uplode")
def uplode():
    if "useremail" in session:
        user_type = "student"
        user_identity = session["useremail"]
    elif "Iname" in session:
        user_type = "institute"
        user_identity = session["Iname"]
    else:
        return redirect("/")

    return render_template("upresult.html")
@app.route('/submit', methods=['POST'])
def submit():
    if "useremail" in session:
        user_type = "student"
        user_identity = session["useremail"]
    elif "Iname" in session:
        user_type = "institute"
        user_identity = session["Iname"]
    else:
        return redirect("/")
    pdf_file = request.files['pdfFile']
    if pdf_file.filename == '':
        return "No PDF file selected"

    if not pdf_file.filename.lower().endswith('.pdf'):
        return "Only PDF files are supported"

    pdf_text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()



    #roll_gpa_list = re.findall(r'(\d{6}) \((\d+\.\d+)\)', pdf_text)
    roll_gpa_list = re.findall(r'(\d{6})\s+\(\s*(\d+\.\d+)\s*\)', pdf_text)


    connection = get_db_connection()
    cursor = connection.cursor()

    create_table_query = """CREATE TABLE IF NOT EXISTS student_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        roll_number VARCHAR(20) NOT NULL,
        gpa FLOAT NOT NULL)
    """
    cursor.execute(create_table_query)

    for roll_number, gpa in roll_gpa_list:
        insert_query = "INSERT INTO student_data (roll_number, gpa) VALUES (%s, %s)"
        cursor.execute(insert_query, (roll_number, gpa))
        connection.commit()

    cursor.close()
    connection.close()

    return render_template('confrimation.html')


@app.route('/confirmation')
def confirmation():
    return render_template('confrimation.html')


@app.route('/get_result')
def get_result():
    if "useremail" in session:
        user_type = "student"
        user_identity = session["useremail"]
    elif "Iname" in session:
        user_type = "institute"
        user_identity = session["Iname"]
    else:
        return redirect("/")
    return render_template('get_result.html')


@app.route('/result', methods=['POST'])
def result():
    if "useremail" in session:
        user_type = "student"
        user_identity = session["useremail"]
    elif "Iname" in session:
        user_type = "institute"
        user_identity = session["Iname"]
    else:
        return redirect("/")
    roll_number = request.form['roll']

    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM student_data WHERE roll_number = %s"
    cursor.execute(query, (roll_number,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('result.html', result=result)




if __name__ == '__main__':
    app.run(debug=True)
