
import mysql.connector
from flask import Flask, render_template, request, redirect
import pickle
import numpy as np

app = Flask(__name__)

# Loading the trained LinearRegression from the pickle file
with open('LinearRegression.pkl', 'rb') as file:
    model = pickle.load(file)

mdb = mysql.connector.connect(
    host="127.0.0.1",
    user="pma",
    password="********",#replace the asterisks with your database password 
    database="teaFarmers"
)

# Get all farmers from farmers database


def get_farmers():
    cursor = mdb.cursor()
    sql = "SELECT * FROM farmers"
    cursor.execute(sql)
    farmers_data = cursor.fetchall()
    cursor.close()
    return farmers_data


def get_farmer():
    cursor = mdb.cursor()
    sql = "SELECT * FROM predicted_fertilizers"
    cursor.execute(sql)
    farmer_data = cursor.fetchall()
    cursor.close()
    return farmer_data


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the form data
        bushes = float(request.form.get('bushes'))
        kilos = float(request.form.get('kilos'))
        size = float(request.form.get('size'))

        # Create an array of input features
        input_features = [[bushes, kilos, size]]

        # Perform prediction
        prediction = model.predict(input_features)

        return render_template('index.html', prediction=prediction, farmers=get_farmers(), fertilizer=get_farmer())

    return render_template('index.html', farmers=get_farmers(), fertilizer=get_farmer())


@app.route("/register", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get the form data
        id_number = request.form.get("id_number")
        name = request.form.get("name")
        bushes = request.form.get("bushes")
        kilos = request.form.get("kilos")
        size = request.form.get("size")

        if not (id_number and name and bushes and kilos and size):
            # Handle missing form data error
            return "Missing form data. Please fill in all fields."

        try:
            # Convert numeric inputs to floats
            bushes = float(bushes)
            kilos = float(kilos)
            size = float(size)
        except ValueError:
            # Handle invalid numeric input error
            return "Invalid numeric input. Please enter valid numbers for bushes, kilos, and size."

        # Create a cursor object to execute SQL queries
        cursor = mdb.cursor()

        # Insert the new farmer into the farmers table
        query = "INSERT INTO farmers (id_number, name, bushes, kilos, size) VALUES (%s, %s, %s, %s, %s)"
        values = (id_number, name, bushes, kilos, size)
        cursor.execute(query, values)

        # Commit the changes to the database
        mdb.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the prediction page after successful registration
        return redirect("/predict")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get the form data
        username = request.form["username"]
        password = request.form["password"]

        # Create a cursor object to execute SQL queries
        cursor = mdb.cursor()

        # Check if the username exists in the database
        query = "SELECT * FROM admin WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            # Verify the password
            if password == user[1]:
                # Password is correct, login successful
                # Redirect to the home page or any other page you want
                return redirect("predict")

        # Close the cursor and database connection
        cursor.close()
        mdb.close()

        return "Invalid username or password. Please try again."

    return render_template("Login.html")


@app.route("/search", methods=["GET"])
def search():
    search_id = request.args.get("search_id")

    # Perform the search in the database
    cursor = mdb.cursor()
    query = "SELECT name, bushes, kilos, size FROM farmers WHERE id_number = %s"
    cursor.execute(query, (search_id,))
    farmer = cursor.fetchone()
    cursor.close()

    if farmer:
        farmer_name = farmer[0]
        bushes = farmer[1]
        kilos = farmer[2]
        size = farmer[3]
        message = ""  # Initialize the message variable
    else:
        farmer_name = ""
        bushes = ""
        kilos = ""
        size = ""
        message = "Farmer ID does not exist"  # Assign a value to the message variable

    return render_template("index.html", search_id=search_id, farmer_name=farmer_name, bushes=bushes, kilos=kilos, size=size, message=message)


@app.route('/predict', methods=['POST'])
def submit():

    id_number = request.form['id_number']
    farmer_name = request.form['farmer_name']
    bushes = request.form['bushes']
    kilos = request.form['kilos']
    size = request.form['size']
    fertilizer = request.form['prediction']

    cursor = mdb.cursor()
    query = "INSERT INTO predicted_fertilizers (id_number, farmer_name, bushes, kilos, size, fertilizer) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (id_number, farmer_name, bushes, kilos, size, fertilizer)
    cursor.execute(query, values)
    mdb.commit()
    cursor.close()
    mdb.close()

    return redirect('/predict')


if __name__ == '__main__':
    app.run(debug=True)
