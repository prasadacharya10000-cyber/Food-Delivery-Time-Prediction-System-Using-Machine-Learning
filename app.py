import re

from flask import Flask, render_template, request,redirect, url_for,flash,session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash  
import joblib
import numpy as np



app=Flask(__name__)
app.secret_key ='1122'

model=joblib.load('delivery_time_model.pkl')  #load the trained model
 #load the label encoder for categorical features

#database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",    
        password="",
        database="food_db",
        #port=3306 --default port for MySQL, can be omitted if using default
    )

@app.route('/')  #/ for root page
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

@app.route('/predict', methods=['GET','POST'])
def predict():
    #check login status
    if 'user_id' not in session:
        flash('Please log in to access the prediction page.', 'warning')
        return redirect(url_for('login'))
    prediction_text=None

    if request.method=='POST':
        #take user input
        distance=float(request.form['Distance'])
        Traffic_Level=request.form['Traffic_Level']
        Preparation_Time_min=int(request.form['Preparation_Time_min'])
        Courier_Experience_yrs=float(request.form['Courier_Experience_yrs'])
        Weather=request.form['Weather']
        Time_of_Day=request.form['Time_of_Day']
        Vehicle_Type=request.form['Vehicle_Type']

        #mapping
        if Traffic_Level=='Low':
            Traffic_Level=0
        elif Traffic_Level=='Medium':
            Traffic_Level=1
        else:
            Traffic_Level=2

        #weather encoding
        Weather_Clear=0
        Weather_Foggy=0
        Weather_Rainy=0
        Weather_Snowy=0
        Weather_Windy=0

        if Weather=='Clear':
            Weather_Clear=1
        if Weather=='Foggy':
            Weather_Foggy=1
        if Weather=='Rainy':
            Weather_Rainy
        if Weather=='Snowy':
            Weather_Snowy=1
        else:
            Weather_Windy=1

        #day of time
        Time_of_Day_Afternoon=0
        Time_of_Day_Evening=0
        Time_of_Day_Morning=0
        Time_of_Day_Night=0


        if Time_of_Day=='Afternoon':
            Time_of_Day_Afternoon=1
        if Time_of_Day=='Evening':
            Time_of_Day_Evening=1
        if Time_of_Day=='Morning':
            Time_of_Day_Morning=1
        else:
            Time_of_Day_Windy=1

        #Vehicle_Type
        Vehicle_Type_Bike=0
        Vehicle_Type_Car=0
        Vehicle_Type_Scooter=0

        if Vehicle_Type=='Bike':
            Vehicle_Type_Bike=1
        if Vehicle_Type=='Car':
            Vehicle_Type_Car=1
        else:
            Vehicle_Type_Scooter=1

        #-----final feature vector-----
        data=[[
            distance,        
            Traffic_Level,              
            Preparation_Time_min,        
            Courier_Experience_yrs,    
            Weather_Clear,              
            Weather_Foggy,               
            Weather_Rainy,               
            Weather_Snowy,               
            Weather_Windy,               
            Time_of_Day_Afternoon,       
            Time_of_Day_Evening,        
            Time_of_Day_Morning,         
            Time_of_Day_Night,          
            Vehicle_Type_Bike,          
            Vehicle_Type_Car,           
            Vehicle_Type_Scooter,
        ]]
        #convert to numpy
        data=np.array(data)

        #------prediction----
        prediction=model.predict(data)[0] #[0]----uses indexing,prints without []
        prediction_text=f"Estimated Delivery Time: {round(prediction,2)} minutes"
                
    return render_template('predict.html', prediction_text=prediction_text)  

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        uname=request.form['uname']
        email=request.form['email']
        password=request.form['password']
        #basic validation
        if not uname.strip():
            flash('username is required','danger')
            return redirect(url_for('register'))
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):   #regular expression to validate email format  
            flash('Invalid email address', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash("password must be at least 6 characters long", 'danger')
            return redirect(url_for('register'))
        
        hashed_password=generate_password_hash(password)  #hash the password for security
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT u_id FROM users WHERE email=%s",(email,))
        if cursor.fetchone():
            flash('Email already registered', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        
        #insert users
        cursor.execute(
            "INSERT INTO users (username,email,password) VALUES (%s,%s,%s)",
            (uname,email,hashed_password)
            )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

#Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        
        email=request.form['email']
        password=request.form['password']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):   #regular expression to validate email format  
            flash('Invalid email address', 'danger')
            return redirect(url_for('login'))
        
        if len(password) < 6:
            flash("password must be at least 6 characters long", 'danger')
            return redirect(url_for('login'))
        
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user=cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']=user['u_id']
            session['username']=user['username']
            flash('Login successful!','success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password','danger')
            return redirect(url_for('login')) 
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


    

if __name__ == '__main__':
    app.run(debug=True)