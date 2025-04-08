from flask import Flask, request, render_template, redirect, url_for, session, flash
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Load the dataset
df = pd.read_excel("Food_Recommendation_Climate_Disease.xlsx")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure secret key

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user_id"] = response.user.id
            return redirect(url_for("home"))
        except Exception as e:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        # Basic validation
        if not email or not password or not confirm_password:
            flash("All fields are required")
            return redirect(url_for("register"))
            
        # Email format validation
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash("Please enter a valid email address")
            return redirect(url_for("register"))
            
        # Password validation
        if len(password) < 8:
            flash("Password must be at least 8 characters long")
            return redirect(url_for("register"))
            
        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))
        
        try:
            # Attempt to create auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "email": email
                    }
                }
            })
            
            if not auth_response.user:
                flash("Registration failed. Please try again.")
                return redirect(url_for("register"))
            
            # Create user profile
            profile_data = {
                "id": auth_response.user.id,
                "email": email
            }
            
            profile_response = supabase.table("user_profiles").insert(profile_data).execute()
            
            if not profile_response.data:
                # If profile creation fails, attempt to delete the auth user
                try:
                    supabase.auth.admin.delete_user(auth_response.user.id)
                except Exception as cleanup_error:
                    print(f"Failed to cleanup auth user: {cleanup_error}")
                flash("Registration failed. Please try again.")
                return redirect(url_for("register"))
            
            session["registration_success"] = True
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
                
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                flash("This email is already registered")
            elif "password" in error_msg.lower():
                flash("Password is too weak. Please use a stronger password")
            else:
                print(f"Registration error: {error_msg}")
                flash("Registration failed. Please try again.")
            return redirect(url_for("register"))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Get input data from the form
    climate = request.form["climate"]
    temperature = float(request.form["temperature"])
    season = request.form["season"]
    disease = request.form["disease"]

    # Validate temperature range
    if temperature < -20 or temperature > 50:
        flash("Temperature must be between -20°C and 50°C for accurate recommendations.")
        return redirect(url_for("home"))

    # Filter the dataset based on input conditions
    filtered_df = df[
        (df['Climate'] == climate) &
        (df['Season'] == season) &
        (df['Disease'] == disease)
    ]

    # If no exact match, find the closest temperature match
    if len(filtered_df) == 0:
        filtered_df = df[
            (df['Climate'] == climate) &
            (df['Season'] == season) &
            (df['Disease'] == disease)
        ]
        # Find the row with the closest temperature
        if len(filtered_df) > 0:
            filtered_df['temp_diff'] = abs(filtered_df['Temperature (°C)'] - temperature)
            filtered_df = filtered_df.sort_values('temp_diff').head(1)

    if len(filtered_df) > 0:
        recommended_food = filtered_df['Recommended Food'].iloc[0]
        nutritional_benefit = filtered_df['Nutritional Benefit'].iloc[0]
    else:
        recommended_food = "No specific recommendation found"
        nutritional_benefit = "Please try different combinations"

    # Store the results in session
    session["climate"] = climate
    session["temperature"] = temperature
    session["season"] = season
    session["disease"] = disease
    session["recommended_food"] = recommended_food
    session["nutritional_benefit"] = nutritional_benefit

    # Redirect to the result page
    return redirect(url_for("result"))

@app.route("/result")
def result():
    # Retrieve the stored session data
    return render_template("result.html",
                           climate=session.get("climate"),
                           temperature=session.get("temperature"),
                           season=session.get("season"),
                           disease=session.get("disease"),
                           recommended_food=session.get("recommended_food"),
                           nutritional_benefit=session.get("nutritional_benefit"))

if __name__ == "__main__":
    app.run(debug=True)
